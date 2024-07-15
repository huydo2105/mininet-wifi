from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.aerial.contract import LedgerContract
from cosmpy.aerial.tx import Transaction
from cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 import MsgExecuteContract
CONTRACT_ADDRESS = "osmo1ljgsg420cm3nseqtjx3m68zzwvhv5dt08t50ysf4cah624qmydjsqqgwgu"  
NODE_URL = "grpc+https://grpc.testnet.osmosis.zone"  

mnemonic = "ring visual luggage taste family economy riot adjust spike begin library rely future target jacket expire dog silver chaos piano color canyon rescue inmate"
wallet = LocalWallet.from_mnemonic(mnemonic, prefix='osmo')

# Initialize the LedgerClient
network_config = NetworkConfig(
    url=NODE_URL,
    chain_id="osmo-test-5",
    fee_minimum_gas_price=1,
    fee_denomination="uosmo",
    staking_denomination="uosmo",
)

ledger_client = LedgerClient(network_config)

# Initialize the CosmWasm contract
contract = LedgerContract(path=None, client=ledger_client, address=CONTRACT_ADDRESS)
