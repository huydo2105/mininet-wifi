import os
import time
import json
from dotenv import load_dotenv
from cosmpy.aerial.client import LedgerClient
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.aerial.tx import Transaction
from cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 import MsgExecuteContract
import logging
from datetime import datetime
from threading import Thread

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constant.main import wallet, contract

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_network_information(file_path):
    with open(file_path, "r") as json_file:
        return json.load(json_file)

def update_contract(network_info):
    timestamp = network_info.get("timestamp")
    stations = network_info.get("stations", {})
    distances = network_info.get("distances", {})

    # Execute store_network_info
    for station_name, station_info in stations.items():
        msg = {
            "store_network_info": {
                "params": {
                    "timestamp": timestamp,
                    "station_name": station_name,
                    "network_info": {
                        "position": station_info["position"],
                        "frequency": station_info["frequency"],
                        "mode": station_info["mode"],
                        "tx_power": station_info["tx_power"],
                        "range": station_info["range"],
                        "antenna_gain": station_info["antenna_gain"],
                        "status": station_info["status"],
                    }
                }
            }
        }

        tx_result = contract.execute(msg, sender=wallet, gas_limit=300000).wait_to_complete()
        print(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} Network information for {station_name} at {timestamp} has been stored")

    # Execute store_distances_info
    for distance_info in distances:
        msg = {
            "store_distances": {
                "params": {
                    "staX": distance_info["staX"],
                    "staY": distance_info["staY"],
                    "distance": distance_info["distance"],
                }
            }
        }
        
        tx_result = contract.execute(msg, sender=wallet, gas_limit=300000).wait_to_complete()
        print(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} Distance information for {station_name} at {timestamp} has been stored")

    # logger.info(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} Bulk operation for store_network_info and store_distances_info completed")

def listen_for_changes():
    file_path = "network_information.json"
    signal_file_path = "simulation_complete.signal"

    while True:
        # Wait until the signal file is created by the simulator
        while not os.path.exists(signal_file_path):
            time.sleep(1)

        try:
            # Read the content of the JSON file
            network_info = read_network_information(file_path)

            # Update the contract with the new network information
            update_contract(network_info)

        except Exception as e:
            logger.error(f"Error: {e}")

        # Remove the signal file to indicate the content has been read
        os.remove(signal_file_path)

def main():
    logger.info(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} Server is running")

    # Start a thread to listen for changes in the network_information.json file
    update_thread = Thread(target=listen_for_changes)
    update_thread.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
