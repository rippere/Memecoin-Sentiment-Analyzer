# Memecoin Sentiment Analyzer - Project Roadmap

**Last Updated:** 2025-12-22
**Status:** Reorganizing for phased development

---

## Project Vision

Build a data-driven system that analyzes correlations between social media sentiment and memecoin price movements, enabling backtesting of trading strategies and real-time trend detection.

---

## Current Status Assessment

### ✅ Completed
- [x] Database schema with SQLAlchemy ORM
- [x] CoinGecko price collection
- [x] FastAPI backend (basic)
- [x] Next.js dashboard (basic UI)
- [x] Trending coin rotation system
- [x] GitHub Actions for price collection

### 🚧 Partially Complete
- [ ] Social media data collection (TikTok, Reddit scrapers exist but not integrated)
- [ ] Sentiment analysis (VADER imported but not fully utilized)
- [ ] Dashboard functionality (UI exists, needs data visualization)

### ❌ Not Started
- [ ] Correlation analysis implementation
- [ ] Backtesting engine
- [ ] Alert/notification system
- [ ] Advanced visualizations
- [ ] Historical pattern recognition

### ⚠️ Technical Debt
- Frontend node_modules in git (need .gitignore)
- Multiple scattered test scripts
- Inconsistent logging
- No automated testing
- API and DB using different connection patterns (raw sqlite3 vs SQLAlchemy)

---

## Development Phases (Revised)

### Phase 1: Foundation & Cleanup ⚙️ CURRENT
**Goal:** Clean architecture, solid foundation, proper planning workflow

**Tasks:**
1. [ ] Create `.gitignore` for frontend/build artifacts
2. [ ] Consolidate and document database access patterns
3. [ ] Set up Gemini planning integration
4. [ ] Create architecture decision records (ADRs)
5. [ ] Establish testing framework (pytest)
6. [ ] Document all existing collectors and APIs
7. [ ] Clean up test scripts into proper test suite

**Deliverables:**
- Clean git history
- Architecture documentation
- Planning workflow established
- Test framework ready

**Duration:** 1-2 weeks

---

### Phase 2: Data Collection Pipeline 📊
**Goal:** Reliable, automated multi-source data collection

**Sub-phases:**

#### 2A: Price Data (Complete ✓)
- CoinGecko API integration
- Trending coin rotation
- Automated GitHub Actions

#### 2B: Social Media Collection
**Plan First:** Use Gemini to design collection strategy

**Considerations:**
- Rate limits for each platform
- Storage efficiency
- Deduplication strategy
- Error handling and retries

**Sources:**
- [ ] Reddit (improve current implementation)
- [ ] Twitter/X (API v2 with proper auth)
- [ ] TikTok (scraper vs API decision needed)

#### 2C: Data Quality & Validation
- [ ] Bot detection for social posts
- [ ] Spam filtering
- [ ] Data validation pipeline
- [ ] Quality metrics and monitoring

**Deliverables:**
- Robust data collection pipeline
- Quality assurance system
- Monitoring dashboard

**Duration:** 3-4 weeks

---

### Phase 3: Sentiment Analysis Engine 🧠
**Goal:** Accurate sentiment scoring from multi-source data

**Plan First:** Research and compare sentiment approaches

**Components:**
1. [ ] Sentiment analyzer selection/configuration
   - VADER baseline
   - Consider FinBERT or crypto-specific models
   - Ensemble approach?

2. [ ] Hype score calculation
   - Emoji analysis
   - Keyword weighting
   - Engagement metrics

3. [ ] Aggregation strategy
   - Time-based windows
   - Source weighting
   - Confidence scoring

4. [ ] Validation
   - Manual labeling dataset
   - Accuracy testing
   - A/B comparison

**Deliverables:**
- Production sentiment engine
- Validation report
- Sentiment API endpoints

**Duration:** 2-3 weeks

---

### Phase 4: Correlation Analysis 📈
**Goal:** Identify meaningful relationships between sentiment and price

**Plan First:** Statistical methodology design with Gemini

**Analysis Types:**
1. [ ] Time-lagged correlation
   - Sentiment leads price by X hours?
   - Price leads sentiment?
   - Bidirectional causality?

2. [ ] Volume spike correlation
   - Social volume vs price volume
   - Prediction of price pumps

3. [ ] Sentiment shift detection
   - Sudden mood changes
   - Bull/bear transitions

4. [ ] Multi-factor models
   - Combine sentiment, volume, price action
   - Feature importance analysis

**Statistical Methods:**
- Pearson/Spearman correlation
- Granger causality tests
- Machine learning regression
- Time series analysis

**Deliverables:**
- Correlation engine
- Statistical reports
- Visualization dashboard

**Duration:** 3-4 weeks

---

### Phase 5: Backtesting Engine 🔙
**Goal:** Test trading strategies on historical data

