from scapy.all import *
import sys
import json
from math import sqrt

nodeRange = 78.67262373579531
def pkt_callback(pkt, name, iface, ip):
    message = bytes.fromhex(pkt.load.hex()).decode('utf-8', errors='ignore')
    print(f"{name} received packet: {message}")
    if IP in pkt:
        if pkt[IP].dst == ip:
            message = bytes.fromhex(pkt.load.hex()).decode('utf-8', errors='ignore')
            print(f"{name} received packet: {message}")
            dest_node_name = extract_destination_from_message(message)
            if dest_node_name != name:
                forward_packet(dest_node_name, name, message)
            else:
                print(f"{name} is the final destination for message: {message}")

def forward_packet(self, sender_ip, message):
        closest_neighbor = self.get_closest_neighbor(exclude=[sender_ip, self.node.IP()])
        if closest_neighbor:
            print(f"{self.name} forwarding packet to closest neighbor {closest_neighbor.node.name}")
            packet = IP(src=self.node.IP(), dst=closest_neighbor.node.IP()) / TCP(sport=8000, dport=6653) / message
            send(packet, iface=self.interface)

def get_closest_neighbor(self, exclude=[]):
    if not self.neighbors:
        self.discover_neighbors()

    neighbors = [
        (neighbor, distance)
        for neighbor, distance in self.neighbors.items()
        if neighbor.IP() not in exclude and neighbor != self.node
    ]

    if neighbors:
        closest_neighbor = min(neighbors, key=lambda x: x[1])[0]
        return OpportunisticNode(closest_neighbor.name, self.net)
    return None

def receive_packet(self):
    print(f"{self.name} starting to listen on {self.interface}")
    sniff(iface=self.interface, filter="tcp and dst port 6653", prn=self.pkt_callback, store=0)

def discover_neighbors(self):
    # Send beacon messages to discover neighbors
    cmd = f'ping -c 1 -p {self.name.encode().hex()} 255.255.255.255'
    self.execute_cmd(cmd)
    # Listen for responses
    self.receive_packet()

def extract_destination_from_message(message):
    return message.split(':')[1]

def execute_cmd(name, cmd, retries=3):
    for attempt in range(retries):
        try:
            result = name.cmd(cmd)
            return result
        except AssertionError:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                raise

if __name__ == '__main__':
    name = sys.argv[1]
    iface = sys.argv[2]
    ip = sys.argv[3]
    nodeRange = sys.argv[4]
    print(f"{name} starting to sniff on {iface}")
    sniff(iface=iface, prn=lambda pkt: pkt_callback(pkt, name, iface, ip), filter="icmp", store=0)  
