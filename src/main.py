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

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
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

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(BASE_DIR, "static")
dashboard_path = os.path.join(static_dir, "index.html")

# Mount static files
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

data_fetcher = DeFiDataFetcher()
ai_agent = YieldOptimizerAgent()


# ========== Helpers ==========

def _is_browser(request: Request) -> bool:
    """Check if request is from a browser (wants HTML)"""
    accept = request.headers.get("accept", "")
    return "text/html" in accept


# ========== Lifecycle Events ==========

@app.on_event("startup")
async def startup():
    logger.info("Starting up...")
    logger.info("DeepSeek API Key configured: %s", bool(ai_agent.api_key))

@app.on_event("shutdown")
async def shutdown():
    await data_fetcher.close()
    logger.info("Shutting down...")


# ========== Root Endpoint: Serves UI for browsers, JSON for API ==========

@app.get("/", include_in_schema=False)
async def root(request: Request):
    """Root endpoint: Serves dashboard for browsers, ASP info for API clients"""
    if _is_browser(request) and os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    # API client - return ASP info
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
        "interactive_dashboard": "/dashboard",
        "api_docs": "/docs",
        "asp_manifest": "/manifest",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/dashboard", include_in_schema=False)
async def dashboard():
    """Interactive web dashboard"""
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return HTMLResponse("<h1>Dashboard not found</h1>", status_code=404)


# ========== Health & Info Endpoints ==========

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
async def manifest(request: Request):
    """OKX.AI ASP Manifest - Shows HTML for browsers, JSON for API"""
    data = {
        "asp_id": "okx-defi-yield-optimizer",
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "author": "Ermias B. HackQuest Builder",
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
                "chain": "X Layer Testnet",
                "chain_id": 1952,
                "contract_address": "0xE5B0F5e6F7358a8836574caEB6330DeDAf9E140C",
                "contract": "YieldOptimizer.sol",
                "features": ["deposit", "withdraw", "harvest", "strategy-management", "yield-optimization"],
                "explorer": "https://www.okx.com/web3/explorer/xlayer-test/address/0xE5B0F5e6F7358a8836574caEB6330DeDAf9E140C"
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

    if _is_browser(request):
        import json
        pretty = json.dumps(data, indent=2)
        html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{APP_NAME} - ASP Manifest</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#080C14;color:#E2E8F0;padding:32px 24px}}
.container{{max-width:800px;margin:0 auto}}
h1{{font-size:24px;font-weight:700;margin-bottom:8px;background:linear-gradient(135deg,#0052FF,#00D67D);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.sub{{color:#7B89A8;font-size:14px;margin-bottom:28px}}
.section{{background:#0F1525;border:1px solid #1A2440;border-radius:12px;padding:20px;margin-bottom:16px}}
.section h3{{font-size:14px;font-weight:600;margin-bottom:14px;color:#E2E8F0}}
.tag{{display:inline-block;padding:4px 10px;background:rgba(0,82,255,0.12);color:#0052FF;border-radius:6px;font-size:12px;margin:0 6px 6px 0}}
.cap-item{{padding:10px 14px;background:#080C14;border:1px solid #1A2440;border-radius:8px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center}}
.cap-item:last-child{{margin-bottom:0}}
.cap-name{{font-weight:600;font-size:14px}}
.cap-desc{{font-size:12px;color:#7B89A8;display:block;margin-top:2px}}
.cap-endpoint{{font-family:monospace;font-size:12px;color:#00D67D;background:rgba(0,214,125,0.08);padding:4px 10px;border-radius:4px}}
.integration{{display:flex;gap:12px;align-items:center}}
.integration span{{font-size:13px}}
pre{{background:#080C14;border:1px solid #1A2440;border-radius:10px;padding:18px;overflow-x:auto;font-size:13px;color:#E2E8F0;line-height:1.6}}
.footer{{text-align:center;margin-top:32px;font-size:12px;color:#7B89A8}}
a{{color:#0052FF;text-decoration:none}}
</style></head>
<body>
<div class="container">
<h1>{APP_NAME}</h1>
<p class="sub">ASP Manifest - {APP_DESCRIPTION}</p>
<div class="section">
<h3>ASP Details</h3>
<p style="font-size:13px;color:#7B89A8;margin-bottom:12px">ID: <strong style="color:#E2E8F0">{data['asp_id']}</strong> &middot; Author: <strong style="color:#E2E8F0">{data['author']}</strong> &middot; Version: <strong style="color:#E2E8F0">{data['version']}</strong></p>
<p style="font-size:13px;color:#7B89A8;margin-bottom:12px">Category: <strong style="color:#E2E8F0">{data['category']}</strong> &middot; Pricing: <strong style="color:#00D67D">{data['pricing']['model']}</strong></p>
{"".join(f'<span class="tag">{t}</span>' for t in data['tags'])}
</div>
<div class="section">
<h3>Capabilities</h3>
{"".join(f'<div class="cap-item"><div><span class="cap-name">{c["name"]}</span><span class="cap-desc">{c["description"]}</span></div><span class="cap-endpoint">{c["endpoint"]}</span></div>' for c in data['capabilities'])}
</div>
<div class="section">
<h3>Blockchain Integration</h3>
{"".join(f'<div class="integration"><strong>{b["chain"]}</strong> <span style="color:#7B89A8">Chain ID: {b["chain_id"]}</span> <span style="color:#7B89A8">Contract: {b["contract"]}</span></div>' for b in data['blockchain_integrations'])}
</div>
<div class="section">
<h3>Raw JSON</h3>
<pre>{pretty}</pre>
</div>
<p class="footer"><a href="/">Dashboard</a> &middot; <a href="/docs">API Docs</a> &middot; Built for OKX.AI Genesis Hackathon</p>
</div></body></html>"""
        return HTMLResponse(html)

    return data


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
    logger.info("Dashboard: http://%s:%s/", HOST, PORT)
    logger.info("API Docs: http://%s:%s/docs", HOST, PORT)
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )