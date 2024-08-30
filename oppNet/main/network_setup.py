from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.wmediumdConnector import interference
from mininet.log import setLogLevel, info
from mininet.node import RemoteController
import threading
import random
import time

def allocate_channels(stations, current_allocation):
    """Dynamically allocate channels to stations based on interference."""
    available_channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # Example channels for 2.4 GHz band
    new_allocation = {}

    for sta in stations:
        other_stations = [other_sta for other_sta in stations if other_sta != sta]
        nearby_channels = {current_allocation[other_sta] for other_sta in other_stations}

        # Choose a channel not used by nearby stations
        possible_channels = [
            ch for ch in available_channels
            if all(ch != nearby_ch for nearby_ch in nearby_channels)
        ]
        new_channel = random.choice(possible_channels) if possible_channels else random.choice(available_channels)
        new_allocation[sta] = new_channel
    
    return new_allocation

def monitor_and_allocate_channels(stations, net):
    """Monitor the network and dynamically allocate channels."""
    current_allocation = {sta: sta.params['channel'] for sta in stations}  # Initial allocation
    while True:
        new_allocation = allocate_channels(stations, current_allocation)
        for sta in stations:
            if new_allocation[sta] != current_allocation[sta]:
                try:
                    if sta.shell and not sta.waiting:
                        intf_name = "{}-wlan0".format(sta.name) 
                        # sta.cmd(f'{sta.name}-wlan0 ibss join adhocNet 2412 02:CA:FF:EE:BA:01')
                        # sta.setChannel(new_allocation[sta], intf=intf_name)
                        # Remove the old ad-hoc link
                        sta.pexec('iw dev {} ibss leave'.format(intf_name))
                        # Set the new channel
                        sta.setChannel(new_allocation[sta])
                        # # Re-create the ad-hoc link with the new channel
                        # adhoc(node=sta, intf=intf_name, ssid='adhocNet', mode='g', channel=new_allocation[sta])
                        print(sta.params)
                        current_allocation[sta] = new_allocation[sta]
                        info("*** Channel for {} changed to {}\n".format(sta, new_allocation[sta]))
                except Exception as e:
                    info("Error setting channel for {}: {}\n".format(sta, e))
        time.sleep(60) 

def delayed_start(stations, net, delay):
    """Delay the start of the monitor_and_allocate_channels function."""
    time.sleep(delay)
    monitor_and_allocate_channels(stations, net)

def setup_network(num_stations):
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)
    c0 = net.addController('c0')
    # c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    info("*** Creating nodes\n")
    stations = []
    kwargs = {}
    kwargs['range'] = 100

    for i in range(num_stations):
        x_pos = random.uniform(0, 100)  # Random X position between 0 and 100
        y_pos = random.uniform(0, 100)  # Random Y position between 0 and 100
        stations.append(net.addStation('sta{}'.format(i+1), ip6='fe80::{}'.format(i+1), 
                                        position='{}, {}, 0'.format(x_pos, y_pos),
                                        **kwargs))

    net.setPropagationModel(model="logDistance", exp=4)


    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    # net.setMobilityModel(time=0, model='RandomDirection', max_x=250, max_y=250, seed=20)

    info("*** Creating ad-hoc links\n")
    for sta in stations:
        net.addLink(sta, cls=adhoc, intf='{}-wlan0'.format(sta.name), ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')

    # info("*** Setting Station TX Power\n")
    # for sta in stations:
    #     sta.setTxPower(21, intf='{}-wlan0'.format(sta.name))

    info("*** Starting network\n")
    net.build()
    c0.start()

    info("\n*** Addressing...\n")
    for i in range(num_stations):
        stations[i].setIP6('2001::{}/64'.format(i+1), intf="sta{}-wlan0".format(i+1))

    # info("*** Starting the dynamic channel allocation thread with a delay to wait for stations's initializtion\n")
    # delay = 15  # Delay in seconds
    # channel_thread = threading.Thread(target=delayed_start, args=(stations, net, delay))
    # channel_thread.daemon = True
    # channel_thread.start()

    return net, stations
