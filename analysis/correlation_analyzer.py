"""
Correlation Analysis Tools
===========================
Statistical analysis of price-sentiment correlations
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.data_pipeline import DataPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class CorrelationAnalyzer:
    """
    Analyzes correlations between sentiment and price movements
    """

    def __init__(self, db_path: str = None):
        """Initialize correlation analyzer"""
        self.pipeline = DataPipeline(db_path)
        logging.info("Correlation analyzer initialized")

    def close(self):
        """Close connections"""
        self.pipeline.close()

    def calculate_correlation(self, x: pd.Series, y: pd.Series,
                            method: str = 'pearson') -> Dict:
        """
        Calculate correlation between two series

        Args:
            x: First series
            y: Second series
            method: 'pearson' or 'spearman'

        Returns:
            Correlation results
        """
        # Remove NaN values
        mask = ~(x.isna() | y.isna())
        x_clean = x[mask]
        y_clean = y[mask]

        if len(x_clean) < 10:
            return {
                'correlation': None,
                'p_value': None,
                'sample_size': len(x_clean),
                'significant': False,
                'error': 'Insufficient data (< 10 samples)'
            }

        if method == 'pearson':
            corr, p_value = stats.pearsonr(x_clean, y_clean)
        elif method == 'spearman':
            corr, p_value = stats.spearmanr(x_clean, y_clean)
        else:
            raise ValueError(f"Unknown method: {method}")

        return {
            'correlation': corr,
            'p_value': p_value,
            'sample_size': len(x_clean),
            'significant': p_value < 0.05,
            'strength': self._interpret_correlation(corr),
            'method': method
        }

    def _interpret_correlation(self, corr: float) -> str:
        """Interpret correlation strength"""
        abs_corr = abs(corr)
        if abs_corr >= 0.7:
            return 'strong'
        elif abs_corr >= 0.4:
            return 'moderate'
        elif abs_corr >= 0.2:
            return 'weak'
        else:
            return 'negligible'

    def analyze_price_sentiment_correlation(self, coin_symbol: str,
                                           time_window: str = '4H',
                                           lag_hours: int = 0) -> Dict:
        """
        Analyze correlation between price changes and sentiment

        Args:
            coin_symbol: Coin to analyze
            time_window: Aggregation window
            lag_hours: Hours to lag sentiment (positive = sentiment leads)

        Returns:
            Correlation analysis results
        """
        # Load data
        prices = self.pipeline.load_prices(coin_symbol)
        sentiment = self.pipeline.load_sentiment(coin_symbol)

        if prices.empty or sentiment.empty:
            return {'error': 'Insufficient data'}

        # Clean data
        prices_clean = self.pipeline.clean_prices(prices)
        sentiment_clean = self.pipeline.clean_sentiment(sentiment)

        # Merge on time windows
        merged = self.pipeline.merge_price_sentiment(prices_clean, sentiment_clean, time_window)

        if len(merged) < 10:
            return {'error': f'Insufficient merged data ({len(merged)} records)'}

        # Calculate price changes
        merged = merged.sort_values('time_bucket')
        merged['price_change_pct'] = merged['price_usd'].pct_change() * 100

        # Apply lag if specified
        if lag_hours > 0:
            # Shift sentiment forward (sentiment from X hours ago)
            merged['sentiment_lagged'] = merged['sentiment_score'].shift(lag_hours)
        else:
            merged['sentiment_lagged'] = merged['sentiment_score']

        # Calculate correlations
        results = {
            'coin_symbol': coin_symbol,
            'time_window': time_window,
            'lag_hours': lag_hours,
            'data_points': len(merged),
            'date_range': {
                'start': merged['time_bucket'].min().isoformat() if not merged.empty else None,
                'end': merged['time_bucket'].max().isoformat() if not merged.empty else None
            }
        }

        # Sentiment vs Price Level
        results['sentiment_vs_price'] = self.calculate_correlation(
            merged['sentiment_lagged'],
            merged['price_usd'],
            method='pearson'
        )

        # Sentiment vs Price Change
        results['sentiment_vs_price_change'] = self.calculate_correlation(
            merged['sentiment_lagged'],
            merged['price_change_pct'],
            method='pearson'
        )

        # Hype vs Price Change
        if 'hype_score' in merged.columns:
            results['hype_vs_price_change'] = self.calculate_correlation(
                merged['hype_score'],
                merged['price_change_pct'],
                method='pearson'
            )

        # Spearman (rank) correlation
        results['sentiment_vs_price_change_spearman'] = self.calculate_correlation(
            merged['sentiment_lagged'],
            merged['price_change_pct'],
            method='spearman'
        )

        return results

    def find_optimal_lag(self, coin_symbol: str, max_lag_hours: int = 48,
                        time_window: str = '4H') -> Dict:
        """
        Find the lag that maximizes correlation

        Args:
            coin_symbol: Coin to analyze
            max_lag_hours: Maximum lag to test
            time_window: Time window for aggregation

        Returns:
            Optimal lag results
        """
        results = []

        for lag in range(0, max_lag_hours + 1, 4):  # Test every 4 hours
            analysis = self.analyze_price_sentiment_correlation(
                coin_symbol, time_window, lag_hours=lag
            )

            if 'error' not in analysis:
                corr_result = analysis['sentiment_vs_price_change']
                if corr_result['correlation'] is not None:
                    results.append({
                        'lag_hours': lag,
                        'correlation': corr_result['correlation'],
                        'p_value': corr_result['p_value'],
                        'significant': corr_result['significant']
                    })

        if not results:
            return {'error': 'Could not calculate correlations at any lag'}

        # Find optimal
        df_results = pd.DataFrame(results)

        # Best absolute correlation
        best_idx = df_results['correlation'].abs().idxmax()
        optimal = df_results.loc[best_idx].to_dict()

        return {
            'coin_symbol': coin_symbol,
            'optimal_lag_hours': int(optimal['lag_hours']),
            'optimal_correlation': optimal['correlation'],
            'optimal_p_value': optimal['p_value'],
            'optimal_significant': optimal['significant'],
            'all_results': results,
            'interpretation': self._interpret_lag(optimal)
        }

    def _interpret_lag(self, result: Dict) -> str:
        """Interpret lag analysis results"""
        lag = result['lag_hours']
        corr = result['correlation']

        if not result['significant']:
            return "No statistically significant correlation found at any lag"

        direction = "positive" if corr > 0 else "negative"
        strength = self._interpret_correlation(corr)

        if lag == 0:
            return f"{strength.capitalize()} {direction} correlation between sentiment and price changes (concurrent)"
        else:
            return f"{strength.capitalize()} {direction} correlation found when sentiment leads price by {lag} hours"

    def analyze_all_coins(self, time_window: str = '4H') -> pd.DataFrame:
        """
        Analyze correlations for all coins

        Returns:
            DataFrame with correlation results for all coins
        """
        # Get all coins
        coins_query = "SELECT DISTINCT symbol FROM coins"
        coins = pd.read_sql_query(coins_query, self.pipeline.conn)

        results = []

        for symbol in coins['symbol']:
            logging.info(f"Analyzing {symbol}...")

            analysis = self.analyze_price_sentiment_correlation(symbol, time_window)

            if 'error' not in analysis:
                result = {
                    'symbol': symbol,
                    'data_points': analysis['data_points']
                }

                if 'sentiment_vs_price_change' in analysis:
                    corr = analysis['sentiment_vs_price_change']
                    result['correlation'] = corr['correlation']
                    result['p_value'] = corr['p_value']
                    result['significant'] = corr['significant']
                    result['strength'] = corr.get('strength', 'unknown')

                results.append(result)

        df = pd.DataFrame(results)

        if not df.empty:
            df = df.sort_values('correlation', ascending=False, key=abs)

        return df

    def generate_report(self, coin_symbol: str = None) -> str:
        """
        Generate a correlation analysis report

        Args:
            coin_symbol: Specific coin or None for all

        Returns:
            Markdown report
        """
        report = "# Correlation Analysis Report\n\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if coin_symbol:
            # Single coin analysis
            analysis = self.analyze_price_sentiment_correlation(coin_symbol)
            lag_analysis = self.find_optimal_lag(coin_symbol)

            report += f"## {coin_symbol} Analysis\n\n"

            if 'error' in analysis:
                report += f"Error: {analysis['error']}\n\n"
            else:
                report += f"**Data Points:** {analysis['data_points']}\n"
                report += f"**Date Range:** {analysis['date_range']['start']} to {analysis['date_range']['end']}\n\n"

                report += "### Correlation Results\n\n"
                report += "| Metric | Correlation | P-Value | Significant | Strength |\n"
                report += "|--------|-------------|---------|-------------|----------|\n"

                for key in ['sentiment_vs_price', 'sentiment_vs_price_change', 'hype_vs_price_change']:
                    if key in analysis:
                        r = analysis[key]
                        if r['correlation'] is not None:
                            report += f"| {key} | {r['correlation']:.3f} | {r['p_value']:.4f} | {r['significant']} | {r['strength']} |\n"

                report += "\n### Optimal Lag Analysis\n\n"
                if 'error' not in lag_analysis:
                    report += f"**Optimal Lag:** {lag_analysis['optimal_lag_hours']} hours\n"
                    report += f"**Correlation at Optimal Lag:** {lag_analysis['optimal_correlation']:.3f}\n"
                    report += f"**Interpretation:** {lag_analysis['interpretation']}\n"
        else:
            # All coins analysis
            all_results = self.analyze_all_coins()

            report += "## All Coins Summary\n\n"

            if all_results.empty:
                report += "No data available for analysis.\n"
            else:
                report += "| Coin | Data Points | Correlation | P-Value | Significant | Strength |\n"
                report += "|------|-------------|-------------|---------|-------------|----------|\n"

                for _, row in all_results.iterrows():
                    if pd.notna(row.get('correlation')):
                        report += f"| {row['symbol']} | {row['data_points']} | {row['correlation']:.3f} | "
                        report += f"{row['p_value']:.4f} | {row['significant']} | {row['strength']} |\n"

                # Summary statistics
                significant = all_results[all_results['significant'] == True]
                report += f"\n**Coins with Significant Correlations:** {len(significant)}/{len(all_results)}\n"

                if not significant.empty:
                    avg_corr = significant['correlation'].mean()
                    report += f"**Average Correlation (significant only):** {avg_corr:.3f}\n"

        return report


def main():
    """CLI for correlation analysis"""
    import argparse

    parser = argparse.ArgumentParser(description='Correlation Analysis')

    parser.add_argument('--coin', type=str, help='Analyze specific coin')
    parser.add_argument('--all', action='store_true', help='Analyze all coins')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--lag', action='store_true', help='Find optimal lag')
    parser.add_argument('--output', type=str, help='Output file for report')

    args = parser.parse_args()

    analyzer = CorrelationAnalyzer()

    try:
        if args.lag and args.coin:
            print(f"\n=== Optimal Lag Analysis for {args.coin} ===\n")
            result = analyzer.find_optimal_lag(args.coin)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Optimal lag: {result['optimal_lag_hours']} hours")
                print(f"Correlation: {result['optimal_correlation']:.3f}")
                print(f"P-value: {result['optimal_p_value']:.4f}")
                print(f"Significant: {result['optimal_significant']}")
                print(f"\nInterpretation: {result['interpretation']}")

        elif args.all or (args.report and not args.coin):
            print("\n=== Analyzing All Coins ===\n")
            results = analyzer.analyze_all_coins()
            print(results.to_string())

        elif args.coin:
            print(f"\n=== Correlation Analysis for {args.coin} ===\n")
            result = analyzer.analyze_price_sentiment_correlation(args.coin)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Data points: {result['data_points']}")
                for key, val in result.items():
                    if isinstance(val, dict) and 'correlation' in val:
                        print(f"\n{key}:")
                        print(f"  Correlation: {val['correlation']:.3f}")
                        print(f"  P-value: {val['p_value']:.4f}")
                        print(f"  Significant: {val['significant']}")

        if args.report:
            report = analyzer.generate_report(args.coin)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"\nReport saved to {args.output}")
            else:
                print(report)

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
