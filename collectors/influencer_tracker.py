"""
Influencer Tracking System
===========================
Tracks cryptocurrency influencer mentions and sentiment
Supports follower-weighted sentiment analysis
"""

import sys
from pathlib import Path
import json
from typing import List, Dict
from datetime import datetime
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors.sentiment_analyzer import SentimentAnalyzer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class InfluencerTracker:
    """
    Tracks and analyzes cryptocurrency influencer activity
    """

    def __init__(self, influencers_file: str = None):
        """
        Initialize influencer tracker

        Args:
            influencers_file: Path to JSON file with influencer data
        """
        if influencers_file is None:
            influencers_file = Path(__file__).parent.parent / 'config' / 'influencers.json'

        self.influencers_file = Path(influencers_file)
        self.influencers = self._load_influencers()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.mentions = []  # Store influencer mentions

        logging.info(f"Influencer tracker initialized ({len(self.influencers)} influencers tracked)")

    def _load_influencers(self) -> Dict:
        """Load influencer database"""
        if not self.influencers_file.exists():
            logging.info(f"Creating influencers file: {self.influencers_file}")
            self.influencers_file.parent.mkdir(parents=True, exist_ok=True)
            default_influencers = self._get_default_influencers()
            self._save_influencers(default_influencers)
            return default_influencers

        try:
            with open(self.influencers_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading influencers: {e}")
            return {}

    def _save_influencers(self, influencers: Dict):
        """Save influencer database"""
        try:
            with open(self.influencers_file, 'w', encoding='utf-8') as f:
                json.dump(influencers, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving influencers: {e}")

    def _get_default_influencers(self) -> Dict:
        """Get default influencer list"""
        return {
            'crypto_influencers': [
                {
                    'id': 'elonmusk',
                    'name': 'Elon Musk',
                    'platform': 'twitter',
                    'followers': 150000000,
                    'category': 'celebrity',
                    'impact_weight': 10.0
                },
                {
                    'id': 'cz_binance',
                    'name': 'CZ Binance',
                    'platform': 'twitter',
                    'followers': 8000000,
                    'category': 'exchange_ceo',
                    'impact_weight': 9.0
                },
                {
                    'id': 'vitalikbuterin',
                    'name': 'Vitalik Buterin',
                    'platform': 'twitter',
                    'followers': 5000000,
                    'category': 'developer',
                    'impact_weight': 8.0
                },
                {
                    'id': 'saylor',
                    'name': 'Michael Saylor',
                    'platform': 'twitter',
                    'followers': 3000000,
                    'category': 'investor',
                    'impact_weight': 7.0
                },
                {
                    'id': 'cryptowizardd',
                    'name': 'Crypto Wizard',
                    'platform': 'twitter',
                    'followers': 500000,
                    'category': 'analyst',
                    'impact_weight': 5.0
                },
                {
                    'id': 'altcoinbuzz',
                    'name': 'Altcoin Buzz',
                    'platform': 'youtube',
                    'followers': 400000,
                    'category': 'media',
                    'impact_weight': 4.0
                }
            ]
        }

    def add_influencer(self, influencer_id: str, name: str, platform: str,
                      followers: int, category: str, impact_weight: float = 5.0):
        """
        Add a new influencer to track

        Args:
            influencer_id: Unique identifier (username/handle)
            name: Display name
            platform: Platform (twitter, youtube, tiktok, etc.)
            followers: Follower count
            category: Category (celebrity, analyst, developer, etc.)
            impact_weight: Manual impact weight (1-10)
        """
        influencer = {
            'id': influencer_id,
            'name': name,
            'platform': platform,
            'followers': followers,
            'category': category,
            'impact_weight': impact_weight,
            'added_at': datetime.utcnow().isoformat()
        }

        if 'crypto_influencers' not in self.influencers:
            self.influencers['crypto_influencers'] = []

        self.influencers['crypto_influencers'].append(influencer)
        self._save_influencers(self.influencers)

        logging.info(f"Influencer added: {name} ({influencer_id})")

    def log_mention(self, influencer_id: str, coin_symbol: str, text: str,
                   platform: str = 'twitter', url: str = None, timestamp: datetime = None):
        """
        Log an influencer mention of a coin

        Args:
            influencer_id: Influencer identifier
            coin_symbol: Coin mentioned
            text: Mention text/content
            platform: Platform where mention occurred
            url: URL to mention (optional)
            timestamp: When the mention occurred (default: now)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Find influencer
        influencer = self._get_influencer(influencer_id)
        if not influencer:
            logging.warning(f"Unknown influencer: {influencer_id}")
            return

        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze_text(text)

        # Calculate weighted impact
        weighted_impact = self._calculate_weighted_impact(influencer, sentiment)

        mention = {
            'id': len(self.mentions) + 1,
            'influencer_id': influencer_id,
            'influencer_name': influencer['name'],
            'coin_symbol': coin_symbol.upper(),
            'text': text,
            'platform': platform,
            'url': url,
            'timestamp': timestamp.isoformat(),
            'sentiment_analysis': sentiment,
            'follower_count': influencer['followers'],
            'impact_weight': influencer['impact_weight'],
            'weighted_impact': weighted_impact,
            'logged_at': datetime.utcnow().isoformat()
        }

        self.mentions.append(mention)
        logging.info(f"Mention logged: {influencer['name']} mentioned {coin_symbol} (impact: {weighted_impact:.2f})")

        return mention

    def _get_influencer(self, influencer_id: str) -> Dict:
        """Get influencer by ID"""
        for inf in self.influencers.get('crypto_influencers', []):
            if inf['id'] == influencer_id:
                return inf
        return None

    def _calculate_weighted_impact(self, influencer: Dict, sentiment: Dict) -> float:
        """
        Calculate weighted impact score

        Factors:
        - Follower count (log scale)
        - Manual impact weight
        - Sentiment strength

        Returns:
            Weighted impact score
        """
        import math

        # Follower weight (logarithmic scale)
        follower_weight = math.log10(max(influencer['followers'], 1)) / 8  # Normalize to ~1

        # Manual impact weight (1-10 scale)
        manual_weight = influencer['impact_weight'] / 10

        # Sentiment strength
        sentiment_strength = abs(sentiment['compound'])

        # Combined weighted impact
        weighted_impact = follower_weight * manual_weight * sentiment_strength * 100

        return weighted_impact

    def get_coin_influencer_sentiment(self, coin_symbol: str,
                                     days: int = 7,
                                     min_impact: float = None) -> Dict:
        """
        Get aggregated influencer sentiment for a coin

        Args:
            coin_symbol: Coin to analyze
            days: Number of days to look back
            min_impact: Minimum weighted impact to include

        Returns:
            Aggregated influencer sentiment metrics
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Filter mentions
        relevant_mentions = [
            m for m in self.mentions
            if m['coin_symbol'] == coin_symbol.upper() and
            datetime.fromisoformat(m['timestamp']) >= cutoff_date
        ]

        if min_impact:
            relevant_mentions = [m for m in relevant_mentions if m['weighted_impact'] >= min_impact]

        if not relevant_mentions:
            return {
                'coin_symbol': coin_symbol,
                'mention_count': 0,
                'avg_sentiment': 0.0,
                'total_weighted_impact': 0.0
            }

        # Calculate metrics
        total_impact = sum(m['weighted_impact'] for m in relevant_mentions)
        avg_sentiment = sum(m['sentiment_analysis']['compound'] for m in relevant_mentions) / len(relevant_mentions)

        # Weighted average sentiment (by impact)
        weighted_sentiment = sum(
            m['sentiment_analysis']['compound'] * m['weighted_impact']
            for m in relevant_mentions
        ) / total_impact if total_impact > 0 else 0

        # Top influencers
        influencer_impacts = {}
        for m in relevant_mentions:
            inf_id = m['influencer_id']
            if inf_id not in influencer_impacts:
                influencer_impacts[inf_id] = {
                    'name': m['influencer_name'],
                    'mentions': 0,
                    'total_impact': 0
                }
            influencer_impacts[inf_id]['mentions'] += 1
            influencer_impacts[inf_id]['total_impact'] += m['weighted_impact']

        top_influencers = sorted(
            influencer_impacts.items(),
            key=lambda x: x[1]['total_impact'],
            reverse=True
        )[:5]

        return {
            'coin_symbol': coin_symbol,
            'mention_count': len(relevant_mentions),
            'avg_sentiment': avg_sentiment,
            'weighted_sentiment': weighted_sentiment,
            'total_weighted_impact': total_impact,
            'top_influencers': [
                {'id': inf_id, **data}
                for inf_id, data in top_influencers
            ],
            'period_days': days
        }

    def get_influencer_statistics(self) -> Dict:
        """Get overall influencer tracking statistics"""
        return {
            'total_influencers': len(self.influencers.get('crypto_influencers', [])),
            'total_mentions': len(self.mentions),
            'unique_coins_mentioned': len(set(m['coin_symbol'] for m in self.mentions)),
            'avg_impact_per_mention': sum(m['weighted_impact'] for m in self.mentions) / len(self.mentions) if self.mentions else 0,
            'top_influencer_by_mentions': self._get_top_influencer_by_mentions()
        }

    def _get_top_influencer_by_mentions(self) -> Dict:
        """Get influencer with most mentions"""
        from collections import Counter

        if not self.mentions:
            return {}

        mention_counts = Counter(m['influencer_name'] for m in self.mentions)
        top = mention_counts.most_common(1)[0]

        return {
            'name': top[0],
            'mention_count': top[1]
        }

    def export_mentions(self, filepath: str, coin_symbol: str = None):
        """Export mentions to JSON file"""
        mentions = self.mentions

        if coin_symbol:
            mentions = [m for m in mentions if m['coin_symbol'] == coin_symbol.upper()]

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(mentions, f, indent=2)

        logging.info(f"Exported {len(mentions)} mentions to {filepath}")


def demo_influencer_tracking():
    """Demonstrate influencer tracking functionality"""
    tracker = InfluencerTracker()

    print("\n=== Influencer Tracker Demo ===\n")

    # Show tracked influencers
    print(f"Tracking {len(tracker.influencers.get('crypto_influencers', []))} influencers\n")

    # Log some sample mentions
    print("Logging sample mentions...\n")

    tracker.log_mention(
        influencer_id='elonmusk',
        coin_symbol='DOGE',
        text='Dogecoin to the moon! 🚀',
        timestamp=datetime.utcnow()
    )

    tracker.log_mention(
        influencer_id='cz_binance',
        coin_symbol='BTC',
        text='Bitcoin fundamentals remain strong',
        timestamp=datetime.utcnow()
    )

    tracker.log_mention(
        influencer_id='saylor',
        coin_symbol='BTC',
        text='Just acquired another 1000 BTC for corporate treasury',
        timestamp=datetime.utcnow()
    )

    # Get coin sentiment
    print("\n=== DOGE Influencer Sentiment ===")
    doge_sentiment = tracker.get_coin_influencer_sentiment('DOGE')
    print(f"Mentions: {doge_sentiment['mention_count']}")
    print(f"Weighted sentiment: {doge_sentiment['weighted_sentiment']:.3f}")
    print(f"Total impact: {doge_sentiment['total_weighted_impact']:.2f}")

    # Statistics
    print("\n=== Tracker Statistics ===")
    stats = tracker.get_influencer_statistics()
    print(f"Total mentions logged: {stats['total_mentions']}")
    print(f"Coins mentioned: {stats['unique_coins_mentioned']}")
    print(f"Avg impact: {stats['avg_impact_per_mention']:.2f}")


if __name__ == "__main__":
    demo_influencer_tracking()
