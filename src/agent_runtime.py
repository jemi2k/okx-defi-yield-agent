"""
OKX.AI Yield Optimizer - Agent Runtime
Stateful AI agent that monitors, analyzes, and executes DeFi yield strategies
"""
import os
import sys
import logging
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3 import Web3
from config.settings import XL1_RPC_URL, YIELD_OPTIMIZER_CONTRACT

logger = logging.getLogger("AgentRuntime")
_executor = ThreadPoolExecutor(max_workers=2)

# Hardcoded ABI - deployed on X Layer Testnet
YIELD_OPTIMIZER_ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {"anonymous": False, "inputs": [
        {"indexed": True, "internalType": "address", "name": "user", "type": "address"},
        {"indexed": True, "internalType": "uint256", "name": "strategyId", "type": "uint256"},
        {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
    ], "name": "Deposit", "type": "event"},
    {"anonymous": False, "inputs": [
        {"indexed": True, "internalType": "uint256", "name": "strategyId", "type": "uint256"},
        {"indexed": False, "internalType": "string", "name": "name", "type": "string"},
        {"indexed": False, "internalType": "address", "name": "protocol", "type": "address"}
    ], "name": "StrategyAdded", "type": "event"},
    {"anonymous": False, "inputs": [
        {"indexed": True, "internalType": "uint256", "name": "strategyId", "type": "uint256"},
        {"indexed": False, "internalType": "uint256", "name": "newApy", "type": "uint256"}
    ], "name": "StrategyUpdated", "type": "event"},
    {"anonymous": False, "inputs": [
        {"indexed": True, "internalType": "address", "name": "user", "type": "address"},
        {"indexed": True, "internalType": "uint256", "name": "strategyId", "type": "uint256"},
        {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
    ], "name": "Withdrawal", "type": "event"},
    {"anonymous": False, "inputs": [
        {"indexed": True, "internalType": "address", "name": "user", "type": "address"},
        {"indexed": True, "internalType": "uint256", "name": "strategyId", "type": "uint256"},
        {"indexed": False, "internalType": "uint256", "name": "yieldAmount", "type": "uint256"}
    ], "name": "YieldHarvested", "type": "event"},
    {"inputs": [
        {"internalType": "string", "name": "_name", "type": "string"},
        {"internalType": "address", "name": "_protocolAddress", "type": "address"},
        {"internalType": "string", "name": "_protocolName", "type": "string"},
        {"internalType": "uint256", "name": "_minDeposit", "type": "uint256"},
        {"internalType": "uint256", "name": "_maxDeposit", "type": "uint256"},
        {"internalType": "uint256", "name": "_initialApy", "type": "uint256"}
    ], "name": "addStrategy", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"components": [
        {"internalType": "uint256", "name": "strategyId", "type": "uint256"},
        {"internalType": "uint256", "name": "amount", "type": "uint256"},
        {"internalType": "uint256", "name": "depositedAt", "type": "uint256"},
        {"internalType": "uint256", "name": "lastHarvestedAt", "type": "uint256"}
    ], "internalType": "struct YieldOptimizer.UserPosition", "name": "_pos", "type": "tuple"}],
        "name": "calculateYield", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "_strategyId", "type": "uint256"}],
        "name": "deposit", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [], "name": "getAllStrategies", "outputs": [{"components": [
        {"internalType": "string", "name": "name", "type": "string"},
        {"internalType": "address", "name": "protocolAddress", "type": "address"},
        {"internalType": "string", "name": "protocolName", "type": "string"},
        {"internalType": "uint256", "name": "minDeposit", "type": "uint256"},
        {"internalType": "uint256", "name": "maxDeposit", "type": "uint256"},
        {"internalType": "uint256", "name": "currentApy", "type": "uint256"},
        {"internalType": "bool", "name": "active", "type": "bool"},
        {"internalType": "uint256", "name": "totalDeposits", "type": "uint256"}
    ], "internalType": "struct YieldOptimizer.Strategy[]", "name": "", "type": "tuple[]"}],
        "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "getBestStrategy", "outputs": [
        {"internalType": "uint256", "name": "bestId", "type": "uint256"},
        {"internalType": "uint256", "name": "bestApy", "type": "uint256"}
    ], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "_user", "type": "address"}],
        "name": "getUserPositions", "outputs": [{"components": [
        {"internalType": "uint256", "name": "strategyId", "type": "uint256"},
        {"internalType": "uint256", "name": "amount", "type": "uint256"},
        {"internalType": "uint256", "name": "depositedAt", "type": "uint256"},
        {"internalType": "uint256", "name": "lastHarvestedAt", "type": "uint256"}
    ], "internalType": "struct YieldOptimizer.UserPosition[]", "name": "", "type": "tuple[]"}],
        "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "_positionIndex", "type": "uint256"}],
        "name": "harvestYield", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view", "type": "function"},
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
    {"inputs": [], "name": "strategyCount", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "_strategyId", "type": "uint256"},
        {"internalType": "bool", "name": "_active", "type": "bool"}],
        "name": "toggleStrategy", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "_strategyId", "type": "uint256"},
        {"internalType": "uint256", "name": "_newApy", "type": "uint256"}],
        "name": "updateStrategyApy", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "", "type": "address"},
        {"internalType": "uint256", "name": "", "type": "uint256"}], "name": "userPositions",
        "outputs": [
        {"internalType": "uint256", "name": "strategyId", "type": "uint256"},
        {"internalType": "uint256", "name": "amount", "type": "uint256"},
        {"internalType": "uint256", "name": "depositedAt", "type": "uint256"},
        {"internalType": "uint256", "name": "lastHarvestedAt", "type": "uint256"}
    ], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "userTotalDeposits", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view", "type": "function"},
    {"stateMutability": "payable", "type": "receive"}
]


