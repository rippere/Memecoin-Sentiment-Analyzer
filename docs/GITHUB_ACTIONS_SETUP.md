# GitHub Actions Setup Guide

## Overview

This project uses GitHub Actions to automatically collect cryptocurrency data:

1. **Price Collection** (`collect-prices.yml`)
   - Runs every hour
   - Collects price data from CoinGecko
   - No credentials needed

2. **Trending Data Collection** (`collect-trending-data.yml`) - NEW!
   - Runs every 3 hours
   - Updates trending coin list
   - Collects Reddit posts and sentiment
   - **Requires Reddit API credentials**

---

## Setting Up Reddit API Credentials

### Step 1: Get Reddit API Credentials

Follow the guide in `docs/REDDIT_API_SETUP.md` to get:
- `REDDIT_CLIENT_ID` (14 characters)
- `REDDIT_CLIENT_SECRET` (27 characters)

This takes about 5 minutes and is completely free.

### Step 2: Add Credentials to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

Add two secrets:

**Secret 1:**
- Name: `REDDIT_CLIENT_ID`
- Value: Your 14-character client ID

Click **Add secret**

**Secret 2:**
- Name: `REDDIT_CLIENT_SECRET`
- Value: Your 27-character secret

Click **Add secret**

### Step 3: Verify Secrets Are Set

You should see two secrets listed:
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`

The values are hidden (this is good for security).

---

## Running the Workflows

### Automatic Runs

Once secrets are set, workflows run automatically:

- **Price collection:** Every hour
- **Trending data:** Every 3 hours

### Manual Runs (For Testing)

1. Go to **Actions** tab in GitHub
2. Select the workflow (e.g., "Collect Trending Data")
3. Click **Run workflow** button
4. Click **Run workflow** to confirm

This triggers an immediate run without waiting for the schedule.

---

## Monitoring Workflows

### Viewing Workflow Runs

1. Go to **Actions** tab
2. See list of recent runs
3. Click any run to see details

### What to Look For

**Successful run:**
- Green checkmark ✓
- All steps completed
- New commit in repository with updated data

**Failed run:**
- Red X ✗
- Check which step failed
- Read error messages

### Common Issues

**"REDDIT_CLIENT_ID not set"**
- Warning shown if secrets not configured
- Reddit collection will be skipped
- Follow Step 2 above to add secrets

**"received 401 HTTP response"**
- Reddit credentials are invalid
- Double-check credentials at https://www.reddit.com/prefs/apps
- Update GitHub secrets with correct values

**"received 429 HTTP response"**
- Rate limit exceeded
- Workflow will succeed on next run
- Consider reducing frequency if persistent

---

## Understanding the Workflow

### What Happens Each Run

```
1. Checkout Code
   ↓
2. Set up Python 3.11
   ↓
3. Install Dependencies
   ↓
4. Create .env with Secrets
   ↓
5. Update Trending Coins
   ↓
6. Collect Reddit Data
   ↓
7. Analyze Sentiment
   ↓
8. Store in Database
   ↓
9. Commit & Push Changes
   ↓
10. Upload Database Backup
```

### Database Updates

After each successful run:
- New commit appears in repository
- Commit message shows statistics
- Database file (`data/memecoin.db`) is updated
- Backup uploaded to Actions artifacts

### Artifacts

Each run uploads the database as an artifact:
- Name: `database-{run_number}`
- Retention: 7 days
- Use this to download database snapshot

To download:
1. Go to workflow run
2. Scroll to **Artifacts** section
3. Click to download ZIP file
4. Extract `memecoin.db`

---

## Free Tier Limits

### GitHub Actions Free Tier

**Personal accounts get:**
- 2,000 minutes/month
- Public repos: unlimited

**Our usage:**
- Price collection: ~12 hours/month
- Trending collection: ~8 hours/month
- **Total: ~20 hours/month** (well under limit)

### API Rate Limits

**Reddit API (authenticated):**
- 60 requests per minute
- 600 requests per 10 minutes
- Our workflow: ~10-20 requests per run
- Running every 3 hours: **safe**

**CoinGecko API (free tier):**
- 50 calls per minute
- Our workflow: ~5 calls per run
- Running every hour: **safe**

---

## Customizing Schedule

Want to run more or less frequently?

Edit `.github/workflows/collect-trending-data.yml`:

```yaml
schedule:
  - cron: '0 */3 * * *'  # Every 3 hours
