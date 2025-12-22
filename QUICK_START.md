# Quick Start - Automated Data Collection

Get your data collection pipeline running in **10 minutes**.

---

## Prerequisites

- GitHub account (you have this)
- Reddit account (free - create at reddit.com)

---

## Step 1: Get Reddit API Credentials (5 minutes)

### Create Reddit App

1. Go to: https://www.reddit.com/prefs/apps
2. Scroll to bottom, click **"create app"**
3. Fill in:
   - **Name:** Memecoin Sentiment Analyzer
   - **Type:** script
   - **Redirect URI:** http://localhost:8000
4. Click **"create app"**

### Copy Credentials

You'll see:
```
personal use script
abc123xyz456...  <-- This is your CLIENT_ID

secret
xyz789abc123def456...  <-- This is your CLIENT_SECRET
```

**Save these!** You'll need them in the next step.

---

## Step 2: Add to GitHub Secrets (2 minutes)

### In Your GitHub Repository

1. Go to: **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**

### Add First Secret

- **Name:** `REDDIT_CLIENT_ID`
- **Secret:** (paste your CLIENT_ID)
- Click **"Add secret"**

### Add Second Secret

- **Name:** `REDDIT_CLIENT_SECRET`
- **Secret:** (paste your CLIENT_SECRET)
- Click **"Add secret"**

---

## Step 3: Test the Workflow (3 minutes)

### Trigger Manual Run

1. Go to **Actions** tab
2. Click **"Collect Trending Data"** (left sidebar)
3. Click **"Run workflow"** button (right side)
4. Click **"Run workflow"** to confirm

### Watch It Run

- Takes ~2-3 minutes
- Watch the progress in real-time
- Green checkmark ✓ = success!

### Verify Results

After successful run:
- New commit will appear in repository
- Commit message shows statistics
- Database updated with Reddit posts

---

## You're Done!

### What Happens Now

Every 3 hours, automatically:
1. Updates trending coin list
2. Collects Reddit posts
3. Analyzes sentiment
4. Stores in database
5. Commits results

### Check Automation

Come back in 3 hours and check:
- Actions tab shows new run
- New commit in repository
- Data is growing

---

## Test Locally (Optional)

Want to run on your computer?

```bash
# 1. Clone the repo (if you haven't)
git clone https://github.com/rippere/Memecoin-Sentiment-Analyzer.git
cd Memecoin-Sentiment-Analyzer

# 2. Set up environment
cp .env.example .env
# Edit .env with your Reddit credentials

# 3. Install dependencies
pip install -r requirements_scrapers.txt

# 4. Run collection
python collect_trending_data.py

# 5. Check results
sqlite3 data/memecoin.db "SELECT COUNT(*) FROM reddit_posts"
```

---

## What You Get

### Automated Data Collection

- **Prices:** Every hour from CoinGecko
- **Trending coins:** Updated every 3 hours
- **Reddit posts:** 50+ per coin per run
- **Sentiment scores:** VADER analysis for each post

### Database

Located at `data/memecoin.db`:
- Coins table with trending status
- Price history
- Reddit posts
- Sentiment scores
- Trending history

### Portfolio Value

You can now say:

> "Built automated data collection pipeline using GitHub Actions, processing 500+ social media posts daily with NLP sentiment analysis"

---

## Need Help?

### Detailed Guides

- Reddit API setup: `docs/REDDIT_API_SETUP.md`
- GitHub Actions: `docs/GITHUB_ACTIONS_SETUP.md`
- Week 1 progress: `WEEK1_PROGRESS.md`

### Common Issues

**No Reddit credentials warning:**
- Double-check secret names (exact match required)
- Make sure you clicked "Add secret"

**401 Unauthorized:**
- Reddit credentials are incorrect
- Go back to https://www.reddit.com/prefs/apps
- Verify CLIENT_ID and SECRET
- Update GitHub secrets

**Workflow won't start:**
- Make sure workflow file is committed to main branch
- Check Actions are enabled (Settings → Actions → Allow all actions)

---

## Next Steps

Once automation is running:

1. **Monitor for 24 hours** - Verify stability
2. **Dashboard integration** - Show data in frontend
3. **Additional sources** - Add TikTok collector
4. **Analytics** - Build sentiment trends visualization
5. **Deploy** - Put live on Vercel

Week 2 awaits!

---

**Most Important:** This entire setup is **free**. No credit card needed for:
- Reddit API ✓
- GitHub Actions ✓ (2,000 minutes/month free)
- CoinGecko API ✓

Perfect for a portfolio project.
