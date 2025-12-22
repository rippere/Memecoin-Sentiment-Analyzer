# Planning Workflow - Gemini Integration

**Purpose:** Prevent "slop" and ensure thoughtful, well-architected implementations

---

## The Problem We're Solving

Without proper planning, projects suffer from:
- ❌ Feature creep and scope sprawl
- ❌ Inconsistent architecture
- ❌ Technical debt accumulation
- ❌ Reimplementation and refactoring
- ❌ "Spaghetti code" and poor maintainability

**Solution:** Plan first with AI assistance, then implement systematically.

---

## Planning Workflow

### Step 1: Define the Task

Before ANY implementation, clearly state what you're building:

```markdown
## Task
Implement Reddit sentiment collection pipeline

## Goals
- Collect Reddit posts mentioning trending coins
- Store in database with sentiment scores
- Handle rate limits and errors gracefully

## Non-Goals
- Twitter integration (separate task)
- Real-time streaming (v2 feature)
- ML-based sentiment (Phase 3)
```

---

### Step 2: Use Gemini for Planning

Use the Gemini CLI to create a detailed plan:

```bash
# General planning
gemini "Create detailed implementation plan for Reddit sentiment collection pipeline.
Include: architecture, data flow, error handling, testing strategy, and potential issues.
Context: Python project using SQLAlchemy, FastAPI, existing database schema."

# Architecture design
gemini-code "Design the architecture for a Reddit data collector.
Show: class structure, data flow diagram, API integration points, database schema changes.
Keep it simple and maintainable."

# Compare approaches
gemini "Compare these approaches for Reddit data collection:
1. PRAW library with Reddit API
2. Web scraping old.reddit.com
3. Reddit pushshift API
Analyze: pros/cons, rate limits, reliability, cost, complexity"
```

---

### Step 3: Create Planning Document

Save Gemini's output to a planning doc:

```bash
# Create plan file
gemini "..." > plans/reddit-collector-plan.md

# Or use interactive planning
gemini-chat
```

**Planning Document Template:**

```markdown
# Plan: [Feature Name]

## Overview
Brief description of what we're building

## Architecture

### Components
- Component 1: Description
- Component 2: Description

### Data Flow
1. Step 1
2. Step 2
3. Step 3

### Database Changes
- New tables: X, Y
- Modified tables: Z
- Migrations needed: Yes/No

## Implementation Steps

1. [ ] Task 1
   - Subtask A
   - Subtask B

2. [ ] Task 2
   - Subtask A

## Testing Strategy
- Unit tests: X
- Integration tests: Y
- Manual testing: Z

## Risks & Mitigation
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API rate limit | High | Medium | Caching, throttling |

## Open Questions
- [ ] Question 1?
- [ ] Question 2?

## Success Criteria
- Criterion 1
- Criterion 2

## Estimated Complexity
Low / Medium / High

## Dependencies
- Dependency 1
- Dependency 2
```

---

### Step 4: Review & Refine

**Ask Gemini to critique the plan:**

```bash
gemini "Review this implementation plan and identify:
- Potential issues
- Missing edge cases
- Better alternatives
- Simplification opportunities

Plan: [paste plan here]"
```

**Ask for specific concerns:**

```bash
gemini "For this Reddit collector plan, specifically analyze:
- How to handle deleted/removed posts
- Rate limit strategy for free Reddit API tier
- Database indexing strategy for fast queries
- Error recovery from network failures"
```

---

### Step 5: Get Approval

**Checklist before implementation:**

- [ ] Architecture makes sense
- [ ] Database changes documented
- [ ] Error handling considered
- [ ] Testing approach defined
- [ ] Risks identified
- [ ] Complexity is manageable
- [ ] No "feature creep" beyond scope

**If unsure, ask Gemini:**
```bash
gemini "Is this plan too complex? Suggest simplifications while keeping core functionality."
```

---

