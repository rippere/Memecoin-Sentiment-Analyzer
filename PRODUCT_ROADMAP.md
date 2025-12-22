# Memecoin Sentiment Analyzer - Realistic Product Roadmap

**Last Updated:** 2025-12-22
**Status:** Product Definition Phase

---

## Executive Summary

**The Hard Question:** Does social media sentiment actually predict memecoin price movements with statistical significance?

**The Reality:** Most crypto sentiment projects fail because:
- Correlation ≠ Causation
- Social sentiment often FOLLOWS price (not leads)
- Market manipulation is rampant
- Data quality is poor
- API limits make comprehensive collection expensive

**Our Approach:** Start with validation, not features. Prove the concept works BEFORE building a product.

---

## Product Vision

### What We're Building
A **research tool** that quantifies the relationship (if any) between social media sentiment and memecoin price movements, enabling data-driven insights for crypto traders and researchers.

### What We're NOT Building
- ❌ Trading bot or automated trading system
- ❌ Investment advice platform (legal issues)
- ❌ Real-time alert system (Phase 1)
- ❌ Mobile app (too early)
- ❌ Social media competitor

### Target Users
1. **Crypto traders** (discretionary, not algo)
2. **Researchers** studying market psychology
3. **Ourselves** (learning data science + crypto)

### Success Criteria
The project is successful if we can answer:
> "Given social sentiment score X for coin Y, what is the probability of price movement Z in the next N hours?"

With **statistical confidence (p < 0.05)** backed by historical data.

---

## The Core Hypothesis (Must Validate)

### Primary Hypothesis
**H1:** Social media sentiment spikes PRECEDE price movements in memecoins by 2-24 hours.

### Alternative Hypotheses
- **H2:** Sentiment FOLLOWS price (people react to pumps)
- **H3:** No correlation exists (random walk)
- **H4:** Correlation exists but is NOT actionable (too noisy)

### Validation Required
**We cannot build features until we prove H1 or pivot based on H2/H3/H4.**

---

## Critical Challenges & Realistic Constraints

### Data Quality Issues
| Challenge | Impact | Mitigation |
|-----------|--------|------------|
| Bot/spam posts | False signals | Bot detection ML model |
| Small sample size | Low confidence | Focus on top 10-20 coins only |
| Missing historical data | Can't backtest old cycles | Accept limitation, focus on forward testing |
| Platform rate limits | Incomplete data | Strategic sampling, paid APIs |

### Technical Challenges
| Challenge | Reality Check | Decision |
|-----------|---------------|----------|
| TikTok scraping unstable | Will break frequently | Use as secondary source only |
| Reddit API limits | 60 req/min | Focus on top subreddits |
| Twitter API costs | $100-5000/month | Delay or use free tier strategically |
| Real-time processing | Complex infrastructure | Start with batch (hourly) |

### Statistical Challenges
| Issue | Implication | Solution |
|-------|-------------|----------|
| Multiple testing problem | False positives | Bonferroni correction |
| Survivorship bias | Over-optimistic results | Include failed coins |
| Non-stationarity | Correlations change over time | Rolling windows, regime detection |
| Confounding variables | False causation | Control for market-wide movements (BTC) |

---

## Minimum Viable Product (MVP)

### MVP Definition
**Goal:** Answer the core hypothesis with ONE coin and ONE platform.

**Scope:**
- Track **DOGE** only (highest volume, most social data)
- Collect **Reddit** only (r/dogecoin, r/CryptoCurrency)
- Historical timeframe: **90 days** of data
- Analysis: **Simple time-lagged correlation**
- Output: **Statistical report + charts**

### MVP Success Criteria
1. ✅ Collect 10,000+ Reddit posts about DOGE
2. ✅ Match with hourly price data (OHLCV)
3. ✅ Calculate sentiment scores (VADER baseline)
4. ✅ Run correlation analysis at lags: 1h, 6h, 12h, 24h
5. ✅ Find **p < 0.05** correlation at ANY lag
6. ✅ Visualize results clearly

### MVP Go/No-Go Decision
**IF p < 0.05:** Expand to more coins/platforms (Phase 2)
**IF p > 0.05:** Pivot or investigate why (H2/H3 analysis)

