import tweepy
from datetime import datetime, timedelta
import pandas as pd
from database import Database
from token_analyzer import TokenAnalyzer
#continue

class KOLTracker:
    def __init__(self, db_connection):
        self.db = db_connection
        self.token_analyzer = TokenAnalyzer()
        self.auth = tweepy.OAuthHandler(config.TWITTER_API_KEY, config.TWITTER_API_SECRET)
        self.auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_SECRET)
        self.api = tweepy.API(self.auth)

    def track_kol(self, twitter_handle):
        """Track a new KOL's activity."""
        kol_data = {
            'twitter_handle': twitter_handle,
            'date_added': datetime.now(),
            'total_calls': 0,
            'successful_calls': 0,
            'scam_calls': 0,
            'trust_score': 100,
            'last_updated': datetime.now()
        }
        self.db.add_kol(kol_data)

    def analyze_token_call(self, kol_id, contract_address):
        """Analyze a new token call from a KOL."""
        token_data = self.token_analyzer.analyze_contract(contract_address)
        
        call_data = {
            'kol_id': kol_id,
            'contract_address': contract_address,
            'timestamp': datetime.now(),
            'initial_price': token_data['price'],
            'initial_liquidity': token_data['liquidity'],
            'risk_score': token_data['risk_score'],
            'status': 'monitoring'
        }
        
        self.db.add_token_call(call_data)
        
        if token_data['risk_score'] > config.SCAM_DETECTION_THRESHOLD:
            self.update_kol_trust_score(kol_id, -10)

    def update_kol_trust_score(self, kol_id, change):
        """Update KOL's trust score based on their performance."""
        kol = self.db.get_kol(kol_id)
        new_score = max(0, min(100, kol['trust_score'] + change))
        self.db.update_kol_trust_score(kol_id, new_score)

    def get_kol_report(self, kol_id):
        """Generate a report for a specific KOL."""
        kol = self.db.get_kol(kol_id)
        recent_calls = self.db.get_recent_calls(kol_id, days=30)
        
        return {
            'twitter_handle': kol['twitter_handle'],
            'trust_score': kol['trust_score'],
            'success_rate': kol['successful_calls'] / max(1, kol['total_calls']),
            'recent_calls': recent_calls,
            'recommendation': 'Trusted' if kol['trust_score'] > 70 else 'Caution' if kol['trust_score'] > 40 else 'Untrusted'
        }
