import sys
from select import poll

from mininet.cli import CLI as MN_CLI
from mininet.log import output, error
from scapy.all import *
from scapy.config import conf

class CLI(MN_CLI):
    "Simple command-line interface to talk to nodes."
    MN_CLI.prompt = 'mininet-wifi> '

    def __init__(self, mn_wifi, stdin=sys.stdin, script=None, cmd=None):
        self.cmd = cmd
        if self.cmd:
            MN_CLI.mn = mn_wifi
            MN_CLI.stdin = stdin
            MN_CLI.inPoller = poll()
            MN_CLI.locals = { 'net': mn_wifi }
            self.do_cmd(self.cmd)
            return
        MN_CLI.__init__(self, mn_wifi, stdin=stdin, script=script)

    def do_cmd(self, cmd):
        """Read commands from an input file.
           Usage: source <file>"""
        MN_CLI.onecmd(self, line=cmd)
        self.cmd = None

    def do_stop(self, line):
        "Stop mobility for a while"
        self.mn.stop_simulation()

    def do_start(self, line):
        "Pause mobility for a while"
        self.mn.start_simulation()

    def do_distance(self, line):
        "Distance between two nodes."
        args = line.split()
        if len(args) != 2:
            error('invalid number of args: distance [sta or ap] [sta or ap]\n')
        elif len(args) == 2 and args[0] == args[1]:
            error('Invalid. Source and Destination are equal\n')
        else:
            self.mn.get_distance(*args)

    def do_dpctl(self, line):
        """Run dpctl (or ovs-ofctl) command on all switches.
           Usage: dpctl command [arg1] [arg2] ..."""
        args = line.split()
        if len(args) < 1:
            error('usage: dpctl command [arg1] [arg2] ...\n')
            return
        nodesL2 = self.mn.switches + self.mn.aps
        for sw in nodesL2:
            output('*** ' + sw.name + ' ' + ('-' * 72) + '\n')
            output(sw.dpctl(*args))
    def do_opportunistic(self, line):
        """Simulate opportunistic network where each station has a queue of pending packets.
           Stations transfer and forward packets to each other every 10 seconds.
           Usage: opportunistic"""
        
        # Start the simulation in a separate thread to allow CLI to remain responsive
        sim_thread = Thread(target=self.run_opportunistic_network)
        sim_thread.daemon = True
        sim_thread.start()

    def run_opportunistic_network(self):
        """Simulate the opportunistic network."""
        while True:
            for station in self.mn.stations:
                self.process_station_queue(station)
            time.sleep(10)

    def process_station_queue(self, station):
        """Process the packet queue for a station."""
        queue = self.packet_queues[station.name]

        if queue:
            new_queue = []
            for packet_info in queue:
                dest_node, content = packet_info
                success = self.forward_packet(station.name, dest_node, content)
                if not success:
                    new_queue.append(packet_info)
            self.packet_queues[station.name] = new_queue

    def do_sendpacket(self, line):
        """Send a packet with content to a destination node by transferring through neighbor nodes until it reaches the destination.
            Usage: sendpacket <source_node> <destination_node> <content>"""
        args = line.split()
        if len(args) != 3:
            error('Usage: sendpacket <source_node> <destination_node> <content>\n')
            return
        
        source_node, dest_node, content = args[0], args[1], args[2]
        
        self.forward_packet(source_node, dest_node, content)

    def forward_packet(self, source_node, dest_node, content):
        """Forward a packet from the current node to the destination node through the nearest neighbor nodes."""
        forwarded_nodes = [source_node]  # Track nodes that have already forwarded the packet
        current_node = source_node

        while True:
            # Find next node to forward packet
            forward_node = self.mn.get_nearest_node_to_dest(current_node, dest_node, exclude=forwarded_nodes)

            if not forward_node:
                error('No valid route from ' + current_node + " to " + "destination node " + dest_node + '\n')
                return

            try:
                print("{} forwarding packet to closest neighbor {}".format(current_node, forward_node))
                output, packet_reached = self.mn.pingOppNet(src_node=self.mn.nameToNode[current_node], 
                                dest_node=self.mn.nameToNode[forward_node], content="hello")
            except Exception as e:
                print("An error occurred while sending packet: {}".format(e))
                break

            # Check if packet has reached the destination
            if packet_reached:
                if self.mn.nameToNode[forward_node].IP() == self.mn.nameToNode[dest_node].IP():
                    print('Packet reached destination {}\n'.format(dest_node))
                    break
                else:
                    print('Packet are forward to neighbour node {}\n'.format(forward_node))
                    # Forward to other nodes
                    forwarded_nodes.append(forward_node)
                    current_node = forward_node
            else:
                print('Packet did not reach the destination. Storing in packet queue.\n')
                packet = (current_node, forward_node, dest_node, content)
                self.mn.nameToNode[current_node].append_packet_queue(packet)