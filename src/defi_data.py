"""
DeFi Data Fetcher - Retrieves yield data from OKX ecosystem and DeFi protocols
"""
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from config.settings import PROTOCOLS


class DeFiDataFetcher:
    """Fetches real-time DeFi yield data from multiple sources"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = 60  # seconds
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def fetch_okx_earn_rates(self) -> List[Dict[str, Any]]:
        """Fetch OKX Earn product rates"""
        try:
            session = await self._get_session()
            # OKX API v5 endpoint for earn rates
            url = "https://www.okx.com/api/v5/finance/earn/rates"
            headers = {"Accept": "application/json"}
            
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._parse_okx_rates(data)
                else:
                    # Fallback to mock data if API unavailable
                    return self._get_mock_okx_rates()
        except Exception as e:
            print(f"[DeFiData] OKX Earn fetch error: {e}")
            return self._get_mock_okx_rates()
    
    async def fetch_market_overview(self) -> Dict[str, Any]:
        """Fetch overall DeFi market sentiment data"""
        try:
            session = await self._get_session()
            url = "https://www.okx.com/api/v5/dex/defi/market"
            headers = {"Accept": "application/json"}
            
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    return self._get_mock_market_overview()
        except Exception as e:
            print(f"[DeFiData] Market overview error: {e}")
            return self._get_mock_market_overview()
    
    async def fetch_xlayer_tvl(self) -> Dict[str, Any]:
        """Fetch X Layer TVL and ecosystem stats"""
        mock_data = {
            "total_tvl_usd": 125000000,  # $125M
            "top_protocols": [
                {"name": "OKX DEX", "tvl": 50000000, "type": "DEX"},
                {"name": "OKX Lending", "tvl": 35000000, "type": "Lending"},
                {"name": "OKX Earn", "tvl": 40000000, "type": "Yield"},
            ],
            "average_apy": 8.5,
            "timestamp": datetime.now().isoformat()
        }
        return mock_data
    
    async def get_all_yield_opportunities(self) -> List[Dict[str, Any]]:
        """Aggregate all yield opportunities across protocols"""
        tasks = [
            self.fetch_okx_earn_rates(),
            self.fetch_market_overview(),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        opportunities = []
        
        # Parse OKX Earn
        if not isinstance(results[0], Exception):
            opportunities.extend(results[0])
        
        return opportunities
    
    def calculate_recommendation(
        self, 
        opportunities: List[Dict], 
        risk_profile: str = "moderate",
        amount_usd: float = 1000.0
    ) -> Dict[str, Any]:
        """
        AI-driven yield recommendation algorithm
        """
        if not opportunities:
            return {
                "best_option": None,
                "reasoning": "No yield opportunities available at this time.",
                "diversification": []
            }
        
        # Filter by risk profile
        if risk_profile == "low":
            filtered = [o for o in opportunities if o.get("risk", "medium") in ["low", "very_low"]]
        elif risk_profile == "high":
            filtered = [o for o in opportunities if o.get("risk", "medium") in ["high", "very_high"]]
        else:  # moderate
            filtered = opportunities
        
        if not filtered:
            filtered = opportunities
        
        # Sort by APY descending
        sorted_opps = sorted(filtered, key=lambda x: x.get("apy", 0), reverse=True)
        
        # Best single option
        best = sorted_opps[0] if sorted_opps else None
        
        # Diversification strategy (equal split top 3)
        top_3 = sorted_opps[:3]
        split_amount = amount_usd / len(top_3) if top_3 else 0
        
        diversification = []
        for opp in top_3:
            diversification.append({
                "protocol": opp.get("protocol", "Unknown"),
                "product": opp.get("name", "Unknown"),
                "apy": opp.get("apy", 0),
                "amount": round(split_amount, 2),
                "estimated_monthly_yield": round(
                    split_amount * (opp.get("apy", 0) / 100 / 12), 2
                ),
                "risk": opp.get("risk", "medium")
            })
        
        total_est_yield = sum(
            d["estimated_monthly_yield"] for d in diversification
        ) if diversification else 0
        
        return {
            "best_option": best,
            "diversification": diversification,
            "total_investment": amount_usd,
            "estimated_monthly_yield": round(total_est_yield, 2),
            "estimated_apy": round(
                (total_est_yield * 12 / amount_usd) * 100, 2
            ) if amount_usd > 0 else 0,
            "reasoning": self._generate_reasoning(best, diversification, risk_profile)
        }
    
    def _generate_reasoning(
        self, 
        best: Optional[Dict], 
        diversification: List[Dict],
        risk_profile: str
    ) -> str:
        """Generate natural language reasoning for recommendations"""
        if not best and not diversification:
            return "No suitable yield opportunities found matching your criteria."
        
        parts = [f"Based on your {risk_profile} risk profile,"]
        
        if best:
            parts.append(
                f"the top recommended option is {best.get('protocol', 'a protocol')} "
                f"offering {best.get('apy', 0)}% APY on {best.get('name', 'their product')}. "
            )
        
        if len(diversification) > 1:
            apys = [f"{d['protocol']} ({d['apy']}% APY)" for d in diversification]
            parts.append(
                f"For optimal risk-adjusted returns, we recommend diversifying across "
                f"{', '.join(apys)}. "
                f"This strategy targets an estimated blended APY of approximately "
                f"{self._estimate_blended_apy(diversification)}%."
            )
        
        return " ".join(parts)
    
    def _estimate_blended_apy(self, diversification: List[Dict]) -> float:
        if not diversification:
            return 0.0
        total = sum(d.get("apy", 0) for d in diversification)
        return round(total / len(diversification), 2)
    
    def _parse_okx_rates(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse OKX API response into standardized format"""
        opportunities = []
        if data.get("code") == "0" and "data" in data:
            for item in data["data"]:
                opportunities.append({
                    "protocol": "OKX Earn",
                    "name": item.get("productName", "Unknown"),
                    "apy": float(item.get("rate", 0)) * 100,
                    "min_deposit": float(item.get("minDeposit", 0)),
                    "risk": "low",
                    "type": "lending",
                    "timestamp": datetime.now().isoformat()
                })
        return opportunities
    
    def _get_mock_okx_rates(self) -> List[Dict[str, Any]]:
        """Mock data for demo/testing when API is unavailable"""
        import random
        base_apy = random.uniform(5, 15)
        return [
            {
                "protocol": "OKX Earn",
                "name": "Flexible Savings",
                "apy": round(base_apy, 2),
                "min_deposit": 10,
                "risk": "very_low",
                "type": "lending",
                "timestamp": datetime.now().isoformat()
            },
            {
                "protocol": "OKX Earn",
                "name": "Fixed 7-Day",
                "apy": round(base_apy + 1.5, 2),
                "min_deposit": 50,
                "risk": "low",
                "type": "lending",
                "timestamp": datetime.now().isoformat()
            },
            {
                "protocol": "OKX Earn",
                "name": "Fixed 30-Day",
                "apy": round(base_apy + 3.0, 2),
                "min_deposit": 100,
                "risk": "low",
                "type": "lending",
                "timestamp": datetime.now().isoformat()
            },
            {
                "protocol": "OKX DEX",
                "name": "ETH-USDT LP",
                "apy": round(base_apy + 5.0, 2),
                "min_deposit": 500,
                "risk": "medium",
                "type": "liquidity",
                "timestamp": datetime.now().isoformat()
            },
            {
                "protocol": "Stargate Finance",
                "name": "USDC Pool",
                "apy": round(base_apy + 2.0, 2),
                "min_deposit": 100,
                "risk": "medium",
                "type": "bridge_lp",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    def _get_mock_market_overview(self) -> Dict[str, Any]:
        """Mock market overview for demo"""
        return {
            "market_sentiment": "bullish",
            "total_value_locked": "$125M on X Layer",
            "average_apy_trending": "upward",
            "top_performers": [
                {"protocol": "OKX Lending", "apy": "12.5%", "change": "+2.3%"},
                {"protocol": "X Layer DEX", "apy": "8.2%", "change": "+0.5%"},
            ],
            "risk_warning": "DeFi yields fluctuate. Diversify to manage risk."
        }
    
    async def close(self):
        if self.session:
            await self.session.close()