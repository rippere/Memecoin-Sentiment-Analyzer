"""
Pipeline Test Script
===================
Quick test to verify all components are working
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import get_db
from collectors.price_collector import PriceCollector
from collectors.sentiment_analyzer import SentimentAnalyzer
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def test_database():
    """Test database connection and initialization"""
    print("\n" + "=" * 70)
    print("TEST 1: Database Connection")
    print("=" * 70)

    try:
        db = get_db()
        stats = db.get_stats()

        print("✅ Database initialized successfully")
        print(f"   Coins in database: {stats['coins']}")
        print(f"   Price records: {stats['prices']}")
        print(f"   Reddit posts: {stats['reddit_posts']}")
        print(f"   TikTok videos: {stats['tiktok_videos']}")
        print(f"   Sentiment scores: {stats['sentiment_scores']}")

        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_price_collector():
    """Test price data collection"""
    print("\n" + "=" * 70)
    print("TEST 2: Price Collector")
    print("=" * 70)

    try:
        collector = PriceCollector()
        prices = collector.fetch_coin_data(['DOGE', 'PEPE'])

        if prices:
            print(f"✅ Price collector working")
            for symbol, data in prices.items():
                print(f"   {symbol}: ${data['price_usd']:.6f}")

            # Test database storage
            db = get_db()
            for symbol, data in prices.items():
                db.add_price(symbol, data)
            print(f"✅ Saved {len(prices)} prices to database")

            return True
        else:
            print("⚠️  No price data returned (may be rate limited)")
            return False

    except Exception as e:
        print(f"❌ Price collector test failed: {e}")
        return False


def test_sentiment_analyzer():
    """Test sentiment analysis"""
    print("\n" + "=" * 70)
    print("TEST 3: Sentiment Analyzer")
    print("=" * 70)

    try:
        analyzer = SentimentAnalyzer()

        # Test with sample Reddit post
        sample_post = {
            'title': 'DOGE to the moon! 🚀🚀🚀',
            'body': 'This is not financial advice but DOGE is pumping hard! HODL!',
            'score': 1234,
            'num_comments': 567
        }

        result = analyzer.analyze_reddit_post(sample_post)

        print("✅ Sentiment analyzer working")
        print(f"   Sentiment score: {result['sentiment_compound']:.3f}")
        print(f"   Hype score: {result['hype_score']:.1f}/100")
        print(f"   Keywords found: {', '.join(result['hype_keywords_found'][:5])}")

        return True

    except Exception as e:
        print(f"❌ Sentiment analyzer test failed: {e}")
        return False


def test_scrapers_available():
    """Test if scrapers can be imported"""
    print("\n" + "=" * 70)
    print("TEST 4: Scraper Availability")
    print("=" * 70)

    try:
        from scrapers.reddit_scraper import RedditScraper
        from scrapers.tiktok_scraper import TikTokScraper

        print("✅ Reddit scraper available")
        print("✅ TikTok scraper available")
        print("   Note: Full scraper test requires headless browser")

        return True

    except Exception as e:
        print(f"❌ Scraper import failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("MEMECOIN PIPELINE TEST SUITE")
    print("=" * 70)

    results = []

    # Run tests
    results.append(("Database", test_database()))
    results.append(("Price Collector", test_price_collector()))
    results.append(("Sentiment Analyzer", test_sentiment_analyzer()))
    results.append(("Scrapers", test_scrapers_available()))

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")

    print("\n" + "=" * 70)
    if passed == total:
        print(f"ALL TESTS PASSED ({passed}/{total})")
        print("\nYou're ready to start collecting data!")
        print("\nNext steps:")
        print("1. Run: python schedule_collection.py --mode once")
        print("2. Check database for collected data")
        print("3. Set up automated collection schedule")
    else:
        print(f"SOME TESTS FAILED ({passed}/{total} passed)")
        print("\nPlease fix the failing tests before proceeding.")
        print("See QUICKSTART.md for troubleshooting.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
