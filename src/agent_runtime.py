"""
OKX.AI Yield Optimizer - Agent Runtime
Stateful AI agent that monitors, analyzes, and executes DeFi yield strategies
"""
import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3 import Web3
from config.settings import XL1_RPC_URL, YIELD_OPTIMIZER_CONTRACT

logger = logging.getLogger("AgentRuntime")
_executor = ThreadPoolExecutor(max_workers=2)


class AgentRuntime:
    """
    Stateful agent that continuously monitors DeFi yields,
    makes intelligent decisions, and executes on-chain actions.
    """

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

        # Load ABI
        abi_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "contracts", "deployment.json"
        )
        if os.path.exists(abi_path):
            with open(abi_path, "r") as f:
                self._abi = json.load(f).get("abi", [])
        else:
            self._abi = []

        self._connect()

    def _connect(self):
        try:
            self.w3 = Web3(Web3.HTTPProvider(XL1_RPC_URL))
            if not self.w3.is_connected():
                logger.warning("Agent: X Layer RPC not connected")
                self._status = "rpc_unavailable"
                return

            if (self.contract_address == "0x0000000000000000000000000000000000000000" or
                    not self._abi):
                logger.warning("Agent: Contract not deployed or ABI missing")
                self._status = "contract_not_deployed"
                return

            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=self._abi
            )
            self._connected = True
            self._status = "active"
            logger.info("Agent runtime connected to YieldOptimizer at %s", self.contract_address)
        except Exception as e:
            logger.error("Agent connection failed: %s", str(e))
            self._status = "connection_failed"

    # ========== AGENT CORE ==========

    async def scan_market(self) -> Dict[str, Any]:
        """
        Agent scans all strategies, finds the best one, checks for changes.
        This is the core autonomous behavior.
        """
        if not self._connected:
            self._connect()
            if not self._connected:
                return {"status": "offline", "message": "Contract not connected"}

        loop = asyncio.get_running_loop()

        try:
            # Read strategies from chain
            count = await loop.run_in_executor(
                _executor,
                self.contract.functions.strategyCount().call
            )
        except Exception as e:
            logger.error("Failed to read strategy count: %s", str(e))
            return {"status": "error", "message": str(e)}

        strategies = []
        best_apy = 0
        best_id = 0

        for i in range(1, count + 1):
            try:
                raw = await loop.run_in_executor(
                    _executor,
                    lambda idx=i: self.contract.functions.strategies(idx).call()
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
                    "min_deposit": self.w3.from_wei(raw[3], "ether"),
                    "max_deposit": self.w3.from_wei(raw[4], "ether"),
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
        if best_id > 0:
            best = strategies[best_id - 1] if best_id <= len(strategies) else None

        # Agent decision logic
        action = "hold"
        action_reason = ""

        if best:
            if best["apy"] > 12:
                action = "deposit_recommend"
                action_reason = f"High APY opportunity: {best['name']} at {best['apy']}%"
            elif best["apy"] < 5:
                action = "rebalance_warning"
                action_reason = "Low APY across all strategies. Consider external options."

        self._status = "active"

        return {
            "status": "active",
            "scan_time": self._last_scan.isoformat(),
            "strategies": strategies,
            "strategy_count": count,
            "best_strategy": best,
            "average_apy": round(sum(s["apy"] for s in strategies) / count, 2) if count > 0 else 0,
            "agent_decision": {
                "action": action,
                "reason": action_reason
            },
            "total_value_managed_okb": round(
                sum(s["total_deposits_okb"] for s in strategies), 4
            ),
            "agent_uptime_minutes": round(
                (datetime.now() - self._started_at).total_seconds() / 60, 1
            ),
            "actions_log": self._actions_taken[-5:]  # Last 5 actions
        }

    def execute_deposit(self, strategy_id: int, amount_okb: float, private_key: str) -> Dict[str, Any]:
        """Execute a deposit into a strategy on-chain"""
        if not self._connected:
            return {"success": False, "error": "Contract not connected"}

        try:
            account = self.w3.eth.account.from_key(private_key)
            amount_wei = self.w3.to_wei(amount_okb, "ether")

            txn = self.contract.functions.deposit(strategy_id).build_transaction({
                "from": account.address,
                "value": amount_wei,
                "nonce": self.w3.eth.get_transaction_count(account.address),
                "gas": 300000,
                "gasPrice": self.w3.to_wei(2, "gwei"),
                "chainId": self.w3.eth.chain_id
            })

            signed = self.w3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            action = {
                "type": "deposit",
                "strategy_id": strategy_id,
                "amount_okb": amount_okb,
                "tx_hash": tx_hash.hex(),
                "status": "success" if receipt["status"] == 1 else "failed",
                "timestamp": datetime.now().isoformat()
            }
            self._actions_taken.append(action)
            return {"success": True, "action": action, "receipt": dict(receipt)}

        except Exception as e:
            action = {
                "type": "deposit",
                "strategy_id": strategy_id,
                "amount_okb": amount_okb,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
            self._actions_taken.append(action)
            return {"success": False, "error": str(e), "action": action}

    def execute_withdraw(self, position_index: int, private_key: str) -> Dict[str, Any]:
        """Execute a withdrawal from a position"""
        if not self._connected:
            return {"success": False, "error": "Contract not connected"}

        try:
            account = self.w3.eth.account.from_key(private_key)

            txn = self.contract.functions.withdraw(position_index).build_transaction({
                "from": account.address,
                "nonce": self.w3.eth.get_transaction_count(account.address),
                "gas": 300000,
                "gasPrice": self.w3.to_wei(2, "gwei"),
                "chainId": self.w3.eth.chain_id
            })

            signed = self.w3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            action = {
                "type": "withdraw",
                "position_index": position_index,
                "tx_hash": tx_hash.hex(),
                "status": "success" if receipt["status"] == 1 else "failed",
                "timestamp": datetime.now().isoformat()
            }
            self._actions_taken.append(action)
            return {"success": True, "action": action, "receipt": dict(receipt)}

        except Exception as e:
            action = {
                "type": "withdraw",
                "position_index": position_index,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
            self._actions_taken.append(action)
            return {"success": False, "error": str(e), "action": action}

    def execute_harvest(self, position_index: int, private_key: str) -> Dict[str, Any]:
        """Harvest yield from a position"""
        if not self._connected:
            return {"success": False, "error": "Contract not connected"}

        try:
            account = self.w3.eth.account.from_key(private_key)

            txn = self.contract.functions.harvestYield(position_index).build_transaction({
                "from": account.address,
                "nonce": self.w3.eth.get_transaction_count(account.address),
                "gas": 300000,
                "gasPrice": self.w3.to_wei(2, "gwei"),
                "chainId": self.w3.eth.chain_id
            })

            signed = self.w3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            action = {
                "type": "harvest",
                "position_index": position_index,
                "tx_hash": tx_hash.hex(),
                "status": "success" if receipt["status"] == 1 else "failed",
                "timestamp": datetime.now().isoformat()
            }
            self._actions_taken.append(action)
            return {"success": True, "action": action, "receipt": dict(receipt)}

        except Exception as e:
            action = {
                "type": "harvest",
                "position_index": position_index,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
            self._actions_taken.append(action)
            return {"success": False, "error": str(e), "action": action}

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_status": self._status,
            "contract_address": self.contract_address,
            "chain": "X Layer Testnet (1952)",
            "started_at": self._started_at.isoformat(),
            "uptime_minutes": round(
                (datetime.now() - self._started_at).total_seconds() / 60, 1
            ),
            "last_scan": self._last_scan.isoformat() if self._last_scan else None,
            "actions_count": len(self._actions_taken),
            "recent_actions": self._actions_taken[-10:],
            "recommendations": self._recommendations
        }