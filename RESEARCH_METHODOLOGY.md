# Research Methodology & Statistical Validity Analysis
## Meme Coin Sentiment Analysis Project

---

## Executive Summary

This document outlines what can be **proven**, what can be **suggested**, and what **cannot be concluded** from the current dataset, along with improvements needed for statistically significant findings.

---

## Part 1: Testable Hypotheses

### Primary Hypothesis
**"Social media sentiment/hype predicts short-term meme coin price movements"**

#### Sub-Hypotheses (Testable):

1. **H1: Lead Time Hypothesis**
   - "Increases in social media volume precede price increases by X hours/days"
   - **Testable with:** Time-lagged correlation analysis (0-7 day lags)
   - **Metric:** Pearson/Spearman correlation coefficient
   - **Required data:** 30+ days minimum, 90+ days ideal

2. **H2: Sentiment Direction Hypothesis**
   - "Positive sentiment correlates with upward price movement"
   - **Testable with:** Regression analysis (sentiment score vs price change)
   - **Metric:** R² value, p-value < 0.05
   - **Required data:** 500+ data points per coin

3. **H3: Hype Threshold Hypothesis**
   - "Price pumps occur when hype score exceeds threshold X"
   - **Testable with:** Binary classification, ROC/AUC analysis
   - **Metric:** Precision, recall, F1-score
   - **Required data:** At least 20 "pump events" per coin

4. **H4: Volume-Price Correlation**
   - "Social media post volume correlates with trading volume"
   - **Testable with:** Multivariate regression
   - **Metric:** Correlation coefficient, Granger causality test
   - **Required data:** 60+ days with consistent sampling

5. **H5: Platform-Specific Effects**
   - "Reddit sentiment has different predictive power than TikTok"
   - **Testable with:** Comparative analysis, A/B testing
   - **Metric:** Comparative R² values
   - **Required data:** 90+ days from both platforms

6. **H6: Influencer Impact**
   - "Posts from high-follower accounts have greater price impact"
   - **Testable with:** Weighted sentiment analysis
   - **Metric:** Effect size comparison
   - **Required data:** Follower counts (currently not collected)

---

## Part 2: What Can Be Extracted from Current Data

### Tier 1: Highly Reliable Findings (With 60+ Days Data)

#### A. Correlation Metrics
**What you CAN prove:**
- Pearson/Spearman correlation coefficients between:
  - Social volume ↔ Price change (24h, 7d)
  - Sentiment score ↔ Price direction
  - Hype score ↔ Volatility
  - Reddit engagement ↔ TikTok engagement

**Statistical methods:**
```python
from scipy.stats import pearsonr, spearmanr
correlation, p_value = pearsonr(sentiment_scores, price_changes)
# Valid if p < 0.05 and n > 30
```

**Interpretation:**
- r > 0.7: Strong correlation (rare in social data)
- r = 0.3-0.7: Moderate correlation (realistic expectation)
- r < 0.3: Weak correlation (still publishable if consistent)
- p < 0.05: Statistically significant

#### B. Lead/Lag Analysis
**What you CAN prove:**
- Optimal lag time between social spike and price movement
- Whether social leads or follows price

**Method:** Cross-correlation with time lags
```python
from statsmodels.tsa.stattools import ccf
cross_corr = ccf(social_volume, price_change, adjusted=False)
optimal_lag = np.argmax(cross_corr)  # Days social leads/lags price
```

**Interpretation:**
- Positive lag: Social predicts price (Holy Grail!)
- Zero lag: Simultaneous movement (still valuable)
- Negative lag: Price predicts social (less useful)

#### C. Volatility Prediction
**What you CAN prove:**
- Social spikes predict increased volatility (easier than direction)
- Hype threshold for "significant events"

**Method:** GARCH models, variance analysis
```python
from arch import arch_model
# Test if social volume predicts price variance
```

**Practical use:**
- Trading signals: "High social activity = expect volatility"
- Risk management: Avoid positions during hype spikes

### Tier 2: Moderate Reliability (Requires 90+ Days)

#### D. Directional Prediction
**What you MIGHT prove:**
- Positive sentiment → upward price movement (next 24-72h)
- Negative sentiment → downward price movement

