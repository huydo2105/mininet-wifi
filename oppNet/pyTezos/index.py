from pytezos import pytezos

# Replace the following with your actual parameters
CONTRACT_CODE_PATH = "path/to/your/contract.py"
CONTRACT_ADDRESS = "KT1YourContractAddress"
CONTRACT_STORAGE = {"timestamps": {}, "latest_info": {}}

# Deploy the contract
py = pytezos.using(key="your_key_alias")
contract = py.contract(origination_block_hash="head").originate(
    storage=CONTRACT_STORAGE,
    code=open(CONTRACT_CODE_PATH, "r").read(),
    public_key="your_public_key"
).autofill().sign().inject()

# Store network information
timestamp = "2024-02-22 17:46:06"
station_name = "sta1"
position = [24.67, 68.67, 0.0]
network_info = {
    "ip": "10.0.0.2/8",
    "channel": 1,
    "freq": 2.4,
    "mode": "g",
    "encrypt": "",
    "passwd": None,
    "mac": "00:00:00:00:00:02",
}

# Call store_network_info entry point
contract.call(
    entry_point="store_network_info",
    params={
        "timestamp": timestamp,
        "station_name": station_name,
        "position": position,
        "network_info": network_info,
    },
).autofill().sign().inject()

# Get network information
result = contract.storage[timestamp][station_name]
print("Network Information:", result)

# Get latest network information
latest_result = contract.storage["latest_info"][station_name]
print("Latest Network Information:", latest_result)