"""
OKX.AI DeFi Yield Optimizer - Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# DeepSeek API configuration (OpenAI-compatible)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# App settings
APP_NAME = "OKX DeFi Yield Optimizer"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-powered DeFi yield optimization agent for OKX.AI"

# X Layer (OKX L2) settings
XL1_RPC_URL = os.getenv("XL1_RPC_URL", "https://testrpc.xlayer.tech/terigon")
XL1_CHAIN_ID = int(os.getenv("XL1_CHAIN_ID", "1952"))  # X Layer testnet

# DeFi protocol addresses (X Layer)
PROTOCOLS = {
    "okx_earn": {
        "name": "OKX Earn",
        "address": "0x..." if False else "OKX Earn",
        "apy_endpoint": "https://www.okx.com/api/v5/finance/earn/rates",
        "type": "lending"
    },
    "xlayer_swap": {
        "name": "X Layer DEX",
        "address": "0x..." if False else "X Layer DEX",
        "apy_endpoint": "", 
        "type": "dex"
    },
    "stargate": {
        "name": "Stargate Finance",
        "address": "0x..." if False else "Stargate",
        "apy_endpoint": "https://api.stargate.finance/api/v1/pools",
        "type": "bridge_lp"
    }
}

# Yield optimizer contract
YIELD_OPTIMIZER_CONTRACT = os.getenv(
    "YIELD_OPTIMIZER_CONTRACT", 
    "0xE5B0F5e6F7358a8836574caEB6330DeDAf9E140C"  # Deployed on X Layer Testnet
)

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))