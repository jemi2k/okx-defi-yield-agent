"""
OKX.AI DeFi Yield Optimizer - AI Agent Core
Uses DeepSeek API (OpenAI-compatible) for intelligent yield optimization
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

import aiohttp

from config.settings import (
    DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL
)

logger = logging.getLogger("YieldOptimizerAgent")


class YieldOptimizerAgent:
    """
    AI Agent that analyzes DeFi markets and provides intelligent
    yield optimization strategies using DeepSeek LLM
    """

    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL.rstrip('/')
        self.model = DEEPSEEK_MODEL

    async def analyze_market(
        self,
        market_data: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use DeepSeek AI to analyze market conditions and provide insights"""
        if not self.api_key:
            return self._get_fallback_analysis(market_data, opportunities)

        prompt = self._build_market_analysis_prompt(market_data, opportunities)

        try:
            response = await self._call_deepseek(prompt)
            return self._parse_analysis_response(response, market_data, opportunities)
        except Exception as e:
            logger.error("DeepSeek call failed: %s", str(e))
            return self._get_fallback_analysis(market_data, opportunities)

    async def generate_strategy(
        self,
        user_profile: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized yield strategy using AI"""
        if not self.api_key:
            return self._get_fallback_strategy(user_profile, opportunities)

        prompt = self._build_strategy_prompt(user_profile, opportunities, market_data)

        try:
            response = await self._call_deepseek(prompt)
            return self._parse_strategy_response(response, user_profile, opportunities)
        except Exception as e:
            logger.error("Strategy generation failed: %s", str(e))
            return self._get_fallback_strategy(user_profile, opportunities)

    async def answer_question(self, question: str, context: Dict[str, Any]) -> str:
        """Answer user questions about DeFi yields and strategies"""
        if not self.api_key:
            return (
                "I can help with DeFi yield optimization. "
                "Try: 'Show me best yields' or 'Analyze my portfolio'."
            )

        opportunities_json = json.dumps(context.get("opportunities", []), indent=2)
        market_data_json = json.dumps(context.get("market_data", {}), indent=2)

        prompt = (
            "You are an OKX.AI DeFi Yield Optimization Agent. Answer the user's question about "
            "their DeFi portfolio and yield strategies.\n\n"
            "Context:\n"
            "- Available Protocols: " + opportunities_json + "\n"
            "- Market Data: " + market_data_json + "\n\n"
            "User Question: " + question + "\n\n"
            "Provide a helpful, specific answer with actionable DeFi advice."
        )

        try:
            response = await self._call_deepseek(prompt, max_tokens=500)
            return (
                response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "I can help optimize your DeFi yields. Check my recommendations above.")
            )
        except Exception as e:
            top_opps = context.get("opportunities", [])[:3]
            opp_strings = [o["name"] + " (" + str(o["apy"]) + "% APY)" for o in top_opps]
            return (
                "I am analyzing the market. Based on current data: "
                + "; ".join(opp_strings)
                + " are top opportunities."
            )

    async def _call_deepseek(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Call DeepSeek API (OpenAI-compatible format)"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert DeFi yield optimization agent on OKX.AI platform. "
                        "You analyze real-time market data, provide yield farming strategies, "
                        "and help users maximize returns while managing risk. You specialize in:\n"
                        "- OKX Earn products\n"
                        "- X Layer (OKX L2) DeFi ecosystem\n"
                        "- Cross-chain yield opportunities\n"
                        "- Risk-adjusted portfolio optimization\n"
                        "- Automated yield harvesting strategies\n\n"
                        "Be specific, data-driven, and actionable in your recommendations."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    error_text = await resp.text()
                    raise Exception(f"DeepSeek API error {resp.status}: {error_text}")

    def _build_market_analysis_prompt(
        self,
        market_data: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ) -> str:
        return (
            f"Analyze the current DeFi market conditions and yield opportunities:\n\n"
            f"MARKET OVERVIEW:\n"
            f"- X Layer TVL: {market_data.get('total_tvl_usd', 'N/A')}\n"
            f"- Average APY: {market_data.get('average_apy', 'N/A')}%\n"
            f"- Top Protocols: {json.dumps(market_data.get('top_protocols', []), indent=2)}\n\n"
            f"AVAILABLE YIELD OPPORTUNITIES:\n"
            f"{json.dumps(opportunities, indent=2)}\n\n"
            f"Please provide:\n"
            f"1. Current market trend analysis\n"
            f"2. Which protocols/products are most attractive right now\n"
            f"3. Risk assessment of current opportunities\n"
            f"4. Recommended allocation strategy (low/medium/high risk)\n"
            f"5. Any specific timing considerations"
        )

    def _build_strategy_prompt(
        self,
        user_profile: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        market_data: Dict[str, Any]
    ) -> str:
        return (
            f"Generate a personalized DeFi yield optimization strategy:\n\n"
            f"USER PROFILE:\n"
            f"- Investment Amount: ${user_profile.get('amount', 1000)}\n"
            f"- Risk Tolerance: {user_profile.get('risk_tolerance', 'moderate')}\n"
            f"- Investment Horizon: {user_profile.get('horizon', 'medium-term')}\n"
            f"- Preferred Protocols: {user_profile.get('preferred_protocols', ['OKX Earn', 'X Layer DEX'])}\n\n"
            f"CURRENT OPPORTUNITIES:\n"
            f"{json.dumps(opportunities, indent=2)}\n\n"
            f"MARKET DATA:\n"
            f"{json.dumps(market_data, indent=2)}\n\n"
            f"Create a detailed strategy including:\n"
            f"1. Optimal allocation across protocols\n"
            f"2. Expected returns (monthly/annual)\n"
            f"3. Risk mitigation steps\n"
            f"4. Rebalancing recommendations\n"
            f"5. Yield harvesting schedule"
        )

    def _parse_analysis_response(
        self,
        response: Dict[str, Any],
        market_data: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

        avg_apy = sum(o.get("apy", 0) for o in opportunities) / len(opportunities) if opportunities else 0
        max_apy = max((o.get("apy", 0) for o in opportunities), default=0)

        return {
            "ai_analysis": content,
            "market_summary": {
                "average_apy": round(avg_apy, 2),
                "highest_apy": round(max_apy, 2),
                "opportunity_count": len(opportunities),
                "market_sentiment": market_data.get("market_sentiment", "neutral"),
                "timestamp": datetime.now().isoformat()
            },
            "top_recommendations": [
                o for o in sorted(
                    opportunities,
                    key=lambda x: x.get("apy", 0),
                    reverse=True
                )[:3]
            ]
        }

    def _parse_strategy_response(
        self,
        response: Dict[str, Any],
        user_profile: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

        amount = user_profile.get("amount", 1000)
        sorted_opps = sorted(opportunities, key=lambda x: x.get("apy", 0), reverse=True)

        allocation = []
        if sorted_opps:
            risk = user_profile.get("risk_tolerance", "moderate")
            count = 3 if risk == "high" else (2 if risk == "moderate" else 1)

            for i, opp in enumerate(sorted_opps[:count]):
                alloc_pct = 0.5 if i == 0 else (0.3 if i == 1 else 0.2)
                alloc_amount = amount * alloc_pct

                allocation.append({
                    "protocol": opp.get("protocol", "Unknown"),
                    "product": opp.get("name", "Unknown"),
                    "apy": opp.get("apy", 0),
                    "allocation_percentage": alloc_pct * 100,
                    "amount": round(alloc_amount, 2),
                    "estimated_monthly_yield": round(
                        alloc_amount * (opp.get("apy", 0) / 100 / 12), 2
                    )
                })

        total_monthly = sum(a["estimated_monthly_yield"] for a in allocation)

        return {
            "ai_strategy": content,
            "allocation": allocation,
            "total_investment": amount,
            "estimated_monthly_return": round(total_monthly, 2),
            "estimated_annual_return": round(total_monthly * 12, 2),
            "estimated_apy": round(
                (total_monthly * 12 / amount) * 100, 2
            ) if amount > 0 else 0,
            "risk_level": user_profile.get("risk_tolerance", "moderate"),
            "timestamp": datetime.now().isoformat()
        }

    def _get_fallback_analysis(
        self,
        market_data: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback when DeepSeek API is unavailable"""
        avg_apy = sum(o.get("apy", 0) for o in opportunities) / len(opportunities) if opportunities else 0
        max_apy = max((o.get("apy", 0) for o in opportunities), default=0)

        return {
            "ai_analysis": (
                f"Market analysis based on {len(opportunities)} available opportunities. "
                f"Average APY is {avg_apy:.2f}% with highest at {max_apy:.2f}%. "
                f"Recommend diversifying across low and medium risk protocols for optimal returns."
            ),
            "market_summary": {
                "average_apy": round(avg_apy, 2),
                "highest_apy": round(max_apy, 2),
                "opportunity_count": len(opportunities),
                "market_sentiment": market_data.get("market_sentiment", "neutral"),
                "timestamp": datetime.now().isoformat()
            },
            "top_recommendations": sorted(
                opportunities, key=lambda x: x.get("apy", 0), reverse=True
            )[:3]
        }

    def _get_fallback_strategy(
        self,
        user_profile: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback strategy when DeepSeek API is unavailable"""
        return {
            "ai_strategy": "Generated algorithmic strategy based on current market data.",
            "strategy_type": "algorithmic",
            "message": "Connect your DeepSeek API key for AI-powered personalized strategies."
        }