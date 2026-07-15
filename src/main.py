"""
OKX.AI DeFi Yield Optimizer - Main Application
FastAPI server that serves as an Agent Service Provider (ASP) on OKX.AI
"""
import os
import sys
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config.settings import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION,
    HOST, PORT
)
from src.defi_data import DeFiDataFetcher
from src.ai_agent import YieldOptimizerAgent

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(APP_NAME)

# ========== Pydantic Models ==========

class UserProfile(BaseModel):
    amount: float = Field(1000, description="Investment amount in USD", ge=10)
    risk_tolerance: str = Field("moderate", description="Risk profile: low, moderate, or high")
    horizon: str = Field("medium-term", description="Investment horizon")
    preferred_protocols: List[str] = Field(
        ["OKX Earn", "X Layer DEX"],
        description="Preferred DeFi protocols"
    )

class QuestionRequest(BaseModel):
    question: str = Field(..., description="User's question about DeFi yields")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class StrategyRequest(BaseModel):
    user_profile: UserProfile

# ========== FastAPI App ==========

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve the dashboard UI
from fastapi.responses import FileResponse
dashboard_path = os.path.join(static_dir, "index.html")

@app.get("/ui", include_in_schema=False)
async def dashboard():
    """Web dashboard UI"""
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"error": "Dashboard not found"}

data_fetcher = DeFiDataFetcher()
ai_agent = YieldOptimizerAgent()


# ========== Lifecycle Events ==========

@app.on_event("startup")
async def startup():
    logger.info("Starting up...")
    logger.info("DeepSeek API Key configured: %s", bool(ai_agent.api_key))

@app.on_event("shutdown")
async def shutdown():
    await data_fetcher.close()
    logger.info("Shutting down...")


# ========== Health & Info Endpoints ==========

@app.get("/")
async def root():
    """Root endpoint - ASP info for OKX.AI"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "type": "Agent Service Provider (ASP)",
        "platform": "OKX.AI",
        "capabilities": [
            "DeFi yield analysis",
            "Portfolio optimization",
            "Risk assessment",
            "Market intelligence",
            "Strategy automation"
        ],
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/manifest")
async def manifest():
    """OKX.AI ASP Manifest - Required for listing"""
    return {
        "asp_id": "okx-defi-yield-optimizer",
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "author": "HackQuest Builder",
        "category": "Finance Copilot / Revenue Rocket",
        "tags": ["defi", "yield", "optimization", "ai-agent", "okx-ecosystem"],
        "pricing": {
            "model": "free",
            "description": "Free to use during hackathon"
        },
        "capabilities": [
            {
                "id": "yield-analysis",
                "name": "Yield Analysis",
                "description": "Analyze current DeFi yield opportunities",
                "endpoint": "/api/v1/analyze"
            },
            {
                "id": "strategy-generation",
                "name": "Strategy Generation",
                "description": "Generate personalized yield strategies",
                "endpoint": "/api/v1/strategy"
            },
            {
                "id": "market-intelligence",
                "name": "Market Intelligence",
                "description": "Get DeFi market insights and trends",
                "endpoint": "/api/v1/market"
            },
            {
                "id": "qa",
                "name": "Q&A",
                "description": "Ask questions about DeFi yields",
                "endpoint": "/api/v1/ask"
            }
        ],
        "blockchain_integrations": [
            {
                "chain": "X Layer (OKX L2)",
                "chain_id": 195,
                "contract": "YieldOptimizer.sol",
                "features": ["deposit", "withdraw", "harvest", "strategy-management"]
            }
        ],
        "timestamp": datetime.now().isoformat()
    }


# ========== API Endpoints ==========

@app.get("/api/v1/opportunities")
async def get_opportunities():
    """Get all available yield opportunities"""
    try:
        opportunities = await data_fetcher.get_all_yield_opportunities()
        market_data = await data_fetcher.fetch_xlayer_tvl()

        return {
            "success": True,
            "data": {
                "opportunities": opportunities,
                "market_overview": market_data,
                "count": len(opportunities),
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error("Failed to fetch opportunities: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analyze")
async def analyze_market():
    """AI-powered market analysis"""
    try:
        opportunities = await data_fetcher.get_all_yield_opportunities()
        market_data = await data_fetcher.fetch_xlayer_tvl()

        analysis = await ai_agent.analyze_market(market_data, opportunities)

        recommendation = data_fetcher.calculate_recommendation(
            opportunities,
            risk_profile="moderate",
            amount_usd=1000
        )

        return {
            "success": True,
            "data": {
                "ai_analysis": analysis,
                "algorithmic_recommendation": recommendation,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error("Failed to analyze market: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/strategy")
async def generate_strategy(request: StrategyRequest):
    """Generate personalized yield strategy"""
    try:
        profile = request.user_profile
        opportunities = await data_fetcher.get_all_yield_opportunities()
        market_data = await data_fetcher.fetch_xlayer_tvl()

        ai_strategy = await ai_agent.generate_strategy(
            profile.model_dump(),
            opportunities,
            market_data
        )

        recommendation = data_fetcher.calculate_recommendation(
            opportunities,
            risk_profile=profile.risk_tolerance,
            amount_usd=profile.amount
        )

        return {
            "success": True,
            "data": {
                "ai_strategy": ai_strategy,
                "algorithmic_recommendation": recommendation,
                "user_profile": profile.model_dump(),
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error("Failed to generate strategy: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market")
async def market_intelligence():
    """Get DeFi market intelligence"""
    try:
        opportunities = await data_fetcher.get_all_yield_opportunities()
        market_data = await data_fetcher.fetch_xlayer_tvl()
        market_overview = await data_fetcher.fetch_market_overview()

        avg_apy = sum(o.get("apy", 0) for o in opportunities) / len(opportunities) if opportunities else 0
        max_apy = max((o.get("apy", 0) for o in opportunities), default=0)

        return {
            "success": True,
            "data": {
                "market_overview": market_overview,
                "xlayer_stats": market_data,
                "metrics": {
                    "total_opportunities": len(opportunities),
                    "average_apy": round(avg_apy, 2),
                    "highest_apy": round(max_apy, 2),
                    "market_trend": "bullish" if avg_apy > 8 else "neutral"
                },
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error("Failed to fetch market data: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question about DeFi yields"""
    try:
        opportunities = await data_fetcher.get_all_yield_opportunities()
        market_data = await data_fetcher.fetch_xlayer_tvl()

        context = request.context or {}
        context["opportunities"] = opportunities
        context["market_data"] = market_data

        answer = await ai_agent.answer_question(request.question, context)

        return {
            "success": True,
            "data": {
                "question": request.question,
                "answer": answer,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error("Failed to answer question: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/optimize")
async def quick_optimize(
    amount: float = Query(1000, description="Investment amount in USD", ge=10),
    risk: str = Query("moderate", description="Risk tolerance: low, moderate, high")
):
    """Quick one-click yield optimization"""
    try:
        opportunities = await data_fetcher.get_all_yield_opportunities()

        recommendation = data_fetcher.calculate_recommendation(
            opportunities,
            risk_profile=risk,
            amount_usd=amount
        )

        return {
            "success": True,
            "data": {
                "recommendation": recommendation,
                "parameters": {
                    "amount": amount,
                    "risk_profile": risk
                },
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error("Failed to optimize: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ========== Main Entry Point ==========

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting %s v%s", APP_NAME, APP_VERSION)
    logger.info("API Docs: http://%s:%s/docs", HOST, PORT)
    logger.info("ASP Manifest: http://%s:%s/manifest", HOST, PORT)
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )