from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.aerial.contract import LedgerContract
from cosmpy.aerial.tx import Transaction
from cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 import MsgExecuteContract

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constant.main import wallet, contract

# Query the latest info for a specific station 
def fetch_latest_info(station_name):
    query_latest_info = {"get_latest_info": {"station_name": station_name}}
    latest_info_response = contract.query(query_latest_info)
    latest_info = latest_info_response.get('network_info', {})
    return latest_info

# Query distances between two stations 
def fetch_distance(sta_x, sta_y):
    query_distances = {"get_distances": {"sta_x": sta_x, "sta_y": sta_y}}
    distances_response = contract.query(query_distances)
    distance = distances_response.get('distance', {})
    return distance
