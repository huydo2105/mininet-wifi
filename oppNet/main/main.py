import argparse
import time
import threading
import subprocess
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from opp_node import OpportunisticNode
from network_setup import setup_network

xterm_pids = []

def start_scapy_on_station(station, name, interface, ip, nodeRange):
    scapy_script = f'/home/huydq/Mininet/mininet-wifi/oppNet/main/{name}.scapy'
    process = station.cmd(f'xterm -hold -e python3 {scapy_script} {name} {interface} {ip} {nodeRange}&')
    # Get the PID of the last background process (xterm)
    pid = station.cmd("echo $!")
    xterm_pids.append(pid.strip())

def close_xterms(station):
    for pid in xterm_pids:
        station.cmd(f'kill {pid}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ad-hoc network simulation")
    parser.add_argument('num_stations', type=int, help="Number of stations in the network")
    args = parser.parse_args()

    setLogLevel('info')
    net, stations = setup_network(args.num_stations)

    nodes = [OpportunisticNode(sta.name, net) for sta in stations]

    # Start Scapy scripts on each station
    for sta in stations:
        start_scapy_on_station(sta, sta.name, 'bat0', sta.IP(), sta.wintfs[0].range)

    try:
        # Simulate Opportunistic Networking
        try:
            # # Ensure nodes are fully initialized
            # time.sleep(30)
            nodes[0].send_packet(nodes[2], 'Hello')
        except Exception as e:
            print(f"An error occurred while sending packet: {e}")
        CLI(net)
        
        
    finally:
        net.stop()
        for sta in stations:
            close_xterms(sta)
