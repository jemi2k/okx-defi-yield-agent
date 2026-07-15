# OKX DeFi Yield Optimizer Agent

An AI-powered Agent Service Provider (ASP) for OKX.AI that optimizes DeFi yield strategies on X Layer (OKX L2).

---

## Overview

| Detail | Value |
|--------|-------|
| **ASP ID** | #6002 |
| **Category** | Revenue Rocket / Finance Copilot |
| **Platform** | OKX.AI Genesis Hackathon |
| **Live URL** | https://okx-defi-yield-agent.onrender.com |

---

## Architecture

The OKX DeFi Yield Optimizer connects users to live X Layer on-chain yield strategies through an autonomous AI agent.

```
User Wallet (MetaMask)
  |
  +-- Dashboard (HTML/CSS/JS)
        |
        +-- FastAPI Server (Python)
              |
              +-- DeepSeek AI Agent (Market Analysis)
              +-- Agent Runtime (Autonomous Scanner)
              +-- DeFi Data Fetcher (On-Chain)
              |
              +-- X Layer Testnet (Chain ID: 1952)
                    |
                    +-- YieldOptimizer.sol
                          0xE5B0F5e6F7358a8836574caEB6330DeDAf9E140C
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12+ / FastAPI |
| AI Agent | DeepSeek API (OpenAI-compatible) |
| Smart Contract | Solidity 0.8.19 |
| Blockchain | X Layer Testnet (Chain ID: 1952) |
| Frontend | HTML / CSS / JavaScript |
| Deployment | Render.com |

---

## Smart Contract

**Contract**: `contracts/YieldOptimizer.sol`
**Address**: `0xE5B0F5e6F7358a8836574caEB6330DeDAf9E140C`
**Explorer**: https://www.okx.com/web3/explorer/xlayer-test/address/0xE5B0F5e6F7358a8836574caEB6330DeDAf9E140C

### Live On-Chain Strategies

| ID | Name | Protocol | APY | Risk |
|----|------|----------|-----|------|
| 1 | OKX Earn Flexible | OKX | 8.5% | Low |
| 2 | OKX Earn 7-Day | OKX | 10.0% | Medium |
| 3 | OKX Earn 30-Day | OKX | 11.7% | Medium |
| 4 | ETH-USDT LP | X Layer DEX | 13.75% | High |
| 5 | USDC Bridge Pool | Stargate Finance | 10.75% | Medium |

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
| GET | `/` | ASP information |
| GET | `/health` | Health check |
| GET | `/manifest` | OKX.AI ASP manifest |
| GET | `/api/v1/agent/scan` | Agent scans on-chain strategies |
| GET | `/api/v1/agent/status` | Agent runtime status |
| POST | `/api/v1/agent/execute` | Execute on-chain action |
| POST | `/api/v1/strategy` | Generate personalized strategy |
| GET | `/api/v1/analyze` | DeepSeek AI market analysis |
| GET | `/api/v1/market` | Market intelligence |
| POST | `/api/v1/ask` | AI Q&A |

---

## Quick Start

### Prerequisites

- Python 3.12+
- DeepSeek API key
- X Layer testnet OKB (for contract deployment)

### Installation

```bash
cd okxai-defi-yield-agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DeepSeek API key
```

### Run

```bash
python src/main.py
# Server starts at http://localhost:8000
# API Docs at http://localhost:8000/docs
```

### Deploy Smart Contract

```bash
pip install web3 py-solc-x
export DEPLOYER_PRIVATE_KEY=0x...
export DEPLOYER_ADDRESS=0x...
python contracts/deploy.py
```

### Run Tests

```bash
pytest tests/ -v
```

---

## Deployment

The application is deployed on Render.com at https://okx-defi-yield-agent.onrender.com

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DEEPSEEK_API_KEY` | DeepSeek API key for AI agent |
| `YIELD_OPTIMIZER_CONTRACT` | Deployed contract address |

### Provider Setup

**Render.com**:
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

---

## Links

- **Dashboard**: https://okx-defi-yield-agent.onrender.com/
- **API Docs**: https://okx-defi-yield-agent.onrender.com/docs
- **ASP Manifest**: https://okx-defi-yield-agent.onrender.com/manifest
- **GitHub**: https://github.com/jemi2k/okx-defi-yield-agent
- **Contract Explorer**: https://www.okx.com/web3/explorer/xlayer-test/address/0xE5B0F5e6F7358a8836574caEB6330DeDAf9E140C

---

## ASP Registration

- **ASP ID**: #6002
- **Service**: Yield Strategy Generator (A2A, 0.5 USDT)
- **Transaction**: 0x2342f6884895c8b479c875364e25000c8ddbb79ab4bb0979564f72d39a0472d8

---

## Acknowledgments

- OKX.AI for the hackathon platform
- HackQuest for the builder journey
- DeepSeek for AI API support
- X Layer for the L2 infrastructure

---

*Built for the OKX.AI Genesis Hackathon*