import os
import time
import json
from pytezos import pytezos
from threading import Thread
import logging
from datetime import datetime

CONTRACT_CODE_PATH = "../contract/main.py"
CONTRACT_ADDRESS = "KT1JnScpF8zQzmYKwXKwYpHyu7eWoeeoLC4T"
CONTRACT_STORAGE = {"timestamps": {}, "latest_info": {}, "distances": {}}
NODE_URL = "https://ghostnet.ecadinfra.com"

pytezos = pytezos.using(key="edskS1Vw8yMGpJTEWh4M7Yzu1h8HVPcwPPxZxFLUx41V4Pctyss8zQDgi2LvXtfzJHhFzMwgwJ6VXezidniysoVApJo7vDYN3G")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a custom formatter
formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

# Create a handler that uses the custom formatter
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

def read_network_information(file_path):
    with open(file_path, "r") as json_file:
        return json.load(json_file)

def update_contract(network_info, contract):
    global CONTRACT_STORAGE

    timestamp = network_info.get("timestamp")
    stations = network_info.get("stations", {})
    distances = network_info.get("distances", {})

    stored_distances = []

    # Create a list of OperationGroup objects for store_network_info calls
    stored_network_info = [
        contract.store_network_info(
            timestamp=timestamp,
            station_name=station_name,
            network_info={
                "position": ",".join(map(str, station_info["coordination"])),
                'freq': str(station_info["frequency"]),
                'mode': str(station_info["mode"]),
            }
        )
        for station_name, station_info in stations.items()
    ]

    # Create a list of OperationGroup objects for store_distances_info calls
    stored_distances = [
        contract.store_distances_info(
            staX=distance_info["staX"],
            staY=distance_info["staY"],
            distance=str(distance_info["distance"])
        )
        for distance_info in distances
    ]

    # Perform bulk operation for store_network_info and store_distances_info calls
    pytezos.bulk(*stored_network_info, *stored_distances).send(min_confirmations=1)
    logger.info("Bulk operation for store_network_info and store_distances_info completed")

def listen_for_changes(file_path, contract):
    last_updated_time = 0

    while True:
        try:
            # Read the content of the JSON file
            network_info = read_network_information(file_path)

            for element in network_info:
                # Update the contract with the new network information
                update_contract(element, contract)

                # Update the last updated time
                last_updated_time = os.path.getmtime(file_path)

        except Exception as e:
            logger.error(f"Error: {e}")

        time.sleep(5)  # Sleep for 5 seconds before checking for changes

def main():
    logger.info("Server is running")
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
