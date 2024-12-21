import asyncio
from solana.rpc.async_api import AsyncClient
import requests
from datetime import datetime, timedelta
import config
from solders.pubkey import Pubkey
import base58
import aiohttp

class TokenAnalyzer:
    def __init__(self):
        self.client = None
        self.jupiter_api = config.JUPITER_API_URL

    async def get_client(self):
        if not self.client:
            self.client = await config.get_solana_client()
        return self.client

    async def analyze_token(self, mint_address):
        """Analyze a Solana token for potential red flags and metrics."""
        try:
            client = await self.get_client()
            
            # Convert string address to Pubkey if needed
            if isinstance(mint_address, str):
                mint_address = Pubkey.from_string(mint_address)

            # Basic token analysis
            token_info = await self._get_token_info(mint_address)
            liquidity = await self._check_liquidity(mint_address)
            holder_info = await self._get_holder_info(mint_address)
            
            # Risk analysis
            risk_factors = {
                'low_liquidity': liquidity < config.MIN_LIQUIDITY_SOL,
                'high_concentration': holder_info['concentration_risk'],
                'suspicious_activity': await self._check_suspicious_activity(mint_address),
                'new_token': token_info['age_days'] < config.MIN_TOKEN_AGE_DAYS
            }
            
            risk_score = self._calculate_risk_score(risk_factors)
            
            return {
                'mint_address': str(mint_address),
                'age_days': token_info['age_days'],
                'liquidity': liquidity,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'price': await self._get_current_price(mint_address),
                'holder_count': holder_info['holder_count'],
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error analyzing token {mint_address}: {str(e)}")
            return None

    async def _get_token_info(self, mint_address):
        """Get basic token information."""
        client = await self.get_client()
        
        # Get token account info
        response = await client.get_account_info(mint_address)
        if not response.value:
            raise ValueError("Token not found")
            
        # Get first transaction (creation date)
        signatures = await client.get_signatures_for_address(mint_address, limit=1)
        creation_time = datetime.fromtimestamp(signatures.value[0].block_time)
        age_days = (datetime.now() - creation_time).days
        
        return {
            'age_days': age_days,
            'exists': True
        }

    async def _check_liquidity(self, mint_address):
        """Check token liquidity across major Solana DEXs."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.jupiter_api}/price?ids={str(mint_address)}") as response:
                    data = await response.json()
                    return float(data.get('data', {}).get(str(mint_address), {}).get('liquidityUsd', 0))
        except:
            return 0

    async def _get_holder_info(self, mint_address):
        """Analyze token holder distribution."""
        client = await self.get_client()
        
        # Get token accounts
        response = await client.get_token_accounts_by_owner(mint_address)
        
        if not response.value:
            return {'holder_count': 0, 'concentration_risk': True}
            
        holders = response.value
        holder_count = len(holders)
        
        # Calculate concentration (simplified)
        concentration_risk = holder_count < 100
        
        return {
            'holder_count': holder_count,
            'concentration_risk': concentration_risk
        }

    async def _check_suspicious_activity(self, mint_address):
        """Check for suspicious token activity patterns."""
        client = await self.get_client()
        
        # Get recent transactions
        signatures = await client.get_signatures_for_address(mint_address, limit=100)
        if not signatures.value:
            return True
            
        # Analysis would look for patterns like:
        # - Unusual transaction frequency
        # - Large dumps
        # - Suspicious wallet interactions
        return False  # Placeholder

    async def _get_current_price(self, mint_address):
        """Get current token price in USD."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.jupiter_api}/price?ids={str(mint_address)}") as response:
                    data = await response.json()
                    return float(data.get('data', {}).get(str(mint_address), {}).get('price', 0))
        except:
            return 0

    def _calculate_risk_score(self, risk_factors):
        """Calculate a risk score from 0 to 1 based on risk factors."""
        score = 0
        if risk_factors['low_liquidity']:
            score += 0.3
        if risk_factors['high_concentration']:
            score += 0.3
        if risk_factors['suspicious_activity']:
            score += 0.2
        if risk_factors['new_token']:
            score += 0.2
        return min(1.0, score)