**Timeline:** 2-3 weeks of focused work

---

## Development Phases

### Phase 0: Validation Sprint (2-3 weeks) ⚠️ CRITICAL
**Goal:** Prove or disprove the core hypothesis with MVP.

**Week 1: Data Collection**
- [ ] Fix Reddit collector (PRAW, proper rate limiting)
- [ ] Collect 90 days historical data for DOGE
- [ ] Validate data quality (dedupe, filter bots)
- [ ] Get historical price data from CoinGecko
- **Deliverable:** Clean dataset ready for analysis

**Week 2: Sentiment Analysis**
- [ ] Implement VADER sentiment scoring
- [ ] Calculate hourly sentiment aggregates
- [ ] Validate sentiment manually (sample 100 posts)
- [ ] Store in database with proper indexing
- **Deliverable:** Sentiment time series

**Week 3: Correlation Analysis**
- [ ] Time-lagged correlation (1-24 hour lags)
- [ ] Statistical tests (Pearson, Spearman, Granger causality)
- [ ] Control for confounders (BTC price, market cap)
- [ ] Visualization (scatter plots, time series overlay)
- **Deliverable:** Research report with findings

**Decision Gate:**
- ✅ **IF significant correlation found:** Proceed to Phase 1
- ❌ **IF no correlation:** Investigate H2/H3, pivot, or conclude

---

### Phase 1: Multi-Coin Validation (3-4 weeks)
**Goal:** Validate findings across top 5-10 memecoins.

**Only proceed if Phase 0 shows promise.**

**Scope:**
- Expand to: SHIB, PEPE, FLOKI, BONK, WIF
- Same methodology as Phase 0
- Look for consistent patterns

**Questions to Answer:**
- Do all memecoins show similar lag times?
- Are some coins more predictable?
- Does market cap affect correlation strength?

**Deliverable:** Comparative analysis report

**Decision Gate:**
- ✅ **IF consistent patterns:** Build production system (Phase 2)
- ⚠️ **IF inconsistent:** Refine methodology or pivot

---

### Phase 2: Production Data Pipeline (4-6 weeks)
**Goal:** Automated, reliable data collection at scale.

**Prerequisites:**
- Phase 0 AND Phase 1 validated
- Clear value proposition identified

**Components:**
1. **Robust Collectors**
   - Reddit (PRAW with retry logic)
   - Twitter (if budget allows, or free tier strategically)
   - TikTok (supplementary, not primary)

2. **Data Quality Pipeline**
   - Bot detection (engagement ratios, posting patterns)
   - Spam filtering (keyword blacklists)
   - Deduplication
   - Quality scoring per post

3. **Sentiment Engine**
   - VADER baseline
   - Crypto-specific lexicon additions
   - Ensemble with FinBERT (optional)
   - Hype metrics (emojis, CAPS, !!! density)

4. **Storage & Indexing**
   - Optimized database schema
   - Time-series indexes
   - Archival strategy for old data

5. **Monitoring**
   - Collection health dashboard
   - Data quality metrics
   - API quota tracking
   - Error alerting

**Deliverable:** Production-grade data pipeline

**Success Metrics:**
- 99% uptime for collectors
- <5% spam/bot rate
- Data available within 15 min of posting
- Cost < $100/month (API fees)

---

### Phase 3: Correlation Engine & Backtesting (3-4 weeks)
**Goal:** Operationalize the correlation analysis.

**Components:**
1. **Correlation Calculator**
   - Rolling window analysis
   - Multiple lag testing
   - Confidence intervals
   - Change detection (regime shifts)

2. **Backtesting Framework**
   - Strategy definition DSL
   - Historical replay engine
   - Performance metrics (Sharpe, max drawdown)
   - Risk analysis

3. **Strategy Library**
   - Sentiment momentum (buy on positive spikes)
   - Contrarian (fade extreme sentiment)
   - Volume confirmation (sentiment + volume spike)

4. **Validation**
   - Walk-forward testing
   - Out-of-sample validation
   - Monte Carlo simulations

**Deliverable:** Backtested strategies with performance reports

