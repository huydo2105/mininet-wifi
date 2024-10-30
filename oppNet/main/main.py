import argparse
import time
import threading
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from network_setup import setup_network, stop_protocol


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ad-hoc network simulation")
    parser.add_argument('num_stations', type=int, help="Number of stations in the network")
    args = parser.parse_args()

    setLogLevel('info')
    net, stations = setup_network(args.num_stations)

    try:
        CLI(net)
        
    finally:
        net.stop()
        stop_protocol()