**Challenges:**
- Meme coins are highly manipulated
- Sentiment often follows price (not leads)
- External factors (BTC movements, regulations)

**Required improvements:**
- Control for Bitcoin price movements
- Account for market-wide sentiment
- Filter bot/spam accounts
- Weight by account credibility

#### E. Platform Comparison
**What you CAN show:**
- Which platform (Reddit/TikTok) has stronger correlation
- Platform-specific hype patterns
- Demographic differences in sentiment

**Method:** Comparative regression
```python
model_reddit = LinearRegression()
model_tiktok = LinearRegression()
# Compare R² values
```

**Findings might show:**
- "TikTok hype predicts retail FOMO pumps"
- "Reddit sentiment aligns with 'smart money'"
- "Cross-platform agreement = stronger signal"

### Tier 3: Exploratory Insights (Qualitative)

#### F. Narrative Analysis
**What you CAN identify:**
- Common themes during pumps vs dumps
- Viral meme effectiveness
- Influencer narrative patterns
- Community growth dynamics

**Method:** NLP topic modeling, keyword extraction
```python
from sklearn.decomposition import LatentDirichletAllocation
# Extract topics from high-hype periods
```

**Business value:**
- Understand "what makes memes go viral"
- Identify early warning signs
- Detect coordinated pump schemes

#### G. Anomaly Detection
**What you CAN detect:**
- Unusual social activity spikes
- Coordinated bot behavior
- Pump-and-dump schemes
- Manipulation attempts

**Method:** Statistical outlier detection
```python
from sklearn.ensemble import IsolationForest
# Detect abnormal social patterns
```

**Use cases:**
- Fraud detection
- Risk flagging
- Market manipulation research

---

## Part 3: Current Limitations & Improvements Needed

### Critical Limitations

#### 1. **Sample Size Constraints**

**Current state:**
- Starting with 0 data points
- Need 30+ days minimum for any analysis
- Need 90+ days for robust findings

**Problem:**
- Small sample size = high variance
- Early correlations may be spurious
- Not enough "pump events" to validate

**Solution:**
```
Week 1-4:   Data collection only (no analysis)
Week 5-8:   Preliminary correlations (exploratory)
Week 9-12:  First statistical tests (30 days)
Week 13+:   Robust analysis, backtesting
```

#### 2. **Temporal Resolution Issues**

**Current collection:** Every 30 minutes
**Problem:** May miss rapid pumps (happen in minutes)

**Improvement needed:**
- Price collection: Every 5-15 minutes
- Social collection: Maintain 30-60 min (scraping limits)
- Store precise timestamps (currently UTC)

**Impact:**
- Better capture of intraday movements
- More granular lead/lag analysis
- Real-time alert possibility

#### 3. **Selection Bias**

**Current state:** 23 meme coins chosen subjectively
**Problems:**
- Survivorship bias (only tracking "successful" coins)
- Missing failed coins that also had hype
- Not representative of all meme coins

**Improvement needed:**
```yaml
# Add to coins.yaml
tier_1_coins: [DOGE, SHIB, PEPE]  # Established
tier_2_coins: [WIF, BONK, BRETT]   # Rising
tier_3_coins: [New launches]       # Risky/new
dead_coins: [Failed coins]         # For contrast
```

**Why this matters:**
- Need "control group" of failed coins
- Test if sentiment predicts *which* coins succeed
- Avoid confirmation bias

#### 4. **Confounding Variables (Not Captured)**

**Missing critical data:**

| Variable | Impact | How to Add |
|----------|--------|------------|
| Bitcoin price | High - drives all crypto | Add BTC to price collector |
| Ethereum price | Medium - L2 token base | Add ETH to price collector |
| Overall market sentiment | High - macro trends | Collect broader market metrics |
| Influencer follower counts | Medium - weight sentiment | Parse user metadata |
| Trading volume | High - validates movement | Already in CoinGecko data ✓ |
| Whale wallet movements | High - manipulation | Requires blockchain analysis |
| Exchange listings | High - pump catalyst | Manual event logging needed |
| Regulatory news | Medium - market shock | News API integration |

