"""
DeFi Data Fetcher - Calculation layer for yield strategies
"""
import logging
from typing import Dict, List, Any

logger = logging.getLogger("DeFiDataFetcher")


class DeFiDataFetcher:
    """Handles yield allocation calculations"""

    def __init__(self):
        pass

    def calculate_recommendation(
        self,
        opportunities: List[Dict],
        risk_profile: str = "moderate",
        amount_usd: float = 1000.0
    ) -> Dict[str, Any]:
        """Calculate yield allocation from any list of strategies"""
        if not opportunities:
            return {
                "best_option": None,
                "reasoning": "No strategies available. Run the agent scan to load live on-chain data.",
                "diversification": []
            }

        # Filter by risk
        if risk_profile == "low":
            filtered = [o for o in opportunities if o.get("risk") in ["low", "very_low"]]
        elif risk_profile == "high":
            filtered = [o for o in opportunities if o.get("risk") in ["high", "very_high"]]
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
            monthly_yield = round(split_amount * (opp.get("apy", 0) / 100 / 12), 2)
            diversification.append({
                "protocol": opp.get("protocol", "Unknown"),
                "product": opp.get("name", "Unknown"),
                "apy": opp.get("apy", 0),
                "amount": round(split_amount, 2),
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
            "reasoning": "Generated from live X Layer on-chain strategies with {} risk profile.".format(risk_profile)
        }

    async def get_all_yield_opportunities(self) -> List[Dict]:
        """Get opportunities from agent runtime cache"""
        from src.main import agent_runtime
        status = agent_runtime.get_status()
        strategies = status.get("recommendations", [])
        if strategies:
            logger.info("Returning %d cached strategies from agent runtime", len(strategies))
        return strategies

    async def fetch_market_overview(self) -> Dict[str, Any]:
        return {"market_sentiment": "neutral"}

    async def fetch_xlayer_tvl(self) -> Dict[str, Any]:
        return {
            "chain": "X Layer Testnet (1952)",
            "contract_address": "0xE5B0F5e6F7358a8836574caEB6330DeDAf9E140C",
            "contract_status": "deployed",
            "explorer": "https://www.okx.com/web3/explorer/xlayer-test/address/0xE5B0F5e6F7358a8836574caEB6330DeDAf9E140C"
        }

    async def close(self):
        pass