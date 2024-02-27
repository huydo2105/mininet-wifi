#!/usr/bin/env python

"""
This example shows how to enable the adhoc mode with a mobility model
and track network information every time a station moves.
"""

import sys
import time
import threading
import math
import json
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import adhoc
from mn_wifi.mobility import Mobility

def track_station_information(station):
    return {
            "coordination": station.position,
            "parameters": station.params,
            "frequency": station.wintfs[0].freq,
            "mode": station.wintfs[0].mode,
            "tx_power": station.wintfs[0].txpower,
            "range": station.wintfs[0].range,
            "antenna_gain": station.wintfs[0].antennaGain
    }


def calculate_distance(net, sta1, sta2):
    pos1 = sta1.position
    pos2 = sta2.position
    # Extract coordinates from the positions
    x1, y1, z1 = pos1
    x2, y2, z2 = pos2

    # Calculate the Euclidean distance
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distance



def track_network_information(net, file_path):
    while True:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        network_info = {"timestamp": timestamp, "stations": {}, "distances": []}
        recorded_distances = set()  # Set to store recorded distances

        for sta in net.stations:
            station_info = track_station_information(sta)
            network_info["stations"][sta.name] = station_info

        for sta1 in net.stations:
            for sta2 in net.stations:
                if sta1 != sta2:
                    distance_pair = frozenset({sta1.name, sta2.name})
                    if distance_pair not in recorded_distances:
                        distance = calculate_distance(net, sta1, sta2)
                        network_info["distances"].append({"staX": sta1.name, "staY": sta2.name, "distance": distance})
                        recorded_distances.add(distance_pair)

        # Write the information to the JSON file
        with open(file_path, "w") as json_file:
            json.dump(network_info, json_file, indent=2)
            json_file.flush()  # Flush the buffer to ensure data is written immediately

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
    
    sta4 = net.addStation('sta4', mac='00:00:00:00:00:05', ip='10.0.0.5/8',
                    min_x=10, max_x=60, min_y=100, max_y=140, min_v=5, max_v=10)
    sta5 = net.addStation('sta5', ip='10.0.0.6/8',
                   min_x=120, max_x=140, min_y=20, max_y=40, min_v=1, max_v=5)
    sta6 = net.addStation('sta6', ip='10.0.0.7/8',
                    min_x=60, max_x=80, min_y=10, max_y=160, min_v=3, max_v=8)

    sta7 = net.addStation('sta7', mac='00:00:00:00:00:08', ip='10.0.0.8/8',
                    min_x=30, max_x=90, min_y=150, max_y=210, min_v=5, max_v=10)
    sta8 = net.addStation('sta8', ip='10.0.0.9/8',
                   min_x=180, max_x=210, min_y=30, max_y=60, min_v=1, max_v=5)
    sta9 = net.addStation('sta9', ip='10.0.0.10/8',
                    min_x=90, max_x=60, min_y=15, max_y=240, min_v=3, max_v=8)

    c1 = net.addController('c1')

    info("*** Configuring propagation model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring nodes\n")
    net.configureNodes()

    if '-p' not in args:
        net.plotGraph()

    net.setMobilityModel(time=0, model='RandomDirection',
                         max_x=250, max_y=250, seed=20)

    info("*** Associating and Creating links\n")
    net.addLink(sta1, cls=adhoc, intf='sta1-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)
    net.addLink(sta2, cls=adhoc, intf='sta2-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)
    net.addLink(sta3, cls=adhoc, intf='sta3-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)

    net.addLink(sta4, cls=adhoc, intf='sta4-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)
    net.addLink(sta5, cls=adhoc, intf='sta5-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)
    net.addLink(sta6, cls=adhoc, intf='sta6-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)
    
    net.addLink(sta7, cls=adhoc, intf='sta7-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)
    net.addLink(sta8, cls=adhoc, intf='sta8-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)
    net.addLink(sta9, cls=adhoc, intf='sta9-wlan0',
                ssid='adhocNet', mode='g', channel=5, **kwargs)

    info("*** Starting network\n")
    net.build()

    info("\n*** Addressing...\n")
    sta1.setIP('10.0.0.2/8', intf="sta1-wlan0")
    sta2.setIP('10.0.0.3/8', intf="sta2-wlan0")
    sta3.setIP('10.0.0.4/8', intf="sta3-wlan0")

    sta4.setIP('10.0.0.5/8', intf="sta4-wlan0")
    sta5.setIP('10.0.0.6/8', intf="sta5-wlan0")
    sta6.setIP('10.0.0.7/8', intf="sta6-wlan0")

    sta7.setIP('10.0.0.8/8', intf="sta7-wlan0")
    sta8.setIP('10.0.0.9/8', intf="sta8-wlan0")
    sta9.setIP('10.0.0.10/8', intf="sta9-wlan0")

    ## Open file for writing network information
    file_path = "network_information.json"

    # Start tracking network information in a separate thread
    tracking_thread = threading.Thread(target=track_network_information, args=(net, file_path))
    tracking_thread.start()

    info("*** Running CLI\n")
    CLI(net)

    # Stop tracking thread when CLI is exited
    tracking_thread.join()

    # Close the file after the CLI is done
    with open(file_path, "w") as json_file:
        json_file.write("")  # Clear the file content

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
