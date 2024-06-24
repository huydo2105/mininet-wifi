import os
import time
import threading
import re
from math import sqrt

class OpportunisticNode:
    def __init__(self, name, net):
        self.name = name
        self.node = net.get(name)
        self.net = net
        self.received_messages = set()
        self.interface = self.node.wintfs[0].name  # Get the correct interface name
        self.tcpdump_output_file = f'/home/huydq/Mininet/mininet-wifi/oppNet/mininet/{self.name}_tcpdump.out'
        self.last_packet_timestamp  = "00:00:00.000000"

    def send_packet(self, dest, message):
        if isinstance(dest, OpportunisticNode):
            dest = dest.node.name
        message_with_dest = f"{dest}:{message}"
        print(f"{self.name} sending packet to {dest} with message: {message_with_dest}")
        closest_neighbor = self.get_closest_neighbor()
        if closest_neighbor:
            print(f"{self.name} forwarding packet to closest neighbor {closest_neighbor.node.name}")
            cmd = f'ping -c 1 -p {message_with_dest.encode().hex()} {closest_neighbor.node.IP()}'
            result = self.execute_cmd(cmd)

    def pkt_callback(self, sender_ip, hex_payload):
        print(f"{self.name} received packet from {sender_ip}: {hex_payload}")
        
        message_with_dest = bytes.fromhex(hex_payload).decode('utf-8', errors='ignore')
        if message_with_dest not in self.received_messages:
            self.received_messages.add(message_with_dest)
            dest_node_name = self.extract_destination_from_message(message_with_dest)
            if dest_node_name != self.name:
                dest_node = self.net.get(dest_node_name)
                if dest_node:
                    self.forward_packet(sender_ip, message_with_dest)
            else:
                print(f"{self.name} is the final destination for message: {message_with_dest}")
        # else:
        #     print(f"{self.name} already processed the message: {message_with_dest}")


    def receive_packet(self):
        print(f"{self.name} starting to listen on {self.interface}")
        tcpdump_cmd = f'tcpdump icmp -l -i {self.interface} -nn -x -c 1 > {self.tcpdump_output_file} 2>&1 &'
        self.node.cmd(tcpdump_cmd)
        reader_thread = threading.Thread(target=self.read_tcpdump_output)
        reader_thread.daemon = True
        reader_thread.start()

    def read_tcpdump_output(self):
        print(f"{self.name} starting to writing incomming message to '/home/huydq/Mininet/mininet-wifi/oppNet/mininet/{self.name}_tcpdump.out'")
        while True:
            if os.path.exists(self.tcpdump_output_file):
                with open(self.tcpdump_output_file, 'r') as f:
                    hex_payload = ""
                    sender_ip = ""
                    current_packet_timestamp = ""
                    capturing = False
                    for line in f:
                        stripped_line = line.strip()
                        if "IP" in stripped_line and ">" in stripped_line:
                            # Extract timestamp and sender IP address
                            parts = stripped_line.split()
                            current_packet_timestamp == parts[0]
                            sender_ip = parts[2]
                        if stripped_line.startswith("0x0030"):
                            parts = line.split()
                            hex_data = ''.join(parts[1:])  # Skip the initial offset part
                            hex_payload += hex_data.replace(' ', '')  # Remove any spaces in the hex data
                            capturing = True
                        elif capturing:
                            break
                    if self.last_packet_timestamp != current_packet_timestamp and hex_payload and sender_ip:
                        self.last_packet_timestamp = current_packet_timestamp
                        self.process_captured_message(sender_ip, hex_payload)
                time.sleep(10)  # Add a small delay to avoid busy-waiting

    def process_captured_message(self, sender_ip, hex_payload):
        # Process the captured message
        non_iterative_sequence = ""
        i = 0
        while i < len(hex_payload) - 4:
            current_chunk = hex_payload[i:i + 4]
            next_chunk = hex_payload[i + 4:i + 8]
            if next_chunk in non_iterative_sequence:
                non_iterative_sequence += current_chunk
                break
            else:
                # Append the current chunk to non_iterative_sequence
                non_iterative_sequence += current_chunk
                i += 4
        # Pass the non-iterative sequence to pkt_callback
        self.pkt_callback(sender_ip, non_iterative_sequence)

    def forward_packet(self, sender_ip, message):
        closest_neighbor = self.get_closest_neighbor(exclude=[sender_ip, self.node.IP()])
        if closest_neighbor:
            print(f"{self.name} forwarding packet to closest neighbor {closest_neighbor.node.name}")
            cmd = f'ping -c 1 -p {message.encode().hex()} {closest_neighbor.node.IP()}'
            self.execute_cmd(cmd)

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