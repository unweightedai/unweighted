from openai import OpenAI
import config
import logging
from typing import List, Dict
import asyncio

logger = logging.getLogger(__name__)

class OpenAIAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.system_prompt = """
        You are an AI analyst specializing in cryptocurrency and Solana token analysis. 
        Your task is to analyze Twitter content and token patterns to:
        1. Identify potential scams or suspicious behavior
        2. Analyze token contract patterns
        3. Evaluate KOL (Key Opinion Leader) credibility
        4. Assess risk levels in token calls
        
        Provide concise, factual analyses without speculation.
        """

    async def analyze_tweet_content(self, tweets: List[Dict]) -> Dict:
        """Analyze tweet content for sentiment and patterns."""
        try:
            tweet_texts = [tweet['text'] for tweet in tweets]
            combined_text = "\n---\n".join(tweet_texts)

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Analyze these tweets for cryptocurrency-related patterns and risks:\n{combined_text}"}
            ]

            response = await self._get_completion(messages)
            return self._parse_content_analysis(response)
        except Exception as e:
            logger.error(f"Error in tweet content analysis: {str(e)}")
            return {"error": str(e)}

    async def analyze_token_pattern(self, token_data: Dict) -> Dict:
        """Analyze token metrics and patterns for risk assessment."""
        try:
            token_info = (
                f"Token Analysis Request:\n"
                f"Liquidity: {token_data['liquidity']}\n"
                f"Holder Count: {token_data['holder_count']}\n"
                f"Age: {token_data['age_days']} days\n"
                f"Recent Transactions: {token_data.get('recent_tx_count', 0)}"
            )

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Analyze this token data for risk patterns:\n{token_info}"}
            ]

            response = await self._get_completion(messages)
            return self._parse_token_analysis(response)
        except Exception as e:
            logger.error(f"Error in token pattern analysis: {str(e)}")
            return {"error": str(e)}

    async def evaluate_kol_credibility(self, kol_data: Dict) -> Dict:
        """Evaluate KOL's credibility based on historical data."""
        try:
            kol_info = (
                f"KOL Analysis Request:\n"
                f"Total Calls: {kol_data['total_calls']}\n"
                f"Success Rate: {kol_data['success_rate']}\n"
                f"Account Age: {kol_data['account_age_days']} days\n"
                f"Engagement Rate: {kol_data['engagement_rate']}"
            )

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Evaluate this KOL's credibility:\n{kol_info}"}
            ]

            response = await self._get_completion(messages)
            return self._parse_kol_analysis(response)
        except Exception as e:
            logger.error(f"Error in KOL credibility evaluation: {str(e)}")
            return {"error": str(e)}

    async def _get_completion(self, messages: List[Dict]) -> str:
        """Get completion from OpenAI API."""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting OpenAI completion: {str(e)}")
            raise

    def _parse_content_analysis(self, response: str) -> Dict:
        """Parse tweet content analysis response."""
        # Implement parsing logic based on expected response format
        try:
            return {
                'sentiment': self._extract_sentiment(response),
                'risk_indicators': self._extract_risk_indicators(response),
                'credibility_score': self._extract_credibility_score(response)
            }
        except Exception as e:
            logger.error(f"Error parsing content analysis: {str(e)}")
            return {'error': 'Failed to parse analysis'}

    def _parse_token_analysis(self, response: str) -> Dict:
        """Parse token analysis response."""
        try:
            return {
                'risk_level': self._extract_risk_level(response),
                'warning_flags': self._extract_warning_flags(response),
                'recommendation': self._extract_recommendation(response)
            }
        except Exception as e:
            logger.error(f"Error parsing token analysis: {str(e)}")
            return {'error': 'Failed to parse analysis'}

    def _parse_kol_analysis(self, response: str) -> Dict:
        """Parse KOL analysis response."""
        try:
            return {
                'credibility_score': self._extract_credibility_score(response),
                'risk_factors': self._extract_risk_factors(response),
                'overall_assessment': self._extract_assessment(response)
            }
        except Exception as e:
            logger.error(f"Error parsing KOL analysis: {str(e)}")
            return {'error': 'Failed to parse analysis'}

    # Helper methods for extracting specific components from OpenAI responses
    def _extract_sentiment(self, response: str) -> float:
        # Implementation for sentiment extraction
        return 0.0

    def _extract_risk_indicators(self, response: str) -> List[str]:
        # Implementation for risk indicators extraction
        return []

    def _extract_credibility_score(self, response: str) -> float:
        # Implementation for credibility score extraction
        return 0.0

    def _extract_risk_level(self, response: str) -> str:
        # Implementation for risk level extraction
        return "Unknown"

    def _extract_warning_flags(self, response: str) -> List[str]:
        # Implementation for warning flags extraction
        return []

    def _extract_recommendation(self, response: str) -> str:
        # Implementation for recommendation extraction
        return ""

    def _extract_risk_factors(self, response: str) -> List[str]:
        # Implementation for risk factors extraction
        return []

    def _extract_assessment(self, response: str) -> str:
        # Implementation for assessment extraction
        return ""