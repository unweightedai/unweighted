import tweepy
import config
from datetime import datetime, timedelta
from utils import extract_token_address
import asyncio
import logging

logger = logging.getLogger(__name__)

class TwitterHandler:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=config.TWITTER_BEARER_TOKEN,
            consumer_key=config.TWITTER_API_KEY,
            consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_SECRET,
            wait_on_rate_limit=True
        )
        self.tracked_keywords = [
            'solana', 'SOL', '$SOL', 'SPL', 'token', 'mint', 'presale',
            'NFT', 'airdrop', 'dex', 'listing', 'launch'
        ]

    async def get_user_tweets(self, username, limit=100, days_back=7):
        """Fetch recent tweets from a specific user."""
        try:
            # Get user ID from username
            user = self.client.get_user(username=username)
            if not user.data:
                logger.error(f"User {username} not found")
                return []

            user_id = user.data.id
            start_time = datetime.utcnow() - timedelta(days=days_back)

            # Get user's tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=limit,
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations']
            )

            if not tweets.data:
                return []

            return self._process_tweets(tweets.data)
        except Exception as e:
            logger.error(f"Error fetching tweets for {username}: {str(e)}")
            return []

    async def monitor_user_activity(self, username):
        """Monitor a user's recent activity for token-related content."""
        try:
            tweets = await self.get_user_tweets(username, limit=50, days_back=2)
            token_mentions = []

            for tweet in tweets:
                tokens = self._extract_token_mentions(tweet)
                if tokens:
                    token_mentions.append({
                        'tweet_id': tweet.id,
                        'created_at': tweet.created_at,
                        'text': tweet.text,
                        'tokens': tokens,
                        'metrics': {
                            'likes': tweet.public_metrics['like_count'],
                            'retweets': tweet.public_metrics['retweet_count'],
                            'replies': tweet.public_metrics['reply_count']
                        }
                    })

            return token_mentions
        except Exception as e:
            logger.error(f"Error monitoring {username}: {str(e)}")
            return []

    def _extract_token_mentions(self, tweet):
        """Extract token addresses from tweet text."""
        # Extract potential token addresses
        addresses = extract_token_address(tweet.text)
        
        # Filter out non-token addresses (could be enhanced)
        return list(set(addresses))

    def _process_tweets(self, tweets):
        """Process and filter relevant tweets."""
        processed_tweets = []
        
        for tweet in tweets:
            # Check if tweet contains any tracked keywords
            if any(keyword.lower() in tweet.text.lower() for keyword in self.tracked_keywords):
                processed_tweets.append(tweet)
                
        return processed_tweets

    async def get_user_influence_score(self, username):
        """Calculate user's influence score based on engagement metrics."""
        try:
            user = self.client.get_user(
                username=username,
                user_fields=['public_metrics', 'created_at', 'verified']
            )
            
            if not user.data:
                return 0

            metrics = user.data.public_metrics
            
            # Basic influence score calculation
            followers = metrics['followers_count']
            following = metrics['following_count']
            tweets = metrics['tweet_count']
            
            # Get recent tweets engagement
            recent_tweets = await self.get_user_tweets(username, limit=20, days_back=30)
            avg_engagement = self._calculate_avg_engagement(recent_tweets)
            
            # Calculate score (simplified version)
            score = (
                (followers * 0.4) +
                (avg_engagement * 0.4) +
                (tweets * 0.2)
            ) / 1000  # Normalize
            
            # Cap at 100
            return min(100, score)
        except Exception as e:
            logger.error(f"Error calculating influence score for {username}: {str(e)}")
            return 0

    def _calculate_avg_engagement(self, tweets):
        """Calculate average engagement rate from tweets."""
        if not tweets:
            return 0
            
        total_engagement = 0
        for tweet in tweets:
            metrics = tweet.public_metrics
            engagement = (
                metrics['like_count'] +
                metrics['retweet_count'] * 2 +
                metrics['reply_count'] * 3
            )
            total_engagement += engagement
            
        return total_engagement / len(tweets)

    async def check_account_credibility(self, username):
        """Check the credibility of a Twitter account."""
        try:
            user = self.client.get_user(
                username=username,
                user_fields=['created_at', 'verified', 'public_metrics', 'description']
            )
            
            if not user.data:
                return {'credible': False, 'reason': 'User not found'}

            user_data = user.data
            
            # Check account age
            account_age = (datetime.utcnow() - user_data.created_at).days
            if account_age < 90:  # Less than 3 months old
                return {'credible': False, 'reason': 'Account too new'}

            # Check followers/following ratio
            metrics = user_data.public_metrics
            if metrics['followers_count'] < 100:
                return {'credible': False, 'reason': 'Too few followers'}
                
            if metrics['followers_count'] < metrics['following_count'] * 0.1:
                return {'credible': False, 'reason': 'Suspicious follower ratio'}

            # Account seems credible
            return {
                'credible': True,
                'metrics': {
                    'followers': metrics['followers_count'],
                    'following': metrics['following_count'],
                    'tweets': metrics['tweet_count'],
                    'account_age_days': account_age
                }
            }
        except Exception as e:
            logger.error(f"Error checking credibility for {username}: {str(e)}")
            return {'credible': False, 'reason': f'Error: {str(e)}'}