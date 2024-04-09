import random
import threading
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

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/huydq/Mininet/mininet-wifi/oppNet/utils')

from tezos import fetch_contract_storage
from index import check_reachability, check_reachability_with_smart_contract, get_station_number, get_key, find_route_with_smart_contract, find_route_without_smart_contract, calculate_distance
from infor import track_station_information

def track_network_information(net, file_path):
    signal_file_path = "simulation_complete.signal"

    online_stations = [sta for sta in net.stations if sta.intf().isUp() == True]
    while True:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        network_info = {"timestamp": timestamp, "stations": {}, "distances": []}
        recorded_distances = set()

        for sta in net.stations:
            station_info = track_station_information(sta, online_stations)
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
  
def main(num_hosts):
    setLogLevel('info')
    net = Mininet_wifi()

    info("*** Creating nodes\n")
    kwargs = {}
    if '-a' in sys.argv:
        kwargs['range'] = 100

    # Add stations based on the specified number of hosts
    stations = []
    for i in range(1, num_hosts + 1):
        station = net.addStation(f'sta{i}', ip=f'10.0.0.{i}/8',
                                 min_x=random.randint(0, 100),
                                 max_x=random.randint(100, 200),
                                 min_y=random.randint(0, 100),
                                 max_y=random.randint(100, 200),
                                 min_v=5, max_v=10)
        stations.append(station)

    c1 = net.addController('c1')
    info("*** Configuring propagation model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring nodes\n")
    net.configureNodes()

    if '-p' not in sys.argv:
        net.plotGraph()

    net.setMobilityModel(time=0, model='RandomDirection',
                         max_x=250, max_y=250, seed=20)

    info("*** Associating and Creating links\n")
    # Add links between stations
    for i in range(len(stations)):
        for j in range(i + 1, len(stations)):
            net.addLink(stations[i], stations[j], cls=adhoc, intf=f'sta{i + 1}-wlan0',
                        ssid='adhocNet', mode='g', channel=5, **kwargs)

    info("*** Starting network\n")
    net.build()

    info("\n*** Addressing...\n")
    # Set IP addresses for stations
    for i, station in enumerate(stations):
        station.setIP(f'10.0.0.{i + 1}/8', intf=f'sta{i + 1}-wlan0')

    file_path = "network_information.json"
    tracking_thread = threading.Thread(target=track_network_information, args=(net, file_path))
    tracking_thread.start()

    # Start the inconsistency model simulation
    inconsistency_simulation_thread = threading.Thread(target=inconsistency_simulation, args=(stations,))
    inconsistency_simulation_thread.start()

    # Wait for a few seconds to ensure the network information is collected
    time.sleep(5)

    # Start the time estimation thread
    time_estimation_thread = threading.Thread(target=time_estimation, args=(net, 'sta1', 'sta9'))
    time_estimation_thread.start()

    

    # Stop the inconsistency model simulation
    stop_inconsistency_simulation.set()
    inconsistency_simulation_thread.join()

    try:
        # Run the Mininet CLI
        info("*** Running CLI\n")
        CLI(net)
    except KeyboardInterrupt:
        # If CLI is interrupted, stop the threads and exit gracefully
        tracking_thread.join()
        inconsistency_simulation.join()
        time_estimation_thread.join()
        net.stop()

    net.stop()

def inconsistency_simulation(stations):
    while not stop_inconsistency_simulation.is_set():
        # Randomly select a station to go offline
        station_to_offline = random.choice(stations)
        print(f"Setting {station_to_offline.name} offline")
        station_to_offline.cmd('ifconfig', station_to_offline.name + '-wlan0', 'down')

        # Sleep for a random duration to simulate inconsistency
        sleep_duration = random.randint(600,900)
        time.sleep(sleep_duration)

        # Bring the station back online after the sleep duration
        print(f"Bringing {station_to_offline.name} back online")
        station_to_offline.cmd('ifconfig', station_to_offline.name + '-wlan0', 'up')

        # Sleep again to simulate the node being online
        sleep_duration = random.randint(600,900)
        time.sleep(sleep_duration)

stop_inconsistency_simulation = threading.Event()

def time_estimation(net, sta_start, sta_end):
    while True:
        start_time = time.time()
        route_without_contract, distance_without_contract = find_route_without_smart_contract(net, sta_start, sta_end)
        time_without_contract = time.time() - start_time

        start_time = time.time()
        route_with_contract, distance_with_contract = find_route_with_smart_contract(net, sta_start, sta_end)
        time_with_contract = time.time() - start_time

        info("\n*** Time Estimation Results ***\n")
        # info("Route without smart contract: {}\n".format(route_without_contract))
        # info("Distance without smart contract: {} meters\n".format(distance_without_contract))
        # info("Time without smart contract: {} seconds\n".format(time_without_contract))

        info("Route with smart contract: {}\n".format(route_with_contract))
        info("Distance with smart contract: {} units\n".format(distance_with_contract))
        info("Time with smart contract: {} seconds\n".format(time_with_contract))

        time.sleep(300)  # Adjust the interval as needed
      
    
if __name__ == '__main__':
    num_hosts = int(input("Enter the number of hosts: "))
    main(num_hosts)
