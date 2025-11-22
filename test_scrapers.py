"""
Test Scrapers - Quick Verification
===================================
Run this to test if TikTok and Reddit scrapers work
"""

import sys
sys.path.append('.')  # Add current directory to path

from scrapers.tiktok_scraper import TikTokScraper
from scrapers.reddit_scraper import RedditScraper
import json
from datetime import datetime

def test_tiktok():
    """Test TikTok scraper"""
    print("\n" + "="*70)
    print("TESTING TIKTOK SCRAPER")
    print("="*70)
    
    config = {
        'headless': False,  # Set to True to hide browser
        'min_delay': 2,
        'max_delay': 4,
    }
    
    try:
        with TikTokScraper(config) as scraper:
            # Test with DOGE hashtag
            videos = scraper.scrape_hashtag('dogecoin', max_results=10)
            
            print(f"\n✅ SUCCESS! Collected {len(videos)} TikTok videos")
            
            if videos:
                print("\n📊 Sample Video Data:")
                sample = videos[0]
                print(json.dumps(sample, indent=2, default=str))
                
                # Save to file
                with open('test_tiktok_results.json', 'w') as f:
                    json.dump(videos, f, indent=2, default=str)
                print("\n💾 Full results saved to: test_tiktok_results.json")
            
            return True
            
    except Exception as e:
        print(f"\n❌ TikTok scraper FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reddit():
    """Test Reddit scraper"""
    print("\n" + "="*70)
    print("TESTING REDDIT SCRAPER")
    print("="*70)
    
    config = {
        'headless': False,  # Set to True to hide browser
        'min_delay': 1,
        'max_delay': 3,
    }
    
    try:
        with RedditScraper(config) as scraper:
            # Test with CryptoCurrency subreddit
            posts = scraper.scrape_subreddit_search(
                subreddit='CryptoCurrency',
                query='dogecoin',
                max_results=10
            )
            
            print(f"\n✅ SUCCESS! Collected {len(posts)} Reddit posts")
            
            if posts:
                print("\n📊 Sample Post Data:")
                sample = posts[0]
                print(json.dumps(sample, indent=2, default=str))
                
                # Save to file
                with open('test_reddit_results.json', 'w') as f:
                    json.dump(posts, f, indent=2, default=str)
                print("\n💾 Full results saved to: test_reddit_results.json")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Reddit scraper FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SCRAPER TEST SUITE")
    print("="*70)
    print("This will test both TikTok and Reddit scrapers")
    print("Browser windows will open (set headless=True to hide them)")
    print("="*70)
    
    results = {}
    
    # Test Reddit (easier, should work first)
    print("\n🧪 Test 1/2: Reddit Scraper")
    results['reddit'] = test_reddit()
    
    # Test TikTok
    print("\n🧪 Test 2/2: TikTok Scraper")
    results['tiktok'] = test_tiktok()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Reddit Scraper: {'✅ PASSED' if results['reddit'] else '❌ FAILED'}")
    print(f"TikTok Scraper: {'✅ PASSED' if results['tiktok'] else '❌ FAILED'}")
    print("="*70)
    
    if all(results.values()):
        print("\n🎉 ALL TESTS PASSED! Scrapers are working!")
        print("\nNext steps:")
        print("1. Check the JSON files for data quality")
        print("2. Adjust selectors if needed")
        print("3. Ready to integrate into main system")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure Chrome is installed")
        print("2. Check internet connection")
        print("3. TikTok/Reddit might have changed HTML structure")
        print("4. Review error messages for clues")


if __name__ == "__main__":
    main()
