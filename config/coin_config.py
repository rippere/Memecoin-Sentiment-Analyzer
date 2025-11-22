"""
Coin Configuration Loader
=========================
Loads coin configuration from coins.yaml
"""

import yaml
from pathlib import Path
from typing import Dict, List


class CoinConfig:
    """Loads and provides access to coin configuration"""

    def __init__(self, config_path: str = None):
        """
        Load coin configuration

        Args:
            config_path: Path to coins.yaml file
        """
        if config_path is None:
            # Default to config/coins.yaml in project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / 'config' / 'coins.yaml'

        self.config_path = Path(config_path)
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        self.coins = config.get('coins', [])
        self.control_coins = config.get('control_coins', [])
        self.social_queries = config.get('social_queries', {})

        # Combine all coins for tracking
        self.all_coins = self.control_coins + self.coins

    def get_all_coins(self) -> List[Dict]:
        """Get all coin configurations (including control coins)"""
        return self.all_coins

    def get_meme_coins(self) -> List[Dict]:
        """Get only meme coins (excluding control coins)"""
        return self.coins

    def get_control_coins(self) -> List[Dict]:
        """Get only control coins (BTC, ETH)"""
        return self.control_coins

    def get_failed_coins(self) -> List[Dict]:
        """Get coins marked as failed/dead"""
        return [coin for coin in self.coins if coin.get('is_failed', False)]

    def get_coin_symbols(self) -> List[str]:
        """Get list of all coin symbols (including control coins)"""
        return [coin['symbol'] for coin in self.all_coins]

    def get_meme_coin_symbols(self) -> List[str]:
        """Get list of only meme coin symbols"""
        return [coin['symbol'] for coin in self.coins]

    def get_coingecko_mapping(self) -> Dict[str, str]:
        """Get mapping of symbol -> coingecko_id"""
        return {coin['symbol']: coin['coingecko_id'] for coin in self.coins}

    def get_social_queries(self, symbol: str) -> List[str]:
        """Get social media queries for a coin"""
        return self.social_queries.get(symbol, [symbol.lower()])

    def get_coin_by_symbol(self, symbol: str) -> Dict:
        """Get coin configuration by symbol"""
        for coin in self.coins:
            if coin['symbol'] == symbol:
                return coin
        return None

    def add_coin(self, symbol: str, name: str, coingecko_id: str, queries: List[str] = None):
        """
        Add a new coin to track (programmatically)
        Note: This doesn't save to YAML, just adds to current session
        """
        new_coin = {
            'symbol': symbol,
            'name': name,
            'coingecko_id': coingecko_id
        }
        self.coins.append(new_coin)

        if queries:
            self.social_queries[symbol] = queries


# Singleton instance
_config_instance = None


def get_coin_config() -> CoinConfig:
    """Get or create coin configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = CoinConfig()
    return _config_instance
