import argparse
import time
import threading
import subprocess
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from network_setup import setup_network

xterm_pids = []

def start_scapy_on_station(station, name, interface, ip, nodeRange):
    scapy_script = '/home/huydq/Mininet/mininet-wifi/oppNet/main/' + name + '.scapy'
    process = station.cmd('xterm -hold -e python3 {} {} {} {} {}&'.format(scapy_script, name, interface, ip, nodeRange))
    # Get the PID of the last background process (xterm)
    pid = station.cmd("echo $!")
    xterm_pids.append(pid.strip())

def close_xterms():
    for pid in xterm_pids:
        try:
            subprocess.call(["kill", "-9", pid])
            print("Killed xterm with PID: {}".format(pid))
        except Exception as e:
            print("Failed to kill xterm with PID: {}. Error: {}".format(pid,e))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ad-hoc network simulation")
    parser.add_argument('num_stations', type=int, help="Number of stations in the network")
    args = parser.parse_args()

    setLogLevel('info')
    net, stations = setup_network(args.num_stations)

    # Start Scapy scripts on each station
    for sta in stations:
        start_scapy_on_station(sta, sta.name, sta.intfs[0].name, sta.IP(), sta.wintfs[0].range)
    #     # start_scapy_on_station(sta, sta.name, 'bat0', sta.IP(), sta.wintfs[0].range)

    try:
        CLI(net)
        
        
    finally:
        net.stop()
        close_xterms()
