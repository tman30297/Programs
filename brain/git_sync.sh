#!/bin/bash
# Brain Git Auto-Commit & Push - Commits and pushes to GitHub

cd /media/tony/Drive2/Brain

# Check if there are changes
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit"
    exit 0
fi

# Add notes and transcripts (exclude .gitignore, db, html)
git add notes/ transcripts/ *.md

# Commit with timestamp
DATE=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "Brain update: $DATE"

# Push to GitHub
git push origin main

echo "Committed and pushed to GitHub"

# Show recent commits
git log --oneline -3
