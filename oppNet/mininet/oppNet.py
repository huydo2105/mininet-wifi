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
import argparse
import random

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/huydq/Mininet/mininet-wifi/oppNet/utils')

from tezos import fetch_contract_storage
from index import check_reachability, check_reachability_with_smart_contract, get_station_number, get_key
from infor import track_station_information

def track_network_information(net, file_path):
    signal_file_path = "simulation_complete.signal"
    while True:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        network_info = {"timestamp": timestamp, "stations": {}, "distances": []}
        recorded_distances = set()

        for sta in net.stations:
            station_info = track_station_information(sta)
            network_info["stations"][sta.name] = station_info

        for sta1 in net.stations:
            for sta2 in net.stations:
                if sta1 != sta2:
                    distance_pair = frozenset({sta1.name, sta2.name})
                    if distance_pair not in recorded_distances:
                        distance = calculate_distance(sta1, sta2)
                        network_info["distances"].append({"staX": sta1.name, "staY": sta2.name, "distance": distance})
                        recorded_distances.add(distance_pair)

        with open(file_path, "w") as json_file:
            json.dump(network_info, json_file, indent=2)

        with open(signal_file_path, "w"):
            pass

        time.sleep(600)

def topology(num_stations):
    net = Mininet_wifi()

    info("*** Creating nodes\n")
    kwargs = {}
    if '-a' in sys.argv:
        kwargs['range'] = 100

    stations = []
    for i in range(1, num_stations + 1):
        # Generate random values for station properties
        min_x = random.uniform(0, 100)
        max_x = random.uniform(min_x, 200)
        min_y = random.uniform(0, 100)
        max_y = random.uniform(min_y, 200)
        min_v = random.uniform(1, 5)
        max_v = random.uniform(min_v, 10)

        station = net.addStation(f'sta{i}', ip=f'10.0.0.{i}/8',
                                min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y, min_v=min_v, max_v=max_v)
        
        stations.append(station)

    c1 = net.addController('c1')

    info("*** Configuring propagation model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring nodes\n")
    net.configureNodes()

    if '-p' not in sys.argv:
        net.plotGraph()

    net.setMobilityModel(time=0, model='RandomDirection', max_x=250, max_y=250, seed=20)

    info("*** Associating and Creating links\n")
    for i in range(num_stations):
        for j in range(i + 1, num_stations):
            sta1 = stations[i]
            sta2 = stations[j]
            net.addLink(sta1, sta2, cls=adhoc, intf=f'sta{i + 1}-wlan0',
                        ssid='adhocNet', mode='g', channel=5, **kwargs)

    info("*** Starting network\n")
    net.build()

    for i in range(num_stations):
        station = stations[i]
        intf_name = f'sta{i + 1}-wlan0'
        station.setIP(f'10.0.0.{i + 2}/8', intf=intf_name)

    file_path = "network_information.json"
    tracking_thread = threading.Thread(target=track_network_information, args=(net, file_path))
    tracking_thread.start()

    info("*** Running CLI\n")
    CLI(net)

    tracking_thread.join()

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ad-hoc network simulation")
    parser.add_argument('num_stations', type=int, help="Number of stations in the network")
    parser.add_argument('-p', action='store_true', help="Plot the network graph")
    args = parser.parse_args()

    setLogLevel('info')
    topology(args.num_stations)