**Plan First:** Backtest framework architecture

**Components:**
1. [ ] Strategy definition framework
2. [ ] Historical data replay system
3. [ ] Position management
4. [ ] Performance metrics calculation
5. [ ] Risk analysis

**Strategies to Test:**
- Sentiment-based entry/exit
- Volume spike trading
- Contrarian strategies
- Trend following with sentiment confirmation

**Deliverables:**
- Backtesting framework
- Strategy results dashboard
- Performance reports

**Duration:** 3-4 weeks

---

### Phase 6: Real-Time Dashboard 📱
**Goal:** Production-ready monitoring and analysis interface

**Features:**
1. [ ] Live price charts with sentiment overlay
2. [ ] Trending coins heatmap
3. [ ] Alert system
4. [ ] Historical analysis views
5. [ ] Backtest comparison tool

**Technology Stack:**
- Next.js frontend (existing)
- Real-time updates (WebSockets?)
- Interactive charts (Recharts + D3)
- Mobile responsive

**Deliverables:**
- Production dashboard
- User documentation
- Mobile app (optional)

**Duration:** 4-5 weeks

---

### Phase 7: Advanced Features 🚀
**Goal:** Production deployment and advanced capabilities

**Features:**
1. [ ] Predictive modeling (ML-based)
2. [ ] Influencer tracking
3. [ ] Whale wallet monitoring
4. [ ] Multi-exchange support
5. [ ] Paper trading mode
6. [ ] Community features

**Duration:** Ongoing

---

## Planning Workflow

### Before Starting ANY Phase:

1. **Create Planning Document**
   ```bash
   # Use Gemini to create detailed plan
   gemini "Create detailed implementation plan for Phase X focusing on Y"
   ```

2. **Architecture Review**
   - Design decisions documented
   - Dependencies identified
   - Trade-offs analyzed
   - Alternative approaches considered

3. **Approval Gate**
   - Review plan
   - Validate approach
   - Estimate complexity
   - Identify risks

4. **Implementation**
   - Follow plan
   - Test incrementally
   - Document deviations
   - Update roadmap

5. **Retrospective**
   - What worked?
   - What didn't?
   - Lessons learned
   - Update processes

---

## Decision Log

### Recent Decisions

**2025-12-22: Dynamic Trending Coins**
- **Decision:** Implement rotating coin list based on CoinGecko trending
- **Rationale:** Catch emerging memecoins automatically
- **Trade-offs:** More API calls, more data storage
- **Status:** Implemented
- **Review:** Needs integration testing

**2025-12-22: Project Reorganization**
- **Decision:** Return to phased approach with planning
- **Rationale:** Prevent feature sprawl and technical debt
- **Action:** This roadmap document
- **Status:** In progress

---

## Success Metrics

### Phase Completion Criteria
- All tasks documented and tested
- Architecture decisions recorded
- No critical technical debt
- Documentation complete
- User acceptance (if applicable)

### Overall Project Success
- **Technical:** System processes 1000+ coins reliably
- **Analysis:** Identifies correlations with p < 0.05
- **Performance:** <1s response time for API queries
- **Reliability:** 99%+ uptime for data collection
- **Value:** Backtest shows viable trading strategies

---

## Risk Management

### Technical Risks
- **API Rate Limits:** Mitigation: Caching, tiered collection
- **Data Quality:** Mitigation: Validation pipeline, manual review
- **Scraper Breaking:** Mitigation: API alternatives, monitoring

### Project Risks
- **Scope Creep:** Mitigation: Strict phase gates
- **Complexity:** Mitigation: Planning workflow
- **Burnout:** Mitigation: Realistic timelines, breaks

---

## Resources & References

### APIs
- CoinGecko: https://www.coingecko.com/api/documentation
- Twitter API: https://developer.twitter.com/en/docs
- Reddit API: https://www.reddit.com/dev/api

### Libraries
- SQLAlchemy: https://docs.sqlalchemy.org/
- FastAPI: https://fastapi.tiangolo.com/
- Next.js: https://nextjs.org/docs

### Research
- [ ] Crypto sentiment analysis papers
- [ ] Trading strategy backtesting methodologies
- [ ] Statistical correlation best practices

---

## Next Actions

**Immediate (This Week):**
1. ✅ Create this roadmap
2. [ ] Set up Gemini planning workflow
3. [ ] Create .gitignore and clean git
4. [ ] Document current architecture
5. [ ] Create Phase 1 detailed plan

**Short Term (Next 2 Weeks):**
- Complete Phase 1 (Foundation)
- Plan Phase 2 with Gemini
- Set up testing framework

**Long Term (3+ Months):**
- Reach Phase 4 (Correlation Analysis)
- Have production-ready backtesting

---

**Remember:** Plan first, build second. Quality over speed.
