import re
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, List
from twitter_handler import TwitterHandler
from token_analyzer import TokenAnalyzer
from openai_analyzer import OpenAIAnalyzer
from database import Database

logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self, twitter_handler: TwitterHandler, token_analyzer: TokenAnalyzer, 
                 openai_analyzer: OpenAIAnalyzer, db: Database):
        self.twitter = twitter_handler
        self.token_analyzer = token_analyzer
        self.openai = openai_analyzer
        self.db = db
        self.bot_username = "unweightedai"
        
        # Command pattern for analyze
        self.command_pattern = r'analyze\s+@(\w+)'

    async def process_mention(self, tweet):
        """Process a mention of the bot."""
        try:
            # Extract username to analyze
            username = self._extract_username(tweet.text)
            if not username:
                await self._send_error_response(tweet, "Invalid command. Use: @unweightedai analyze @username")
                return

            # Execute analysis
            response = await self._analyze_kol(username)
            
            # Log analysis
            self._log_analysis(tweet, username, response)
            
            # Send response
            await self._send_response(tweet, response)
            
        except Exception as e:
            logger.error(f"Error processing mention: {str(e)}")
            await self._send_error_response(tweet, "Sorry, an error occurred during analysis.")

    def _extract_username(self, tweet_text: str) -> Optional[str]:
        """Extract target username from tweet text."""
        clean_text = re.sub(f'@{self.bot_username}\\s+', '', tweet_text.lower())
        
        match = re.search(self.command_pattern, clean_text)
        if match:
            return match.group(1)
        return None

    async def _analyze_kol(self, username: str) -> Dict:
        """Analyze a KOL's activity using both on-chain and AI analysis."""
        # Get recent token mentions and activity
        token_mentions = await self.twitter.monitor_user_activity(username)
        
        # Collect on-chain data
        token_analyses = []
        for mention in token_mentions:
            for token in mention['tokens']:
                analysis = await self.token_analyzer.analyze_token(token)
                if analysis:
                    token_analyses.append(analysis)

        # AI Analysis of tweets
        tweet_analysis = await self.openai.analyze_tweet_content(token_mentions)
        
        # AI Analysis of token patterns
        token_pattern_analysis = await self.openai.analyze_token_pattern({
            'tokens': token_analyses,
            'mention_count': len(token_mentions),
            'unique_tokens': len(set(m['token'] for m in token_analyses))
        })
        
        # Get user metrics for AI evaluation
        user_metrics = await self.twitter.get_user_metrics(username)
        kol_credibility = await self.openai.evaluate_kol_credibility({
            'total_calls': len(token_analyses),
            'success_rate': self._calculate_success_rate(token_analyses),
            'account_age_days': user_metrics['account_age_days'],
            'engagement_rate': user_metrics['engagement_rate']
        })
        
        # Combine all analyses
        return {
            'username': username,
            'metrics': {
                'total_calls': len(token_analyses),
                'unique_tokens': len(set(m['token'] for m in token_analyses))
            },
            'ai_analysis': {
                'content_analysis': tweet_analysis,
                'token_patterns': token_pattern_analysis,
                'credibility': kol_credibility
            },
            'timestamp': datetime.now()
        }

    def _calculate_success_rate(self, token_analyses: List[Dict]) -> float:
        """Calculate success rate from token analyses."""
        if not token_analyses:
            return 0.0
        successful = len([t for t in token_analyses if t.get('performance', 0) > 0])
        return successful / len(token_analyses)

    def _format_response(self, analysis: Dict) -> str:
        """Format analysis results into a tweet-sized message."""
        ai_analysis = analysis['ai_analysis']
        metrics = analysis['metrics']
        
        risk_level = ai_analysis['token_patterns'].get('risk_level', 'Unknown')
        credibility = ai_analysis['credibility'].get('credibility_score', 0)
        
        return (
            f"Analysis for @{analysis['username']}:\n\n"
            f"Account Status: {'Credible' if credibility > 0.7 else 'Suspicious'}\n"
            f"Risk Level: {risk_level}\n"
            f"Total Calls: {metrics['total_calls']}\n"
            f"Warning Flags: {len(ai_analysis['token_patterns'].get('warning_flags', []))}"
        )

    async def _send_response(self, original_tweet, analysis: Dict):
        """Send response tweet."""
        try:
            message = self._format_response(analysis)
            await self.twitter.send_reply(original_tweet.id, message)
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")

    async def _send_error_response(self, tweet, error_message: str):
        """Send error response tweet."""
        await self.twitter.send_reply(tweet.id, error_message)

    def _log_analysis(self, tweet, username: str, analysis: Dict):
        """Log analysis for monitoring."""
        log_entry = {
            'tweet_id': tweet.id,
            'requester': tweet.user.screen_name,
            'analyzed_user': username,
            'ai_analysis': analysis['ai_analysis'],
            'metrics': analysis['metrics'],
            'timestamp': datetime.now()
        }
        self.db.log_analysis(log_entry)