"""
Deployment script for YieldOptimizer.sol on X Layer (OKX L2) Testnet
"""
import os
import sys
import json
from web3 import Web3
from solcx import compile_source, install_solc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import XL1_RPC_URL


def compile_contract():
    """Compile the YieldOptimizer Solidity contract"""
    print("[Deploy] Installing Solidity compiler...")
    install_solc("0.8.19")

    contract_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "YieldOptimizer.sol"
    )

    with open(contract_path, "r") as f:
        source = f.read()

    print("[Deploy] Compiling YieldOptimizer.sol...")
    compiled = compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version="0.8.19",
        optimize=True,
        optimize_runs=200
    )

    contract_id, contract_interface = compiled.popitem()

    return {
        "abi": contract_interface["abi"],
        "bin": contract_interface["bin"],
        "name": "YieldOptimizer"
    }


def deploy_contract(private_key: str, deployer_address: str):
    """Deploy contract to X Layer Testnet"""
    print(f"[Deploy] Connecting to X Layer at {XL1_RPC_URL}")
    w3 = Web3(Web3.HTTPProvider(XL1_RPC_URL))

    if not w3.is_connected():
        print("[Deploy] Failed to connect to X Layer")
        return None

    chain_id = w3.eth.chain_id
    balance = w3.eth.get_balance(deployer_address)
    print(f"[Deploy] Connected to X Layer Testnet (Chain ID: {chain_id})")
    print(f"[Deploy] Deployer balance: {w3.from_wei(balance, 'ether')} OKB")

    contract_data = compile_contract()

    YieldOptimizer = w3.eth.contract(
        abi=contract_data["abi"],
        bytecode=contract_data["bin"]
    )

    nonce = w3.eth.get_transaction_count(deployer_address)
    gas_price = w3.to_wei(2, 'gwei')

    transaction = YieldOptimizer.constructor().build_transaction({
        "from": deployer_address,
        "nonce": nonce,
        "gas": 5000000,
        "gasPrice": gas_price,
        "chainId": chain_id
    })

    print(f"[Deploy] Gas price: {w3.from_wei(gas_price, 'gwei')} gwei, Gas limit: 5,000,000")

    signed_txn = w3.eth.account.sign_transaction(
        transaction,
        private_key=private_key
    )

    print("[Deploy] Sending deployment transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"[Deploy] TX Hash: {tx_hash.hex()}")

    print("[Deploy] Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

    if receipt["status"] == 0:
        print("[Deploy] Transaction reverted! Check gas/contract issues.")
        return None

    print(f"[Deploy] Contract deployed at: {receipt.contractAddress}")
    print(f"[Deploy] Gas used: {receipt.gasUsed}")

    deployment_info = {
        "contract_address": receipt.contractAddress,
        "transaction_hash": tx_hash.hex(),
        "block_number": receipt.blockNumber,
        "chain_id": chain_id,
        "deployer": deployer_address,
        "abi": contract_data["abi"],
        "timestamp": str(w3.eth.get_block(receipt.blockNumber)["timestamp"])
    }

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "deployment.json"
    )
    with open(output_path, "w") as f:
        json.dump(deployment_info, f, indent=2)

    print(f"[Deploy] Deployment info saved to {output_path}")

    return deployment_info


if __name__ == "__main__":
    print("=" * 60)
    print("OKX DeFi Yield Optimizer - Contract Deployment")
    print("=" * 60)

    private_key = os.getenv("DEPLOYER_PRIVATE_KEY", "")
    deployer_address = os.getenv("DEPLOYER_ADDRESS", "")

    if not private_key or not deployer_address:
        print("\nMissing deployer credentials!")
        print("Set DEPLOYER_PRIVATE_KEY and DEPLOYER_ADDRESS environment variables.")
        sys.exit(1)

    result = deploy_contract(private_key, deployer_address)

    if result:
        print(f"\nDeployment successful!")
        print(f"\nContract: {result['contract_address']}")
        print(f"Add to .env: YIELD_OPTIMIZER_CONTRACT={result['contract_address']}")
    else:
        print("\nDeployment failed. Check balance and network connectivity.")