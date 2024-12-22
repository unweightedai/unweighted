import os
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient

load_dotenv()

# Twitter API Settings
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Twitter Monitoring Settings
TWITTER_SCAN_INTERVAL = 300  # 5 minutes
TWITTER_MAX_TWEETS_PER_SCAN = 100
TWITTER_MIN_ACCOUNT_AGE_DAYS = 90
TWITTER_MIN_FOLLOWERS = 100
TWITTER_ENGAGEMENT_THRESHOLD = 50  # Minimum engagement rate for consideration

# Solana RPC URL
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
SOLANA_WS_URL = os.getenv('SOLANA_WS_URL', 'wss://api.mainnet-beta.solana.com')

# Jupiter API for price data
JUPITER_API_URL = 'https://price.jup.ag/v4'

# Database
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = 'unweighted_ai'

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = "gpt-4-turbo-preview"
OPENAI_MAX_TOKENS = 500
OPENAI_TEMPERATURE = 0.3

# Analysis Settings
MIN_CREDIBILITY_SCORE = 0.7
MIN_SUCCESS_RATE = 0.5
HIGH_RISK_THRESHOLD = 0.7
MEDIUM_RISK_THRESHOLD = 0.4

# KOL Tracking
WATCH_LIST_UPDATE_INTERVAL = 3600  # 1 hour
PERFORMANCE_UPDATE_INTERVAL = 86400  # 24 hours

# Initialize Solana client
async def get_solana_client():
    return AsyncClient(SOLANA_RPC_URL)
