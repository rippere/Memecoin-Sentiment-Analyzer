"""
Quick Event Logging Script
===========================
Convenient script for logging events from command line
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from events.event_logger import EventLogger


def main():
    """Command-line interface for event logging"""
    parser = argparse.ArgumentParser(
        description='Log cryptocurrency events for analysis',
        epilog='Examples:\n'
               '  python log_event.py DOGE exchange_listing "Listed on Binance" --impact 9\n'
               '  python log_event.py PEPE influencer_mention "Elon Musk tweet" --sentiment positive --impact 8\n'
               '  python log_event.py ALL regulatory "SEC announcement" --sentiment negative --impact 7',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('coin', type=str,
                       help='Coin symbol (e.g., DOGE, PEPE) or ALL for market-wide')

    parser.add_argument('category', type=str,
                       choices=EventLogger.EVENT_CATEGORIES,
                       help='Event category')

    parser.add_argument('description', type=str,
                       help='Event description')

    parser.add_argument('--sentiment', type=str,
                       choices=['positive', 'negative', 'neutral'],
                       default='neutral',
                       help='Expected sentiment impact (default: neutral)')

    parser.add_argument('--impact', type=float,
                       default=5.0,
                       help='Impact score 1-10 (default: 5)')

    parser.add_argument('--source', type=str,
                       help='Information source (e.g., Twitter, CoinDesk)')

    parser.add_argument('--url', type=str,
                       help='Source URL')

    parser.add_argument('--timestamp', type=str,
                       help='Event timestamp (ISO format, default: now)')

    parser.add_argument('--list', action='store_true',
                       help='List recent events instead of logging')

    parser.add_argument('--stats', action='store_true',
                       help='Show event statistics')

    args = parser.parse_args()

    logger = EventLogger()

    # List events
    if args.list:
        events = logger.get_events(coin_symbol=args.coin if args.coin != 'ALL' else None)
        print(f"\n=== Recent Events ({len(events)} total) ===\n")
        for event in sorted(events, key=lambda x: x['timestamp'], reverse=True)[:10]:
            print(f"[{event['timestamp'][:16]}] {event['coin_symbol']} - {event['category']}")
            print(f"  {event['description']}")
            print(f"  Impact: {event['impact_score']}/10, Sentiment: {event['sentiment']}\n")
        return

    # Show statistics
    if args.stats:
        stats = logger.get_statistics(args.coin if args.coin != 'ALL' else None)
        print(f"\n=== Event Statistics ===\n")
        print(f"Total events: {stats['total_events']}")
        print(f"Average impact: {stats['avg_impact']:.1f}/10")
        print(f"High impact events (7+): {stats['high_impact_count']}")
        print(f"\nBy category:")
        for cat, count in stats['by_category'].items():
            print(f"  {cat}: {count}")
        print(f"\nBy sentiment:")
        for sent, count in stats['by_sentiment'].items():
            print(f"  {sent}: {count}")
        return

    # Parse timestamp if provided
    timestamp = None
    if args.timestamp:
        try:
            timestamp = datetime.fromisoformat(args.timestamp)
        except ValueError:
            print(f"Error: Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            sys.exit(1)

    # Log the event
    event = logger.log_event(
        coin_symbol=args.coin,
        category=args.category,
        description=args.description,
        timestamp=timestamp,
        sentiment=args.sentiment,
        impact_score=args.impact,
        source=args.source,
        url=args.url
    )

    print(f"\n Event logged successfully!")
    print(f"  ID: {event['id']}")
    print(f"  Coin: {event['coin_symbol']}")
    print(f"  Category: {event['category']}")
    print(f"  Impact: {event['impact_score']}/10")
    print(f"  Sentiment: {event['sentiment']}")
    print(f"  Timestamp: {event['timestamp']}")


if __name__ == "__main__":
    main()
