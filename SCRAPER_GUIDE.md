# 🎯 Scraper System - Setup & Testing Guide

## 📦 What You Got

Based on your Instagram bot architecture, I've built:

### **✅ 3 Scraper Files:**

1. **base_scraper.py** - Foundation class
   - Your anti-detection measures
   - WebDriver management
   - Common scraping patterns
   - Rate limiting

2. **tiktok_scraper.py** - TikTok hashtag scraper
   - Uses your selectors: `#challenge-item-list` and `#column-item-video-container-{n}`
   - Extracts: video_id, username, views, caption
   - Scrolls to load more videos
   - Returns structured data

3. **reddit_scraper.py** - Reddit search scraper
   - Uses old.reddit.com (simple HTML)
   - Extracts: title, author, score, comments
   - No login required
   - Very reliable

### **✅ Test Script:**

4. **test_scrapers.py** - Verify everything works
   - Tests both scrapers
   - Shows you the data structure
   - Saves results to JSON

---

## 🚀 Quick Start (10 Minutes)

### **Step 1: Install Dependencies**

```bash
pip install -r requirements_scrapers.txt
```

This installs:
- Selenium (browser automation)
- BeautifulSoup (HTML parsing)
- WebDriver Manager (auto ChromeDriver)

### **Step 2: Test the Scrapers**

```bash
python test_scrapers.py
```

**What happens:**
- Browser windows open (Chrome)
- Scrapes TikTok #dogecoin (10 videos)
- Scrapes Reddit r/CryptoCurrency for "dogecoin" (10 posts)
- Shows results in terminal
- Saves to JSON files

**Expected output:**
```
✅ SUCCESS! Collected 10 TikTok videos
✅ SUCCESS! Collected 10 Reddit posts
🎉 ALL TESTS PASSED!
```

---

## 📊 Data Structure

### **TikTok Video Data:**

```json
{
  "video_id": "7123456789012345678",
  "username": "cryptoking",
  "video_url": "https://www.tiktok.com/@cryptoking/video/7123456789012345678",
  "caption": "DOGE to the moon! 🚀 #dogecoin",
  "views": 123456,
  "likes": 0,
  "shares": 0,
  "comments": 0,
  "hashtag_searched": "dogecoin",
  "scraped_at": "2025-01-15 10:30:45",
  "container_index": 0
}
```

**Note:** Likes/shares/comments are 0 because they require clicking into each video (slow). We get views from the listing page.

### **Reddit Post Data:**

```json
{
  "post_id": "t3_abc123",
  "post_url": "https://old.reddit.com/r/CryptoCurrency/comments/abc123/doge_discussion/",
  "title": "DOGE to the moon! What do you think?",
  "author": "cryptoenthusiast",
  "score": 456,
  "num_comments": 89,
  "created_utc": "2025-01-15T08:20:30+00:00",
  "subreddit": "CryptoCurrency",
  "flair": "Discussion",
  "is_self": true,
  "query": "dogecoin",
  "scraped_at": "2025-01-15 10:31:00"
}
```

---

## 🔧 Configuration Options

### **Headless Mode (Hide Browser):**

```python
config = {
    'headless': True,  # No visible browser
    'min_delay': 2,
    'max_delay': 5,
}
```

### **Custom Delays:**

```python
config = {
    'min_delay': 1,   # Faster (less polite)
    'max_delay': 3,
}
```

### **Collect More Results:**

```python
# TikTok
videos = scraper.scrape_hashtag('dogecoin', max_results=50)

# Reddit
posts = scraper.scrape_subreddit_search('CryptoCurrency', 'dogecoin', max_results=100)
```

---

## 🎯 Using in Your Project

### **Example: Collect Multiple Coins**

```python
from scrapers.tiktok_scraper import TikTokScraper
from scrapers.reddit_scraper import RedditScraper

coins = ['dogecoin', 'pepe', 'shiba']

# TikTok
tiktok_config = {'headless': True, 'min_delay': 2, 'max_delay': 4}
with TikTokScraper(tiktok_config) as scraper:
    for coin in coins:
        videos = scraper.scrape_hashtag(coin, max_results=20)
        print(f"Collected {len(videos)} TikTok videos for {coin}")

# Reddit
reddit_config = {'headless': True, 'min_delay': 1, 'max_delay': 3}
with RedditScraper(reddit_config) as scraper:
    for coin in coins:
        posts = scraper.scrape_multiple_subreddits(
            subreddits=['CryptoCurrency', 'CryptoMoonShots'],
            query=coin,
            max_per_subreddit=10
        )
        print(f"Collected {len(posts)} Reddit posts for {coin}")
```

