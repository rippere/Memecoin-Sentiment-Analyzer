#!/bin/bash
# Auto-sync Memecoin project to GitHub
# Run this at the end of each session or whenever you want to save progress

cd "$(dirname "$0")"

# Get current timestamp for commit message
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

# Check for changes
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit"
    exit 0
fi

# Show what's being committed
echo "=== Changes to be committed ==="
git status --short
echo ""

# Stage all changes
git add -A

# Create commit with timestamp
git commit -m "Session update: $TIMESTAMP

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
echo ""
echo "=== Pushing to GitHub ==="
git push origin main

echo ""
echo "✓ Synced to GitHub successfully!"
echo "Repo: https://github.com/rippere/Memecoin-Sentiment-Analyzer"
