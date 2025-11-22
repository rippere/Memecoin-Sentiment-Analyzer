"""
Unit tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_check(self, client):
        """Test health endpoint returns healthy status"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestCorsConfiguration:
    """Tests for CORS configuration"""

    def test_cors_allowed_origin(self, client):
        """Test CORS allows configured origins"""
        response = client.options(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )
        # Should not return 403 for allowed origin
        assert response.status_code != 403

    def test_cors_blocked_origin(self, client):
        """Test CORS blocks non-configured origins"""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://malicious-site.com"}
        )
        # Request still succeeds but without CORS headers for unauthorized origin
        assert response.status_code == 200
        # Access-Control-Allow-Origin should not be set for blocked origins
        assert response.headers.get("access-control-allow-origin") != "http://malicious-site.com"


class TestCoinsEndpoint:
    """Tests for coins endpoints"""

    def test_get_coins(self, client):
        """Test get all coins endpoint"""
        response = client.get("/api/coins")
        # May return 200 with empty list or actual data
        assert response.status_code == 200
        data = response.json()
        assert 'coins' in data
        assert 'count' in data

    def test_get_coin_not_found(self, client):
        """Test get non-existent coin"""
        response = client.get("/api/coins/NOTACOIN")
        assert response.status_code == 404


class TestStatsEndpoint:
    """Tests for stats endpoint"""

    def test_get_stats(self, client):
        """Test dashboard stats endpoint"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert 'total_coins' in data
        assert 'record_counts' in data


class TestEventsEndpoint:
    """Tests for events endpoints"""

    def test_get_events(self, client):
        """Test get events endpoint"""
        response = client.get("/api/events")
        assert response.status_code == 200
        data = response.json()
        assert 'events' in data
        assert 'count' in data

    def test_get_events_with_limit(self, client):
        """Test events endpoint with limit parameter"""
        response = client.get("/api/events?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data['events']) <= 5
