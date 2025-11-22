"""
SCRIPT C: BACKTEST ANALYZER
============================
Analyzes historical social metrics vs price movements to prove/disprove hypothesis.
This is where you validate your meme coin sentiment theory!

WHAT THIS DOES:
- Loads historical social data (from Script B)
- Loads historical price data (from your meme_coin_tracker)
- Finds correlations between social spikes and price pumps
- Calculates lag times (does social lead price?)
- Generates reports and visualizations
- PROVES OR DISPROVES your hypothesis!

LEARNING NOTES:
- Time series alignment and lag analysis
- Statistical correlation calculations
- Data merging and manipulation with pandas
- Basic data visualization
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy import stats
import os

# =============================================================================
# CONFIGURATION
# =============================================================================

# Input files
LUNARCRUSH_FILE = 'lunarcrush_historical_data.csv'
PRICE_FILE = 'meme_coin_data.csv'  # From your original tracker

# Output
REPORT_FILE = 'backtest_report.txt'
CORRELATION_CSV = 'correlation_results.csv'

# Analysis parameters
LAG_DAYS = [0, 1, 2, 3, 7]  # Test if social metrics lead price by X days
SPIKE_THRESHOLD = 2.0  # 2x increase in social volume = "spike"
PRICE_PUMP_THRESHOLD = 5.0  # 5% price increase = "pump"

# =============================================================================
# DATA LOADING
# =============================================================================

def load_lunarcrush_data(filename=LUNARCRUSH_FILE):
    """
    Load LunarCrush historical data
    """
    try:
        df = pd.read_csv(filename)
        df['date'] = pd.to_datetime(df['date'])
        print(f"✅ Loaded LunarCrush data: {len(df)} records")
        print(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        print(f"   Coins: {df['symbol'].unique().tolist()}")
        return df
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found")
        print("   Run Script B (lunarcrush_historical_collector.py) first!")
        return None
    except Exception as e:
        print(f"❌ Error loading LunarCrush data: {e}")
        return None


def load_price_data(filename=PRICE_FILE):
    """
    Load your collected price data (optional - LunarCrush has prices too)
    """
    try:
        df = pd.read_csv(filename)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['date'] = df['Timestamp'].dt.date
        df['date'] = pd.to_datetime(df['date'])
        
        print(f"✅ Loaded price data: {len(df)} records")
        return df
    except FileNotFoundError:
        print(f"⚠️  {filename} not found - using LunarCrush prices instead")
        return None
    except Exception as e:
        print(f"⚠️  Error loading price data: {e}")
        return None


# =============================================================================
# SPIKE DETECTION
# =============================================================================

def detect_social_spikes(df, threshold=SPIKE_THRESHOLD):
    """
    Detect when social volume spikes significantly
    
    Returns: DataFrame with spike indicators
    """
    df_with_spikes = df.copy()
    
    for coin in df['symbol'].unique():
        coin_mask = df_with_spikes['symbol'] == coin
        coin_df = df_with_spikes[coin_mask].copy()
        
        # Calculate rolling average (7-day)
        coin_df['social_volume_ma'] = coin_df['social_volume'].rolling(window=7, min_periods=1).mean()
        
        # Detect spikes (volume > threshold * moving average)
        coin_df['is_spike'] = coin_df['social_volume'] > (coin_df['social_volume_ma'] * threshold)
        
        # Calculate spike magnitude
        coin_df['spike_magnitude'] = coin_df['social_volume'] / coin_df['social_volume_ma']
        
        # Update main dataframe
        df_with_spikes.loc[coin_mask, 'social_volume_ma'] = coin_df['social_volume_ma']
        df_with_spikes.loc[coin_mask, 'is_spike'] = coin_df['is_spike']
        df_with_spikes.loc[coin_mask, 'spike_magnitude'] = coin_df['spike_magnitude']
    
    return df_with_spikes


def detect_price_pumps(df, threshold=PRICE_PUMP_THRESHOLD):
    """
    Detect significant price increases
    
    Returns: DataFrame with pump indicators
    """
    df_with_pumps = df.copy()
    
    for coin in df['symbol'].unique():
        coin_mask = df_with_pumps['symbol'] == coin
        coin_df = df_with_pumps[coin_mask].copy()
        
        # Calculate day-over-day price change
        coin_df['price_change'] = coin_df['percent_change_24h']
        
        # Detect pumps (price increase > threshold)
        coin_df['is_pump'] = coin_df['price_change'] > threshold
        
        # Update main dataframe
        df_with_pumps.loc[coin_mask, 'price_change'] = coin_df['price_change']
        df_with_pumps.loc[coin_mask, 'is_pump'] = coin_df['is_pump']
    
    return df_with_pumps


# =============================================================================
# LAG ANALYSIS
# =============================================================================

def calculate_lag_correlation(df, lag_days=0):
    """
    Calculate correlation between social metrics and price change
    with a specified lag (does social predict future price?)
    
    lag_days = 0: Same day correlation
    lag_days = 1: Social today vs price tomorrow
    lag_days = 2: Social today vs price in 2 days, etc.
    """
    results = []
    
    for coin in df['symbol'].unique():
        coin_df = df[df['symbol'] == coin].copy().sort_values('date')
        
        if len(coin_df) < lag_days + 2:
            continue
        
        # Shift price data by lag days
        coin_df['future_price_change'] = coin_df['price_change'].shift(-lag_days)
        
        # Drop NaN values
        coin_df = coin_df.dropna(subset=['social_volume', 'future_price_change'])
        
        if len(coin_df) < 10:
            continue
        
        # Calculate correlations
        correlations = {
            'coin': coin,
            'lag_days': lag_days,
            'social_volume_corr': coin_df['social_volume'].corr(coin_df['future_price_change']),
            'social_score_corr': coin_df['social_score'].corr(coin_df['future_price_change']),
            'sentiment_corr': coin_df['sentiment'].corr(coin_df['future_price_change']),
            'galaxy_score_corr': coin_df['galaxy_score'].corr(coin_df['future_price_change']),
            'tweets_corr': coin_df['tweets'].corr(coin_df['future_price_change']),
            'reddit_corr': coin_df['reddit_posts'].corr(coin_df['future_price_change']),
            'n_samples': len(coin_df)
        }
        
        results.append(correlations)
    
    return pd.DataFrame(results)


def analyze_all_lags(df, lag_days_list=LAG_DAYS):
    """
    Test multiple lag periods to find optimal prediction timeframe
    """
    all_results = []
    
    print("\n" + "="*70)
    print("⏱️  LAG ANALYSIS - Does Social Predict Future Price?")
    print("="*70)
    
    for lag in lag_days_list:
        print(f"\n📊 Testing {lag}-day lag...")
        results = calculate_lag_correlation(df, lag_days=lag)
        all_results.append(results)
    
    combined_results = pd.concat(all_results, ignore_index=True)
    return combined_results


# =============================================================================
# SPIKE-TO-PUMP ANALYSIS
# =============================================================================

def analyze_spike_pump_relationship(df):
    """
    Analyze: When social spikes, does price pump soon after?
    """
    print("\n" + "="*70)
    print("🚀 SPIKE-TO-PUMP ANALYSIS")
    print("="*70)
    
    results = []
    
    for coin in df['symbol'].unique():
        coin_df = df[df['symbol'] == coin].copy().sort_values('date')
        
        # Find spike days
        spike_days = coin_df[coin_df['is_spike'] == True]
        
        if len(spike_days) == 0:
            print(f"\n{coin}: No social spikes detected")
            continue
        
        print(f"\n{coin}:")
        print(f"   Social spikes detected: {len(spike_days)}")
        
        # For each spike, check if price pumped within next 1-3 days
        pumps_after_spike = {1: 0, 2: 0, 3: 0}
        
        for idx, spike_row in spike_days.iterrows():
            spike_date = spike_row['date']
            
            # Check next 3 days
            for days_ahead in [1, 2, 3]:
                future_date = spike_date + timedelta(days=days_ahead)
                future_data = coin_df[coin_df['date'] == future_date]
                
                if not future_data.empty and future_data.iloc[0]['is_pump']:
                    pumps_after_spike[days_ahead] += 1
        
        # Calculate success rates
        for days_ahead, pump_count in pumps_after_spike.items():
            success_rate = (pump_count / len(spike_days)) * 100 if len(spike_days) > 0 else 0
            print(f"   Pumps within {days_ahead} day(s): {pump_count}/{len(spike_days)} ({success_rate:.1f}%)")
            
            results.append({
                'coin': coin,
                'days_ahead': days_ahead,
                'spike_count': len(spike_days),
                'pump_count': pump_count,
                'success_rate': success_rate
            })
    
    return pd.DataFrame(results)


# =============================================================================
# CASE STUDIES
# =============================================================================

def find_best_predictions(df, top_n=5):
    """
    Find the best examples where social predicted price pumps
    """
    print("\n" + "="*70)
    print("🎯 TOP PREDICTION EXAMPLES")
    print("="*70)
    print("\nBest cases where social spike preceded price pump:\n")
    
    all_cases = []
    
    for coin in df['symbol'].unique():
        coin_df = df[df['symbol'] == coin].copy().sort_values('date')
        
        # Find spike days
        spike_days = coin_df[coin_df['is_spike'] == True]
        
        for idx, spike_row in spike_days.iterrows():
            spike_date = spike_row['date']
            
            # Check next day for pump
            next_date = spike_date + timedelta(days=1)
            next_data = coin_df[coin_df['date'] == next_date]
            
            if not next_data.empty:
                next_row = next_data.iloc[0]
                
                if next_row['is_pump']:
                    all_cases.append({
                        'coin': coin,
                        'spike_date': spike_date,
                        'spike_magnitude': spike_row['spike_magnitude'],
                        'pump_date': next_date,
                        'price_change': next_row['price_change'],
                        'social_volume': spike_row['social_volume'],
                        'social_score': spike_row['social_score']
                    })
    
    if not all_cases:
        print("⚠️  No clear prediction examples found")
        return
    
    # Sort by price change
    cases_df = pd.DataFrame(all_cases).sort_values('price_change', ascending=False).head(top_n)
    
    for idx, case in cases_df.iterrows():
        print(f"📈 {case['coin']}:")
        print(f"   Spike date: {case['spike_date'].date()}")
        print(f"   Social spike: {case['spike_magnitude']:.1f}x above average")
        print(f"   Social volume: {case['social_volume']:,.0f}")
        print(f"   Next day pump: +{case['price_change']:.2f}%")
        print()


# =============================================================================
# REPORTING
# =============================================================================

def generate_report(df, lag_results, spike_pump_results):
    """
    Generate comprehensive backtest report
    """
    report_lines = []
    
    report_lines.append("="*70)
    report_lines.append("MEME COIN SENTIMENT BACKTEST REPORT")
    report_lines.append("="*70)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Dataset summary
    report_lines.append("DATASET SUMMARY:")
    report_lines.append(f"  Total records: {len(df)}")
    report_lines.append(f"  Coins analyzed: {', '.join(df['symbol'].unique())}")
    report_lines.append(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    report_lines.append(f"  Days of data: {(df['date'].max() - df['date'].min()).days}")
    report_lines.append("")
    
    # Best correlations
    report_lines.append("BEST CORRELATIONS (Social → Price):")
    report_lines.append("")
    
    for coin in lag_results['coin'].unique():
        coin_results = lag_results[lag_results['coin'] == coin]
        
        # Find best correlation across all lags and metrics
        best_row = coin_results.loc[
            coin_results[['social_volume_corr', 'social_score_corr', 'sentiment_corr', 'galaxy_score_corr']].abs().max(axis=1).idxmax()
        ]
        
        best_metric = None
        best_value = 0
        
        for metric in ['social_volume_corr', 'social_score_corr', 'sentiment_corr', 'galaxy_score_corr']:
            if abs(best_row[metric]) > abs(best_value):
                best_value = best_row[metric]
                best_metric = metric.replace('_corr', '').replace('_', ' ').title()
        
        report_lines.append(f"  {coin}:")
        report_lines.append(f"    Best metric: {best_metric}")
        report_lines.append(f"    Correlation: {best_value:.3f}")
        report_lines.append(f"    Optimal lag: {int(best_row['lag_days'])} day(s)")
        report_lines.append(f"    Interpretation: {'STRONG' if abs(best_value) > 0.5 else 'MODERATE' if abs(best_value) > 0.3 else 'WEAK'}")
        report_lines.append("")
    
    # Spike-to-pump success rates
    report_lines.append("SPIKE-TO-PUMP SUCCESS RATES:")
    report_lines.append("")
    
    if not spike_pump_results.empty:
        for coin in spike_pump_results['coin'].unique():
            coin_spike_data = spike_pump_results[spike_pump_results['coin'] == coin]
            report_lines.append(f"  {coin}:")
            
            for _, row in coin_spike_data.iterrows():
                report_lines.append(f"    {row['days_ahead']}-day prediction: {row['success_rate']:.1f}% ({row['pump_count']}/{row['spike_count']})")
            report_lines.append("")
    
    # Conclusion
    report_lines.append("CONCLUSION:")
    
    # Calculate overall statistics
    avg_correlation = lag_results[['social_volume_corr', 'social_score_corr']].abs().mean().mean()
    
    if avg_correlation > 0.4:
        report_lines.append("  ✅ HYPOTHESIS SUPPORTED")
        report_lines.append("  Social metrics show moderate-to-strong correlation with price movements.")
    elif avg_correlation > 0.2:
        report_lines.append("  ⚠️  HYPOTHESIS PARTIALLY SUPPORTED")
        report_lines.append("  Social metrics show weak-to-moderate correlation with price movements.")
    else:
        report_lines.append("  ❌ HYPOTHESIS NOT SUPPORTED")
        report_lines.append("  Social metrics show weak correlation with price movements.")
    
    report_lines.append("")
    report_lines.append("="*70)
    
    # Write to file
    with open(REPORT_FILE, 'w') as f:
        f.write('\n'.join(report_lines))
    
    # Print to console
    print('\n'.join(report_lines))
    
    print(f"\n💾 Full report saved to: {REPORT_FILE}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Run complete backtest analysis
    """
    print("\n" + "="*70)
    print("🔬 MEME COIN SENTIMENT BACKTEST ANALYZER")
    print("="*70)
    
    # Load data
    print("\n📂 Loading data...")
    lunarcrush_df = load_lunarcrush_data()
    
    if lunarcrush_df is None:
        return
    
    # Optional: Load your price data
    # price_df = load_price_data()
    
    # Detect spikes and pumps
    print("\n🔍 Detecting social spikes and price pumps...")
    df = detect_social_spikes(lunarcrush_df, threshold=SPIKE_THRESHOLD)
    df = detect_price_pumps(df, threshold=PRICE_PUMP_THRESHOLD)
    
    # Count spikes and pumps
    total_spikes = df['is_spike'].sum()
    total_pumps = df['is_pump'].sum()
    print(f"   Social spikes detected: {total_spikes}")
    print(f"   Price pumps detected: {total_pumps}")
    
    # Lag analysis
    lag_results = analyze_all_lags(df, lag_days_list=LAG_DAYS)
    
    # Spike-to-pump analysis
    spike_pump_results = analyze_spike_pump_relationship(df)
    
    # Find best examples
    find_best_predictions(df, top_n=5)
    
    # Save correlation results
    lag_results.to_csv(CORRELATION_CSV, index=False)
    print(f"\n💾 Correlation data saved to: {CORRELATION_CSV}")
    
    # Generate comprehensive report
    generate_report(df, lag_results, spike_pump_results)
    
    print("\n✅ Backtest analysis complete!")
    print("\n🎯 Key Takeaways:")
    print("   - Check the report for overall findings")
    print("   - Look for correlations > 0.3 (moderate) or > 0.5 (strong)")
    print("   - Note which metrics are most predictive")
    print("   - See if social leads price by 1-2 days")
    print("\n💡 Next: Review the report and decide if hypothesis is validated! 🚀\n")


if __name__ == "__main__":
    main()
