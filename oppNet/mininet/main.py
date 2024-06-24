import argparse
import time
import threading
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from opportunistic_node import OpportunisticNode
from network_setup import setup_network

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ad-hoc network simulation")
    parser.add_argument('num_stations', type=int, help="Number of stations in the network")
    args = parser.parse_args()

    setLogLevel('info')
    net, stations = setup_network(args.num_stations)

    nodes = [OpportunisticNode(sta.name, net) for sta in stations]

    # Start message listener threads
    for node in nodes:
        listener_thread = threading.Thread(target=node.receive_packet)
        listener_thread.daemon = True
        listener_thread.start()
    # # Start message listener threads
    # for sta in stations:
    #     start_scapy_on_station(sta, sta.name, f'{sta.name}-wlan0', sta.IP(), sta.wintfs[0].range)

    # Ensure nodes are fully initialized
    time.sleep(30)  

    # Simulate Opportunistic Networking
    nodes[0].send_packet(nodes[2], 'Hello')

    CLI(net)
    net.stop()
