#!/usr/bin/env python

"""
This example shows how to enable the adhoc mode with a mobility model
and track network information every time a station moves.
"""

import sys
import time
import threading
import math
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import adhoc
from mn_wifi.mobility import Mobility

def track_station_information(station, timestamp, network_info, file):
    info = (f"Station {station.name} information: "
            f"Coordination: {station.position}, "
            f"Parameters: {station.params}, "
            f"Wireless Interfaces: {station.wintfs}, "
            f"Frequency: {station.wintfs[0].freq}, "
            f"Mode: {station.wintfs[0].mode}, "
            f"Tx Power: {station.wintfs[0].txpower}, "
            f"Range: {station.wintfs[0].range}, "
            f"Antenna Gain: {station.wintfs[0].antennaGain}"
            # f"Received signal strength indicator: {station.wintfs[0].rssi}" # adhoc has no 'rssi'
            )

    network_info += info

    # Write the information to the file
    file.write(f"{network_info}\n")

def calculate_distance(net, sta1, sta2):
    pos1 = sta1.position
    pos2 = sta2.position
    # Extract coordinates from the positions
    x1, y1, z1 = pos1
    x2, y2, z2 = pos2

    # Calculate the Euclidean distance
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distance


def track_network_information(net, file):
    while True:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        # Write the information to the file
        file.write(f"\nTimestamp: {timestamp}\n")
        network_info= ""
        recorded_distances = set()  # Set to store recorded distances

        for sta in net.stations:
            track_station_information(sta, timestamp, network_info, file)
        for sta1 in net.stations:
            for sta2 in net.stations:
                if sta1 != sta2:
                    distance_pair = frozenset({sta1.name, sta2.name})
                    if distance_pair not in recorded_distances:
                        distance = calculate_distance(net, sta1, sta2)
                        file.write(f"Distance between {sta1.name} and {sta2.name}: {distance:.2f} meters,")
                        recorded_distances.add(distance_pair)

        file.flush()  # Flush the buffer to ensure data is written immediately
        time.sleep(5)  # Sleep for 5 seconds before the next iteration

def topology(args):
    "Create a network."
    net = Mininet_wifi()

    info("*** Creating nodes\n")
    kwargs = {}
    if '-a' in args:
        kwargs['range'] = 100
    sta1 = net.addStation('sta1', mac='00:00:00:00:00:02', ip='10.0.0.2/8',
                    min_x=10, max_x=30, min_y=50, max_y=70, min_v=5, max_v=10)
    sta2 = net.addStation('sta2', ip='10.0.0.3/8',
                   min_x=60, max_x=70, min_y=10, max_y=20, min_v=1, max_v=5)
    sta3 = net.addStation('sta3', ip='10.0.0.4/8',
                    min_x=30, max_x=40, min_y=5, max_y=80, min_v=3, max_v=8)
    c1 = net.addController('c1')

    info("*** Configuring propagation model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring nodes\n")
    net.configureNodes()

    if '-p' not in args:
        net.plotGraph()

    net.setMobilityModel(time=0, model='RandomDirection',
                         max_x=100, max_y=100, seed=20)

    info("*** Associating and Creating links\n")
    net.addLink(sta1, cls=adhoc, intf='sta1-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)
    net.addLink(sta2, cls=adhoc, intf='sta2-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)
    net.addLink(sta3, cls=adhoc, intf='sta3-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)

    info("*** Starting network\n")
    net.build()

    info("\n*** Addressing...\n")
    sta1.setIP('10.0.0.2/8', intf="sta1-wlan0")
    sta2.setIP('10.0.0.3/8', intf="sta2-wlan0")
    sta3.setIP('10.0.0.4/8', intf="sta3-wlan0")

    # Open file for writing network information
    with open("network_information.txt", "w") as file:
        # Start tracking network information in a separate thread
        tracking_thread = threading.Thread(target=track_network_information, args=(net, file))
        tracking_thread.start()

        info("*** Running CLI\n")
        CLI(net)

        # Stop tracking thread when CLI is exited
        tracking_thread.join()

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
