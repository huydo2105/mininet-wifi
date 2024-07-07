import os
import time
import threading
import re
from math import sqrt
from scapy.all import *

class OpportunisticNode:
    def __init__(self, name, net):
        self.name = name
        self.node = net.get(name)
        self.net = net
        self.received_messages = set()
        self.interface = 'bat0' 
        # self.interface = self.node.wintfs[0].name 

    def send_packet(self, dest, message):
        if isinstance(dest, OpportunisticNode):
            dest = dest.node.name
        print(f"{self.name} sending packet to {dest} with message: {message}")
        closest_neighbor = self.get_closest_neighbor()
        if closest_neighbor:
            print(f"{self.name} forwarding packet to closest neighbor {closest_neighbor.node.name}")
            src_ip = self.node.IP()
            dst_ip = closest_neighbor.node.IP()
            print(f"Source IP: {src_ip}, Destination IP: {dst_ip}, Interface: {self.interface}")
            
            # Verify if the interface exists
            if self.interface not in self.node.cmd('ip link show'):
                print(f"Interface {self.interface} does not exist on {self.name}")
                return

            packet = IP(src="192.168.123.1", dst="192.168.123.3") / ICMP(type='echo-request', id=1, seq=1) / message
            try:
                sendp(packet, iface="bat0")
            except Exception as e:
                print(f"An error occurred while sending packet: {e}")

    def get_closest_neighbor(self, exclude=[]):
        neighbors = []
        for sta in self.net.stations:
            if sta.IP() not in exclude and sta != self.node:
                distance = self.distance_to(sta)
                if distance <= self.node.wintfs[0].range:
                    neighbors.append((sta, distance))
        if neighbors:
            closest_neighbor = min(neighbors, key=lambda x: x[1])[0]
            return OpportunisticNode(closest_neighbor.name, self.net)
        return None

    def distance_to(self, other_node):
        x1, y1, _ = self.node.position
        x2, y2, _ = other_node.position
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def extract_destination_from_message(self, message):
        match = re.search(r'sta\d', message)
        if match:
            return match.group(0)
        return None

    def execute_cmd(self, cmd, retries=3):
        for attempt in range(retries):
            try:
                result = self.node.cmd(cmd)
                return result
            except AssertionError:
                if attempt < retries - 1:
                    time.sleep(1)
                else:
                    raise
                    
    def setChannel(self, channel):
        "Set Channel"
        from mn_wifi.node import AP
        self.channel = channel
        if isinstance(self, AP):
            self.setAPChannel(channel)
        elif isinstance(self, mesh):
            self.setMeshChannel(channel)
        elif isinstance(self, adhoc):
            self.ibss_leave()
            adhoc(node=self.node, intf=self, chann=channel)