from scapy.all import *
import sys
import json
from math import sqrt

def pkt_callback(pkt, name, iface, ip):
    message = bytes.fromhex(pkt.load.hex()).decode('utf-8', errors='ignore')
    print(f"{name} received packet: {message}")
    if IP in pkt:
        if pkt[IP].dst == ip:
            message = bytes.fromhex(pkt.load.hex()).decode('utf-8', errors='ignore')
            print(f"{name} received packet: {message}")
            print(f"{name} is the final destination for message: {message}")

if __name__ == '__main__':
    name = sys.argv[1]
    iface = sys.argv[2]
    ip = sys.argv[3]
    nodeRange = sys.argv[4]
    print(f"{name} starting to sniff on {iface}")
    # sniff(iface=iface, prn=lambda pkt: pkt_callback(pkt, name, iface, ip), filter="icmp", store=0)  
    sniff(iface=iface, prn=lambda pkt: pkt_callback(pkt, name, iface, ip), store=0)  