**Statistical impact:**
Without controlling for these, correlations may be:
- Spurious (false positive)
- Understated (false negative)
- Direction reversed (confounding)

**Fix:**
```python
# Multivariate regression controlling for confounds
from statsmodels.formula.api import ols
model = ols('price_change ~ sentiment + btc_change + volume + market_cap', data=df)
results = model.fit()
```

#### 5. **Data Quality Issues**

**Current problems:**

**A. Scraper Reliability:**
- TikTok view counts returning 0 (HTML changes)
- Reddit may miss posts (search limitations)
- Duplicate detection not perfect

**Improvement:**
```python
# Add data quality checks
def validate_data_quality(collected_data):
    quality_metrics = {
        'duplicate_rate': calculate_duplicates(collected_data),
        'missing_fields': check_missing_fields(collected_data),
        'outlier_rate': detect_outliers(collected_data),
        'timestamp_gaps': find_collection_gaps(collected_data)
    }

    if quality_metrics['duplicate_rate'] > 0.05:
        log_warning("High duplicate rate detected")

    return quality_metrics
```

**B. Sentiment Analysis Accuracy:**
- VADER trained on general text, not crypto slang
- Sarcasm detection poor
- Emojis may be misinterpreted

**Improvement:**
- Fine-tune sentiment model on crypto data
- Create custom lexicon for crypto terms
- Manual validation of 100-200 samples
- Calculate inter-rater reliability

#### 6. **Temporal Causality Issues**

**The fundamental problem:**
- Correlation ≠ Causation
- Social might follow price (not lead)
- Both might be driven by external events

**Example:**
```
Elon Musk tweets about DOGE
    ↓
Price pumps (5 min)
    ↓
Social media explodes (30 min)
    ↓
Your system sees "correlation"
```

**But:** Social didn't cause the pump - Elon did!

**Solution:**
- Granger causality tests
- Event study methodology
- Control for known catalysts (news, listings)

**Implementation:**
```python
from statsmodels.tsa.stattools import grangercausalitytests
# Test if social "Granger-causes" price
results = grangercausalitytests(df[['price', 'social']], maxlag=7)
```

#### 7. **Market Manipulation Concerns**

**Reality of meme coins:**
- Pump-and-dump schemes common
- Bot networks inflate engagement
- Coordinated shilling

**Impact on research:**
- Your "sentiment" might be measuring manipulation
- Correlations might be artificially created
- Ethical concerns about profiting from manipulation

**Solution:**
```python
# Bot detection heuristics
def detect_bot_behavior(posts):
    red_flags = {
        'identical_posts': check_duplicates(posts),
        'account_age': check_new_accounts(posts),
        'posting_frequency': check_spam_rate(posts),
        'sentiment_uniformity': check_bot_like_sentiment(posts)
    }
    return red_flags

# Filter suspected manipulation
cleaned_data = remove_likely_bots(raw_data)
```

---

## Part 4: Statistical Significance Requirements

### Minimum Viable Dataset

For **publishable** or **academically rigorous** findings:

| Analysis Type | Minimum Data | Ideal Data | Power |
|---------------|--------------|------------|-------|
| Correlation (basic) | 30 days | 90 days | 0.80 |
| Regression (single var) | 50 observations | 200 observations | 0.80 |
| Multiple regression | 100 observations | 500 observations | 0.80 |
| Time series (ARIMA) | 50 time points | 200 time points | 0.80 |
| Machine learning | 1000 samples | 10,000 samples | 0.90 |
| Causal inference | 60 days | 180 days | 0.85 |

**Power analysis:**
```python
from statsmodels.stats.power import tt_ind_solve_power
# Calculate required sample size
n_required = tt_ind_solve_power(
    effect_size=0.5,  # Medium effect
    alpha=0.05,       # 5% significance
    power=0.80,       # 80% power
    alternative='two-sided'
)
print(f"Need {n_required} samples per group")
```

### P-Value Thresholds

**Standard:** p < 0.05 (95% confidence)
**Rigorous:** p < 0.01 (99% confidence)
**Highly rigorous:** p < 0.001 (99.9% confidence)