---

## 🐛 Troubleshooting

### **"ChromeDriver not found"**

**Fix:**
```bash
pip install webdriver-manager
```

Or manually download ChromeDriver: https://chromedriver.chromium.org/

### **TikTok Returns No Videos**

**Possible causes:**
1. TikTok changed HTML structure (selectors need updating)
2. TikTok blocking automated access
3. Hashtag doesn't exist

**Debug:**
- Set `headless=False` to see what's happening
- Check browser manually navigates to URL
- Look for anti-bot challenges

### **Reddit Returns No Posts**

**Check:**
- Subreddit name correct (no r/ prefix)
- Search query exists in that subreddit
- old.reddit.com is accessible

### **Browser Opens But Nothing Happens**

**Try:**
- Increase timeouts in wait_for_element
- Check internet connection
- Verify website is accessible manually

---

## 🎨 Customization

### **Add More TikTok Data:**

Want likes/shares/comments? Modify `tiktok_scraper.py`:

```python
def get_detailed_metrics(self, video_id):
    """Click into video page to get full metrics"""
    # Navigate to video
    # Extract likes, shares, comments
    # Return detailed data
```

### **Get Reddit Post Body:**

```python
content = scraper.get_post_content(post_url)
print(content['body'])  # Full post text
print(content['top_comments'])  # Top 5 comments
```

### **Add More Subreddits:**

```python
subreddits = [
    'CryptoCurrency',
    'CryptoMoonShots',
    'SatoshiStreetBets',
    'dogecoin',
    'SHIBArmy',
]

posts = scraper.scrape_multiple_subreddits(subreddits, 'pepe', max_per_subreddit=5)
```

---

## 📈 Performance Tips

### **Speed vs Politeness:**

**Fast (risky):**
```python
config = {
    'min_delay': 0.5,
    'max_delay': 1.5,
    'headless': True,
}
```

**Polite (recommended):**
```python
config = {
    'min_delay': 2,
    'max_delay': 5,
    'headless': True,
}
```

### **Batch Collection:**

Collect all at once:
```python
all_data = {
    'tiktok': [],
    'reddit': [],
}

# TikTok batch
with TikTokScraper(config) as scraper:
    for coin in coins:
        all_data['tiktok'].extend(scraper.scrape_hashtag(coin))

# Reddit batch
with RedditScraper(config) as scraper:
    for coin in coins:
        all_data['reddit'].extend(scraper.scrape_subreddit_search('CryptoCurrency', coin))
```

---

## 🔄 Integration with Main System

Next steps (once scrapers are tested):

1. **Create collectors** (like `TikTokCollector`)
   - Wraps scraper
   - Adds virality scoring
   - Matches our data format

2. **Add to config.yaml**
   ```yaml
   data_sources:
     tiktok:
       enabled: true
       method: scraper
     reddit:
       enabled: true
       method: scraper
   ```

3. **Run daily collection**
   - Automated via scheduler
   - Saves to database
   - Feeds into analysis

---

## ✅ Validation Checklist

Before integrating into main system:

- [ ] Test script runs successfully
- [ ] TikTok returns video data
- [ ] Reddit returns post data
- [ ] Data structure looks correct
- [ ] No errors in logs
- [ ] JSON files created
- [ ] Comfortable with how it works

---

## 🎯 Next Actions

### **Immediate (Now):**

1. Run `pip install -r requirements_scrapers.txt`
2. Run `python test_scrapers.py`
3. Check JSON output files
4. Verify data quality

### **Then Tell Me:**

- ✅ Did both scrapers work?
- ⚠️ Any errors or issues?
- 🤔 Do the selectors need adjustment?
- 💡 What data fields are most important?

### **Once Working:**

We'll integrate into your main system:
- Add virality scoring
- Database storage
- Automated collection
- Connect to volatility analysis

---

## 📞 Support

If you hit issues:

1. **Share error messages** - Copy/paste the full error
2. **Check JSON files** - Do they have data?
3. **Try headless=False** - See what browser is doing
4. **Test manually** - Can you access TikTok/Reddit in regular browser?

---

**Ready to test?** Run that test script and let me know what happens! 🚀
