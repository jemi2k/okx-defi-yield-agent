"""
X Layer Smart Contract Client
Reads yield strategy data from the deployed YieldOptimizer contract
"""
import logging
from typing import Dict, List, Any
from web3 import Web3

from config.settings import XL1_RPC_URL, YIELD_OPTIMIZER_CONTRACT
from src.agent_runtime import YIELD_OPTIMIZER_ABI

logger = logging.getLogger("ContractClient")


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
                logger.warning("ContractClient: X Layer RPC not connected")
                return False
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=YIELD_OPTIMIZER_ABI
            )
            code = self.w3.eth.get_code(Web3.to_checksum_address(self.contract_address)).hex()
            if len(code) <= 4:
                logger.warning("ContractClient: No contract code at %s", self.contract_address)
                return False
            self._connected = True
            logger.info("ContractClient: Connected to YieldOptimizer at %s", self.contract_address)
            return True
        except Exception as e:
            logger.error("ContractClient connection failed: %s", str(e))
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
                    apy_bps = raw[5]
                    apy_pct = round(apy_bps / 100, 2)

                    if apy_pct < 9:
                        risk = "low"
                    elif apy_pct < 12:
                        risk = "medium"
                    else:
                        risk = "medium"

                    strategies.append({
                        "protocol": raw[2] if raw[2] else "X Layer",
                        "name": raw[0] if raw[0] else "Strategy #{}".format(i),
                        "apy": apy_pct,
                        "min_deposit": round(self.w3.from_wei(raw[3], "ether"), 4),
                        "risk": risk,
                        "type": "onchain",
                        "active": raw[6],
                        "total_deposits_okb": round(self.w3.from_wei(raw[7], "ether"), 2),
                        "strategy_id": i
                    })
                except Exception as e:
                    logger.warning("ContractClient: Failed to read strategy %d: %s", i, str(e))
                    continue

            return strategies
        except Exception as e:
            logger.error("ContractClient: Failed to fetch strategies: %s", str(e))
            return []

    def get_contract_info(self) -> Dict[str, Any]:
        """Get basic contract info for display"""
        return {
            "address": self.contract_address,
            "chain": "X Layer Testnet",
            "chain_id": self.w3.eth.chain_id if self.w3 and self.w3.is_connected() else 1952,
            "connected": self._connected,
            "explorer": "https://www.okx.com/web3/explorer/xlayer-test/address/{}".format(self.contract_address)
        }