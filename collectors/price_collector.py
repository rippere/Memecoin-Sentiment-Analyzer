"""
Price Data Collector
===================
Collects cryptocurrency price data from CoinGecko API
Refactored from meme_coin_tracker.py for integration with database
"""

import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class PriceCollector:
    """Collects price data from CoinGecko API"""

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, timeout: int = 10):
        """
        Initialize price collector

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()

        # Load coin mapping from config
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from config.coin_config import get_coin_config
            coin_config = get_coin_config()
            self.COIN_IDS = coin_config.get_coingecko_mapping()
        except Exception as e:
            logging.warning(f"Could not load coins from config: {e}, using defaults")
            self.COIN_IDS = {
                'DOGE': 'dogecoin',
                'PEPE': 'pepe',
                'SHIB': 'shiba-inu',
            }

        logging.info(f"✅ Price collector initialized ({len(self.COIN_IDS)} coins)")

    def fetch_coin_data(self, coin_symbols: List[str] = None) -> Dict[str, Dict]:
        """
        Fetch current market data for specified coins

        Args:
            coin_symbols: List of coin symbols (e.g., ['DOGE', 'PEPE'])
                         If None, fetches all tracked coins

        Returns:
            Dictionary mapping symbol -> price data
        """
        if coin_symbols is None:
            coin_symbols = list(self.COIN_IDS.keys())

        # Convert symbols to CoinGecko IDs
        coin_ids = [self.COIN_IDS[symbol] for symbol in coin_symbols if symbol in self.COIN_IDS]

        if not coin_ids:
            logging.warning("No valid coin symbols provided")
            return {}

        ids_string = ','.join(coin_ids)

        url = f"{self.BASE_URL}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'ids': ids_string,
            'order': 'market_cap_desc',
            'per_page': len(coin_ids),
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '1h,24h,7d'
        }

        try:
            logging.info(f"📡 Fetching price data for {len(coin_ids)} coins...")
            response = self.session.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                logging.info(f"✅ Successfully fetched data for {len(data)} coins")

                # Convert to symbol-keyed dictionary
                result = {}
                for coin in data:
                    # Find symbol from COIN_IDS
                    symbol = self._get_symbol_from_id(coin['id'])
                    if symbol:
                        result[symbol] = self._parse_coin_data(coin)

                return result

            elif response.status_code == 429:
                logging.warning("⚠️  Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                return {}
            else:
                logging.error(f"❌ API returned status code {response.status_code}")
                return {}

        except requests.exceptions.Timeout:
            logging.error("❌ Request timeout")
            return {}
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Network error: {e}")
            return {}
        except Exception as e:
            logging.error(f"❌ Unexpected error: {e}")
            return {}

    def _get_symbol_from_id(self, coin_id: str) -> Optional[str]:
        """Get symbol from CoinGecko ID"""
        for symbol, cg_id in self.COIN_IDS.items():
            if cg_id == coin_id:
                return symbol
        return None

    def _parse_coin_data(self, coin: Dict) -> Dict:
        """
        Parse raw CoinGecko data into standardized format

        Args:
            coin: Raw coin data from CoinGecko API

        Returns:
            Parsed price data
        """
        return {
            'timestamp': datetime.utcnow(),
            'price_usd': coin.get('current_price', 0),
            'market_cap': coin.get('market_cap'),
            'volume_24h': coin.get('total_volume'),
            'change_1h_pct': coin.get('price_change_percentage_1h_in_currency'),
            'change_24h_pct': coin.get('price_change_percentage_24h'),
            'change_7d_pct': coin.get('price_change_percentage_7d_in_currency'),
        }

    def fetch_single_coin(self, symbol: str) -> Optional[Dict]:
        """
        Fetch data for a single coin

        Args:
            symbol: Coin symbol (e.g., 'DOGE')

        Returns:
            Price data or None if failed
        """
        result = self.fetch_coin_data([symbol])
        return result.get(symbol)

    def close(self):
        """Close requests session"""
        self.session.close()
        logging.info("Price collector session closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit"""
        self.close()
