from pymongo import MongoClient
import config
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.client = MongoClient(config.MONGODB_URI)
        self.db = self.client[config.DB_NAME]
        self.kols = self.db.kols
        self.token_calls = self.db.token_calls
        self.performance_history = self.db.performance_history

    def add_kol(self, kol_data):
        """Add a new KOL to the database."""
        return self.kols.insert_one(kol_data).inserted_id

    def get_kol(self, kol_id):
        """Retrieve KOL information."""
        return self.kols.find_one({'_id': kol_id})

    def update_kol_trust_score(self, kol_id, new_score):
        """Update a KOL's trust score."""
        self.kols.update_one(
            {'_id': kol_id},
            {'$set': {'trust_score': new_score, 'last_updated': datetime.now()}}
        )

    def add_token_call(self, call_data):
        """Record a new token call."""
        return self.token_calls.insert_one(call_data).inserted_id

    def get_recent_calls(self, kol_id, days=30):
        """Get recent token calls for a KOL."""
        cutoff_date = datetime.now() - timedelta(days=days)
        return list(self.token_calls.find({
            'kol_id': kol_id,
            'timestamp': {'$gte': cutoff_date}
        }).sort('timestamp', -1))

    def update_call_performance(self, call_id, performance_data):
        """Update the performance metrics for a token call."""
        self.token_calls.update_one(
            {'_id': call_id},
            {'$set': {
                'performance': performance_data,
                'last_updated': datetime.now()
            }}
        )

    def get_top_kols(self, limit=10):
        """Get top performing KOLs."""
        return list(self.kols.find({
            'total_calls': {'$gt': 5}  # Minimum calls for ranking
        }).sort('trust_score', -1).limit(limit))

    def get_suspicious_kols(self, threshold=40):
        """Get KOLs with low trust scores."""
        return list(self.kols.find({
            'trust_score': {'$lt': threshold},
            'total_calls': {'$gt': 2}  # Minimum calls to be considered
        }))