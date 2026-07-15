"""
X Layer Smart Contract Client
Reads yield strategy data from the deployed YieldOptimizer contract
"""
import os
import logging
from typing import Dict, List, Any
from web3 import Web3
import json

from config.settings import XL1_RPC_URL, YIELD_OPTIMIZER_CONTRACT

logger = logging.getLogger("ContractClient")

# Load ABI from deployment.json or use the known ABI
DEPLOYMENT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "contracts", "deployment.json"
)

YIELD_OPTIMIZER_ABI = None

# Try to load ABI from deployment file
if os.path.exists(DEPLOYMENT_FILE):
    with open(DEPLOYMENT_FILE, "r") as f:
        dep = json.load(f)
        YIELD_OPTIMIZER_ABI = dep.get("abi")

# Fallback minimal ABI for reading
if not YIELD_OPTIMIZER_ABI:
    YIELD_OPTIMIZER_ABI = [
        {
            "inputs": [],
            "name": "strategyCount",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view", "type": "function"
        },
        {
            "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "name": "strategies",
            "outputs": [
                {"internalType": "string", "name": "name", "type": "string"},
                {"internalType": "address", "name": "protocolAddress", "type": "address"},
                {"internalType": "string", "name": "protocolName", "type": "string"},
                {"internalType": "uint256", "name": "minDeposit", "type": "uint256"},
                {"internalType": "uint256", "name": "maxDeposit", "type": "uint256"},
                {"internalType": "uint256", "name": "currentApy", "type": "uint256"},
                {"internalType": "bool", "name": "active", "type": "bool"},
                {"internalType": "uint256", "name": "totalDeposits", "type": "uint256"}
            ],
            "stateMutability": "view", "type": "function"
        },
        {
            "inputs": [],
            "name": "getBestStrategy",
            "outputs": [
                {"internalType": "uint256", "name": "bestId", "type": "uint256"},
                {"internalType": "uint256", "name": "bestApy", "type": "uint256"}
            ],
            "stateMutability": "view", "type": "function"
        }
    ]


class ContractClient:
    """Client for interacting with the deployed YieldOptimizer contract on X Layer"""

    def __init__(self):
        self.rpc_url = XL1_RPC_URL
        self.contract_address = YIELD_OPTIMIZER_CONTRACT
        self.w3 = None
        self.contract = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to X Layer and the deployed contract"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not self.w3.is_connected():
                logger.warning("Failed to connect to X Layer RPC")
                return False

            if self.contract_address == "0x0000000000000000000000000000000000000000":
                logger.warning("YieldOptimizer contract not deployed yet")
                return False

            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=YIELD_OPTIMIZER_ABI
            )
            self._connected = True
            logger.info("Connected to YieldOptimizer at %s", self.contract_address)
            return True
        except Exception as e:
            logger.error("Contract connection failed: %s", str(e))
            return False

    def is_connected(self) -> bool:
        return self._connected

    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Fetch all strategies from the deployed contract"""
        if not self._connected and not self.connect():
            return []

        try:
            count = self.contract.functions.strategyCount().call()
            strategies = []

            for i in range(1, count + 1):
                try:
                    raw = self.contract.functions.strategies(i).call()
                    # APY is stored in basis points (e.g., 850 = 8.5%)
                    apy_bps = raw[5]
                    apy_pct = round(apy_bps / 100, 2)

                    # Map risk based on APY
                    if apy_pct < 9:
                        risk = "low"
                    elif apy_pct < 12:
                        risk = "medium"
                    else:
                        risk = "medium"

                    strategies.append({
                        "protocol": raw[2] if raw[2] else "X Layer Protocol",
                        "name": raw[0] if raw[0] else f"Strategy #{i}",
                        "apy": apy_pct,
                        "min_deposit": round(self.w3.from_wei(raw[3], "ether"), 4),
                        "risk": risk,
                        "type": "onchain",
                        "active": raw[6],
                        "total_deposits": round(self.w3.from_wei(raw[7], "ether"), 2),
                        "strategy_id": i
                    })
                except Exception as e:
                    logger.warning("Failed to read strategy %d: %s", i, str(e))
                    continue

            return strategies
        except Exception as e:
            logger.error("Failed to fetch strategies: %s", str(e))
            return []

    def get_best_strategy(self) -> Dict[str, Any]:
        """Get the strategy with the highest APY"""
        if not self._connected and not self.connect():
            return {}

        try:
            best_id, best_apy_bps = self.contract.functions.getBestStrategy().call()
            if best_id == 0:
                return {}

            raw = self.contract.functions.strategies(best_id).call()
            apy_pct = round(best_apy_bps / 100, 2)

            return {
                "protocol": raw[2] if raw[2] else "X Layer Protocol",
                "name": raw[0] if raw[0] else f"Strategy #{best_id}",
                "apy": apy_pct,
                "min_deposit": round(self.w3.from_wei(raw[3], "ether"), 4),
                "risk": "medium",
                "type": "onchain",
                "strategy_id": best_id
            }
        except Exception as e:
            logger.error("Failed to get best strategy: %s", str(e))
            return {}

    def get_contract_info(self) -> Dict[str, Any]:
        """Get basic contract info for display"""
        return {
            "address": self.contract_address,
            "chain": "X Layer Testnet",
            "chain_id": self.w3.eth.chain_id if self.w3 and self.w3.is_connected() else 1952,
            "connected": self._connected,
            "explorer": f"https://www.okx.com/web3/explorer/xlayer-test/address/{self.contract_address}"
        }