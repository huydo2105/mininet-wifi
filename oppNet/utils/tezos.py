from pytezos import pytezos

CONTRACT_CODE_PATH = "../contract/main.py"
CONTRACT_ADDRESS = "KT1JnScpF8zQzmYKwXKwYpHyu7eWoeeoLC4T"
CONTRACT_STORAGE = {"timestamps": {}, "latest_info": {}, "distances": {}}
NODE_URL = "https://ghostnet.ecadinfra.com"

def fetch_contract_storage():
    # Load the existing contract using the provided CONTRACT_ADDRESS
    py = pytezos.using(shell=NODE_URL)
    contract = py.contract(CONTRACT_ADDRESS)

    distances = contract.storage()['distances']
    latest_info = contract.storage()['latest_infor']

    return distances, latest_info