**Success Metrics:**
- At least ONE strategy with Sharpe > 1.0
- Consistent performance across multiple test periods
- Maximum drawdown < 30%

---

### Phase 4: Dashboard & Insights (3-4 weeks)
**Goal:** Make insights accessible and actionable.

**Only if Phases 0-3 show viable strategies.**

**Features:**
1. **Overview Dashboard**
   - Current top trending coins
   - Sentiment heatmap
   - Recent alerts (sentiment spikes)

2. **Coin Detail Pages**
   - Price chart with sentiment overlay
   - Historical correlation metrics
   - Social volume trends
   - Top posts/videos

3. **Analysis Tools**
   - Correlation explorer
   - Backtest results viewer
   - Strategy comparisons

4. **Alerts (Simple)**
   - Email notifications
   - Sentiment threshold alerts
   - No real-time (too complex for Phase 4)

**Technology:**
- Next.js frontend (existing)
- FastAPI backend (existing)
- PostgreSQL (migrate from SQLite)
- Redis for caching
- Simple deployment (Vercel + Railway or similar)

**Deliverable:** Functional web dashboard

---

### Phase 5: Advanced Features (Ongoing)
**Only if Phase 4 is being actively used and provides value.**

**Potential Features:**
- Real-time WebSocket updates
- Influencer tracking (whale wallets, Twitter influencers)
- News integration (CoinDesk, CryptoSlate)
- Advanced ML models (LSTM for predictions)
- Community features (sharing strategies)
- Mobile app
- API for third-party integrations

**Monetization Options (if applicable):**
- Premium API access ($50-200/month)
- Advanced analytics subscription
- White-label for trading groups
- Research reports
- **Free tier** for basic features (community building)

---

## Technical Architecture

### Current State Assessment

**✅ Good:**
- Database schema is reasonable
- Trending coin rotation is smart
- GitHub Actions automation works
- Basic collectors exist

**❌ Needs Fixing:**
- Mixed database patterns (raw sqlite3 + SQLAlchemy) → Standardize on SQLAlchemy
- No testing framework → Implement pytest
- Scattered scripts → Consolidate
- SQLite for production → Migrate to PostgreSQL before Phase 2
- No logging strategy → Structured logging with log aggregation
- Frontend in git (node_modules) → Already fixed with .gitignore

### Target Architecture (Phase 2+)

```
┌─────────────────────────────────────────────┐
│          Data Collection Layer              │
├─────────────────────────────────────────────┤
│ Reddit    │ Twitter   │ TikTok   │ News    │
│ Collector │ Collector │ Collector│Scraper  │
└────┬──────┴─────┬─────┴────┬─────┴────┬────┘
     │            │          │          │
     └────────────┴──────────┴──────────┘
                    │
          ┌─────────▼──────────┐
          │  Data Quality      │
          │  Pipeline          │
          │ (Bot Filter, Dedupe)│
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │  Sentiment Engine  │
          │  (VADER + Custom)  │
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │   PostgreSQL DB    │
          │  (Time-series opt) │
          └─────────┬──────────┘
                    │
     ┌──────────────┴──────────────┐
     │                             │
┌────▼─────┐              ┌───────▼────────┐
│Correlation│              │   FastAPI      │
│ Engine   │              │   Backend      │
│(Analysis)│              │  (Dashboard)   │
└────┬─────┘              └───────┬────────┘
     │                            │
     │                    ┌───────▼────────┐
     │                    │   Next.js      │
     │                    │   Frontend     │
     └────────────────────┴────────────────┘
```

### Technology Stack Decisions

| Component | Current | Target (Phase 2+) | Reasoning |
|-----------|---------|-------------------|-----------|
| Database | SQLite | PostgreSQL | Time-series performance, production-ready |
| API Framework | FastAPI | FastAPI | Keep, it's good |
| Frontend | Next.js | Next.js | Keep, modern and fast |
| Sentiment | VADER | VADER + FinBERT | Start simple, add complexity if needed |
| Deployment | Local | Cloud (Railway/Fly.io) | Free tier sufficient initially |
| Monitoring | None | Sentry + Grafana | Essential for production |
| Testing | None | pytest + coverage | Non-negotiable |
| **Schedulers** | **Manual** | **GitHub Actions / Cloud Cron** | **No always-on needed** |