**Multiple testing correction:**
```python
from statsmodels.stats.multitest import multipletests
# If testing 23 coins, adjust p-values
_, p_adjusted, _, _ = multipletests(p_values, method='bonferroni')
# Now use p_adjusted < 0.05
```

### Effect Size Requirements

Correlation strength needed for **practical significance**:

| r value | Interpretation | Trading Viability |
|---------|----------------|-------------------|
| 0.1-0.3 | Weak | Not useful for trading |
| 0.3-0.5 | Moderate | Potentially useful |
| 0.5-0.7 | Strong | Good trading signal |
| 0.7-0.9 | Very strong | Excellent signal |
| 0.9-1.0 | Nearly perfect | Suspiciously good (check for errors) |

**Reality check:**
- In finance, r > 0.3 is considered good
- Most published crypto studies show r = 0.2-0.4
- Don't expect r > 0.6 (if you get it, validate thoroughly)

---

## Part 5: Research Design Improvements

### Phase 1: Current State (Months 1-3)
**Goal:** Build dataset, exploratory analysis

**Actions:**
- ✅ Collect data consistently (no gaps)
- ✅ Validate data quality weekly
- ❌ DO NOT make trading decisions yet
- ❌ DO NOT claim findings are significant

**Analysis:**
- Descriptive statistics
- Visualization of trends
- Correlation matrices (exploratory)
- Pattern identification

### Phase 2: Preliminary Validation (Months 4-6)
**Goal:** Test initial hypotheses

**Add:**
- Bitcoin/Ethereum price data (confound control)
- Manual event logging (catalysts)
- Data quality metrics
- Bot detection filters

**Analysis:**
- Time-lagged correlations
- Granger causality tests
- Preliminary regression models
- Cross-validation

**Criteria for moving to Phase 3:**
- Consistent correlations (r > 0.3, p < 0.05)
- Data quality > 95%
- At least 90 days of data
- Results stable across different time windows

### Phase 3: Robust Analysis (Months 7-12)
**Goal:** Publish-quality findings

**Add:**
- Expanded coin list (50+ coins)
- Failed/dead coins (control group)
- Influencer tracking
- News sentiment
- Whale wallet monitoring

**Analysis:**
- Multivariate regression
- Machine learning models
- Backtesting with walk-forward analysis
- Out-of-sample testing
- Sensitivity analysis

**Deliverables:**
- Research paper
- Trading strategy (if viable)
- Open-source dataset
- Predictive dashboard

---

## Part 6: Specific Improvements to Implement

### Immediate (Week 1-4)

#### 1. Add Bitcoin/Ethereum Control
```python
# In config/coins.yaml, add:
control_coins:
  - symbol: BTC
    name: Bitcoin
    coingecko_id: bitcoin
  - symbol: ETH
    name: Ethereum
    coingecko_id: ethereum
```

**Why:** Control for market-wide movements

#### 2. Increase Price Collection Frequency
```python
# In schedule_collection.py
# Separate schedulers:
# Prices every 15 min
# Social every 60 min
```

**Why:** Capture intraday price movements

#### 3. Add Data Quality Logging
```python
# New file: collectors/quality_monitor.py
def log_collection_quality(data):
    metrics = {
        'timestamp': datetime.now(),
        'records_collected': len(data),
        'null_percentage': calculate_nulls(data),
        'duplicate_count': count_duplicates(data),
        'outlier_count': detect_outliers(data)
    }
    db.log_quality_metrics(metrics)
```

**Why:** Identify data issues early

### Short-term (Month 2-3)

#### 4. Manual Event Catalog
```yaml
# events.yaml
events:
  - date: 2025-01-15
    coin: DOGE
    event_type: exchange_listing
    exchange: Binance
    impact: high

  - date: 2025-01-20
    coin: PEPE
    event_type: influencer_mention
    influencer: elonmusk
    platform: twitter
    impact: extreme
```

**Why:** Control for known pump catalysts

#### 5. Bot Detection
```python
# In collectors/sentiment_analyzer.py
class BotDetector:
    def is_likely_bot(self, post):
        score = 0
        if post['account_age_days'] < 30:
            score += 2
        if post['identical_to_other_posts']:
            score += 3
        if post['posts_per_hour'] > 10:
            score += 2
        if post['sentiment_identical_to_others']:
            score += 1

        return score >= 5  # Threshold
```

