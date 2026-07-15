"""
Tests for OKX.AI DeFi Yield Optimizer API
"""
import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Don't import web3 here - it has broken pytest integration
# The main application imports web3 only when deploying, not at startup

from src.main import app


@pytest.fixture
def client():
    """Create test client"""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "OKX DeFi Yield Optimizer" in data["service"]


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "OKX DeFi Yield Optimizer"
    assert data["type"] == "Agent Service Provider (ASP)"


@pytest.mark.asyncio
async def test_manifest_endpoint(client):
    """Test ASP manifest endpoint"""
    response = await client.get("/manifest")
    assert response.status_code == 200
    data = response.json()
    assert data["asp_id"] == "okx-defi-yield-optimizer"
    assert "capabilities" in data
    assert len(data["capabilities"]) >= 4


@pytest.mark.asyncio
async def test_opportunities_endpoint(client):
    """Test yield opportunities"""
    response = await client.get("/api/v1/opportunities")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["opportunities"]) > 0


@pytest.mark.asyncio
async def test_analyze_endpoint(client):
    """Test market analysis"""
    response = await client.get("/api/v1/analyze")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "ai_analysis" in data["data"]
    assert "algorithmic_recommendation" in data["data"]


@pytest.mark.asyncio
async def test_strategy_endpoint(client):
    """Test strategy generation"""
    payload = {
        "user_profile": {
            "amount": 5000,
            "risk_tolerance": "high",
            "horizon": "long-term",
            "preferred_protocols": ["OKX Earn", "X Layer DEX"]
        }
    }
    response = await client.post("/api/v1/strategy", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "ai_strategy" in data["data"]
    assert "algorithmic_recommendation" in data["data"]


@pytest.mark.asyncio
async def test_market_endpoint(client):
    """Test market intelligence"""
    response = await client.get("/api/v1/market")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "metrics" in data["data"]
    assert data["data"]["metrics"]["total_opportunities"] > 0


@pytest.mark.asyncio
async def test_optimize_endpoint(client):
    """Test quick optimize"""
    response = await client.get("/api/v1/optimize?amount=2000&risk=low")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["parameters"]["amount"] == 2000
    assert data["data"]["parameters"]["risk_profile"] == "low"


@pytest.mark.asyncio
async def test_ask_endpoint(client):
    """Test Q&A endpoint"""
    payload = {
        "question": "What's the best yield opportunity right now?"
    }
    response = await client.post("/api/v1/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["question"] == "What's the best yield opportunity right now?"
    assert len(data["data"]["answer"]) > 0


@pytest.mark.asyncio
async def test_quick_optimize_defaults(client):
    """Test optimize with default params"""
    response = await client.get("/api/v1/optimize")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["parameters"]["amount"] == 1000
    assert data["data"]["parameters"]["risk_profile"] == "moderate"


@pytest.mark.asyncio
async def test_invalid_risk_profile(client):
    """Test with invalid risk profile"""
    response = await client.get("/api/v1/optimize?amount=100&risk=extreme")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_invalid_amount(client):
    """Test with invalid amount"""
    response = await client.get("/api/v1/optimize?amount=5")
    assert response.status_code == 422