### Deployment Strategy: Cloud-Scheduled (No Always-On Required)

**Key Principle:** Use scheduled cloud runners instead of always-on servers until Phase 4+.

#### Phase 0-1: GitHub Actions (Free)

**Perfect for MVP validation:**
```yaml
# .github/workflows/collect-data.yml
name: Collect Data
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run collector
        run: python collectors/reddit_collector.py
      - name: Commit data
        run: |
          git config user.name "bot"
          git add data/
          git commit -m "Data: $(date)" || exit 0
          git push
```

**Benefits:**
- ✅ 2,000 minutes/month free (enough for MVP)
- ✅ No infrastructure management
- ✅ Already using this for price collection
- ✅ Data committed to git (simple backup)
- ❌ Limited to ~200 runs/month if each takes 10 min

**Good for:** Phase 0-1 validation with infrequent collection (every 6-12 hours)

#### Phase 2: Cloud Functions + Managed Cron

**When GitHub Actions limits are reached:**

**Option A: Railway Cron Jobs (Free tier: $5 credit/month)**
```yaml
# railway.yml
services:
  reddit-collector:
    schedule: "0 */2 * * *"  # Every 2 hours
    command: python collectors/reddit_collector.py

  sentiment-processor:
    schedule: "30 */4 * * *"  # Every 4 hours, offset
    command: python processors/sentiment_analyzer.py
```

**Option B: Google Cloud Functions + Cloud Scheduler**
- Free tier: 2M invocations/month
- Pay per execution (fractions of a cent)
- Scales to zero when not running

**Option C: AWS Lambda + EventBridge**
- Free tier: 1M requests/month
- Similar to GCP, pay per use
- Generous free tier

**Cost Comparison:**
| Service | Free Tier | Cost After Free |
|---------|-----------|-----------------|
| GitHub Actions | 2,000 min/mo | $0.008/min |
| Railway | $5 credit/mo | $0.000463/GB-s |
| GCP Functions | 2M calls/mo | $0.40/M calls |
| AWS Lambda | 1M calls/mo | $0.20/M calls |
| Render Cron | 750 hours/mo | $7/mo (always-on) |

**Recommendation Phase 2:**
- Start: GitHub Actions (already working)
- If limits hit: Railway Cron (simple migration)
- If scaling needed: GCP Functions (most generous free tier)

#### Phase 3-4: Hybrid Approach

**Data Collection:** Cloud scheduled (as above)
**Dashboard/API:** Managed hosting
  - Frontend: Vercel (Next.js) - Free tier
  - Backend: Railway/Fly.io - Free tier or $5/mo
  - Database: Supabase/Neon PostgreSQL - Free tier

**Architecture:**
```
GitHub Actions (every 2 hours)
    ↓
Collect & Process Data
    ↓
PostgreSQL (Supabase free tier)
    ↓
FastAPI (Railway, scales to zero)
    ↓
Next.js (Vercel, edge deployment)
```

**No always-on servers needed until real-time features (Phase 5+)**

#### Phase 5+: Real-Time Requirements

**Only when adding:**
- Live WebSocket updates
- Sub-minute data collection
- Real-time alerts

**Then consider:**
- Single VPS (Hetzner: $5/mo, Linode: $5/mo)
- Or scale managed services (Railway Pro: $20/mo)

#### Deployment Timeline

| Phase | Collection Frequency | Solution | Cost |
|-------|---------------------|----------|------|
| 0-1 | Every 6-12 hours | GitHub Actions | $0 |
| 2 | Every 2-4 hours | GitHub Actions or Railway Cron | $0-5/mo |
| 3 | Every 1-2 hours | Railway Cron + Supabase | $0-10/mo |
| 4 | Every 30-60 min | GCP Functions or Railway | $5-20/mo |
| 5+ | Real-time (< 5 min) | VPS or managed platform | $20-50/mo |

**No need for always-on infrastructure until Phase 5.**

---

## Resource & Cost Analysis

