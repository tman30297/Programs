#!/usr/bin/env python3
"""
Brain Auto-Sync - Hourly script to sync new content into Brain.
Run hourly to keep content automatically importing.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from brain import init_db, sync_external_sources, get_db, NOTES_DIR, TRANSCRIPTS_DIR, BRAIN_DIR
import json
import re

def get_existing_graph_nodes():
    """Get IDs already in the current graph."""
    graph_file = BRAIN_DIR / "graph.html"
    if not graph_file.exists():
        return set()
    try:
        content = graph_file.read_text()
        ids = re.findall(r'"id":\s*"([nt]\d+)"', content)
        return set(ids)
    except:
        return set()

def get_all_items():
    """Get all notes and transcripts from database."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM notes")
    note_ids = {f"n{r[0]}" for r in c.fetchall()}
    c.execute("SELECT id FROM transcripts")
    transcript_ids = {f"t{r[0]}" for r in c.fetchall()}
    conn.close()
    return note_ids, transcript_ids

def main():
    print("🔄 Brain Auto-Sync")
    print("-" * 30)
    
    # Get counts before
    note_ids_before, transcript_ids_before = get_all_items()
    print(f"📝 Notes before: {len(note_ids_before)}")
    
    # Run sync
    print("\n🔄 Syncing external sources...")
    sync_external_sources()
    
    # Get counts after
    note_ids_after, transcript_ids_after = get_all_items()
    print(f"\n📝 Notes after: {len(note_ids_after)}")
    
    new_notes = len(note_ids_after) - len(note_ids_before)
    new_transcripts = len(transcript_ids_after) - len(transcript_ids_before)
    
    total_new = new_notes + new_transcripts
    print(f"✨ New items: {total_new}")
    
    # NOTE: Graph updates are handled by graph_updater.py (every 4 hours)
    # auto_sync.py only does the content sync now to avoid duplication
    if total_new > 0:
        print("\n📊 Graph will be updated by graph_updater.py (every 4 hours)")
    else:
        print("\nℹ️ No new items to sync")
    
    return total_new

if __name__ == "__main__":
    main()