class AgentRuntime:
    """Stateful agent that monitors DeFi yields and executes on-chain actions."""

    def __init__(self):
        self.w3 = None
        self.contract = None
        self.contract_address = YIELD_OPTIMIZER_CONTRACT
        self._connected = False
        self._started_at = datetime.now()
        self._last_scan = None
        self._actions_taken = []
        self._recommendations = []
        self._status = "initializing"
        self._connect()

    def _connect(self):
        try:
            self.w3 = Web3(Web3.HTTPProvider(XL1_RPC_URL))
            if not self.w3.is_connected():
                logger.warning("Agent: X Layer RPC not connected")
                self._status = "rpc_unavailable"
                return

            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=YIELD_OPTIMIZER_ABI
            )

            # Verify contract exists
            code = self.w3.eth.get_code(Web3.to_checksum_address(self.contract_address)).hex()
            if len(code) <= 4:
                logger.warning("Agent: No contract code at %s", self.contract_address)
                self._status = "contract_not_deployed"
                return

            self._connected = True
            self._status = "active"
            logger.info("Agent runtime connected to YieldOptimizer at %s", self.contract_address)
        except Exception as e:
            logger.error("Agent connection failed: %s", str(e))
            self._status = "connection_failed"

    async def scan_market(self) -> Dict[str, Any]:
        if not self._connected:
            self._connect()
            if not self._connected:
                return {"status": "offline", "message": "Contract not connected", "strategy_count": 0, "strategies": []}

        loop = asyncio.get_running_loop()

        try:
            count = await loop.run_in_executor(
                _executor, self.contract.functions.strategyCount().call
            )
        except Exception as e:
            logger.error("Failed to read strategy count: %s", str(e))
            return {"status": "error", "message": str(e), "strategy_count": 0, "strategies": []}

        strategies = []
        best_apy = 0
        best_id = 0

        for i in range(1, count + 1):
            try:
                idx = i
                raw = await loop.run_in_executor(
                    _executor, lambda: self.contract.functions.strategies(idx).call()
                )
                apy_bps = raw[5]
                apy_pct = round(apy_bps / 100, 2)
                is_active = raw[6]
                total_deposits = self.w3.from_wei(raw[7], "ether")

                strategy = {
                    "id": i,
                    "name": raw[0],
                    "protocol": raw[2],
                    "apy": apy_pct,
                    "min_deposit": round(self.w3.from_wei(raw[3], "ether"), 4),
                    "max_deposit": round(self.w3.from_wei(raw[4], "ether"), 4),
                    "active": is_active,
                    "total_deposits_okb": round(total_deposits, 4),
                    "risk": "low" if apy_pct < 9 else ("medium" if apy_pct < 12 else "high")
                }
                strategies.append(strategy)

                if is_active and apy_pct > best_apy:
                    best_apy = apy_pct
                    best_id = i
            except Exception as e:
                logger.warning("Failed to read strategy %d: %s", i, str(e))

        self._last_scan = datetime.now()
        self._recommendations = strategies

        best = None
        if best_id > 0 and best_id <= len(strategies):
            best = strategies[best_id - 1]

        action = "hold"
        action_reason = ""

        if best:
            if best["apy"] > 12:
                action = "deposit_recommend"
                action_reason = "High APY opportunity: {} at {}%".format(best["name"], best["apy"])
            elif best["apy"] < 5:
                action = "rebalance_warning"
                action_reason = "Low APY across all strategies."

        self._status = "active"

        return {
            "status": "active",
            "scan_time": self._last_scan.isoformat(),
            "strategies": strategies,
            "strategy_count": count,
            "best_strategy": best,
            "average_apy": round(sum(s["apy"] for s in strategies) / count, 2) if count > 0 else 0,
            "agent_decision": {"action": action, "reason": action_reason},
            "total_value_managed_okb": round(sum(s["total_deposits_okb"] for s in strategies), 4),
            "agent_uptime_minutes": round((datetime.now() - self._started_at).total_seconds() / 60, 1),
            "actions_log": self._actions_taken[-5:]
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_status": self._status,
            "contract_address": self.contract_address,
            "chain": "X Layer Testnet (1952)",
            "started_at": self._started_at.isoformat(),
            "uptime_minutes": round((datetime.now() - self._started_at).total_seconds() / 60, 1),
            "last_scan": self._last_scan.isoformat() if self._last_scan else None,
            "actions_count": len(self._actions_taken),
            "recent_actions": self._actions_taken[-10:],
            "recommendations": self._recommendations
        }