### Step 6: Implement

**Follow the plan systematically:**

```bash
# During implementation, ask Gemini for code help
gemini-code "Implement the RedditCollector class based on this plan: [paste relevant section]"

# For specific problems
gemini "How do I handle Reddit API authentication with PRAW? Show best practices."

# For testing
gemini "Generate pytest test cases for this RedditCollector class"
```

**Implementation Rules:**
- ✅ Follow the plan
- ✅ Test incrementally
- ✅ Document deviations
- ✅ Update plan if needed
- ❌ Don't add unplanned features
- ❌ Don't skip testing

---

### Step 7: Retrospective

After completion, document learnings:

```markdown
## Retrospective: Reddit Collector

### What Worked
- Planning prevented overengineering
- Gemini suggested good error handling approach
- Testing strategy caught 3 bugs early

### What Didn't
- Underestimated rate limit complexity
- Should have planned caching from start

### Lessons Learned
- Always plan caching for external APIs
- Test with real API before full implementation

### Plan Accuracy
- Estimated: Medium complexity
- Actual: Medium-High complexity
- Reason: Rate limiting more complex than expected

### Would Do Differently
- Research rate limits deeper before planning
- Add caching to initial architecture
```

---

## Gemini CLI Commands Reference

### Available Commands

```bash
# Chat mode (interactive planning)
gemini-chat

# Single query
gemini "your question here"

# Code-focused queries
gemini-code "code-related question"

# Select model
gemini-model           # Shows current model
gemini-model set       # Change model
```

### Effective Prompts

**✅ Good Prompts:**
```bash
gemini "Design a database schema for storing Reddit posts with:
- Post metadata (title, author, score, timestamp)
- Sentiment scores
- Coin mentions
- Efficient querying for time-series analysis
Show CREATE TABLE statements and explain indexing strategy."
```

**❌ Bad Prompts:**
```bash
gemini "how to reddit"
gemini "database help"
```

**Best Practices:**
- Provide context about your project
- Be specific about constraints (Python, SQLAlchemy, etc.)
- Ask for trade-off analysis
- Request examples when helpful
- Ask for potential issues

---

## Planning Templates

### Feature Planning Template

```bash
gemini "I'm adding [FEATURE] to a crypto sentiment analyzer.

Current stack:
- Python 3.12
- SQLAlchemy ORM
- FastAPI backend
- Next.js frontend
- PostgreSQL database

Requirements:
- [Requirement 1]
- [Requirement 2]

Create a detailed implementation plan including:
1. Architecture design
2. Database schema changes
3. API endpoints needed
4. Implementation steps (prioritized)
5. Testing strategy
6. Potential issues and solutions
7. Time estimate (simple/medium/complex)

Keep it simple and maintainable."
```

### Architecture Review Template

```bash
gemini "Review this architecture for [FEATURE]:

[Paste your design]

Analyze:
1. Is it over-engineered? Suggest simplifications
2. Are there obvious bugs or edge cases missed?
3. Is the database design efficient?
4. Are there better design patterns?
5. What could go wrong?
6. Rate complexity: Low/Medium/High"
```

### Debugging Template

```bash
gemini "I'm getting this error in my [COMPONENT]:

Error: [error message]

Code context:
[paste relevant code]

What's wrong and how do I fix it? Explain the root cause."
```

---

## Integration with Development Flow

### Daily Workflow

```bash
# Morning: Review what to build
gemini-chat
> "Review today's tasks from PROJECT_ROADMAP.md and suggest priorities"

# Before coding: Plan
gemini "Plan implementation for [today's task]"

# During coding: Get help
gemini-code "Implement [specific function] from plan"

# Stuck: Debug
gemini "Debug this issue: [problem]"

# End of day: Document
gemini "Generate documentation for [what I built today]"
```

### Weekly Planning

