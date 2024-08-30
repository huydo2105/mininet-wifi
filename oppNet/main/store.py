def forward_packet(self, source_node, dest_node, content):
        """Forward a packet from the source node to the destination node through the nearest neighbor nodes."""
        forwarded_nodes = [source_node]  # Track nodes that have already forwarded the packet
        current_node = source_node

        while True:
            forward_node = self.get_next_forward_node(current_node, dest_node, forwarded_nodes)

            if not forward_node:
                error(f'No valid route from {current_node} to destination node {dest_node}\n')
                return

            packet = self.create_packet(current_node, forward_node, content)
            if not self.send_and_receive_packet(packet, current_node):
                # If sending fails, retry after 10 seconds
                print(f"Retrying to send packet from {current_node} after 10 seconds...")
                time.sleep(10)
                continue
            
            # Check if packet has reached the destination
            if forward_node == dest_node:
                output(f'Packet reached destination {dest_node}\n')
                break
            
            forwarded_nodes.append(forward_node)
            current_node = forward_node

    def get_next_forward_node(self, current_node, dest_node, exclude_nodes):
        """Find the next node to forward the packet to, excluding already forwarded nodes."""
        return self.get_nearest_node_to_dest(current_node, dest_node, exclude=exclude_nodes)

    def create_packet(self, src_node, dst_node, content):
        """Create an IP packet with ICMP echo-request."""
        ip_layer = IP(src=self.mn.nameToNode[src_node].IP(), dst=self.mn.nameToNode[dst_node].IP())
        icmp_layer = ICMP(type='echo-request', id=1, seq=1) / content
        return ip_layer / icmp_layer

    def send_and_receive_packet(self, packet, current_node):
        """Send the packet and wait for a response. Return True if successful, False otherwise."""
        iface = '{}-wlan0'.format(current_node)
        try:
            print(f"Sending packet from {current_node} to {packet[IP].dst}")
            response = sr1(packet, iface=iface, timeout=2, verbose=0)
            if response:
                print(f"Received response from {response[IP].src}")
                return True
            else:
                print(f"No response received, forwarding failed.")
                return False
        except Exception as e:
            print(f"An error occurred while sending packet: {e}")
            return False