**Why:** Remove manipulation from sentiment scores

#### 6. Sentiment Model Validation
```python
# Validate VADER on crypto text
def validate_sentiment():
    # Manually label 200 crypto posts
    manual_labels = load_manual_labels()
    vader_predictions = [vader.predict(text) for text in posts]

    accuracy = accuracy_score(manual_labels, vader_predictions)
    print(f"Sentiment accuracy: {accuracy:.2%}")

    if accuracy < 0.70:
        print("WARNING: Sentiment model may be unreliable for crypto")
```

**Why:** Ensure sentiment scores are accurate

### Medium-term (Month 4-6)

#### 7. Expand Coin Universe
```
Current: 23 coins
Target: 50-100 coins including:
  - Top 10 meme coins
  - Mid-tier meme coins
  - New launches (< 6 months)
  - Dead/failed coins (for contrast)
```

**Why:** Reduce survivorship bias

#### 8. Add Trading Volume Analysis
```python
# Already have volume data, but add:
def analyze_volume_patterns():
    # Volume spike threshold
    # Unusual volume detection
    # Volume-price divergence
    # Social volume vs trading volume correlation
```

**Why:** Volume validates price movements

#### 9. News Sentiment Integration
```python
# Use News API or web scraping
class NewsSentiment:
    def collect_news(self, coin):
        articles = newsapi.get_articles(coin)
        sentiment = analyze_news_sentiment(articles)
        return sentiment
```

**Why:** News is a major price driver

#### 10. Influencer Tracking
```python
# Track specific high-impact accounts
CRYPTO_INFLUENCERS = {
    'twitter': ['elonmusk', 'VitalikButerin', 'cz_binance'],
    'reddit': ['major_crypto_accounts'],
    'tiktok': ['crypto_tiktokers']
}

def track_influencer_mentions():
    # Flag posts from influential accounts
    # Weight sentiment by follower count
    # Track influencer activity patterns
```

**Why:** Influencer posts have outsized impact

---

## Part 7: Expected Outcomes & Realistic Expectations

### What You WILL Likely Find

#### 1. **Weak to Moderate Correlations (r = 0.2-0.4)**
This is actually good! Published crypto research shows similar values.

**Interpretation:**
- Social explains 10-20% of price variance
- Other factors (manipulation, macro trends) dominate
- Still valuable for risk assessment

#### 2. **Social Follows Price More Than Leads**
Most likely scenario: Price pumps → People talk about it

**Business value:**
- Still useful for momentum trading
- Detect FOMO phases
- Identify overheated markets

#### 3. **Platform-Specific Patterns**
Likely findings:
- Reddit: More analytical, longer-term sentiment
- TikTok: FOMO-driven, shorter-term spikes
- Cross-platform agreement = stronger signal

#### 4. **Coin-Specific Behavior**
Each coin will have unique patterns:
- DOGE: Elon-driven
- PEPE: Meme-driven
- SHIB: Community-driven

**Implication:** One model won't fit all coins

### What You MIGHT Find (Requires Luck + Good Data)

#### 5. **Predictive Lag Window**
Best case: "Social volume predicts price 4-8 hours ahead"

**Requirements:**
- High-frequency data collection
- Low-latency analysis
- Filtering of bot activity
- Validation across multiple coins

#### 6. **Hype Threshold Effect**
Possible: "When hype score > 75, price pump occurs within 24h with 60% probability"

**Use case:**
- Early warning system
- Entry/exit signals
- Risk management

### What You PROBABLY WON'T Find

#### 7. **High Predictive Accuracy (>70%)**
Unrealistic expectation in crypto markets

**Why:**
- High noise-to-signal ratio
- Manipulation common
- External shocks unpredictable
- Markets are partially efficient

#### 8. **Universal Formula**
Won't find one model that works for all coins, all times

**Why:**
- Market regimes change
- Each coin has different drivers
- Social platform trends evolve

---

## Part 8: Academic Rigor Checklist

To publish findings or claim statistical significance:

