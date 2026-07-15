"""
X Layer Smart Contract Client
Reads yield strategy data from the deployed YieldOptimizer contract
"""
import logging
from typing import Dict, List, Any

logger = logging.getLogger("ContractClient")

# Hardcoded ABI - deployed on X Layer Testnet
ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {"inputs": [], "name": "strategyCount", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "strategies",
        "outputs": [
        {"internalType": "string", "name": "name", "type": "string"},
        {"internalType": "address", "name": "protocolAddress", "type": "address"},
        {"internalType": "string", "name": "protocolName", "type": "string"},
        {"internalType": "uint256", "name": "minDeposit", "type": "uint256"},
        {"internalType": "uint256", "name": "maxDeposit", "type": "uint256"},
        {"internalType": "uint256", "name": "currentApy", "type": "uint256"},
        {"internalType": "bool", "name": "active", "type": "bool"},
        {"internalType": "uint256", "name": "totalDeposits", "type": "uint256"}
    ], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "getBestStrategy", "outputs": [{"internalType": "uint256", "name": "bestId", "type": "uint256"}, {"internalType": "uint256", "name": "bestApy", "type": "uint256"}], "stateMutability": "view", "type": "function"}
]

# Deployed contract
CONTRACT_ADDRESS = "0xE5B0F5e6F7358a8836574caEB6330DeDAf9E140C"
RPC_URL = "https://testrpc.xlayer.tech/terigon"

try:
    from web3 import Web3
    _w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if _w3.is_connected():
        CONTRACT = _w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)
        code = _w3.eth.get_code(Web3.to_checksum_address(CONTRACT_ADDRESS)).hex()
        CONNECTED = len(code) > 4
        logger.info("ContractClient: Connected=%s, Code=%d bytes", CONNECTED, len(code))
    else:
        CONTRACT = None
        CONNECTED = False
        logger.warning("ContractClient: RPC not reachable")
except Exception as e:
    CONTRACT = None
    CONNECTED = False
    logger.warning("ContractClient: web3 not available: %s", str(e))


class ContractClient:

    def __init__(self):
        self._connected = CONNECTED
        self.contract = CONTRACT

    def connect(self) -> bool:
        return self._connected

    def is_connected(self) -> bool:
        return self._connected

    def get_all_strategies(self) -> List[Dict[str, Any]]:
        if not self._connected or not self.contract or not CONTRACT:
            return []

        try:
            from web3 import Web3
            w3 = _w3
            count = self.contract.functions.strategyCount().call()
            strategies = []

            for i in range(1, count + 1):
                try:
                    raw = self.contract.functions.strategies(i).call()
                    apy_pct = round(raw[5] / 100, 2)
                    risk = "low" if apy_pct < 9 else ("medium" if apy_pct < 12 else "high")
                    strategies.append({
                        "protocol": raw[2] or "X Layer",
                        "name": raw[0] or "Strategy #{}".format(i),
                        "apy": apy_pct,
                        "min_deposit": round(w3.from_wei(raw[3], "ether"), 4),
                        "risk": risk,
                        "type": "onchain",
                        "active": raw[6],
                        "total_deposits_okb": round(w3.from_wei(raw[7], "ether"), 2),
                        "strategy_id": i
                    })
                except Exception as e:
                    logger.warning("Failed to read strategy %d: %s", i, str(e))
            return strategies
        except Exception as e:
            logger.error("Failed to fetch strategies: %s", str(e))
            return []

    def get_contract_info(self) -> Dict[str, Any]:
        return {
            "address": CONTRACT_ADDRESS,
            "chain": "X Layer Testnet",
            "chain_id": 1952,
            "connected": self._connected,
            "explorer": "https://www.okx.com/web3/explorer/xlayer-test/address/" + CONTRACT_ADDRESS
        }