from database import Database
from kol_tracker import KOLTracker
from token_analyzer import TokenAnalyzer
import time
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize components
    db = Database()
    kol_tracker = KOLTracker(db)
    token_analyzer = TokenAnalyzer()

    while True:
        try:
            # Update KOL watchlist
            logger.info("Updating KOL watchlist...")
            top_kols = db.get_top_kols()
            suspicious_kols = db.get_suspicious_kols()

            # Generate reports
            logger.info("Generating KOL reports...")
            for kol in top_kols:
                report = kol_tracker.get_kol_report(kol['_id'])
                logger.info(f"Top KOL {report['twitter_handle']}: Trust Score {report['trust_score']}")

            for kol in suspicious_kols:
                report = kol_tracker.get_kol_report(kol['_id'])
                logger.info(f"Suspicious KOL {report['twitter_handle']}: Trust Score {report['trust_score']}")

            # Monitor new token calls
            logger.info("Monitoring for new token calls...")
            for kol in top_kols + suspicious_kols:
                try:
                    new_calls = kol_tracker.check_new_calls(kol['_id'])
                    for call in new_calls:
                        kol_tracker.analyze_token_call(kol['_id'], call['contract_address'])
                except Exception as e:
                    logger.error(f"Error processing KOL {kol['twitter_handle']}: {str(e)}")

            # Update performance metrics
            logger.info("Updating performance metrics...")
            recent_calls = db.get_recent_calls(None, days=7)  # Get all recent calls
            for call in recent_calls:
                try:
                    token_analyzer.update_performance(call['_id'])
                except Exception as e:
                    logger.error(f"Error updating performance for call {call['_id']}: {str(e)}")

            # Sleep before next update
            logger.info("Update cycle completed. Sleeping...")
            time.sleep(config.WATCH_LIST_UPDATE_INTERVAL)

        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            time.sleep(60)  # Sleep for 1 minute before retrying

if __name__ == "__main__":
    main()