### Data Requirements
- [ ] Minimum 90 days of consistent data
- [ ] Data quality > 95% (null rate < 5%)
- [ ] Duplicate detection implemented
- [ ] Bot filtering active
- [ ] Manual validation of 100+ samples

### Statistical Requirements
- [ ] Sample size justified via power analysis
- [ ] Multiple testing corrections applied
- [ ] Effect sizes reported (not just p-values)
- [ ] Confidence intervals calculated
- [ ] Sensitivity analysis performed

### Methodological Requirements
- [ ] Hypotheses pre-registered
- [ ] Control variables included (BTC, ETH, volume)
- [ ] Known confounds addressed
- [ ] Temporal causality tested (Granger)
- [ ] Robustness checks performed

### Validation Requirements
- [ ] Out-of-sample testing
- [ ] Cross-validation (k-fold)
- [ ] Walk-forward analysis
- [ ] Regime change testing
- [ ] Replication across time periods

### Reporting Requirements
- [ ] Full methodology documented
- [ ] Limitations explicitly stated
- [ ] Negative results reported
- [ ] Code and data available (reproducibility)
- [ ] Peer review (if academic)

---

## Part 9: Actionable Roadmap

### Month 1: Foundation
- Collect data (no analysis)
- Validate data quality
- Fix scraper issues
- Add BTC/ETH to tracking

### Month 2: Quality
- Implement bot detection
- Add event logging
- Increase price frequency to 15 min
- Validate sentiment model

### Month 3: Exploration
- First correlation analysis (exploratory)
- Visualize patterns
- Identify anomalies
- Quality report

### Month 4: Testing
- Formal hypothesis tests
- Control for confounds
- Granger causality tests
- Cross-validation begins

### Month 5: Refinement
- Add news sentiment
- Track influencers
- Expand coin list
- Dead coin control group

### Month 6: Validation
- Out-of-sample testing
- Sensitivity analysis
- Robustness checks
- Draft findings

### Month 7-12: Publication
- Academic paper (if applicable)
- Trading strategy (if viable)
- Open-source dataset
- Dashboard for monitoring

---

## Part 10: Key Takeaways

### What This Dataset CAN Prove (With Sufficient Data)

1. ✅ **Correlation strength** between social metrics and price
2. ✅ **Optimal lag time** for social-to-price relationship
3. ✅ **Platform differences** (Reddit vs TikTok)
4. ✅ **Volatility prediction** (easier than direction)
5. ✅ **Relative coin rankings** (which coins are most social-driven)

### What This Dataset CANNOT Prove (Current Limitations)

1. ❌ **Causation** (correlation ≠ causation without controls)
2. ❌ **Trading profitability** (need real trading, transaction costs)
3. ❌ **Manipulation detection** (need blockchain data, whale wallets)
4. ❌ **Fundamental value** (meme coins have no fundamentals)
5. ❌ **Long-term predictions** (only short-term correlations testable)

### Critical Success Factors

1. **Consistency:** No gaps in data collection
2. **Quality:** > 95% data quality maintained
3. **Patience:** Minimum 90 days before strong claims
4. **Controls:** Bitcoin, market sentiment, known events
5. **Honesty:** Report negative results, acknowledge limitations

### Realistic Expectations

**Best case scenario:**
- r = 0.4-0.5 correlation (statistically significant)
- 4-8 hour predictive lag window
- 60% accuracy for volatility prediction
- Platform-specific insights

**Most likely scenario:**
- r = 0.2-0.3 correlation (weak but real)
- Social mostly follows price
- Useful for risk assessment, not trading
- Valuable research contribution

**Worst case scenario:**
- No significant correlations
- Social is pure noise
- Manipulation dominates
- Still learned data science skills!

---

## Conclusion

This dataset has **real research value** but requires:
- Realistic expectations (weak-moderate correlations)
- Methodological rigor (controls, validation)
- Sufficient data (90+ days minimum)
- Honest reporting (acknowledge limitations)

The improvements outlined above will transform this from a "hobby project" into **academically rigorous research** or a **data-driven trading strategy**.

**Most important:** Even null results ("social doesn't predict price") are publishable if the methodology is sound!

---

*Last Updated: 2025-11-20*
*Status: Phase 1 (Data Collection)*
