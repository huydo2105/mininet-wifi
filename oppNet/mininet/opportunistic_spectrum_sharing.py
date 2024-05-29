from mn_wifi.net import Mininet_wifi
# from mininet.node import Controller, OVSKernelAP
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.wmediumdConnector import interference
from math import sqrt
import threading
import time
import argparse
import random
import matplotlib
matplotlib.use('Agg')

# Opportunistic Network Node class
class OpportunisticNode:
    def __init__(self, name, net):
        self.name = name
        self.node = net.get(name)
        self.net = net
        self.message_queue = []
        self.channel_lock = threading.Lock()

    def send_message(self, message, dest):
        print(f"{self.name} sending message to {dest}")
        self.message_queue.append((message, dest))

    def receive_message(self):
        if self.message_queue:
            message, dest = self.message_queue.pop(0)
            print(f"{self.name} received message: {message} for {dest}")
            # Simulate message forwarding in opportunistic manner
            if dest == self.name:
                print(f"{self.name} received final message: {message}")
            else:
                # Forward the message to another node (randomly chosen here)
                self.forward_message(message, dest)

    def forward_message(self, message, dest):
        # Simulate opportunistic forwarding by sending to a random neighbor
        closest_neighbor = self.get_closest_neighbor()
        if closest_neighbor:
            print(f"{self.name} forwarding message to {closest_neighbor.name}")
            closest_neighbor.send_message(message, dest)
    
    def get_neighbors(self):
        neighbors = []
        for intf in self.node.wintfs.values():
            for neighbor in intf.rangeNodes:
                if neighbor != self.node:
                    neighbors.append(OpportunisticNode(neighbor.name, self.node.wintfs))
        return neighbors

    def get_closest_neighbor(self):
        neighbors = []
        for sta in self.node.wintfs.values():
            for other_node in self.net.stations:
                if other_node != self.node:
                    distance = self.distance_to(other_node)
                    if distance <= sta.range:
                        neighbors.append((other_node, distance))

        if neighbors:
            # Find the closest neighbor
            closest_neighbor = min(neighbors, key=lambda x: x[1])[0]
            return OpportunisticNode(closest_neighbor.name, self.node.wintfs)
        return None

    def distance_to(self, other_node):
        x1, y1, _ = self.node.position
        x2, y2, _ = other_node.position
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


    def dynamic_spectrum_access(self):
        while True:
            free_channels = [1, 6, 11]
            with self.channel_lock:
                current_channel = self.node.params['channel']
                new_channel = next((ch for ch in free_channels if ch != current_channel), current_channel)
                if new_channel != current_channel:
                    print(f"DSA: {self.name} switching from channel {current_channel} to {new_channel}")
                    self.node.setChannel(new_channel)
            time.sleep(10)

    def cognitive_radio(self):
        while True:
            occupied_channels = random.sample([1, 6, 11], k=1)
            available_channels = [ch for ch in [1, 6, 11] if ch not in occupied_channels]
            if available_channels:
                with self.channel_lock:
                    current_channel = self.node.params['channel']
                    new_channel = random.choice(available_channels)
                    if new_channel != current_channel:
                        print(f"CR: {self.name} switching from channel {current_channel} to {new_channel}")
                        self.node.setChannel(new_channel)
            time.sleep(10)

def setup_network(num_stations):
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)
    c0 = net.addController('c0')

    
    info("*** Creating nodes\n")
    stations = []
    for i in range(num_stations):
        stations.append(net.addStation(f'sta{i+1}', position=f'{10 * (i+1)},40,0'))

    info("*** Configuring wifi nodes\n")
    net.setPropagationModel(model="logDistance", exp=4)
    net.configureWifiNodes()
    net.plotGraph()

    net.setMobilityModel(time=0, model='RandomDirection', max_x=250, max_y=250, seed=20)

    info("*** Creating ad-hoc links\n")
    for sta in stations:
        net.addLink(sta, cls=adhoc, intf=f'{sta.name}-wlan0', ssid='adhocNet', mode='g', channel=5)

    info("*** Starting network\n")
    net.build()
    c0.start()

    return net, stations

def plot_network_graph(stations):
    G = nx.Graph()

    for sta in stations:
        G.add_node(sta.name)

    for sta in stations:
        for other_sta in stations:
            if sta != other_sta:
                dist = sqrt((sta.params['position'][0] - other_sta.params['position'][0]) ** 2 + 
                            (sta.params['position'][1] - other_sta.params['position'][1]) ** 2)
                if dist <= sta.params['range']:
                    G.add_edge(sta.name, other_sta.name)

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=500, node_color="skyblue", font_size=10, font_color="black", font_weight="bold")
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ad-hoc network simulation")
    parser.add_argument('num_stations', type=int, help="Number of stations in the network")
    parser.add_argument('-p', '--plot', action='store_true', help="Plot the network graph")
    args = parser.parse_args()

    setLogLevel('info')
    net, stations = setup_network(args.num_stations)

    # Opportunistic nodes
    nodes = [OpportunisticNode(sta.name, net) for sta in stations]

    # Dynamic Spectrum Access and Cognitive Radio Threads
    for node in nodes:
        dsa_thread = threading.Thread(target=node.dynamic_spectrum_access)
        cr_thread = threading.Thread(target=node.cognitive_radio)
        dsa_thread.daemon = True
        cr_thread.daemon = True
        dsa_thread.start()
        cr_thread.start()

    # Simulate Opportunistic Networking
    nodes[0].send_message('Hello, sta3!', 'sta3')
    for _ in range(10):
        for node in nodes:
            node.receive_message()
        time.sleep(2)

    CLI(net)
    net.stop()