```

**Common schedules:**

```yaml
# Every hour
- cron: '0 * * * *'

# Every 2 hours
- cron: '0 */2 * * *'

# Every 6 hours
- cron: '0 */6 * * *'

# Every day at 9 AM UTC
- cron: '0 9 * * *'

# Twice daily (9 AM and 9 PM UTC)
- cron: '0 9,21 * * *'
```

Use https://crontab.guru/ to test cron expressions.

---

## Security Best Practices

### Secrets Are Secure

- Secrets never appear in logs
- Only available during workflow execution
- Encrypted by GitHub
- Can't be read by pull requests from forks

### What NOT to Do

❌ Don't commit `.env` file
❌ Don't put credentials in workflow files
❌ Don't print secrets in logs

### What TO Do

✅ Use GitHub Secrets for credentials
✅ Keep `.env` in `.gitignore`
✅ Use `secrets.VARIABLE_NAME` syntax
✅ Use `continue-on-error` for external APIs

---

## Troubleshooting

### Workflow Won't Start

**Check:**
1. Is the workflow enabled? (Actions tab → workflow → enable)
2. Is the schedule correct? (cron syntax)
3. Are there any branch protection rules blocking commits?

**Fix:**
- Manually trigger to test
- Check repository settings

### Commits Not Appearing

**Check:**
1. Are there actual data changes?
2. Is git push succeeding?
3. Any merge conflicts?

**Fix:**
- Check workflow logs for "No changes to commit"
- Look for git push errors
- Pull latest changes locally

### Reddit Collection Fails

**Check:**
1. Are secrets set correctly?
2. Are credentials still valid?
3. Is Reddit API down?

**Fix:**
- Verify secrets in Settings
- Test credentials locally
- Check https://www.redditstatus.com/

---

## Testing Locally

Before relying on GitHub Actions, test locally:

```bash
# 1. Set up .env file
cp .env.example .env
# Edit .env with your credentials

# 2. Run the collection script
python collect_trending_data.py

# 3. Check results
sqlite3 data/memecoin.db "SELECT COUNT(*) FROM reddit_posts"

# 4. If successful, commit and push
git add .github/workflows/collect-trending-data.yml
git commit -m "Add trending data collection workflow"
git push
```

---

## Portfolio Value

Having GitHub Actions automation demonstrates:

- **DevOps Skills** - CI/CD pipeline setup
- **Automation** - Scheduled job orchestration
- **Security** - Proper credential management
- **Monitoring** - Workflow health tracking
- **Production Thinking** - Free tier optimization

This is exactly what employers look for in junior-to-mid level engineers.

---

## Next Steps

After setting up:

1. **Add Reddit secrets** (required)
2. **Trigger manual run** (test it works)
3. **Wait for scheduled run** (verify automation)
4. **Monitor for 24 hours** (ensure stability)
5. **Update README** (mention automated collection)

Once stable, you can confidently say on your resume:

> "Implemented automated data collection pipeline using GitHub Actions, processing 500+ social media posts daily with sentiment analysis"

---

## Questions?

Common questions answered:

**Q: Will this use all my free tier minutes?**
A: No, only ~20 hours/month out of 2,000 available.

**Q: Can I pause data collection?**
A: Yes, disable the workflow in Actions tab.

**Q: What if I don't have Reddit credentials?**
A: Price collection still works. Trending updates work. Just Reddit posts skipped.

**Q: How do I download the database?**
A: Go to Actions → workflow run → Artifacts → download ZIP.

**Q: Can I run this more frequently?**
A: Yes, but watch rate limits. Every 2 hours is safe.

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Schedule Helper](https://crontab.guru/)
- [Reddit API Status](https://www.redditstatus.com/)
- [GitHub Actions Free Tier](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions)