### Time Investment
- **Phase 0 (MVP):** 40-60 hours
- **Phase 1 (Multi-coin):** 40-60 hours
- **Phase 2 (Production pipeline):** 80-120 hours
- **Phase 3 (Backtesting):** 60-80 hours
- **Phase 4 (Dashboard):** 60-80 hours

**Total to "working product":** 280-400 hours (~3-5 months part-time)

### Financial Costs
| Service | Free Tier | Paid Need | Cost |
|---------|-----------|-----------|------|
| **Data Collection Scheduling** | **GitHub Actions** | **Phase 2-3** | **$0-10/mo** |
| CoinGecko API | 30 calls/min | Maybe Phase 2 | $0-129/mo |
| Twitter API | Limited | Likely Phase 1 | $100-5000/mo |
| Reddit API | 60 req/min | Sufficient | $0 |
| Hosting (Frontend) | Vercel free | Phase 4+ | $0-20/mo |
| Hosting (Backend) | Railway free | Phase 4+ | $0-10/mo |
| Database | SQLite local | PostgreSQL (Supabase) Phase 2 | $0-10/mo |
| Monitoring | Open source | Optional Phase 3+ | $0-20/mo |

**Total Phase 0-1:** $0 (GitHub Actions free tier sufficient)
**Total Phase 2-3:** $0-20/month (still on free tiers, skip Twitter)
**Total Phase 4:** $20-50/month (managed hosting + DB)
**Total with Twitter API:** +$100-5000/month (ONLY if needed)

### Alternative: Skip Twitter
- Focus on Reddit + TikTok (free)
- Reduces costs to near-$0
- May reduce data quality
- Decision point: Phase 1 results

---

## Risk Assessment & Mitigation

### Project-Killing Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| No correlation exists | 40% | Fatal | Phase 0 validates early |
| API costs too high | 30% | High | Skip Twitter, use free sources |
| Data quality too poor | 25% | High | Bot detection, manual validation |
| Scrapers keep breaking | 50% | Medium | Use APIs where possible, monitoring |
| Legal/compliance issues | 10% | Fatal | Disclaimer, no investment advice |
| Market regime change | 30% | Medium | Continuous revalidation |

### Technical Risks

| Risk | Mitigation |
|------|------------|
| SQLite performance limits | Migrate to PostgreSQL Phase 2 |
| No automated tests | Implement pytest from Phase 0 |
| Complex deployment | Use managed services (Railway, Fly.io) |
| Data loss | Automated backups, git for code |

---

## Decision Framework

### Phase Gates (Go/No-Go)

**Phase 0 → Phase 1:**
- ✅ Statistically significant correlation found (p < 0.05)
- ✅ Methodology is sound (no obvious flaws)
- ✅ Data quality is acceptable (>80% clean)
- ❌ If NO: Investigate H2/H3, pivot or stop

**Phase 1 → Phase 2:**
- ✅ Consistent patterns across multiple coins
- ✅ Actionable lag times identified
- ✅ Cost analysis shows Phase 2 is affordable
- ❌ If NO: Conclude research, publish findings

**Phase 2 → Phase 3:**
- ✅ Data pipeline is stable (99% uptime)
- ✅ Data quality metrics are good
- ✅ Costs are within budget
- ❌ If NO: Fix issues before proceeding

**Phase 3 → Phase 4:**
- ✅ At least ONE viable strategy found
- ✅ Backtest results are convincing
- ✅ Clear value proposition for users
- ❌ If NO: Stop at research tool, don't build dashboard

**Phase 4 → Phase 5:**
- ✅ Dashboard has active users
- ✅ Positive feedback from users
- ✅ Clear path to sustainability/monetization
- ❌ If NO: Maintain at Phase 4 level

---

## Validation Experiments (Before Full Build)

### Experiment 1: Manual Correlation Test (1 week)
**Question:** Does sentiment predict DOGE price?

**Method:**
1. Download 1 month of r/dogecoin posts (free)
2. Manually score 100 posts (positive/negative/neutral)
3. Compare to DOGE price that day
4. Visual inspection: any patterns?

**Cost:** $0, ~10 hours
**Decision:** If YES → Build automation. If NO → Stop.

### Experiment 2: Bot Detection Test (3 days)
**Question:** How much Reddit data is bots/spam?

