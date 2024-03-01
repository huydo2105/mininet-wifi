import os
import time
import json
from dotenv import load_dotenv
from pytezos import pytezos
from threading import Thread
import logging
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# Fetch the key from the environment variable
PYTEZOS_KEY = os.environ["PYTEZOS_KEY"]

if not PYTEZOS_KEY:
    raise ValueError("PYTEZOS_KEY environment variable is not set")

CONTRACT_CODE_PATH = "../contract/main.py"
CONTRACT_ADDRESS = "KT1JnScpF8zQzmYKwXKwYpHyu7eWoeeoLC4T"
CONTRACT_STORAGE = {"timestamps": {}, "latest_info": {}, "distances": {}}
NODE_URL = "https://ghostnet.ecadinfra.com"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} Bulk operation for store_network_info and store_distances_info completed")

def listen_for_changes(file_path, contract):
    signal_file_path = "simulation_complete.signal"

    while True:
        # Wait until the signal file is created by the simulator
        while not os.path.exists(signal_file_path):
            time.sleep(1)

        try:
            # Read the content of the JSON file
            network_info = read_network_information(file_path)

            # Update the contract with the new network information
            update_contract(network_info, contract)

        except Exception as e:
            logger.error(f"Error: {e}")

        # Remove the signal file to indicate the content has been read
        os.remove(signal_file_path)

def main():
    logger.info(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} Server is running")
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
