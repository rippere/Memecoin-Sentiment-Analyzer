"""
Data Validation and Cleaning Pipeline
======================================
Tools for validating, cleaning, and preparing data for analysis
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class DataPipeline:
    """
    Comprehensive data validation, cleaning, and export pipeline
    """

    def __init__(self, db_path: str = None):
        """
        Initialize data pipeline

        Args:
            db_path: Path to SQLite database
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'data' / 'memecoin.db'

        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        logging.info(f"Data pipeline connected to: {self.db_path}")

    def close(self):
        """Close database connection"""
        self.conn.close()

    # ==================== DATA LOADING ====================

    def load_prices(self, coin_symbol: str = None, start_date: datetime = None,
                   end_date: datetime = None) -> pd.DataFrame:
        """
        Load price data from database

        Args:
            coin_symbol: Filter by coin (optional)
            start_date: Start date filter
            end_date: End date filter

        Returns:
            DataFrame with price data
        """
        query = """
            SELECT p.*, c.symbol, c.name, c.is_control, c.is_failed
            FROM prices p
            JOIN coins c ON p.coin_id = c.id
            WHERE 1=1
        """
        params = []

        if coin_symbol:
            query += " AND c.symbol = ?"
            params.append(coin_symbol)

        if start_date:
            query += " AND p.timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND p.timestamp <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY p.timestamp"

        df = pd.read_sql_query(query, self.conn, params=params, parse_dates=['timestamp', 'collected_at'])
        logging.info(f"Loaded {len(df)} price records")
        return df

    def load_sentiment(self, coin_symbol: str = None, source: str = None,
                      start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        """
        Load sentiment data from database

        Args:
            coin_symbol: Filter by coin
            source: Filter by source (reddit, tiktok)
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with sentiment data
        """
        query = """
            SELECT s.*, c.symbol, c.name
            FROM sentiment_scores s
            JOIN coins c ON s.coin_id = c.id
            WHERE 1=1
        """
        params = []

        if coin_symbol:
            query += " AND c.symbol = ?"
            params.append(coin_symbol)

        if source:
            query += " AND s.source = ?"
            params.append(source)

        if start_date:
            query += " AND s.timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND s.timestamp <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY s.timestamp"

        df = pd.read_sql_query(query, self.conn, params=params, parse_dates=['timestamp', 'calculated_at'])
        logging.info(f"Loaded {len(df)} sentiment records")
        return df

    def load_events(self, coin_symbol: str = None) -> pd.DataFrame:
        """Load events from JSON file"""
        import json

        events_path = Path(__file__).parent.parent / 'events' / 'events.json'

        if not events_path.exists():
            return pd.DataFrame()

        with open(events_path, 'r') as f:
            events = json.load(f)

        df = pd.DataFrame(events)

        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            if coin_symbol:
                df = df[(df['coin_symbol'] == coin_symbol) | (df['coin_symbol'] == 'ALL')]

        logging.info(f"Loaded {len(df)} events")
        return df

    # ==================== VALIDATION ====================

    def validate_prices(self, df: pd.DataFrame) -> Dict:
        """
        Validate price data quality

        Args:
            df: Price DataFrame

        Returns:
            Validation report
        """
        report = {
            'total_records': len(df),
            'date_range': None,
            'issues': [],
            'warnings': [],
            'passed': True
        }

        if df.empty:
            report['issues'].append('No data to validate')
            report['passed'] = False
            return report

        report['date_range'] = {
            'start': df['timestamp'].min().isoformat(),
            'end': df['timestamp'].max().isoformat(),
            'days': (df['timestamp'].max() - df['timestamp'].min()).days
        }

        # Check for nulls
        null_counts = df[['price_usd', 'volume_24h', 'market_cap']].isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                pct = count / len(df) * 100
                if pct > 5:
                    report['issues'].append(f'{col}: {count} nulls ({pct:.1f}%)')
                else:
                    report['warnings'].append(f'{col}: {count} nulls ({pct:.1f}%)')

        # Check for negative prices
        neg_prices = (df['price_usd'] < 0).sum()
        if neg_prices > 0:
            report['issues'].append(f'{neg_prices} negative prices found')

        # Check for outliers using IQR
        for col in ['price_usd', 'volume_24h']:
            if col in df.columns and df[col].notna().sum() > 0:
                q1, q3 = df[col].quantile([0.25, 0.75])
                iqr = q3 - q1
                outliers = ((df[col] < q1 - 3*iqr) | (df[col] > q3 + 3*iqr)).sum()
                if outliers > 0:
                    report['warnings'].append(f'{col}: {outliers} extreme outliers')

        # Check for gaps
        if len(df) > 1:
            df_sorted = df.sort_values('timestamp')
            time_diffs = df_sorted['timestamp'].diff()
            expected_interval = time_diffs.median()

            # Gaps > 3x expected interval
            gaps = (time_diffs > expected_interval * 3).sum()
            if gaps > 0:
                report['warnings'].append(f'{gaps} data gaps detected')

        # Check for duplicates
        duplicates = df.duplicated(subset=['coin_id', 'timestamp']).sum()
        if duplicates > 0:
            report['issues'].append(f'{duplicates} duplicate records')

        report['passed'] = len(report['issues']) == 0
        return report

    def validate_sentiment(self, df: pd.DataFrame) -> Dict:
        """
        Validate sentiment data quality

        Args:
            df: Sentiment DataFrame

        Returns:
            Validation report
        """
        report = {
            'total_records': len(df),
            'issues': [],
            'warnings': [],
            'passed': True
        }

        if df.empty:
            report['issues'].append('No data to validate')
            report['passed'] = False
            return report

        # Check sentiment ranges
        if 'sentiment_score' in df.columns:
            out_of_range = ((df['sentiment_score'] < -1) | (df['sentiment_score'] > 1)).sum()
            if out_of_range > 0:
                report['issues'].append(f'{out_of_range} sentiment scores out of [-1, 1] range')

        # Check hype scores
        if 'hype_score' in df.columns:
            out_of_range = ((df['hype_score'] < 0) | (df['hype_score'] > 100)).sum()
            if out_of_range > 0:
                report['issues'].append(f'{out_of_range} hype scores out of [0, 100] range')

        # Check for nulls
        null_count = df['sentiment_score'].isnull().sum()
        if null_count > 0:
            pct = null_count / len(df) * 100
            if pct > 10:
                report['issues'].append(f'{null_count} null sentiment scores ({pct:.1f}%)')
            else:
                report['warnings'].append(f'{null_count} null sentiment scores ({pct:.1f}%)')

        report['passed'] = len(report['issues']) == 0
        return report

    # ==================== CLEANING ====================

    def clean_prices(self, df: pd.DataFrame, remove_outliers: bool = True,
                    fill_gaps: bool = True, remove_duplicates: bool = True) -> pd.DataFrame:
        """
        Clean price data

        Args:
            df: Raw price DataFrame
            remove_outliers: Remove extreme outliers
            fill_gaps: Fill data gaps with interpolation
            remove_duplicates: Remove duplicate records

        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        original_len = len(df_clean)

        # Remove duplicates
        if remove_duplicates:
            df_clean = df_clean.drop_duplicates(subset=['coin_id', 'timestamp'], keep='last')
            removed = original_len - len(df_clean)
            if removed > 0:
                logging.info(f"Removed {removed} duplicate records")

        # Remove extreme outliers (> 3 IQR)
        if remove_outliers:
            for col in ['price_usd', 'volume_24h']:
                if col in df_clean.columns:
                    q1, q3 = df_clean[col].quantile([0.25, 0.75])
                    iqr = q3 - q1
                    lower = q1 - 3 * iqr
                    upper = q3 + 3 * iqr

                    outliers = (df_clean[col] < lower) | (df_clean[col] > upper)
                    outlier_count = outliers.sum()

                    if outlier_count > 0:
                        # Replace outliers with NaN (will be interpolated)
                        df_clean.loc[outliers, col] = np.nan
                        logging.info(f"Marked {outlier_count} outliers in {col}")

        # Fill gaps with interpolation
        if fill_gaps:
            for col in ['price_usd', 'volume_24h', 'market_cap']:
                if col in df_clean.columns:
                    null_before = df_clean[col].isnull().sum()
                    df_clean[col] = df_clean[col].interpolate(method='linear')
                    filled = null_before - df_clean[col].isnull().sum()
                    if filled > 0:
                        logging.info(f"Filled {filled} gaps in {col}")

        # Remove negative prices
        neg_mask = df_clean['price_usd'] < 0
        if neg_mask.sum() > 0:
            df_clean = df_clean[~neg_mask]
            logging.info(f"Removed {neg_mask.sum()} negative price records")

        logging.info(f"Cleaning complete: {original_len} -> {len(df_clean)} records")
        return df_clean

    def clean_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean sentiment data

        Args:
            df: Raw sentiment DataFrame

        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()

        # Clamp sentiment scores to [-1, 1]
        if 'sentiment_score' in df_clean.columns:
            df_clean['sentiment_score'] = df_clean['sentiment_score'].clip(-1, 1)

        # Clamp hype scores to [0, 100]
        if 'hype_score' in df_clean.columns:
            df_clean['hype_score'] = df_clean['hype_score'].clip(0, 100)

        # Remove records with null sentiment
        null_mask = df_clean['sentiment_score'].isnull()
        if null_mask.sum() > 0:
            df_clean = df_clean[~null_mask]
            logging.info(f"Removed {null_mask.sum()} records with null sentiment")

        return df_clean

    # ==================== AGGREGATION ====================

    def aggregate_hourly(self, df: pd.DataFrame, value_col: str = 'price_usd') -> pd.DataFrame:
        """
        Aggregate data to hourly intervals

        Args:
            df: DataFrame with timestamp column
            value_col: Column to aggregate

        Returns:
            Hourly aggregated DataFrame
        """
        df_agg = df.copy()
        df_agg['hour'] = df_agg['timestamp'].dt.floor('H')

        agg_funcs = {
            value_col: ['mean', 'min', 'max', 'std', 'count']
        }

        if 'volume_24h' in df_agg.columns:
            agg_funcs['volume_24h'] = 'mean'

        result = df_agg.groupby(['symbol', 'hour']).agg(agg_funcs).reset_index()
        result.columns = ['_'.join(col).strip('_') for col in result.columns]

        return result

    def aggregate_daily(self, df: pd.DataFrame, value_col: str = 'price_usd') -> pd.DataFrame:
        """
        Aggregate data to daily intervals

        Args:
            df: DataFrame with timestamp column
            value_col: Column to aggregate

        Returns:
            Daily aggregated DataFrame
        """
        df_agg = df.copy()
        df_agg['date'] = df_agg['timestamp'].dt.date

        result = df_agg.groupby(['symbol', 'date']).agg({
            value_col: ['mean', 'min', 'max', 'first', 'last'],
            'volume_24h': 'mean' if 'volume_24h' in df_agg.columns else 'count'
        }).reset_index()

        result.columns = ['_'.join(col).strip('_') for col in result.columns]
        return result

    # ==================== MERGING ====================

    def merge_price_sentiment(self, prices_df: pd.DataFrame, sentiment_df: pd.DataFrame,
                             time_window: str = '1H') -> pd.DataFrame:
        """
        Merge price and sentiment data on time windows

        Args:
            prices_df: Price DataFrame
            sentiment_df: Sentiment DataFrame
            time_window: Time window for grouping ('1H', '4H', '1D')

        Returns:
            Merged DataFrame
        """
        # Round timestamps to window
        prices = prices_df.copy()
        sentiment = sentiment_df.copy()

        prices['time_bucket'] = prices['timestamp'].dt.floor(time_window)
        sentiment['time_bucket'] = sentiment['timestamp'].dt.floor(time_window)

        # Aggregate sentiment per bucket
        sentiment_agg = sentiment.groupby(['symbol', 'time_bucket']).agg({
            'sentiment_score': 'mean',
            'hype_score': 'mean',
            'post_count': 'sum'
        }).reset_index()

        # Aggregate prices per bucket
        price_agg = prices.groupby(['symbol', 'time_bucket']).agg({
            'price_usd': 'mean',
            'volume_24h': 'mean',
            'change_24h_pct': 'last'
        }).reset_index()

        # Merge
        merged = pd.merge(price_agg, sentiment_agg, on=['symbol', 'time_bucket'], how='outer')

        logging.info(f"Merged {len(merged)} records (window: {time_window})")
        return merged

    # ==================== EXPORT ====================

    def export_to_csv(self, df: pd.DataFrame, filename: str, output_dir: str = None):
        """
        Export DataFrame to CSV

        Args:
            df: DataFrame to export
            filename: Output filename
            output_dir: Output directory (default: exports/)
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / 'exports'

        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        filepath = output_dir / filename
        df.to_csv(filepath, index=False)
        logging.info(f"Exported {len(df)} records to {filepath}")

    def export_for_analysis(self, coin_symbol: str = None, start_date: datetime = None,
                           end_date: datetime = None, output_dir: str = None) -> Dict[str, str]:
        """
        Export cleaned, merged data ready for analysis

        Args:
            coin_symbol: Filter by coin
            start_date: Start date
            end_date: End date
            output_dir: Output directory

        Returns:
            Dictionary of exported file paths
        """
        exports = {}

        # Load and clean prices
        prices = self.load_prices(coin_symbol, start_date, end_date)
        if not prices.empty:
            prices_clean = self.clean_prices(prices)
            self.export_to_csv(prices_clean, 'prices_clean.csv', output_dir)
            exports['prices'] = 'prices_clean.csv'

            # Daily aggregation
            prices_daily = self.aggregate_daily(prices_clean)
            self.export_to_csv(prices_daily, 'prices_daily.csv', output_dir)
            exports['prices_daily'] = 'prices_daily.csv'

        # Load and clean sentiment
        sentiment = self.load_sentiment(coin_symbol, start_date=start_date, end_date=end_date)
        if not sentiment.empty:
            sentiment_clean = self.clean_sentiment(sentiment)
            self.export_to_csv(sentiment_clean, 'sentiment_clean.csv', output_dir)
            exports['sentiment'] = 'sentiment_clean.csv'

        # Merge price and sentiment
        if not prices.empty and not sentiment.empty:
            merged = self.merge_price_sentiment(prices_clean, sentiment_clean, '4H')
            self.export_to_csv(merged, 'price_sentiment_merged.csv', output_dir)
            exports['merged'] = 'price_sentiment_merged.csv'

        # Export events
        events = self.load_events(coin_symbol)
        if not events.empty:
            self.export_to_csv(events, 'events.csv', output_dir)
            exports['events'] = 'events.csv'

        logging.info(f"Exported {len(exports)} files")
        return exports

    # ==================== STATISTICS ====================

    def get_data_summary(self) -> Dict:
        """Get comprehensive data summary"""

        summary = {
            'database_path': self.db_path,
            'tables': {}
        }

        # Count records in each table
        tables = ['coins', 'prices', 'reddit_posts', 'tiktok_videos', 'sentiment_scores', 'collection_logs']

        for table in tables:
            try:
                count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", self.conn)
                summary['tables'][table] = count['count'].values[0]
            except:
                summary['tables'][table] = 0

        # Get date range
        try:
            dates = pd.read_sql_query(
                "SELECT MIN(timestamp) as min_date, MAX(timestamp) as max_date FROM prices",
                self.conn
            )
            summary['date_range'] = {
                'start': dates['min_date'].values[0],
                'end': dates['max_date'].values[0]
            }
        except:
            summary['date_range'] = None

        # Get coin breakdown
        try:
            coins = pd.read_sql_query(
                """SELECT c.symbol, COUNT(p.id) as price_count
                   FROM coins c LEFT JOIN prices p ON c.id = p.coin_id
                   GROUP BY c.symbol ORDER BY price_count DESC""",
                self.conn
            )
            summary['coins'] = coins.to_dict('records')
        except:
            summary['coins'] = []

        return summary


def main():
    """CLI for data pipeline operations"""
    import argparse

    parser = argparse.ArgumentParser(description='Data Validation and Cleaning Pipeline')

    parser.add_argument('--validate', action='store_true', help='Validate data quality')
    parser.add_argument('--clean', action='store_true', help='Clean and export data')
    parser.add_argument('--summary', action='store_true', help='Show data summary')
    parser.add_argument('--coin', type=str, help='Filter by coin symbol')
    parser.add_argument('--output', type=str, default='exports', help='Output directory')

    args = parser.parse_args()

    pipeline = DataPipeline()

    try:
        if args.summary:
            summary = pipeline.get_data_summary()
            print("\n=== Data Summary ===\n")
            print(f"Database: {summary['database_path']}")
            print("\nTable counts:")
            for table, count in summary['tables'].items():
                print(f"  {table}: {count:,}")
            if summary['date_range']:
                print(f"\nDate range: {summary['date_range']['start']} to {summary['date_range']['end']}")

        if args.validate:
            print("\n=== Validating Data ===\n")

            prices = pipeline.load_prices(args.coin)
            price_report = pipeline.validate_prices(prices)

            print("Price Data:")
            print(f"  Records: {price_report['total_records']}")
            print(f"  Passed: {price_report['passed']}")
            if price_report['issues']:
                print("  Issues:")
                for issue in price_report['issues']:
                    print(f"    - {issue}")
            if price_report['warnings']:
                print("  Warnings:")
                for warning in price_report['warnings']:
                    print(f"    - {warning}")

        if args.clean:
            print("\n=== Cleaning and Exporting ===\n")
            exports = pipeline.export_for_analysis(args.coin, output_dir=args.output)
            print("Exported files:")
            for name, path in exports.items():
                print(f"  {name}: {path}")

    finally:
        pipeline.close()


if __name__ == "__main__":
    main()
