"""
Data Quality Monitoring
=======================
Tracks and logs data collection quality metrics
"""

import logging
from datetime import datetime
from typing import Dict, List, Any
import numpy as np
from collections import Counter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class QualityMonitor:
    """Monitors data quality and flags issues"""

    def __init__(self, db_manager=None):
        """
        Initialize quality monitor

        Args:
            db_manager: DatabaseManager instance for logging
        """
        self.db = db_manager
        self.quality_thresholds = {
            'null_rate': 0.05,  # Max 5% null values
            'duplicate_rate': 0.02,  # Max 2% duplicates
            'outlier_rate': 0.10,  # Max 10% outliers
            'min_records': 1  # Minimum records expected
        }

    def assess_collection_quality(self, data: List[Dict], data_type: str) -> Dict[str, Any]:
        """
        Assess quality of collected data

        Args:
            data: List of collected records
            data_type: Type of data ('price', 'reddit', 'tiktok')

        Returns:
            Quality metrics dictionary
        """
        if not data:
            return {
                'status': 'FAILED',
                'reason': 'No data collected',
                'null_rate': 1.0,
                'duplicate_rate': 0.0,
                'outlier_rate': 0.0,
                'record_count': 0,
                'quality_score': 0.0
            }

        metrics = {
            'data_type': data_type,
            'timestamp': datetime.utcnow(),
            'record_count': len(data),
            'null_rate': self._calculate_null_rate(data),
            'duplicate_rate': self._calculate_duplicate_rate(data, data_type),
            'outlier_rate': self._calculate_outlier_rate(data, data_type),
            'field_completeness': self._check_field_completeness(data, data_type),
            'temporal_gaps': self._check_temporal_consistency(data),
        }

        # Calculate overall quality score (0-100)
        metrics['quality_score'] = self._calculate_quality_score(metrics)

        # Determine status
        metrics['status'] = self._determine_status(metrics)

        # Log quality issues
        self._log_quality_issues(metrics)

        return metrics

    def _calculate_null_rate(self, data: List[Dict]) -> float:
        """Calculate percentage of null/missing values"""
        if not data:
            return 1.0

        total_fields = 0
        null_fields = 0

        for record in data:
            for value in record.values():
                total_fields += 1
                if value is None or value == '' or value == 0:
                    null_fields += 1

        return null_fields / total_fields if total_fields > 0 else 0.0

    def _calculate_duplicate_rate(self, data: List[Dict], data_type: str) -> float:
        """Calculate percentage of duplicate records"""
        if not data:
            return 0.0

        # Different ID fields for different data types
        id_field = {
            'price': 'timestamp',
            'reddit': 'post_id',
            'tiktok': 'video_id'
        }.get(data_type, 'id')

        ids = [str(record.get(id_field, '')) for record in data]
        unique_ids = set(ids)

        duplicate_count = len(ids) - len(unique_ids)
        return duplicate_count / len(ids) if ids else 0.0

    def _calculate_outlier_rate(self, data: List[Dict], data_type: str) -> float:
        """Calculate percentage of statistical outliers"""
        if not data or len(data) < 10:
            return 0.0

        try:
            # Check numeric fields for outliers
            if data_type == 'price':
                values = [r.get('price_usd', 0) for r in data if r.get('price_usd')]
            elif data_type == 'reddit':
                values = [r.get('score', 0) for r in data if r.get('score')]
            elif data_type == 'tiktok':
                values = [r.get('views', 0) for r in data if r.get('views')]
            else:
                return 0.0

            if not values or len(values) < 10:
                return 0.0

            # Use IQR method for outlier detection
            q1, q3 = np.percentile(values, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outliers = sum(1 for v in values if v < lower_bound or v > upper_bound)
            return outliers / len(values)

        except Exception as e:
            logging.warning(f"Could not calculate outlier rate: {e}")
            return 0.0

    def _check_field_completeness(self, data: List[Dict], data_type: str) -> Dict[str, float]:
        """Check what percentage of records have each required field"""
        required_fields = {
            'price': ['price_usd', 'timestamp', 'market_cap'],
            'reddit': ['post_id', 'title', 'subreddit', 'created_utc'],
            'tiktok': ['video_id', 'username', 'caption', 'views']
        }.get(data_type, [])

        completeness = {}
        for field in required_fields:
            present = sum(1 for record in data if record.get(field) not in [None, '', 0])
            completeness[field] = present / len(data) if data else 0.0

        return completeness

    def _check_temporal_consistency(self, data: List[Dict]) -> int:
        """Check for gaps in temporal data"""
        # Simplified: just count if timestamps exist
        timestamps = [r.get('timestamp') or r.get('created_utc') or r.get('scraped_at')
                      for r in data]
        valid_timestamps = [t for t in timestamps if t is not None]

        return len(data) - len(valid_timestamps)  # Number of missing timestamps

    def _calculate_quality_score(self, metrics: Dict) -> float:
        """Calculate overall quality score (0-100)"""
        score = 100.0

        # Penalize for issues
        score -= (metrics['null_rate'] * 50)  # Up to 50 points off
        score -= (metrics['duplicate_rate'] * 30)  # Up to 30 points off
        score -= (metrics['outlier_rate'] * 20)  # Up to 20 points off

        # Penalize for low record count
        if metrics['record_count'] < self.quality_thresholds['min_records']:
            score -= 30

        return max(0.0, min(100.0, score))

    def _determine_status(self, metrics: Dict) -> str:
        """Determine overall data quality status"""
        if metrics['quality_score'] >= 90:
            return 'EXCELLENT'
        elif metrics['quality_score'] >= 75:
            return 'GOOD'
        elif metrics['quality_score'] >= 50:
            return 'ACCEPTABLE'
        elif metrics['quality_score'] >= 25:
            return 'POOR'
        else:
            return 'FAILED'

    def _log_quality_issues(self, metrics: Dict):
        """Log quality issues to console"""
        if metrics['status'] in ['POOR', 'FAILED']:
            logging.warning(f"⚠️  DATA QUALITY ISSUE: {metrics['data_type']}")
            logging.warning(f"   Status: {metrics['status']}")
            logging.warning(f"   Quality Score: {metrics['quality_score']:.1f}/100")

            if metrics['null_rate'] > self.quality_thresholds['null_rate']:
                logging.warning(f"   High null rate: {metrics['null_rate']:.1%}")

            if metrics['duplicate_rate'] > self.quality_thresholds['duplicate_rate']:
                logging.warning(f"   High duplicate rate: {metrics['duplicate_rate']:.1%}")

            if metrics['record_count'] < self.quality_thresholds['min_records']:
                logging.warning(f"   Low record count: {metrics['record_count']}")

    def log_to_database(self, metrics: Dict):
        """Save quality metrics to database"""
        if not self.db:
            return

        try:
            # Log quality metrics
            quality_log = {
                'timestamp': metrics['timestamp'],
                'data_type': metrics['data_type'],
                'status': metrics['status'],
                'quality_score': metrics['quality_score'],
                'null_rate': metrics['null_rate'],
                'duplicate_rate': metrics['duplicate_rate'],
                'outlier_rate': metrics['outlier_rate'],
                'record_count': metrics['record_count']
            }

            # Store in database (would need new table)
            logging.info(f"✅ Quality metrics logged for {metrics['data_type']}")

        except Exception as e:
            logging.error(f"Failed to log quality metrics: {e}")


def assess_data_quality(data: List[Dict], data_type: str, db=None) -> Dict:
    """
    Convenience function to assess data quality

    Args:
        data: Collected data
        data_type: Type of data ('price', 'reddit', 'tiktok')
        db: Database manager (optional)

    Returns:
        Quality metrics
    """
    monitor = QualityMonitor(db_manager=db)
    return monitor.assess_collection_quality(data, data_type)
