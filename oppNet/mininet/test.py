import sys
import time
import json
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import adhoc
from mn_wifi.mobility import Mobility
import threading
import math

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/huydq/Mininet/mininet-wifi/oppNet/utils')

from tezos import fetch_contract_storage
from index import check_reachability, check_reachability_with_smart_contract, get_station_number, get_key, find_route_with_smart_contract, find_route_without_smart_contract

def main():
    setLogLevel('info')
    net = Mininet_wifi()
    
    info("*** Creating nodes\n")
    kwargs = {}
    if '-a' in sys.argv:
        kwargs['range'] = 100
    sta1 = net.addStation('sta1', mac='00:00:00:00:00:02', ip='10.0.0.2/8',
                    min_x=10, max_x=30, min_y=50, max_y=70, min_v=5, max_v=10)
    sta2 = net.addStation('sta2', ip='10.0.0.3/8',
                   min_x=40, max_x=65, min_y=35, max_y=35, min_v=1, max_v=5)
    sta3 = net.addStation('sta3', ip='10.0.0.4/8',
                    min_x=15, max_x=40, min_y=55, max_y=78, min_v=3, max_v=8)
    
    sta4 = net.addStation('sta4', mac='00:00:00:00:00:05', ip='10.0.0.5/8',
                    min_x=55, max_x=69, min_y=32, max_y=220, min_v=5, max_v=10)
    sta5 = net.addStation('sta5', ip='10.0.0.6/8',
                   min_x=120, max_x=140, min_y=20, max_y=40, min_v=1, max_v=5)
    sta6 = net.addStation('sta6', ip='10.0.0.7/8',
                    min_x=60, max_x=80, min_y=10, max_y=160, min_v=3, max_v=8)

    sta7 = net.addStation('sta7', mac='00:00:00:00:00:08', ip='10.0.0.8/8',
                    min_x=30, max_x=90, min_y=150, max_y=210, min_v=5, max_v=10)
    sta8 = net.addStation('sta8', ip='10.0.0.9/8',
                   min_x=180, max_x=210, min_y=30, max_y=60, min_v=1, max_v=5)
    sta9 = net.addStation('sta9', ip='10.0.0.10/8',
                    min_x=65, max_x=82, min_y=15, max_y=240, min_v=3, max_v=8)

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

    # Wait for a few seconds to ensure the network information is collected
    time.sleep(5)

    # Select two stations for the route finding experiment
    sta_start = 'sta1'
    sta_end = 'sta9'

    # Measure the time taken to find a route without using a smart contract
    start_time = time.time()
    route_without_contract, distance_without_contract = find_route_without_smart_contract(net, sta_start, sta_end)
    time_without_contract = time.time() - start_time

    # Measure the time taken to find a route using a smart contract
    start_time = time.time()
    route_with_contract = find_route_with_smart_contract(net, sta_start, sta_end)
    time_with_contract = time.time() - start_time

    # Display results
    info("\n*** Experiment Results ***\n")
    info("Route without smart contract: {}\n".format(route_without_contract))
    info("Distance without smart contract: {} meters\n".format(distance_without_contract))
    info("Time without smart contract: {} seconds\n".format(time_without_contract))

    info("Route with smart contract: {}\n".format(route_with_contract))
    # info("Distance with smart contract: {} units\n".format(distance_with_contract))
    info("Time with smart contract: {} seconds\n".format(time_with_contract))

    net.stop()

if __name__ == '__main__':
    main()
