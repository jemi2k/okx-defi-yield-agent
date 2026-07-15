"""
DeFi Data Fetcher - Live data from X Layer on-chain contract
"""
import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.contract_client import ContractClient
from config.settings import PROTOCOLS

logger = logging.getLogger("DeFiDataFetcher")


class DeFiDataFetcher:
    """Fetches live DeFi yield data from on-chain contract on X Layer"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.contract_client = ContractClient()
        self.contract_client.connect()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def get_all_yield_opportunities(self) -> List[Dict[str, Any]]:
        """Fetch live yield data from the deployed YieldOptimizer contract on X Layer"""
        opportunities = []

        # Read from on-chain contract
        onchain_strategies = self.contract_client.get_all_strategies()
        if onchain_strategies:
            opportunities.extend(onchain_strategies)
            logger.info("Loaded %d strategies from X Layer contract", len(onchain_strategies))
        else:
            logger.warning("No on-chain strategies found")

        return opportunities

    async def fetch_market_overview(self) -> Dict[str, Any]:
        """Fetch market sentiment from OKX API"""
        try:
            session = await self._get_session()
            url = "https://www.okx.com/api/v5/dex/defi/market"
            headers = {"Accept": "application/json"}
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"market_sentiment": "neutral", "note": "OKX API unavailable"}
        except Exception:
            return {"market_sentiment": "neutral", "note": "OKX API unavailable"}

    async def fetch_xlayer_tvl(self) -> Dict[str, Any]:
        """Fetch X Layer contract info"""
        contract_info = self.contract_client.get_contract_info()
        return {
            "chain": "X Layer Testnet (1952)",
            "contract_address": contract_info.get("address", "N/A"),
            "contract_status": "deployed" if contract_info.get("connected") else "not deployed",
            "explorer": contract_info.get("explorer", ""),
            "timestamp": datetime.now().isoformat()
        }

    def calculate_recommendation(
        self,
        opportunities: List[Dict],
        risk_profile: str = "moderate",
        amount_usd: float = 1000.0
    ) -> Dict[str, Any]:
        """Calculate yield allocation from live on-chain strategies"""
        if not opportunities:
            return {
                "best_option": None,
                "reasoning": "No yield opportunities found on-chain.",
                "diversification": []
            }

        if risk_profile == "low":
            filtered = [o for o in opportunities if o.get("risk", "medium") in ["low", "very_low"]]
        elif risk_profile == "high":
            filtered = [o for o in opportunities if o.get("risk", "medium") in ["high", "very_high"]]
        else:
            filtered = opportunities

        if not filtered:
            filtered = opportunities

        sorted_opps = sorted(filtered, key=lambda x: x.get("apy", 0), reverse=True)
        best = sorted_opps[0] if sorted_opps else None

        top_3 = sorted_opps[:3]
        split_amount = amount_usd / len(top_3) if top_3 else 0

        diversification = []
        for opp in top_3:
            allocation_amount = round(split_amount, 2)
            monthly_yield = round(allocation_amount * (opp.get("apy", 0) / 100 / 12), 2)
            diversification.append({
                "protocol": opp.get("protocol", "Unknown"),
                "product": opp.get("name", "Unknown"),
                "apy": opp.get("apy", 0),
                "amount": allocation_amount,
                "estimated_monthly_yield": monthly_yield,
                "risk": opp.get("risk", "medium"),
                "source": opp.get("type", "onchain")
            })

        total_yield = sum(d["estimated_monthly_yield"] for d in diversification) if diversification else 0

        return {
            "best_option": best,
            "diversification": diversification,
            "total_investment": amount_usd,
            "estimated_monthly_yield": round(total_yield, 2),
            "estimated_apy": round((total_yield * 12 / amount_usd) * 100, 2) if amount_usd > 0 and total_yield > 0 else 0,
            "reasoning": self._generate_reasoning(best, diversification, risk_profile)
        }

    def _generate_reasoning(
        self,
        best: Optional[Dict],
        diversification: List[Dict],
        risk_profile: str
    ) -> str:
        if not best and not diversification:
            return "No suitable yield opportunities found on X Layer."

        parts = ["Based on live X Layer on-chain data and your {} risk profile,".format(risk_profile)]
        if best:
            parts.append(
                "the top recommended option is {} offering {}% APY on {}.".format(
                    best.get("protocol", "a protocol"),
                    best.get("apy", 0),
                    best.get("name", "their product")
                )
            )
        if len(diversification) > 1:
            apys = ["{} ({}% APY)".format(d["protocol"], d["apy"]) for d in diversification]
            parts.append("We recommend diversifying across: {}.".format(", ".join(apys)))
        return " ".join(parts)

    async def close(self):
        if self.session:
            await self.session.close()