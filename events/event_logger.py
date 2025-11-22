"""
Manual Event Logging System
============================
Tracks important events (exchange listings, influencer mentions, etc.)
for correlation with price and sentiment changes
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class EventLogger:
    """
    Logs and manages cryptocurrency-related events

    Event categories:
    - exchange_listing: New exchange listings (Binance, Coinbase, etc.)
    - influencer_mention: Celebrity/influencer mentions
    - news_major: Major news coverage (mainstream media)
    - news_minor: Minor news coverage (crypto blogs)
    - regulatory: Regulatory announcements
    - technical: Technical updates, hard forks, etc.
    - social_campaign: Coordinated social media campaigns
    - partnership: Partnership announcements
    - whale_activity: Large wallet movements
    - other: Miscellaneous events
    """

    EVENT_CATEGORIES = [
        'exchange_listing',
        'influencer_mention',
        'news_major',
        'news_minor',
        'regulatory',
        'technical',
        'social_campaign',
        'partnership',
        'whale_activity',
        'other'
    ]

    SENTIMENT_TYPES = ['positive', 'negative', 'neutral']

    def __init__(self, events_file: str = None):
        """
        Initialize event logger

        Args:
            events_file: Path to JSON file for storing events
        """
        if events_file is None:
            events_file = Path(__file__).parent / 'events.json'

        self.events_file = Path(events_file)
        self.events = self._load_events()
        logging.info(f"Event logger initialized ({len(self.events)} events loaded)")

    def _load_events(self) -> List[Dict]:
        """Load events from JSON file"""
        if not self.events_file.exists():
            logging.info(f"Creating new events file: {self.events_file}")
            self.events_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_events([])
            return []

        try:
            with open(self.events_file, 'r') as f:
                events = json.load(f)
            logging.info(f"Loaded {len(events)} events from {self.events_file}")
            return events
        except Exception as e:
            logging.error(f"Error loading events: {e}")
            return []

    def _save_events(self, events: List[Dict]):
        """Save events to JSON file"""
        try:
            with open(self.events_file, 'w') as f:
                json.dump(events, f, indent=2, default=str)
        except Exception as e:
            logging.error(f"Error saving events: {e}")

    def log_event(self,
                  coin_symbol: str,
                  category: str,
                  description: str,
                  timestamp: datetime = None,
                  sentiment: str = 'neutral',
                  impact_score: float = 5.0,
                  source: str = None,
                  url: str = None,
                  metadata: Dict = None) -> Dict:
        """
        Log a new event

        Args:
            coin_symbol: Coin symbol (e.g., 'DOGE', 'PEPE', or 'ALL' for market-wide)
            category: Event category (see EVENT_CATEGORIES)
            description: Brief description of the event
            timestamp: Event timestamp (default: now)
            sentiment: Expected sentiment impact ('positive', 'negative', 'neutral')
            impact_score: Expected impact score 1-10 (1=minimal, 10=massive)
            source: Source of information (e.g., 'Twitter', 'Binance', 'CoinDesk')
            url: URL to source
            metadata: Additional event-specific data

        Returns:
            The logged event dictionary
        """
        if category not in self.EVENT_CATEGORIES:
            logging.warning(f"Unknown category '{category}', using 'other'")
            category = 'other'

        if sentiment not in self.SENTIMENT_TYPES:
            logging.warning(f"Unknown sentiment '{sentiment}', using 'neutral'")
            sentiment = 'neutral'

        if timestamp is None:
            timestamp = datetime.utcnow()

        event = {
            'id': len(self.events) + 1,
            'coin_symbol': coin_symbol.upper(),
            'category': category,
            'description': description,
            'timestamp': timestamp.isoformat(),
            'sentiment': sentiment,
            'impact_score': max(1.0, min(10.0, impact_score)),  # Clamp 1-10
            'source': source,
            'url': url,
            'metadata': metadata or {},
            'logged_at': datetime.utcnow().isoformat()
        }

        self.events.append(event)
        self._save_events(self.events)

        logging.info(f"Event logged: {coin_symbol} - {category} - {description}")
        return event

    def get_events(self,
                   coin_symbol: str = None,
                   category: str = None,
                   start_date: datetime = None,
                   end_date: datetime = None,
                   min_impact: float = None) -> List[Dict]:
        """
        Query events with filters

        Args:
            coin_symbol: Filter by coin symbol
            category: Filter by category
            start_date: Filter events after this date
            end_date: Filter events before this date
            min_impact: Minimum impact score

        Returns:
            List of matching events
        """
        filtered = self.events

        if coin_symbol:
            filtered = [e for e in filtered if e['coin_symbol'] == coin_symbol.upper() or e['coin_symbol'] == 'ALL']

        if category:
            filtered = [e for e in filtered if e['category'] == category]

        if start_date:
            filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) >= start_date]

        if end_date:
            filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) <= end_date]

        if min_impact:
            filtered = [e for e in filtered if e['impact_score'] >= min_impact]

        return filtered

    def get_events_for_timerange(self, coin_symbol: str, start: datetime, end: datetime) -> List[Dict]:
        """
        Get all events for a coin within a time range
        (Useful for correlating with price/sentiment changes)
        """
        return self.get_events(coin_symbol=coin_symbol, start_date=start, end_date=end)

    def get_high_impact_events(self, min_impact: float = 7.0) -> List[Dict]:
        """Get high-impact events (default: 7+/10)"""
        return self.get_events(min_impact=min_impact)

    def delete_event(self, event_id: int) -> bool:
        """Delete an event by ID"""
        initial_len = len(self.events)
        self.events = [e for e in self.events if e['id'] != event_id]

        if len(self.events) < initial_len:
            self._save_events(self.events)
            logging.info(f"Event {event_id} deleted")
            return True

        logging.warning(f"Event {event_id} not found")
        return False

    def update_event(self, event_id: int, **kwargs) -> Optional[Dict]:
        """Update an event's fields"""
        for event in self.events:
            if event['id'] == event_id:
                for key, value in kwargs.items():
                    if key in event:
                        event[key] = value
                self._save_events(self.events)
                logging.info(f"Event {event_id} updated")
                return event

        logging.warning(f"Event {event_id} not found")
        return None

    def get_statistics(self, coin_symbol: str = None) -> Dict:
        """Get event statistics"""
        events = self.get_events(coin_symbol=coin_symbol) if coin_symbol else self.events

        if not events:
            return {
                'total_events': 0,
                'by_category': {},
                'by_sentiment': {},
                'avg_impact': 0,
                'high_impact_count': 0
            }

        from collections import Counter

        return {
            'total_events': len(events),
            'by_category': dict(Counter(e['category'] for e in events)),
            'by_sentiment': dict(Counter(e['sentiment'] for e in events)),
            'avg_impact': sum(e['impact_score'] for e in events) / len(events),
            'high_impact_count': sum(1 for e in events if e['impact_score'] >= 7),
            'date_range': {
                'earliest': min(e['timestamp'] for e in events),
                'latest': max(e['timestamp'] for e in events)
            }
        }

    def export_events(self, filepath: str, coin_symbol: str = None):
        """Export events to CSV"""
        import csv

        events = self.get_events(coin_symbol=coin_symbol) if coin_symbol else self.events

        if not events:
            logging.warning("No events to export")
            return

        with open(filepath, 'w', newline='') as f:
            fieldnames = ['id', 'coin_symbol', 'category', 'description', 'timestamp',
                         'sentiment', 'impact_score', 'source', 'url']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')

            writer.writeheader()
            writer.writerows(events)

        logging.info(f"Exported {len(events)} events to {filepath}")


