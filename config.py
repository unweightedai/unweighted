import os
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient

load_dotenv()

# API Keys
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')

# Solana RPC URL
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
SOLANA_WS_URL = os.getenv('SOLANA_WS_URL', 'wss://api.mainnet-beta.solana.com')

# Jupiter API for price data
JUPITER_API_URL = 'https://price.jup.ag/v4'

# Database
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = 'unweighted_ai'

# Analysis Settings
MIN_TOKEN_AGE_DAYS = 7
MIN_LIQUIDITY_SOL = 100  # Minimum liquidity in SOL
SCAM_DETECTION_THRESHOLD = 0.8
SUCCESS_THRESHOLD_PERCENT = 20

# KOL Tracking
WATCH_LIST_UPDATE_INTERVAL = 3600  # 1 hour
PERFORMANCE_UPDATE_INTERVAL = 86400  # 24 hours

# Initialize Solana client
async def get_solana_client():
    return AsyncClient(SOLANA_RPC_URL)