```bash
# Sunday: Plan the week
gemini "Based on PROJECT_ROADMAP.md Phase 1:
- Break down this week's tasks
- Identify dependencies
- Suggest 5-day schedule
- Flag potential blockers"
```

---

## Quality Gates

Before committing code, verify:

- [ ] Follows the plan (or plan updated with rationale)
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No obvious bugs (asked Gemini to review)
- [ ] Complexity is justified

**Quick Gemini review:**
```bash
gemini "Quick code review of this implementation:
[paste code]
Check for: bugs, performance issues, better patterns, edge cases"
```

---

## Advanced: Architecture Decision Records (ADRs)

For major decisions, create ADR documents:

```bash
gemini "Create an Architecture Decision Record for choosing between:
- PRAW (Reddit API library)
- Web scraping old.reddit.com

Include: Context, Decision, Consequences, Alternatives Considered

Format as ADR using standard template."
```

**Save as:** `docs/adr/001-reddit-api-choice.md`

---

## Example: Planning a New Feature

**Scenario:** Add TikTok trending video tracker

**Step-by-step with Gemini:**

```bash
# 1. High-level planning
gemini "I want to add TikTok trending video tracking to my crypto sentiment analyzer.
Current system tracks coins via Reddit/Twitter.
What are the key considerations and approaches?"

# 2. Architecture design
gemini-code "Design the architecture for TikTok video tracker:
- Data model for storing videos
- Collection strategy (API vs scraping)
- Integration with existing sentiment pipeline
Keep it modular and testable."

# 3. Specific implementation questions
gemini "For TikTok data collection:
1. Is there an official API? Costs?
2. Scraping feasibility and legal concerns?
3. Rate limiting strategies?
4. How to detect trending vs spam videos?"

# 4. Create the plan
gemini "Create full implementation plan for TikTok tracker with:
- Prioritized tasks
- Database schema changes
- Testing approach
- Risk mitigation
Output as markdown checklist" > plans/tiktok-tracker-plan.md

# 5. Review and refine
gemini "Review this plan and suggest simplifications:
[paste plan]"

# 6. Get started
# Read plan
# Implement incrementally
# Use gemini-code for specific implementations
```

---

## Tips for Better Planning

1. **Start Small**
   - Plan one feature at a time
   - Break large features into phases
   - Deliver incrementally

2. **Ask "Why?"**
   - Use Gemini to question assumptions
   - "Is this really needed?"
   - "What's the simplest solution?"

3. **Consider Maintenance**
   - Ask Gemini about long-term implications
   - "How hard is this to maintain?"
   - "What could break in 6 months?"

4. **Learn from Others**
   - Ask Gemini about industry best practices
   - "How do production systems handle this?"
   - "What patterns do successful projects use?"

5. **Validate Assumptions**
   - Test critical assumptions early
   - Use Gemini to identify risky assumptions
   - Build proof-of-concepts for uncertain areas

---

## Gemini Configuration

Your Gemini CLI is configured at: `~/gemini-mcp-server/`

**Current settings:**
```bash
# Check current model
gemini-model

# Available models:
# - gemini-2.0-flash-exp (fast, current default)
# - gemini-1.5-pro (more capable)
# - gemini-1.5-flash (balanced)
```

**For planning, use:**
- `gemini-2.0-flash-exp` - Fast iteration, brainstorming
- `gemini-1.5-pro` - Complex architecture decisions

---

## Summary

**The Golden Rule:**
> "If you're about to code, ask yourself: Did I plan this properly? What could go wrong?"

**Use Gemini to:**
- ✅ Design before building
- ✅ Identify edge cases
- ✅ Compare approaches
- ✅ Review your work
- ✅ Prevent over-engineering

**Don't use Gemini to:**
- ❌ Replace your judgment
- ❌ Skip understanding the code
- ❌ Avoid reading documentation
- ❌ Copy-paste without understanding

---

**Remember:** Planning takes 20% of the time but saves 80% of the problems.
