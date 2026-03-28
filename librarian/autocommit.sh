#!/bin/bash
# Git Auto-Sync for Librarian CSV
# Commits changes to later_list.csv when modified

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_FILE="later_list.csv"

cd "$SCRIPT_DIR"

# Check for changes
if [[ -n $(git status --porcelain $CSV_FILE 2>/dev/null) ]]; then
    echo "Changes detected. Committing..."
    git add $CSV_FILE
    git commit -m "Auto-update: $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin master
    echo "Synced."
else
    echo "No changes."
fi