"""
Trending Coin Tracker
=====================
Fetches trending coins from CoinGecko and rotates tracked coins dynamically
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class TrendingTracker:
    """
    Tracks trending coins and manages coin rotation
    Uses CoinGecko's trending coins API
    """

    def __init__(self, max_trending_coins: int = 50):
        """
        Initialize trending tracker

        Args:
            max_trending_coins: Maximum number of trending coins to track actively
        """
        self.max_trending_coins = max_trending_coins
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Memecoin-Sentiment-Analyzer/1.0"})

    def fetch_trending_coins(self) -> List[Dict]:
        """
        Fetch trending coins from CoinGecko

        Returns:
            List of trending coin data with rank, id, symbol, name
        """
        try:
            logger.info("Fetching trending coins from CoinGecko...")

            # CoinGecko trending endpoint (free tier)
            url = f"{self.base_url}/search/trending"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            trending_coins = []
            rank = 1

            # Extract coin data from trending response
            if "coins" in data:
                for item in data["coins"]:
                    coin_data = item.get("item", {})
                    trending_coins.append(
                        {
                            "rank": rank,
                            "coingecko_id": coin_data.get("id"),
                            "symbol": coin_data.get("symbol", "").upper(),
                            "name": coin_data.get("name"),
                            "market_cap_rank": coin_data.get("market_cap_rank"),
                            "trending_score": coin_data.get("score"),  # CoinGecko's trending score
                        }
                    )
                    rank += 1

            logger.info(f"✓ Found {len(trending_coins)} trending coins")
            return trending_coins

        except requests.RequestException as e:
            logger.error(f"Error fetching trending coins: {e}")
            return []

    def fetch_top_gainers(self, limit: int = 30) -> List[Dict]:
        """
        Fetch top gaining coins (alternative trending metric)

        Args:
            limit: Number of top gainers to fetch

        Returns:
            List of top gainer coin data
        """
        try:
            logger.info("Fetching top gainers from CoinGecko...")

            # Get market data sorted by 24h price change
            url = f"{self.base_url}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "price_change_percentage_24h_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h",
            }

            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()

            gainers = []
            rank = 1

            for coin in data:
                # Filter for memecoins/small caps with significant gains
                change_24h = coin.get("price_change_percentage_24h", 0)

                if change_24h > 5:  # Only include coins with >5% gain
                    gainers.append(
                        {
                            "rank": rank,
                            "coingecko_id": coin.get("id"),
                            "symbol": coin.get("symbol", "").upper(),
                            "name": coin.get("name"),
                            "price_usd": coin.get("current_price"),
                            "volume_24h": coin.get("total_volume"),
                            "market_cap": coin.get("market_cap"),
                            "change_24h": change_24h,
                            "trending_score": change_24h / 10,  # Normalize to 0-10 scale
                        }
                    )
                    rank += 1

            logger.info(f"✓ Found {len(gainers)} top gainers")
            return gainers

        except requests.RequestException as e:
            logger.error(f"Error fetching top gainers: {e}")
            return []

    def update_trending_coins(self, db_manager) -> Dict[str, int]:
        """
        Update database with current trending coins

        Args:
            db_manager: DatabaseManager instance

        Returns:
            Dict with counts of new, updated, archived coins
        """
        from database.models import Coin, TrendingHistory

        # Fetch trending data
        trending_coins = self.fetch_trending_coins()
        top_gainers = self.fetch_top_gainers(limit=20)

        # Combine and deduplicate
        all_trending = {}

        for coin in trending_coins:
            coin_id = coin["coingecko_id"]
            all_trending[coin_id] = coin

        for coin in top_gainers:
            coin_id = coin["coingecko_id"]
            if coin_id not in all_trending:
                # Assign rank continuing from trending coins
                coin["rank"] = len(all_trending) + 1
                all_trending[coin_id] = coin

        # Limit to max trending coins
        trending_list = sorted(all_trending.values(), key=lambda x: x["rank"])[: self.max_trending_coins]

        stats = {"new": 0, "updated": 0, "archived": 0, "errors": 0}

        with db_manager.get_session() as session:
            current_time = datetime.utcnow()

            # Mark currently trending coins
            trending_ids = {c["coingecko_id"] for c in trending_list}

            # Archive coins that are no longer trending
            previously_trending = session.query(Coin).filter(Coin.is_trending == True).all()

            for coin in previously_trending:
                if coin.coingecko_id not in trending_ids:
                    # Coin exited trending
                    coin.is_trending = False
                    coin.status = "archived"
                    coin.trending_rank = None

                    # Log trending history
                    history = TrendingHistory(
                        coin_id=coin.id,
                        event_type="exited",
                        timestamp=current_time,
                        notes="Exited trending rotation",
                    )
                    session.add(history)
                    stats["archived"] += 1
                    logger.info(f"  Archived: {coin.symbol} ({coin.name})")

            # Add or update trending coins
            for trend_data in trending_list:
                coin_id = trend_data["coingecko_id"]
                symbol = trend_data["symbol"]
                name = trend_data["name"]
                rank = trend_data["rank"]

                # Check if coin exists
                coin = session.query(Coin).filter(Coin.coingecko_id == coin_id).first()

                if coin:
                    # Update existing coin
                    previous_rank = coin.trending_rank
                    was_trending = coin.is_trending

                    coin.is_trending = True
                    coin.trending_rank = rank
                    coin.last_trending_check = current_time
                    coin.status = "active"

                    if not was_trending:
                        # Coin entered trending
                        coin.trending_since = current_time
                        history = TrendingHistory(
                            coin_id=coin.id,
                            event_type="entered",
                            trending_rank=rank,
                            timestamp=current_time,
                            trending_score=trend_data.get("trending_score"),
                            price_usd=trend_data.get("price_usd"),
                            volume_24h=trend_data.get("volume_24h"),
                            market_cap=trend_data.get("market_cap"),
                        )
                        session.add(history)
                        stats["new"] += 1
                        logger.info(f"  NEW: {symbol} ({name}) - Rank #{rank}")

                    elif previous_rank != rank:
                        # Rank changed
                        history = TrendingHistory(
                            coin_id=coin.id,
                            event_type="rank_change",
                            trending_rank=rank,
                            previous_rank=previous_rank,
                            timestamp=current_time,
                        )
                        session.add(history)
                        stats["updated"] += 1

                else:
                    # Create new coin
                    new_coin = Coin(
                        symbol=symbol,
                        name=name,
                        coingecko_id=coin_id,
                        is_trending=True,
                        trending_since=current_time,
                        trending_rank=rank,
                        last_trending_check=current_time,
                        status="active",
                    )
                    session.add(new_coin)
                    session.flush()  # Get the ID

                    # Log trending history
                    history = TrendingHistory(
                        coin_id=new_coin.id,
                        event_type="entered",
                        trending_rank=rank,
                        timestamp=current_time,
                        trending_score=trend_data.get("trending_score"),
                        price_usd=trend_data.get("price_usd"),
                        volume_24h=trend_data.get("volume_24h"),
                        market_cap=trend_data.get("market_cap"),
                    )
                    session.add(history)
                    stats["new"] += 1
                    logger.info(f"  NEW: {symbol} ({name}) - Rank #{rank}")

            session.commit()

        logger.info(
            f"✓ Trending update complete: {stats['new']} new, {stats['updated']} updated, {stats['archived']} archived"
        )
        return stats

    def get_active_coins(self, db_manager, include_control: bool = True) -> List[Dict]:
        """
        Get list of currently active (trending) coins for data collection

        Args:
            db_manager: DatabaseManager instance
            include_control: Include control coins (BTC, ETH) in results

        Returns:
            List of active coin data dicts
        """
        from database.models import Coin

        with db_manager.get_session() as session:
            query = session.query(Coin).filter(Coin.status == "active")

            if include_control:
                # Include both trending and control coins
                query = query.filter((Coin.is_trending == True) | (Coin.is_control == True))
            else:
                # Only trending coins
                query = query.filter(Coin.is_trending == True)

            query = query.order_by(Coin.trending_rank.asc().nullsfirst())

            coins = query.all()

            return [
                {
                    "id": coin.id,
                    "symbol": coin.symbol,
                    "name": coin.name,
                    "coingecko_id": coin.coingecko_id,
                    "is_trending": coin.is_trending,
                    "trending_rank": coin.trending_rank,
                }
                for coin in coins
            ]

    def close(self):
        """Close HTTP session"""
        self.session.close()


if __name__ == "__main__":
    # Test the trending tracker
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from database.db_manager import DatabaseManager

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    db = DatabaseManager()
    tracker = TrendingTracker(max_trending_coins=50)

    print("\nFetching trending coins...")
    stats = tracker.update_trending_coins(db)

    print(f"\nResults:")
    print(f"  New coins: {stats['new']}")
    print(f"  Updated: {stats['updated']}")
    print(f"  Archived: {stats['archived']}")

    print("\nActive coins for tracking:")
    active = tracker.get_active_coins(db)
    for coin in active[:10]:  # Show top 10
        print(f"  #{coin.get('trending_rank', 'N/A'):3} {coin['symbol']:6} - {coin['name']}")

    tracker.close()
    db.close()
