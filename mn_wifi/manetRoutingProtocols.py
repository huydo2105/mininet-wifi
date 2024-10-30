# author: Ramon Fontes (ramonrf@dca.fee.unicamp.br)

from re import findall
from os import getpid
from threading import Thread
from time import time, sleep
from random import randint
import socket
import uuid  # For generating unique packet IDs
import socket
from mininet.log import info
from random import randrange


class manetProtocols(object):
    def __init__(self, intf, proto_args, node=None, mn_wifi=None):
        if intf.proto == 'epidemic':
            self.protocol = epidemic(node, mn_wifi)
        else:
            self.protocol = eval(intf.proto)(intf, proto_args)

    def stopProtocol(self):
        if hasattr(self, 'stopProtocol'):
            self.protocol.stopProtocol()
        else:
            print("Protocol not initialized or does not exist.")

class batmand(object):
    def __init__(self, intf, proto_args):
        self.set_batmand_iface(intf, proto_args)

    def set_batmand_iface(self, intf, proto_args):
        intf.cmd('batmand {} {}'.format(proto_args, intf.name))


class batman_adv(object):
    def __init__(self, intf, proto_args):
        self.load_module(intf)
        self.add_iface(intf)
        self.set_link_up(intf)

    def add_iface(self, intf):
        intf.cmd('batctl if add %s' % intf.name)

    def set_link_up(self, intf):
        intf.cmd('ip link set up dev bat0')
        self.setIP(intf)

    def setIP(self, intf):
        nums = findall(r'\d+', intf.node.name)[0]
        intf.cmd('ip addr add 192.168.123.%s/24 '
                 'dev bat0' % nums)

    def load_module(self, intf):
        intf.cmd('modprobe batman-adv')


class olsrd(object):
    def __init__(self, intf, proto_args):
        cmd = 'olsrd -i %s -d 0 ' % intf.name
        cmd += proto_args
        intf.cmd(cmd)
        info('Starting olsrd in {}...\n'.format(intf.name))


class olsrd2(object):
    def __init__(self, intf, proto_args):
        pid = getpid()
        filename = "mn_{}_{}.staconf ".format(intf.node, pid)
        cmd = "echo \"[global]\nlockfile %s.lock\" >> %s " % (intf.name, filename)
        intf.cmd(cmd + ' &')
        cmd = 'olsrd2_static %s -l %s & ' % (intf.name, filename)
        cmd += proto_args
        intf.cmd(cmd)
        info('Starting olsrd2 in {}...\n'.format(intf.name))


class babel(object):
    def __init__(self, intf, proto_args):
        pid = getpid()
        cmd = "babeld {} -I mn_{}_{}.staconf ".format(intf.name, intf.node, pid)
        cmd += proto_args
        intf.cmd(cmd + ' &')
        info('Starting babeld in {}...\n'.format(intf.name))

class epidemic(object):
    def __init__(self, node, mn_wifi, hopCount=9, queueLength=9, queueEntryExpireTime=100,
                 hostRecentPeriod=10, beaconInterval=10, beaconRandomness=1000):
        """
        Initialize the Epidemic Routing protocol for given stations.
        :param stations: List of OpportunisticNetworkNode stations
        :param hopCount: Maximum number of times a packet will be flooded
        :param queueEntryExpireTime: Maximum time a packet can live in the epidemic
                                    queues since generated at the source
        :param hostRecentPeriod: Time in seconds for host recent period, in which hosts
                            can not re-exchange summary vectors
        :param beaconInterval: Time in seconds after which a beacon packet is broadcast
        :param beaconRandomness: Upper bound of the uniform distribution random time
                                added to avoid collisions, in milliseconds
        """
        self.station = node
        self.mn = mn_wifi
        self.hopCount = hopCount
        self.queueLength = queueLength
        self.queueEntryExpireTime = queueEntryExpireTime
        self.hostRecentPeriod = hostRecentPeriod
        self.beaconInterval = beaconInterval
        self.beaconRandomness = beaconRandomness
        self.packet_id = 0
        self.startProtocol()

    def broadcastBeacon(self, station):
        """
        Each station broadcasts a beacon with its IP address to find neighbors.
        """
        while True:
            # Simulating the beacon broadcast with the station's IP address.
            print("{}: broadcasting beacon".format(station.name))
            
            # Check for neighboring stations within the range.
            neighbors = self.findNeighbors(station)
            if neighbors:
                print("{}: found neighbors: {}".format(station.name, [neighbor.name for neighbor in neighbors]))

                # Create a unique packet ID and set expiration time to 2 minutes (120 seconds)
                packet_id = '{}-{}-{}'.format(self.station.name, neighbors[-1].name, self.packet_id)  # Generate a global packet ID
                self.packet_id += 1
                start_time = time()
                expire_time = start_time + 120  # Set expiration time 2 minutes from now
                destination_index = randrange(0, len(neighbors))
                
                # Create a packet with source, destination, and other details
                packet = {
                    'source': station.name,
                    'destination': neighbors[destination_index].name,  # Set destination to the neighbor's IP
                    'packet_id': packet_id,
                    'start_time': start_time,
                    'expire_time': expire_time,
                    'hopCount': 0,
                    'hops': [],
                    'content': "Data from {} to {}".format(station.name, neighbors[destination_index].name)
                }

                # Enqueue the packet into the station's packet queue
                result = station.enqueue(station, packet)

                if result:
                    # Send a packet back to the neighbor stations with its IP address.
                    station.sendSummaryVector(neighbors)

            sleep(5)

    def findNeighbors(self, station):
        """
        Check if there are any neighbor nodes within the specified range.
        :param station: The station broadcasting the beacon
        :return: List of neighboring stations within the range
        """
        neighbors = []
        for other_station in self.mn.stations:
            if other_station != self.station:
                if self.mn.get_distance_number(station.name, other_station.name) <= station.wintfs[0].range:
                    neighbors.append(other_station)
        return neighbors

    def listenForSummaryVectors(self, station):
        """
        Continuously listen for incoming summary vectors and process them.
        """
        station.listenForSummaryVectors(station)


    def startProtocol(self):
        """
        Start the epidemic routing protocol on the station by initiating the beacon broadcast
        and listen summary vector
        """
        sleep(10)
        # Start the summary vector listening thread.
        self.listen_thread = Thread(target=self.listenForSummaryVectors, args=(self.station,))
        self.listen_thread.daemon = True
        self.listen_thread.start()

        sleep(10)
        # Start beacon broadcasting thread.
        self.broadcast_thread = Thread(target=self.broadcastBeacon, args=(self.station,))
        self.broadcast_thread.daemon = True  # Make it a daemon thread
        self.broadcast_thread.start()

