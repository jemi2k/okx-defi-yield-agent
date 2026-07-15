"""
Deployment script for YieldOptimizer.sol on X Layer (OKX L2)
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
        solc_version="0.8.19"
    )

    contract_id, contract_interface = compiled.popitem()

    return {
        "abi": contract_interface["abi"],
        "bin": contract_interface["bin"],
        "name": "YieldOptimizer"
    }


def deploy_contract(private_key: str, deployer_address: str):
    """Deploy contract to X Layer"""
    print(f"[Deploy] Connecting to X Layer at {XL1_RPC_URL}")
    w3 = Web3(Web3.HTTPProvider(XL1_RPC_URL))

    if not w3.is_connected():
        print("[Deploy] Failed to connect to X Layer")
        return None

    print(f"[Deploy] Connected to X Layer (Chain ID: {w3.eth.chain_id})")

    contract_data = compile_contract()

    YieldOptimizer = w3.eth.contract(
        abi=contract_data["abi"],
        bytecode=contract_data["bin"]
    )

    transaction = YieldOptimizer.constructor().build_transaction({
        "from": deployer_address,
        "nonce": w3.eth.get_transaction_count(deployer_address),
        "gas": 2000000,
        "gasPrice": w3.eth.gas_price,
        "chainId": w3.eth.chain_id
    })

    signed_txn = w3.eth.account.sign_transaction(
        transaction,
        private_key=private_key
    )

    print("[Deploy] Deploying contract...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"[Deploy] Contract deployed at: {receipt.contractAddress}")
    print(f"[Deploy] Transaction: {tx_hash.hex()}")

    deployment_info = {
        "contract_address": receipt.contractAddress,
        "transaction_hash": tx_hash.hex(),
        "block_number": receipt.blockNumber,
        "chain_id": w3.eth.chain_id,
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
        print("\nRun with:")
        print("  export DEPLOYER_PRIVATE_KEY=0x...")
        print("  export DEPLOYER_ADDRESS=0x...")
        print("  python contracts/deploy.py")
        sys.exit(1)

    result = deploy_contract(private_key, deployer_address)

    if result:
        print("\nDeployment successful!")
        print(f"\nAdd to .env file:")
        print(f"  YIELD_OPTIMIZER_CONTRACT={result['contract_address']}")