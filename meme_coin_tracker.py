"""
MEME COIN DATA COLLECTOR - Your First Script!
==============================================
This script fetches live cryptocurrency data from CoinGecko (free, no API key needed)
Focus: DOGE, PEPE, and other popular meme coins

WHAT YOU'LL LEARN:
- How to make API requests
- How to handle JSON data
- How to structure data with pandas
- Basic error handling
"""

import requests  # This library lets us talk to websites/APIs
import pandas as pd  # This is like Excel but in Python
from datetime import datetime  # For timestamps
import time  # For delays between requests
import json  # For pretty printing data

# =============================================================================
# CONFIGURATION - Easy to modify coins here
# =============================================================================

# These are CoinGecko's official IDs for each coin
MEME_COINS = {
    'dogecoin': 'DOGE',
    'pepe': 'PEPE',
    'shiba-inu': 'SHIB',
    'bonk': 'BONK',
    'floki': 'FLOKI',
    'dogwifhat': 'WIF',
}

# CoinGecko API endpoint (free tier, no key needed)
BASE_URL = "https://api.coingecko.com/api/v3"


# =============================================================================
# FUNCTION 1: Fetch Current Price Data
# =============================================================================

def fetch_coin_data(coin_ids):
    """
    Fetches current market data for specified coins
    
    Parameters:
    - coin_ids: list of CoinGecko coin IDs (e.g., ['dogecoin', 'pepe'])
    
    Returns:
    - Dictionary containing coin data
    """
    # Join coin IDs with commas for the API request
    ids_string = ','.join(coin_ids)
    
    # Build the API URL
    url = f"{BASE_URL}/coins/markets"
    
    # Parameters for our request
    params = {
        'vs_currency': 'usd',  # Price in USD
        'ids': ids_string,
        'order': 'market_cap_desc',
        'per_page': len(coin_ids),
        'page': 1,
        'sparkline': False,
        'price_change_percentage': '1h,24h,7d'  # Price changes over time
    }
    
    try:
        print(f"📡 Fetching data from CoinGecko...")
        response = requests.get(url, params=params, timeout=10)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully fetched data for {len(data)} coins!")
            return data
        else:
            print(f"❌ Error: API returned status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None


# =============================================================================
# FUNCTION 2: Process and Display Data
# =============================================================================

def process_and_display(coin_data):
    """
    Takes raw API data and creates a clean pandas DataFrame
    Then displays it in an easy-to-read format
    """
    if not coin_data:
        print("No data to process!")
        return None
    
    # Extract the fields we care about
    processed_data = []
    
    for coin in coin_data:
        processed_data.append({
            'Symbol': coin['symbol'].upper(),
            'Name': coin['name'],
            'Price (USD)': coin['current_price'],
            'Market Cap': coin['market_cap'],
            'Volume 24h': coin['total_volume'],
            '1h Change %': coin.get('price_change_percentage_1h_in_currency', 0),
            '24h Change %': coin.get('price_change_percentage_24h', 0),
            '7d Change %': coin.get('price_change_percentage_7d_in_currency', 0),
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Create a pandas DataFrame (like an Excel spreadsheet)
    df = pd.DataFrame(processed_data)
    
    return df


# =============================================================================
# FUNCTION 3: Save Data to CSV
# =============================================================================

def save_to_csv(df, filename='meme_coin_data.csv'):
    """
    Saves the DataFrame to a CSV file
    If file exists, it appends new data (building historical data)
    """
    if df is None:
        return
    
    try:
        # Try to load existing data
        existing_df = pd.read_csv(filename)
        # Append new data
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_csv(filename, index=False)
        print(f"📝 Data appended to {filename}")
    except FileNotFoundError:
        # File doesn't exist yet, create it
        df.to_csv(filename, index=False)
        print(f"📝 New file created: {filename}")


# =============================================================================
# FUNCTION 4: Display Summary Statistics
# =============================================================================

def display_summary(df):
    """
    Shows interesting insights from the data
    """
    if df is None or df.empty:
        return
    
    print("\n" + "="*70)
    print("📊 MEME COIN MARKET SUMMARY")
    print("="*70)
    
    # Find biggest gainers and losers
    biggest_gainer = df.loc[df['24h Change %'].idxmax()]
    biggest_loser = df.loc[df['24h Change %'].idxmin()]
    
    print(f"\n🚀 Biggest 24h Gainer: {biggest_gainer['Symbol']} "
          f"({biggest_gainer['24h Change %']:.2f}%)")
    print(f"📉 Biggest 24h Loser: {biggest_loser['Symbol']} "
          f"({biggest_loser['24h Change %']:.2f}%)")
    
    # Total market cap of these meme coins
    total_market_cap = df['Market Cap'].sum()
    print(f"\n💰 Combined Market Cap: ${total_market_cap:,.0f}")
    
    # Show which coins are most actively traded
    most_volume = df.loc[df['Volume 24h'].idxmax()]
    print(f"📈 Most Active (24h volume): {most_volume['Symbol']} "
          f"(${most_volume['Volume 24h']:,.0f})")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main function that runs everything
    """
    print("\n" + "="*70)
    print("🐕 MEME COIN TRACKER - LIVE DATA")
    print("="*70)
    print(f"Tracking: {', '.join([MEME_COINS[coin] for coin in MEME_COINS.keys()])}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    # Step 1: Fetch data from API
    coin_ids = list(MEME_COINS.keys())
    raw_data = fetch_coin_data(coin_ids)
    
    if raw_data:
        # Step 2: Process the data
        df = process_and_display(raw_data)
        
        if df is not None:
            # Step 3: Display the data nicely
            print("\n📋 CURRENT MARKET DATA:")
            print("-" * 70)
            # Format the display with better precision
            pd.options.display.float_format = '{:,.2f}'.format
            print(df.to_string(index=False))
            
            # Step 4: Show summary insights
            display_summary(df)
            
            # Step 5: Save to CSV for historical tracking
            save_to_csv(df)
            
            print("\n" + "="*70)
            print("✅ Script completed successfully!")
            print("💡 TIP: Run this script multiple times to build historical data")
            print("="*70 + "\n")


# =============================================================================
# RUN THE SCRIPT
# =============================================================================

if __name__ == "__main__":
    main()
    
    # Optional: Uncomment below to run continuously every 5 minutes
    # This will keep collecting data automatically
    """
    print("\n🔄 Running in continuous mode (collecting data every 5 minutes)")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            main()
            print("⏳ Waiting 5 minutes before next collection...")
            time.sleep(300)  # Wait 5 minutes (300 seconds)
    except KeyboardInterrupt:
        print("\n\n⏹️  Script stopped by user")
    """
