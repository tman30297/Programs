#!/usr/bin/env python3
"""
Brain Graph Updater - Incremental update script for knowledge graph.
Only rebuilds when there are enough new items to make it worth the time.
"""

import sys
import time
from pathlib import Path

# Add brain module path
sys.path.insert(0, str(Path(__file__).parent))

from brain import init_db, get_db, show_graph_html, NOTES_DIR, TRANSCRIPTS_DIR, BRAIN_DIR
import json
import signal

# Timeout for graph generation (seconds)
GRAPH_TIMEOUT = 300  # 5 minutes

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Graph generation timed out")

def get_existing_graph_nodes():
    """Get IDs already in the current graph."""
    graph_file = BRAIN_DIR / "graph.html"
    if not graph_file.exists():
        return set()
    
    try:
        content = graph_file.read_text()
        # Extract node IDs from the HTML
        import re
        ids = re.findall(r'"id":\s*"([nt]\d+)"', content)
        return set(ids)
    except:
        return set()

def get_all_items():
    """Get all notes and transcripts from database."""
    conn = get_db()
    c = conn.cursor()
    
    # Get all notes
    c.execute("SELECT id FROM notes")
    note_ids = {f"n{r[0]}" for r in c.fetchall()}
    
    # Get all transcripts  
    c.execute("SELECT id FROM transcripts")
    transcript_ids = {f"t{r[0]}" for r in c.fetchall()}
    
    conn.close()
    return note_ids, transcript_ids

def main():
    print("🧠 Brain Graph Updater (Incremental)")
    print("-" * 40)
    
    # Get what's currently in graph
    existing = get_existing_graph_nodes()
    print(f"📊 Currently graphed: {len(existing)} items")
    
    # Get all items in database
    note_ids, transcript_ids = get_all_items()
    all_ids = note_ids | transcript_ids
    
    print(f"📝 Total notes: {len(note_ids)}")
    print(f"📹 Total transcripts: {len(transcript_ids)}")
    print(f"📦 Total items: {len(all_ids)}")
    
    # Find missing items
    missing = all_ids - existing
    print(f"🔄 Missing from graph: {len(missing)}")
    
    if not missing:
        print("\n✅ Graph is up to date!")
        return 0
    
    # Only rebuild if there are enough new items to justify the time
    # This prevents constantly rebuilding for just 1-2 new notes
    if len(missing) < 10:
        print(f"\n⏭️  Only {len(missing)} new items - skipping rebuild (need 10+)")
        print("   Run manually when you have more new notes to add.")
        return len(missing)
    
    print(f"\n⚡ Regenerating graph with {len(all_ids)} items...")
    print(f"   (this may take a few minutes with {len(all_ids)} nodes)")
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(GRAPH_TIMEOUT)
    
    try:
        start_time = time.time()
        show_graph_html()
        elapsed = time.time() - start_time
        signal.alarm(0)  # Cancel timeout
        
        print(f"✅ Graph updated! {len(all_ids)} items in {elapsed:.1f}s")
        return 0
        
    except TimeoutError:
        print(f"⏱️  Graph generation timed out after {GRAPH_TIMEOUT}s")
        print("   The graph has too many items. Consider running manually.")
        return len(missing)
    except Exception as e:
        signal.alarm(0)
        print(f"❌ Error generating graph: {e}")
        return len(missing)

if __name__ == "__main__":
    remaining = main()
    # Exit 0 if graph is up to date, 1 if there are pending items
    sys.exit(0 if remaining == 0 else 1)