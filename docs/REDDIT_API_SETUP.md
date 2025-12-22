# Reddit API Setup Guide

## Why You Need This

Reddit's API requires authentication (even for reading public posts). The good news: it's **free** and takes **5 minutes** to set up.

## Step-by-Step Setup

### 1. Create a Reddit Account

If you don't have one, create a free Reddit account at https://reddit.com

### 2. Create an App

1. Go to: https://www.reddit.com/prefs/apps
2. Scroll to the bottom
3. Click **"create app"** or **"create another app"**

### 3. Fill Out the Form

```
Name: Memecoin Sentiment Analyzer
App type: script
Description: Portfolio project analyzing crypto sentiment
About url: (leave blank)
Redirect uri: http://localhost:8000
```

4. Click **"create app"**

### 4. Get Your Credentials

You'll see:

```
personal use script
<-- This is your CLIENT_ID (14 character string)

secret
<-- This is your CLIENT_SECRET (27 character string)
```

### 5. Add to .env File

Open/create `.env` in the project root:

```bash
# Reddit API Credentials
REDDIT_CLIENT_ID=your_14_char_client_id_here
REDDIT_CLIENT_SECRET=your_27_char_secret_here
REDDIT_USER_AGENT=MemecoinsAnalyzer/1.0
```

**Example:**
```bash
REDDIT_CLIENT_ID=h3Kd9s2Jf8Ls9d
REDDIT_CLIENT_SECRET=xK3nDk9sL2mF4pQ7tR8vZ3bN5c
REDDIT_USER_AGENT=MemecoinsAnalyzer/1.0
```

### 6. Test It

```bash
python collectors/reddit_praw_collector.py
```

You should see:
```
Initializing PRAW with authenticated access
PRAW initialized (authenticated: True)
Collecting Reddit posts for DOGE (dogecoin)
Collected X unique posts for DOGE
```

## Rate Limits

With authentication:
- **60 requests per minute**
- **600 requests per 10 minutes**

This is plenty for the portfolio project. You can collect data from hundreds of posts per run.

## Troubleshooting

### "received 401 HTTP response"
- Your credentials are wrong or not loaded
- Check `.env` file exists and has correct values
- Make sure no extra spaces or quotes in `.env`

### "received 429 HTTP response" (rate limited)
- You're making too many requests
- Wait 1 minute and try again
- The collector has built-in delays to prevent this

## Security Notes

- **.env is gitignored** - your credentials won't be committed to GitHub
- These are **read-only credentials** - they can't post or comment
- If compromised, just delete the app and create a new one

## Portfolio Benefits

Having Reddit API integration shows:
- API authentication skills
- Working with OAuth-style credentials
- Rate limit handling
- Environment variable management

All valuable for your resume!
