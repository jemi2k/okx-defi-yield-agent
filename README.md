# OKX DeFi Yield Optimizer Agent

An AI-powered Agent Service Provider (ASP) for OKX.AI that optimizes DeFi yield strategies on X Layer (OKX L2).

---

## Hackathon Submission

- **Category**: Revenue Rocket / Finance Copilot
- **Platform**: OKX.AI Genesis Hackathon
- **Deadline**: July 17, 2026 @ 23:59 UTC
- **Builder**: HackQuest Journey Participant

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Smart Contract](#smart-contract)
- [API Endpoints](#api-endpoints)
- [Quick Start](#quick-start)
- [Deployment Guide](#deployment-guide)
- [Demo Script](#demo-script)
- [Submission Guide](#submission-guide)
- [Revenue Model](#revenue-model)

---

## Problem Statement

DeFi users face three major challenges:

1. **Information Overload**: Hundreds of yield opportunities across multiple protocols
2. **Complex Decision Making**: Understanding risk-adjusted returns requires deep DeFi knowledge
3. **Manual Management**: Constantly monitoring and rebalancing positions is time-consuming

OKX.AI needs intelligent ASPs that turn complex DeFi data into actionable strategies.

---

## Solution Overview

The OKX DeFi Yield Optimizer Agent is an AI-powered ASP that:

1. Aggregates real-time yield data from OKX Earn, X Layer DEX, and cross-chain protocols
2. Analyzes market conditions using DeepSeek AI (OpenAI-compatible)
3. Generates personalized yield strategies based on user risk profile
4. Executes via smart contracts on X Layer for automated yield harvesting
5. Monitors positions and recommends rebalancing

### Key Features

| Feature | Description |
|---------|-------------|
| AI-Powered Analysis | DeepSeek LLM analyzes market trends and generates strategies |
| Real-Time Data | Fetches live APY rates from OKX ecosystem |
| Personalized Strategies | Risk-adjusted portfolio allocation |
| On-Chain Execution | Solidity smart contracts on X Layer |
| Natural Language Q&A | Ask questions about your DeFi portfolio |
| One-Click Optimize | Quick yield optimization with any amount |

---

## Architecture

```
OKX.AI Platform
  |
  +-- DeFi Yield Optimizer ASP
  |     |
  |     +-- FastAPI Server (Python)
  |     +-- DeepSeek AI Agent
  |     +-- DeFi Data Fetcher
  |     |
  |     +-- X Layer (OKX L2) Blockchain
  |           |
  |           +-- YieldOptimizer.sol Contract
  |                 - Strategy Management
  |                 - Deposit / Withdraw
  |                 - Yield Harvesting
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11+ / FastAPI |
| AI Agent | DeepSeek API (OpenAI-compatible) |
| Smart Contract | Solidity 0.8.19 |
| Blockchain | X Layer (OKX L2, Chain ID: 195) |
| Data Fetching | aiohttp / OKX API v5 |
| Testing | pytest / httpx |

---

## Smart Contract

**Contract**: `contracts/YieldOptimizer.sol`

The smart contract manages:
- Strategy Registry: Add, update, and toggle yield strategies
- User Positions: Track deposits, withdrawals, and yield
- Yield Calculation: Time-based APY calculation
- Best Strategy Finder: Auto-identify highest APY strategy

### Key Functions

```solidity
// Admin
addStrategy(name, protocol, minDeposit, maxDeposit, apy)
updateStrategyApy(strategyId, newApy)
toggleStrategy(strategyId, active)

// User
deposit(strategyId)        // payable
withdraw(positionIndex)
harvestYield(positionIndex)

// View
getAllStrategies()
getUserPositions(user)
getBestStrategy()
calculateYield(position)
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | ASP info for OKX.AI |
| GET | `/health` | Health check |
| GET | `/manifest` | OKX.AI ASP manifest (required for listing) |
| GET | `/api/v1/opportunities` | All yield opportunities |
| GET | `/api/v1/analyze` | AI-powered market analysis |
| POST | `/api/v1/strategy` | Generate personalized strategy |
| GET | `/api/v1/market` | Market intelligence |
| POST | `/api/v1/ask` | Natural language Q&A |
| GET | `/api/v1/optimize` | One-click quick optimize |

---

## Quick Start

### Prerequisites

- Python 3.11+
- DeepSeek API key (or any OpenAI-compatible API)
- X Layer testnet funds (optional, for contract deployment)

### Installation

```bash
# Navigate to project directory
cd okxai-defi-yield-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DeepSeek API key
```

### Run the Server

```bash
# Start the API server
python src/main.py

# Server starts at http://localhost:8000
# API Docs at http://localhost:8000/docs
```

### Run Tests

```bash
pytest tests/ -v
```

### Deploy Smart Contract (Optional)

```bash
# Install deployment dependencies
pip install web3 py-solc-x

# Set deployer credentials
export DEPLOYER_PRIVATE_KEY=0x...
export DEPLOYER_ADDRESS=0x...

# Deploy to X Layer testnet
python contracts/deploy.py
```

---

## Deployment Guide

### Option 1: Render.com (Recommended - Free Tier)

1. Push the code to a GitHub repository
2. Go to https://render.com and sign up with GitHub
3. Click "New +" then "Web Service"
4. Connect your GitHub repository
5. Fill in the following:
   - **Name**: `okx-defi-yield-optimizer`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variable:
   - `DEEPSEEK_API_KEY` = `your_deepseek_api_key_here`
7. Click "Create Web Service"

### Option 2: Railway.app

1. Go to https://railway.app and sign up
2. Click "New Project" then "Deploy from GitHub"
3. Select your repository
4. Add the same environment variable
5. Automatic deployment will begin

### Option 3: Manual VPS

```bash
# On your server:
git clone <your-repo-url>
cd okxai-defi-yield-agent
pip install -r requirements.txt
export DEEPSEEK_API_KEY=your_deepseek_api_key_here
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## Demo Script

### 90-Second Demo Walkthrough

**Scene 1 (0-15s)**: Introduction
"Meet the OKX DeFi Yield Optimizer -- an AI agent that helps you maximize your DeFi yields on X Layer."

**Scene 2 (15-35s)**: Show market intelligence
```bash
curl https://your-app-url.onrender.com/api/v1/market
```

**Scene 3 (35-60s)**: Generate a personalized strategy
```bash
curl -X POST https://your-app-url.onrender.com/api/v1/strategy \
  -H "Content-Type: application/json" \
  -d '{"user_profile": {"amount": 5000, "risk_tolerance": "moderate"}}'
```

**Scene 4 (60-90s)**: Smart contract integration
"The AI analyzes market conditions and recommends diversifying across OKX Earn, X Layer DEX, and Stargate Finance. All backed by our YieldOptimizer smart contract on X Layer, enabling automated deposits, withdrawals, and yield harvesting."

### Demo Requirements
- Length: 90 seconds maximum
- Platform: X (Twitter)
- Hashtag: #OKXAI
- Include clear demonstration of the ASP in action

---

## Submission Guide

### Step 1: Build the ASP
The DeFi Yield Optimizer Agent is complete and ready.

### Step 2: Submit for OKX.AI Listing
1. Deploy the FastAPI server to a public URL (Render, Railway, or VPS)
2. Submit your ASP for listing through OKX.AI
3. Ensure it passes OKX AI's internal review

### Step 3: Post on X

Post content template:
```
Just built the OKX DeFi Yield Optimizer Agent for #OKXAI Genesis Hackathon!

AI-powered yield optimization on X Layer
Real-time DeFi analysis
Smart contract automation

Check out the demo! [link to demo video]

#OKXAI #DeFi #YieldOptimization
```

### Step 4: Submit Google Form
Before July 17, 23:59 UTC, submit:
- ASP details
- Link to X participation post
- Demo video link

---

## Revenue Model

The ASP targets the Revenue Rocket category with:

1. **Free Tier**: Basic yield analysis and recommendations
2. **Premium Tier** (post-hackathon):
   - Automated yield harvesting
   - Advanced portfolio tracking
   - Priority AI analysis
3. **Revenue Streams**:
   - 0.5% performance fee on harvested yields
   - Subscription model for advanced features
   - Referral fees from protocol partnerships

---

## Links

- **GitHub**: [Your Repository URL]
- **API Docs**: [Deployed URL]/docs
- **Demo Video**: [YouTube/Vimeo Link]
- **X Post**: [Link to your #OKXAI post]

---

## Acknowledgments

- OKX.AI for the hackathon platform
- HackQuest for the builder journey
- DeepSeek for AI API support
- X Layer for the L2 infrastructure

---

*Built for the OKX.AI Genesis Hackathon*