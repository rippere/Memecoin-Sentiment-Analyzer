"""
Trading Volume Analysis
========================
Advanced volume analysis for detecting spikes, anomalies, and patterns
"""

import sys
from pathlib import Path
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging
from collections import deque

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class VolumeAnalyzer:
    """
    Analyzes trading volume patterns for anomaly detection
    """

    def __init__(self):
        """Initialize volume analyzer"""
        self.volume_history = {}  # coin_symbol -> deque of (timestamp, volume, price)
        logging.info("Volume analyzer initialized")

    def add_volume_data(self, coin_symbol: str, timestamp: datetime, volume: float, price: float):
        """
        Add volume data point for analysis

        Args:
            coin_symbol: Coin symbol
            timestamp: Data timestamp
            volume: 24h trading volume (USD)
            price: Price at time of volume measurement
        """
        if coin_symbol not in self.volume_history:
            self.volume_history[coin_symbol] = deque(maxlen=1000)  # Keep last 1000 data points

        self.volume_history[coin_symbol].append((timestamp, volume, price))

    def detect_volume_spike(self, coin_symbol: str, threshold: float = 2.0) -> Dict:
        """
        Detect volume spikes (volume significantly above average)

        Args:
            coin_symbol: Coin to analyze
            threshold: Spike threshold as multiple of standard deviation (default: 2.0)

        Returns:
            Spike detection results
        """
        if coin_symbol not in self.volume_history or len(self.volume_history[coin_symbol]) < 10:
            return {
                'spike_detected': False,
                'reason': 'Insufficient data'
            }

        history = list(self.volume_history[coin_symbol])
        volumes = [v[1] for v in history]

        # Get latest volume
        latest_volume = volumes[-1]

        # Calculate statistics on historical data (excluding latest)
        historical_volumes = volumes[:-1]
        mean_volume = np.mean(historical_volumes)
        std_volume = np.std(historical_volumes)

        # Z-score for latest volume
        if std_volume > 0:
            z_score = (latest_volume - mean_volume) / std_volume
        else:
            z_score = 0

        spike_detected = z_score > threshold

        # Calculate percentage increase
        pct_increase = ((latest_volume - mean_volume) / mean_volume * 100) if mean_volume > 0 else 0

        return {
            'spike_detected': spike_detected,
            'latest_volume': latest_volume,
            'mean_volume': mean_volume,
            'std_volume': std_volume,
            'z_score': z_score,
            'pct_increase': pct_increase,
            'threshold': threshold,
            'timestamp': history[-1][0]
        }

    def detect_volume_anomaly(self, coin_symbol: str, method: str = 'iqr') -> Dict:
        """
        Detect volume anomalies using statistical methods

        Args:
            coin_symbol: Coin to analyze
            method: Detection method ('iqr' or 'zscore')

        Returns:
            Anomaly detection results
        """
        if coin_symbol not in self.volume_history or len(self.volume_history[coin_symbol]) < 10:
            return {
                'anomaly_detected': False,
                'reason': 'Insufficient data'
            }

        history = list(self.volume_history[coin_symbol])
        volumes = [v[1] for v in history]
        latest_volume = volumes[-1]

        if method == 'iqr':
            # Interquartile Range method
            q1, q3 = np.percentile(volumes[:-1], [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            anomaly_detected = latest_volume < lower_bound or latest_volume > upper_bound

            return {
                'anomaly_detected': anomaly_detected,
                'method': 'iqr',
                'latest_volume': latest_volume,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'q1': q1,
                'q3': q3,
                'iqr': iqr,
                'anomaly_type': 'high' if latest_volume > upper_bound else 'low' if latest_volume < lower_bound else 'normal'
            }

        elif method == 'zscore':
            # Z-score method
            mean_volume = np.mean(volumes[:-1])
            std_volume = np.std(volumes[:-1])

            if std_volume > 0:
                z_score = abs((latest_volume - mean_volume) / std_volume)
            else:
                z_score = 0

            anomaly_detected = z_score > 3  # 3 standard deviations

            return {
                'anomaly_detected': anomaly_detected,
                'method': 'zscore',
                'latest_volume': latest_volume,
                'mean_volume': mean_volume,
                'std_volume': std_volume,
                'z_score': z_score,
                'threshold': 3.0
            }

    def analyze_volume_price_correlation(self, coin_symbol: str, window: int = 50) -> Dict:
        """
        Analyze correlation between volume and price changes

        Args:
            coin_symbol: Coin to analyze
            window: Number of recent data points to analyze

        Returns:
            Correlation analysis results
        """
        if coin_symbol not in self.volume_history or len(self.volume_history[coin_symbol]) < window:
            return {
                'error': 'Insufficient data',
                'required': window,
                'available': len(self.volume_history.get(coin_symbol, []))
            }

        history = list(self.volume_history[coin_symbol])[-window:]

        volumes = [v[1] for v in history]
        prices = [v[2] for v in history]

        # Calculate price changes
        price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        volume_changes = [volumes[i] - volumes[i-1] for i in range(1, len(volumes))]

        # Pearson correlation
        if len(price_changes) > 1:
            correlation = np.corrcoef(price_changes, volume_changes)[0, 1]
        else:
            correlation = 0.0

        # Identify volume-price divergence (high volume, low price change)
        recent_volume_increase = (volumes[-1] - volumes[-2]) / volumes[-2] if volumes[-2] > 0 else 0
        recent_price_change = (prices[-1] - prices[-2]) / prices[-2] if prices[-2] > 0 else 0

        divergence = abs(recent_volume_increase) > 0.5 and abs(recent_price_change) < 0.02

        return {
            'correlation': correlation,
            'window_size': window,
            'interpretation': self._interpret_correlation(correlation),
            'recent_volume_change': recent_volume_increase,
            'recent_price_change': recent_price_change,
            'divergence_detected': divergence,
            'divergence_note': 'High volume with minimal price change - potential manipulation or accumulation' if divergence else None
        }

    def _interpret_correlation(self, correlation: float) -> str:
        """Interpret correlation coefficient"""
        if correlation > 0.7:
            return 'Strong positive correlation (volume follows price)'
        elif correlation > 0.3:
            return 'Moderate positive correlation'
        elif correlation > -0.3:
            return 'Weak or no correlation'
        elif correlation > -0.7:
            return 'Moderate negative correlation'
        else:
            return 'Strong negative correlation (inverse relationship)'

    def detect_wash_trading_indicators(self, coin_symbol: str) -> Dict:
        """
        Detect potential wash trading indicators

        Wash trading signs:
        - Unusually high volume with minimal price movement
        - Repeated volume spikes at same times
        - Volume patterns that don't match market trends

        Args:
            coin_symbol: Coin to analyze

        Returns:
            Wash trading indicator results
        """
        if coin_symbol not in self.volume_history or len(self.volume_history[coin_symbol]) < 50:
            return {
                'suspicious': False,
                'reason': 'Insufficient data'
            }

        history = list(self.volume_history[coin_symbol])
        volumes = [v[1] for v in history]
        prices = [v[2] for v in history]

        # Calculate recent volume-to-price movement ratio
        recent_window = 20
        recent_volumes = volumes[-recent_window:]
        recent_prices = prices[-recent_window:]

        avg_volume = np.mean(recent_volumes)
        price_volatility = np.std(recent_prices) / np.mean(recent_prices) if np.mean(recent_prices) > 0 else 0

        # High volume, low volatility = suspicious
        volume_price_ratio = avg_volume * (1 / price_volatility) if price_volatility > 0 else 0

        # Check for abnormal volume consistency (volumes too similar = suspicious)
        volume_std = np.std(recent_volumes)
        volume_mean = np.mean(recent_volumes)
        volume_cv = volume_std / volume_mean if volume_mean > 0 else 0  # Coefficient of variation

        suspicious_signals = []

        # Signal 1: High volume, low price movement
        if price_volatility < 0.02 and avg_volume > np.mean(volumes[:-recent_window]) * 1.5:
            suspicious_signals.append('High volume with abnormally low price volatility')

        # Signal 2: Too consistent volume (low coefficient of variation)
        if volume_cv < 0.3:  # Volumes are suspiciously similar
            suspicious_signals.append('Volume levels are unnaturally consistent')

        # Signal 3: Volume doesn't correlate with price (from previous analysis)
        corr_result = self.analyze_volume_price_correlation(coin_symbol, window=recent_window)
        if abs(corr_result.get('correlation', 0)) < 0.1:
            suspicious_signals.append('Volume and price are uncorrelated')

        return {
            'suspicious': len(suspicious_signals) >= 2,  # 2+ signals = likely wash trading
            'signals': suspicious_signals,
            'signal_count': len(suspicious_signals),
            'metrics': {
                'avg_volume': avg_volume,
                'price_volatility': price_volatility,
                'volume_cv': volume_cv,
                'correlation': corr_result.get('correlation', 0)
            },
            'confidence': 'HIGH' if len(suspicious_signals) >= 3 else 'MEDIUM' if len(suspicious_signals) == 2 else 'LOW'
        }

    def analyze_volume_trend(self, coin_symbol: str, window: int = 30) -> Dict:
        """
        Analyze volume trend over time

        Args:
            coin_symbol: Coin to analyze
            window: Analysis window in data points

        Returns:
            Volume trend analysis
        """
        if coin_symbol not in self.volume_history or len(self.volume_history[coin_symbol]) < window:
            return {
                'error': 'Insufficient data',
                'required': window
            }

        history = list(self.volume_history[coin_symbol])[-window:]
        volumes = [v[1] for v in history]

        # Linear regression for trend
        x = np.arange(len(volumes))
        slope, intercept = np.polyfit(x, volumes, 1)

        # Trend direction
        if slope > 0:
            trend = 'increasing'
        elif slope < 0:
            trend = 'decreasing'
        else:
            trend = 'stable'

        # Calculate trend strength (R-squared)
        y_pred = slope * x + intercept
        ss_res = np.sum((volumes - y_pred) ** 2)
        ss_tot = np.sum((volumes - np.mean(volumes)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Recent vs historical comparison
        recent_avg = np.mean(volumes[-7:])  # Last week
        historical_avg = np.mean(volumes[:-7])  # Earlier data
        pct_change = ((recent_avg - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0

        return {
            'trend': trend,
            'slope': slope,
            'r_squared': r_squared,
            'trend_strength': 'strong' if r_squared > 0.7 else 'moderate' if r_squared > 0.3 else 'weak',
            'recent_avg_volume': recent_avg,
            'historical_avg_volume': historical_avg,
            'pct_change': pct_change,
            'window_days': window
        }

    def get_volume_summary(self, coin_symbol: str) -> Dict:
        """Get comprehensive volume analysis summary"""
        if coin_symbol not in self.volume_history or len(self.volume_history[coin_symbol]) < 10:
            return {'error': 'Insufficient data for analysis'}

        spike = self.detect_volume_spike(coin_symbol)
        anomaly = self.detect_volume_anomaly(coin_symbol, method='iqr')
        correlation = self.analyze_volume_price_correlation(coin_symbol)
        wash_trading = self.detect_wash_trading_indicators(coin_symbol)
        trend = self.analyze_volume_trend(coin_symbol)

        return {
            'coin_symbol': coin_symbol,
            'data_points': len(self.volume_history[coin_symbol]),
            'spike_detection': spike,
            'anomaly_detection': anomaly,
            'volume_price_correlation': correlation,
            'wash_trading_indicators': wash_trading,
            'volume_trend': trend,
            'timestamp': datetime.utcnow().isoformat()
        }


def analyze_volume_from_db(coin_symbol: str, db_path: str = None):
    """
    Load volume data from database and perform analysis

    Args:
        coin_symbol: Coin to analyze
        db_path: Database path (optional)
    """
    from database.db_manager import DatabaseManager

    db = DatabaseManager(db_path=db_path)
    analyzer = VolumeAnalyzer()

    # Fetch price data (includes volume)
    with db.Session() as session:
        from database.models import Price, Coin

        coin = session.query(Coin).filter_by(symbol=coin_symbol).first()
        if not coin:
            print(f"Coin {coin_symbol} not found")
            return

        prices = session.query(Price).filter_by(coin_id=coin.id).order_by(Price.timestamp).all()

        for price in prices:
            analyzer.add_volume_data(
                coin_symbol=coin_symbol,
                timestamp=price.timestamp,
                volume=price.volume_24h or 0,
                price=price.price_usd
            )

    # Get summary
    summary = analyzer.get_volume_summary(coin_symbol)

    print(f"\n=== Volume Analysis: {coin_symbol} ===\n")
    print(f"Data points: {summary['data_points']}")

    print(f"\nVolume Spike Detection:")
    spike = summary['spike_detection']
    if spike.get('spike_detected'):
        print(f"  SPIKE DETECTED!")
        print(f"  Z-score: {spike['z_score']:.2f}")
        print(f"  Increase: {spike['pct_increase']:.1f}%")
    else:
        print(f"  No spike detected")

    print(f"\nWash Trading Indicators:")
    wash = summary['wash_trading_indicators']
    if wash.get('suspicious'):
        print(f"  SUSPICIOUS ACTIVITY ({wash['confidence']} confidence)")
        for signal in wash['signals']:
            print(f"    - {signal}")
    else:
        print(f"  No suspicious activity detected")

    print(f"\nVolume Trend:")
    trend_data = summary['volume_trend']
    if 'error' not in trend_data:
        print(f"  Direction: {trend_data['trend']}")
        print(f"  Strength: {trend_data['trend_strength']}")
        print(f"  Change: {trend_data['pct_change']:.1f}%")

    db.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_volume_from_db(sys.argv[1])
    else:
        print("Usage: python volume_analyzer.py <COIN_SYMBOL>")
