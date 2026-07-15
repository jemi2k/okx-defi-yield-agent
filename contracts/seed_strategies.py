"""Seed demo strategies into the deployed YieldOptimizer contract"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3 import Web3
from config.settings import XL1_RPC_URL, YIELD_OPTIMIZER_CONTRACT
import json

# Load ABI
abi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deployment.json")
with open(abi_path, "r") as f:
    dep = json.load(f)
    abi = dep["abi"]

# Connect
w3 = Web3(Web3.HTTPProvider(XL1_RPC_URL))
print(f"Connected: {w3.is_connected()}, Chain ID: {w3.eth.chain_id}")

contract = w3.eth.contract(
    address=Web3.to_checksum_address(YIELD_OPTIMIZER_CONTRACT),
    abi=abi
)

# Check existing strategies
count = contract.functions.strategyCount().call()
print(f"Current strategy count: {count}")

if count > 0:
    print("Strategies already exist, skipping seed.")
    sys.exit(0)

# Credentials
private_key = "da4df15c5b0e161576297e8af110fed38ba845ea9a64f151ef2a88d29f26c40d"
deployer = "0x27F36ac63520e7b226Abd1287dC2c3B1CB725994"

# Demo strategies to add (name, protocolName, minDeposit_wei, maxDeposit_wei, apy_bps)
strategies = [
    ("OKX Earn Flexible", "OKX", Web3.to_wei(0.01, "ether"), Web3.to_wei(100, "ether"), 850),
    ("OKX Earn 7-Day", "OKX", Web3.to_wei(0.05, "ether"), Web3.to_wei(100, "ether"), 1000),
    ("OKX Earn 30-Day", "OKX", Web3.to_wei(0.1, "ether"), Web3.to_wei(500, "ether"), 1170),
    ("ETH-USDT LP", "X Layer DEX", Web3.to_wei(0.5, "ether"), Web3.to_wei(1000, "ether"), 1375),
    ("USDC Bridge Pool", "Stargate Finance", Web3.to_wei(0.1, "ether"), Web3.to_wei(200, "ether"), 1075),
]

print("Adding demo strategies...")
dummy_addr = "0x0000000000000000000000000000000000000001"

for name, protocol, min_dep, max_dep, apy in strategies:
    nonce = w3.eth.get_transaction_count(deployer)
    txn = contract.functions.addStrategy(
        name,
        Web3.to_checksum_address(dummy_addr),
        protocol,
        min_dep,
        max_dep,
        apy
    ).build_transaction({
        "from": deployer,
        "nonce": nonce,
        "gas": 300000,
        "gasPrice": w3.eth.gas_price,
        "chainId": w3.eth.chain_id
    })
    
    signed = w3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"  Added: {name} ({apy/100}% APY) - TX: {tx_hash.hex()[:10]}...")

count = contract.functions.strategies(1).call()
print(f"\nFirst strategy: {count[0]} at {count[5]/100}% APY")
print(f"Total strategies: {contract.functions.strategyCount().call()}")
print("\nSeed complete!")