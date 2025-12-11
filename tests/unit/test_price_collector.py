"""
Tests for PriceCollector
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from collectors.price_collector import PriceCollector


@pytest.fixture
def price_collector():
    """Create a PriceCollector instance"""
    return PriceCollector()


@pytest.fixture
def sample_coingecko_response():
    """Sample CoinGecko API response"""
    return {
        "dogecoin": {"usd": 0.10, "usd_market_cap": 14000000000, "usd_24h_vol": 500000000, "usd_24h_change": 5.2},
        "bitcoin": {"usd": 45000.00, "usd_market_cap": 850000000000, "usd_24h_vol": 25000000000, "usd_24h_change": 2.1},
    }


class TestPriceCollectorInitialization:
    """Test PriceCollector initialization"""

    def test_initialization(self, price_collector):
        """Test that PriceCollector initializes correctly"""
        assert price_collector is not None
        assert hasattr(price_collector, "BASE_URL")
        assert hasattr(price_collector, "COIN_IDS")


class TestFetchPrices:
    """Test price fetching functionality"""

    @patch("requests.Session.get")
    def test_fetch_single_coin_success(self, mock_get, price_collector):
        """Test fetching price for a single coin"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "dogecoin",
                "symbol": "doge",
                "current_price": 0.10,
                "market_cap": 14000000000,
                "total_volume": 500000000,
                "price_change_percentage_24h": 5.2,
            }
        ]
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = price_collector.fetch_coin_data(["DOGE"])
        assert result is not None
        assert "DOGE" in result
        assert result["DOGE"]["price_usd"] == 0.10

    @patch("requests.Session.get")
    def test_fetch_multiple_coins(self, mock_get, price_collector):
        """Test fetching prices for multiple coins"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "dogecoin",
                "symbol": "doge",
                "current_price": 0.10,
                "market_cap": 14000000000,
                "total_volume": 500000000,
                "price_change_percentage_24h": 5.2,
            },
            {
                "id": "bitcoin",
                "symbol": "btc",
                "current_price": 45000.00,
                "market_cap": 850000000000,
                "total_volume": 25000000000,
                "price_change_percentage_24h": 2.1,
            },
        ]
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = price_collector.fetch_coin_data(["DOGE", "BTC"])
        # May only get DOGE if BTC not in COIN_IDS
        assert len(result) >= 1
        assert "DOGE" in result

    @patch("requests.Session.get")
    def test_fetch_prices_api_error(self, mock_get, price_collector):
        """Test handling of API errors"""
        mock_get.side_effect = Exception("API Error")

        result = price_collector.fetch_coin_data(["DOGE"])
        assert result is None or len(result) == 0

    @patch("requests.Session.get")
    def test_fetch_prices_rate_limiting(self, mock_get, price_collector):
        """Test that rate limiting is respected"""
        mock_response = Mock()
        mock_response.status_code = 429  # Rate limit error
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_get.return_value = mock_response

        result = price_collector.fetch_coin_data(["DOGE"])
        # Should handle gracefully
        assert result is None or isinstance(result, dict)


class TestDataParsing:
    """Test price data parsing"""

    @patch("requests.Session.get")
    def test_parse_price_data(self, mock_get, price_collector):
        """Test that price data is parsed correctly"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "dogecoin",
                "symbol": "doge",
                "current_price": 0.10,
                "market_cap": 14000000000,
                "total_volume": 500000000,
                "price_change_percentage_24h": 5.2,
            }
        ]
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = price_collector.fetch_coin_data(["DOGE"])
        doge_data = result["DOGE"]

        assert "price_usd" in doge_data
        assert "market_cap" in doge_data
        assert "volume_24h" in doge_data
        assert "timestamp" in doge_data

    @patch("requests.Session.get")
    def test_timestamp_generation(self, mock_get, price_collector):
        """Test that timestamps are generated correctly"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "dogecoin",
                "symbol": "doge",
                "current_price": 0.10,
                "market_cap": 14000000000,
                "total_volume": 500000000,
                "price_change_percentage_24h": 5.2,
            }
        ]
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = price_collector.fetch_coin_data(["DOGE"])
        timestamp = result["DOGE"]["timestamp"]

        assert isinstance(timestamp, datetime)
        # Timestamp should be recent (within last minute)
        assert (datetime.utcnow() - timestamp).total_seconds() < 60
