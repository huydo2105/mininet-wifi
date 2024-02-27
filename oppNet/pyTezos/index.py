import os
import time
import json
from pytezos import pytezos
from threading import Thread

CONTRACT_CODE_PATH = "../contract/main.py"
CONTRACT_ADDRESS = "KT1GJsDGs1WnSCPMaErYJ8mqHSwwZoJtVMXk"
CONTRACT_STORAGE = {"timestamps": {}, "latest_info": {}, "distances": {}}
NODE_URL = "https://ghostnet.ecadinfra.com"

def read_network_information(file_path):
    with open(file_path, "r") as json_file:
        return json.load(json_file)

def update_contract(network_info, contract):
    global CONTRACT_STORAGE

    timestamp = network_info.get("timestamp")
    stations = network_info.get("stations", {})
    distances = network_info.get("distances", {})

    for station_name, station_info in stations.items():
        # Call store_network_info for each station
        contract.store_network_info(
            timestamp=timestamp,
            station_name=station_name,
            network_info={
                "position": ",".join(map(str, station_info["coordination"])),
                'ip': station_info["parameters"].get('ip', ''),
                'channel': station_info["parameters"].get('channel', ''),
                'freq': station_info["frequency"],
                'mode': station_info["mode"],
                'mac': station_info["parameters"].get('mac', '')
            }
        )

    for distance_info in distances:
        # Call store_distances_info for each pair of stations
        contract.store_distances_info(
            staX=distance_info["staX"],
            staY=distance_info["staY"],
            distance=distance_info["distance"]
        )

def listen_for_changes(file_path, contract):
    last_updated_time = 0

    while True:
        try:
            # Read the content of the JSON file
            network_info = read_network_information(file_path)

            # Update the contract with the new network information
            update_contract(network_info, contract)

            # Update the last updated time
            last_updated_time = os.path.getmtime(file_path)

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(5)  # Sleep for 5 seconds before checking for changes

def main():
    # Load the existing contract using the provided CONTRACT_ADDRESS
    py = pytezos.using(shell=NODE_URL)
    contract = py.contract(CONTRACT_ADDRESS)

    # Start a thread to listen for changes in the network_information.json file
    file_path = "network_information.json"
    update_thread = Thread(target=listen_for_changes, args=(file_path, contract))
    update_thread.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