**Method:**
1. Sample 200 random posts
2. Manually classify (human/bot/spam)
3. Calculate percentage
4. Identify detection patterns

**Decision:** If >30% bots → Need detection before Phase 0

### Experiment 3: TikTok Scraper Reliability (1 week)
**Question:** Is TikTok worth the scraping hassle?

**Method:**
1. Run scraper daily for 7 days
2. Track: success rate, data volume, unique videos
3. Compare to Reddit data volume

**Decision:** If <70% success rate → Skip TikTok for MVP

---

## Success Metrics (Measurable)

### Phase 0 Success
- [ ] 10,000+ Reddit posts collected
- [ ] 90 days of DOGE price data aligned
- [ ] Correlation coefficient |r| > 0.3
- [ ] p-value < 0.05
- [ ] Report documenting findings

### Phase 1 Success
- [ ] Analysis complete for 5+ coins
- [ ] At least 3/5 show significant correlation
- [ ] Lag times consistent across coins
- [ ] Methodology documented

### Phase 2 Success
- [ ] Data collection automated
- [ ] 99% uptime for 30 days
- [ ] <5% bad data rate
- [ ] Costs within budget

### Phase 3 Success
- [ ] Backtesting framework working
- [ ] 1+ strategy with Sharpe > 1.0
- [ ] Performance consistent across test periods

### Phase 4 Success
- [ ] Dashboard deployed and accessible
- [ ] Load time < 2 seconds
- [ ] Mobile responsive
- [ ] 10+ active users testing

---

## What "Done" Looks Like

### Minimal "Done" (Research Tool)
After Phase 0-1, if correlations exist:
- Published research report
- GitHub repo with findings
- Reproducible analysis
- **Value:** Educational, portfolio piece

### Full "Done" (Production Tool)
After Phase 2-4:
- Web dashboard showing live sentiment
- Historical correlation data
- Backtested strategies
- Documentation for users
- **Value:** Usable tool for traders/researchers

### Ambitious "Done" (Product)
After Phase 5:
- Real-time alerts
- Mobile app
- Community features
- Monetized (if viable)
- **Value:** Sustainable product

---

## Recommended Immediate Actions

### This Week
1. **Run Experiment 1** (Manual correlation test)
   - Download r/dogecoin posts (1 month)
   - Manual sentiment scoring
   - Visual correlation check
   - **Decision:** Continue or pivot?

2. **Fix Technical Debt**
   - Consolidate DB access (all SQLAlchemy)
   - Set up pytest
   - Clean up test scripts

3. **Plan Phase 0 Properly**
   - Use Gemini to create detailed Phase 0 plan
   - Break into daily tasks
   - Set realistic timeline

### Next 2 Weeks
- Complete Phase 0 validation sprint
- Make go/no-go decision
- If GO: Plan Phase 1 with Gemini
- If NO-GO: Document learnings, pivot or conclude

---

## Open Questions to Resolve

1. **Is sentiment leading or lagging price?**
   - Need: Granger causality test in Phase 0

2. **What's the optimal lag time?**
   - Need: Test 1h, 2h, 4h, 6h, 12h, 24h lags

3. **Does it vary by coin?**
   - Need: Phase 1 multi-coin validation

4. **Is the effect real or noise?**
   - Need: Proper statistical controls

5. **Can we build a trading strategy?**
   - Need: Phase 3 backtesting

6. **Would anyone use this?**
   - Need: User research, MVP testing

---

## Conclusion

### The Honest Assessment

This project has value **IF** the core hypothesis proves true. But there's a 40-50% chance it doesn't, and that's okay.

The right approach:
1. **Validate cheaply** (Phase 0)
2. **Decide quickly** (go/no-go)
3. **Build incrementally** (only if validated)
4. **Stay realistic** (don't over-engineer)

### The Path Forward

**Start here:**
- Run manual correlation experiment (1 week)
- If promising → Build Phase 0 MVP (2-3 weeks)
- If validated → Expand systematically

**Don't:**
- Build features before validation
- Over-engineer the architecture
- Assume correlations exist
- Skip testing and quality gates

---

**Remember:** The goal is to learn if this works, not to build a massive system that might be useless.

**Validate first, build second.**