def log_event_cli():
    """Interactive CLI for logging events"""
    logger = EventLogger()

    print("\n=== Manual Event Logger ===\n")

    coin_symbol = input("Coin symbol (e.g., DOGE, PEPE, or ALL): ").strip().upper()

    print("\nEvent categories:")
    for i, cat in enumerate(EventLogger.EVENT_CATEGORIES, 1):
        print(f"  {i}. {cat}")

    cat_idx = int(input("\nSelect category (1-10): ")) - 1
    category = EventLogger.EVENT_CATEGORIES[cat_idx]

    description = input("Description: ").strip()

    print("\nSentiment: 1=positive, 2=negative, 3=neutral")
    sent_idx = int(input("Select sentiment (1-3): "))
    sentiment = ['positive', 'negative', 'neutral'][sent_idx - 1]

    impact_score = float(input("Impact score (1-10): "))
    source = input("Source (optional): ").strip() or None
    url = input("URL (optional): ").strip() or None

    event = logger.log_event(
        coin_symbol=coin_symbol,
        category=category,
        description=description,
        sentiment=sentiment,
        impact_score=impact_score,
        source=source,
        url=url
    )

    print(f"\nEvent logged successfully (ID: {event['id']})")


if __name__ == "__main__":
    # Interactive CLI
    log_event_cli()
