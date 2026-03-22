#!/usr/bin/env python3
"""
Brain - Personal Knowledge Hub
A shared knowledge system for voice memos, YouTube transcripts, notes, and semantic search.
"""

import argparse
import glob
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configuration
BRAIN_DIR = Path("/media/tony/Drive2/Brain")
DB_PATH = BRAIN_DIR / "brain.db"
NOTES_DIR = BRAIN_DIR / "notes"
TRANSCRIPTS_DIR = BRAIN_DIR / "transcripts"
GRAPH_FILE = BRAIN_DIR / "graph.json"

BRAIN_DIR.mkdir(parents=True, exist_ok=True)
NOTES_DIR.mkdir(exist_ok=True)
TRANSCRIPTS_DIR.mkdir(exist_ok=True)

def init_db():
    """Initialize SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL,
        author TEXT DEFAULT 'unknown', source TEXT DEFAULT 'manual',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, tags TEXT, title TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transcripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT, content TEXT NOT NULL,
        author TEXT DEFAULT 'unknown', source TEXT DEFAULT 'youtube', duration TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, tags TEXT)''')
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect(DB_PATH)

def add_note(content: str, title: str = "", author: str = "Tony", tags: str = ""):
    if not title:
        title = f"Note {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO notes (content, author, source, tags, title) VALUES (?, ?, ?, ?, ?)",
              (content, author, "manual", tags, title))
    note_id = c.lastrowid
    conn.commit()
    conn.close()
    note_file = NOTES_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    note_file.write_text(f"# {title}\n\n{content}\n\nTags: {tags}\n")
    print(f"✅ Note saved! (ID: {note_id})")

def list_notes(limit: int = 10):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, author, source, created_at, tags FROM notes ORDER BY created_at DESC LIMIT ?", (limit,))
    print("\n📝 Recent Notes:\n")
    for row in c.fetchall():
        print(f"  #{row[0]}: {row[1]} ({row[2]}) - {row[4][:10]}")
    conn.close()

def show_graph():
    """Text view of graph."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title FROM notes ORDER BY created_at DESC")
    notes = c.fetchall()
    c.execute("SELECT id, title FROM transcripts ORDER BY created_at DESC")
    transcripts = c.fetchall()
    conn.close()
    print(f"\n📊 Knowledge Graph: {len(notes)} notes, {len(transcripts)} transcripts")

def compute_tfidf_links(nodes, min_score: float = 0.02, max_links: int = 50000):
    """
    Compute links using TF-IDF (Term Frequency-Inverse Document Frequency).
    
    This weights important words higher and ignores common words, giving
    much better connections than simple word overlap.
    
    TODO: Add semantic embeddings via Ollama for even better matching:
    - Use Ollama with a small embedding model (e.g., nomic-embed-text)
    - Would catch synonyms: "async" ≈ "asyncio" ≈ "await"
    - Would connect: "ESP32" to "microcontroller" even without exact words
    """
    import math
    from collections import Counter
    
    if len(nodes) < 2:
        return []
    
    # Common stop words to ignore
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
        'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as',
        'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'between', 'under', 'again', 'further', 'then', 'once', 'here',
        'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few',
        'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
        'and', 'but', 'if', 'or', 'because', 'until', 'while', 'although',
        'this', 'that', 'these', 'those', 'am', 'it', 'its', 'they',
        'their', 'them', 'what', 'which', 'who', 'whom', 'we', 'our',
        'you', 'your', 'he', 'she', 'him', 'her', 'his', 'i', 'me', 'my',
        'also', 'see', 'use', 'using', 'used', 'get', 'one', 'two', 'new',
        'like', 'way', 'make', 'made', 'know', 'want', 'think', 'take',
        'come', 'first', 'last', 'long', 'great', 'little', 'even',
        'back', 'still', 'well', 'much', 'say', 'said', 'over', 'now',
        'file', 'folder', 'directory', 'code', 'run', 'python', 'example'
    }
    
    # 1. Build vocabulary and document frequencies
    word_doc_freq = Counter()  # How many docs contain each word
    doc_words = []  # List of (word, count) per doc
    
    for node in nodes:
        words = node.get("words", set())
        # Filter stop words and short words
        filtered = {w for w in words if w not in stop_words and len(w) > 2}
        
        word_counts = Counter(filtered)
        doc_words.append(word_counts)
        
        for word in filtered:
            word_doc_freq[word] += 1
    
    # 2. Compute TF-IDF for each document
    n_docs = len(nodes)
    doc_vectors = []
    
    for word_counts in doc_words:
        total_words = sum(word_counts.values()) or 1
        tfidf = {}
        
        for word, count in word_counts.items():
            tf = count / total_words
            # IDF with smoothing to avoid division by zero
            idf = math.log(n_docs / (1 + word_doc_freq[word]))
            tfidf[word] = tf * idf
        
        doc_vectors.append(tfidf)
    
    # 3. Compute cosine similarity between all pairs
    links = []
    
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            vec1 = doc_vectors[i]
            vec2 = doc_vectors[j]
            
            # Cosine similarity
            common_words = set(vec1.keys()) & set(vec2.keys())
            if not common_words:
                continue
            
            dot_product = sum(vec1[w] * vec2[w] for w in common_words)
            mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
            mag2 = math.sqrt(sum(v**2 for v in vec2.values()))
            
            if mag1 > 0 and mag2 > 0:
                similarity = dot_product / (mag1 * mag2)
                
                if similarity >= min_score:
                    # Get the top connecting words
                    word_scores = [(w, vec1[w] * vec2[w]) for w in common_words]
                    word_scores.sort(key=lambda x: x[1], reverse=True)
                    top_words = ", ".join(w for w, _ in word_scores[:3])
                    
                    links.append({
                        "source": nodes[i]["id"],
                        "target": nodes[j]["id"],
                        "label": top_words,
                        "score": round(similarity, 3)
                    })
    
    # Sort by score and limit
    links.sort(key=lambda x: x["score"], reverse=True)
    links = links[:max_links]
    
    print(f"🔗 TF-IDF: computed {len(links)}高质量 connections (min score: {min_score})")
    return links


def show_graph_html():
    """Generate HTML visualization with notes AND transcripts."""
    import json
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, source, created_at FROM notes ORDER BY created_at DESC")
    notes = c.fetchall()
    c.execute("SELECT id, title, source, created_at FROM transcripts ORDER BY created_at DESC")
    transcripts = c.fetchall()
    
    # Build nodes for both notes and transcripts
    all_nodes = []
    
    # Process notes
    for n in notes:
        c.execute("SELECT content, tags FROM notes WHERE id = ?", (n[0],))
        row = c.fetchone()
        words = set(row[0].lower().split()[:30]) if row and row[0] else set()
        # Add tags to words for better linking
        if row and row[1]:
            words.update(row[1].lower().split(','))
        all_nodes.append({"id": f"n{n[0]}", "label": n[1][:25] if n[1] else f"Note {n[0]}", "type": "note", "words": words, "db_id": n[0]})
    
    # Process transcripts - KEY ENHANCEMENT: now included in graph
    for t in transcripts:
        c.execute("SELECT content, tags FROM transcripts WHERE id = ?", (t[0],))
        row = c.fetchone()
        words = set(row[0].lower().split()[:50]) if row and row[0] else set()
        if row and row[1]:
            words.update(row[1].lower().split(','))
        all_nodes.append({"id": f"t{t[0]}", "label": t[1][:25] if t[1] else f"Transcript {t[0]}", "type": "transcript", "words": words, "db_id": t[0]})
    
    # TF-IDF Linking (better than simple word overlap)
    link_data = compute_tfidf_links(all_nodes)
    conn.close()
    
    # Count node types
    note_count = len([n for n in all_nodes if n["type"] == "note"])
    transcript_count = len([n for n in all_nodes if n["type"] == "transcript"])
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Brain Knowledge Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 12px; background: #0d1117; color: #c9d1d9; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
        h1 {{ color: #58a6ff; margin: 0 0 8px 0; font-size: 20px; }}
        p {{ margin: 0 0 12px 0; color: #8b949e; font-size: 12px; }}
        #container {{ flex: 1; border: 1px solid #30363d; border-radius: 8px; background: #161b22; position: relative; overflow: hidden; min-height: 300px; }}
        #graph {{ width: 100%; height: 100%; }}
        .node circle {{ stroke: #fff; stroke-width: 2px; cursor: pointer; transition: all 0.2s; }}
        .node circle:hover {{ stroke: #58a6ff; stroke-width: 3px; }}
        .node text {{ font-size: 11px; fill: #c9d1d9; pointer-events: none; text-shadow: 1px 1px 2px #000; }}
        .link {{ stroke: #f78166; stroke-opacity: 0.7; }}
        .tooltip {{ position: fixed; background: #21262d; border: 1px solid #30363d; padding: 12px; border-radius: 6px; max-width: 350px; display: none; z-index: 1000; box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
        .tooltip strong {{ color: #58a6ff; display: block; margin-bottom: 4px; }}
        .tooltip small {{ color: #8b949e; }}
        .legend {{ margin-top: 12px; display: flex; gap: 20px; }}
        .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 13px; }}
        .zoom-controls {{ position: fixed; bottom: 20px; right: 20px; display: flex; flex-direction: column; gap: 5px; }}
        .zoom-btn {{ width: 44px; height: 44px; border-radius: 8px; border: none; background: #21262d; color: #c9d1d9; font-size: 22px; cursor: pointer; display: flex; align-items: center; justify-content: center; touch-action: manipulation; }}
        .zoom-btn:hover {{ background: #30363d; }}
        @media (max-width: 600px) {{ 
            body {{ padding: 8px; }} 
            h1 {{ font-size: 16px; }}
            p {{ font-size: 11px; }}
            .zoom-btn {{ width: 40px; height: 40px; font-size: 20px; }}
            .zoom-controls {{ bottom: 10px; right: 10px; }}
            .legend {{ flex-direction: column; gap: 8px; font-size: 11px; }}
        }}
    </style>
</head>
<body>
    <h1>🧠 Brain Knowledge Graph</h1>
    <p>📝 {note_count} Notes | 📹 {transcript_count} Transcripts | 🔗 {len(link_data)} Connections | Scroll to pan, drag nodes, wheel to zoom</p>
    <div id="container"><div id="graph"></div></div>
    <div class="legend">
        <div class="legend-item"><circle cx="6" cy="6" r="6" fill="#58a6ff"></circle> Notes</div>
        <div class="legend-item"><circle cx="6" cy="6" r="6" fill="#f78166"></circle> Transcripts</div>
    </div>
    <div class="zoom-controls">
        <button class="zoom-btn" onclick="zoomIn()" title="Zoom In">+</button>
        <button class="zoom-btn" onclick="zoomOut()" title="Zoom Out">−</button>
        <button class="zoom-btn" onclick="resetZoom()" title="Reset View">↺</button>
    </div>
    <div class="tooltip" id="tooltip"></div>
    <script>
        const nodes = {json.dumps([{"id": n["id"], "label": n["label"], "type": n["type"]} for n in all_nodes])};
        const links = {json.dumps(link_data)};
        
        const container = document.getElementById('container');
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        const svg = d3.select('#graph').append('svg').attr('width', width).attr('height', height);
        const g = svg.append('g');
        
        const zoom = d3.zoom().scaleExtent([0.1, 4]).on('zoom', (e) => g.attr('transform', e.transform));
        svg.call(zoom).call(zoom.transform, d3.zoomIdentity.translate(width/4, height/4).scale(0.7));
        
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-350))
            .force('center', d3.forceCenter(width/2, height/2))
            .force('collision', d3.forceCollide().radius(35));
        
        g.append('g').selectAll('line').data(links).enter().append('line').attr('class', 'link').attr('stroke-width', 2);
        
        const node = g.append('g').selectAll('g').data(nodes).enter().append('g').attr('class', 'node')
            .call(d3.drag().on('start', (e) => {{ if(!e.active) simulation.alphaTarget(0.3).restart(); e.subject.fx=e.subject.x; e.subject.fy=e.subject.y; }})
                .on('drag', (e) => {{ e.subject.fx=e.x; e.subject.fy=e.y; }})
                .on('end', (e) => {{ if(!e.active) simulation.alphaTarget(0); e.subject.fx=null; e.subject.fy=null; }}));
        
        node.append('circle').attr('r', 16).attr('fill', d => d.type==='note'?'#58a6ff':'#f78166').attr('stroke','#fff')
            .on('click', (e,d) => {{ const t=document.getElementById('tooltip'); t.style.display='block'; t.style.left=(e.clientX+15)+'px'; t.style.top=(e.clientY+15)+'px'; t.innerHTML='<strong>'+(d.title||d.label)+'</strong><small>Type: '+d.type+' | ID: '+d.id+'</small>'; }});
        
        node.append('text').attr('dx', 20).attr('dy', 4).text(d => d.label);
        
        simulation.on('tick', () => {{
            g.selectAll('line').attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
            node.attr('transform', d => "translate(" + d.x + "," + d.y + ")");
        }});
        
        document.addEventListener('click', e => {{ if(!e.target.closest('.node')) document.getElementById('tooltip').style.display='none'; }});
        
        // Zoom functions
        let currentZoom = 1;
        function zoomIn() {{ svg.transition().call(zoom.scaleBy, 1.3); }}
        function zoomOut() {{ svg.transition().call(zoom.scaleBy, 0.7); }}
        function resetZoom() {{ svg.transition().call(zoom.transform, d3.zoomIdentity.translate(width/4, height/4).scale(0.7)); }}
    </script>
</body>
</html>'''
    
    html_file = BRAIN_DIR / "graph.html"
    # Preserve enhanced graph.html if it has 3D support
    if html_file.exists():
        existing = html_file.read_text()
        if '3d-force-graph' in existing:
            print(f"📊 Preserving enhanced graph.html with 3D support")
            # Just regenerate the data file using existing all_nodes and link_data
            nodes_data = [{"id": n["id"], "title": n.get("label", ""), "label": n["label"][:40], "type": n["type"]} for n in all_nodes]
            links_data = [{"source": l["source"], "target": l["target"], "label": l.get("label", ""), "score": l.get("score", 1)} for l in link_data]
            data_file = BRAIN_DIR / "graph_data.json"
            graph_data = {"nodes": nodes_data, "links": links_data}
            data_file.write_text(json.dumps(graph_data, indent=2))
            print(f"📊 Updated graph_data.json: {len(nodes_data)} nodes, {len(links_data)} links")
            return
    
    html_file.write_text(html)
    print(f"📊 Generated: {html_file}")

def add_transcript(title: str, url: str, content: str, author: str = "unknown", duration: str = "", tags: str = ""):
    """Add a YouTube transcript to the database."""
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO transcripts (title, url, content, author, source, duration, tags) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (title, url, content, author, "youtube", duration, tags))
    transcript_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # Save to markdown file
    safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()[:50]
    transcript_file = TRANSCRIPTS_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_title}.md"
    transcript_file.write_text(f"# {title}\n\n**Source:** {url}\n**Duration:** {duration}\n**Tags:** {tags}\n\n---\n\n{content}\n")
    print(f"✅ Transcript saved! (ID: {transcript_id})")
    return transcript_id

def import_youtube(url: str):
    """Import YouTube video and transcribe it."""
    import re as re_module
    print(f"📥 Downloading: {url}")
    
    # Extract video ID from URL
    match = re_module.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
    if not match:
        match = re_module.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
    video_id = match.group(1) if match else "unknown"
    
    # Get video info
    try:
        result = subprocess.run(
            ["yt-dlp", "--print", "%(title)s|%(duration)s", url],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            print(f"❌ Error getting video info: {result.stderr}")
            return
        info = result.stdout.strip()
        if "|" in info:
            title, duration = info.split("|", 1)
            # Format duration nicely
            try:
                dur_secs = int(duration)
                mins = dur_secs // 60
                secs = dur_secs % 60
                duration_formatted = f"{mins}:{secs:02d}"
            except:
                duration_formatted = duration
        else:
            title = info
            duration_formatted = "Unknown"
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print(f"📹 Title: {title}")
    print(f"⏱️  Duration: {duration_formatted}")
    
    # Try to get transcript first (most YouTube videos have auto-generated captions)
    print("📝 Getting transcript...")
    try:
        # Clean up any old subtitle files for this video
        for ext in ['srt', 'vtt']:
            for f in glob.glob(f"/tmp/ytdlp_{video_id}.en.{ext}"):
                os.remove(f)
        
        result = subprocess.run(
            ["yt-dlp", "--write-subs", "--write-auto-subs", "--skip-download", 
             "--sub-lang", "en", "--convert-subs", "srt", "-o", f"/tmp/ytdlp_{video_id}", url],
            capture_output=True, text=True, timeout=120
        )
        
        # Look for the subtitle file
        sub_files = glob.glob(f"/tmp/ytdlp_{video_id}.en.srt") + glob.glob(f"/tmp/ytdlp_{video_id}.en.vtt")
        
        if sub_files:
            sub_file = sub_files[0]
            print(f"📄 Found subtitles: {sub_file}")
            
            # Convert SRT/VTT to plain text
            with open(sub_file, 'r') as f:
                content = f.read()
            
            # Parse SRT to plain text
            import re
            # Remove SRT numbering and timestamps
            text = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
            text = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', text)
            text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
            text = text.strip()
            
            # Clean up extra whitespace
            text = re.sub(r'\n\s*\n', '\n\n', text)
            
            if len(text) > 100:  # Reasonable transcript length
                add_transcript(title, url, text, "YouTube", duration_formatted, "youtube,video")
                return
    except Exception as e:
        print(f"⚠️ Could not get subtitles: {e}")
    
    print("❌ No subtitles available for this video.")
    print("   Try a different video or wait for faster-whisper integration.")

def search_pdfs(search_term: str, directory: str = "/media/tony/Drive2/python3/", verbose: bool = False, timeout_per_pdf: int = 10):
    """Search for text in PDF files with timeout per PDF using subprocess."""
    import json
    
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Installing pypdf...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
        from pypdf import PdfReader
    
    search_dir = Path(directory).expanduser().resolve()
    
    if not search_dir.exists():
        print(f"❌ Directory not found: {search_dir}")
        return
    
    # Search only top-level PDFs (faster)
    if search_dir.is_file() and search_dir.suffix == '.pdf':
        pdf_files = [search_dir]
    else:
        pdf_files = list(search_dir.glob("*.pdf"))  # Only top level
    
    if not pdf_files:
        print(f"❌ No PDF files found in {search_dir}")
        return
    
    print(f"🔍 Searching for '{search_term}' in {len(pdf_files)} PDF(s)...\n")
    
    results = []
    skipped = 0
    
    # Path to worker script
    worker_script = Path(__file__).parent / "pdf_search_worker.py"
    
    for pdf_path in pdf_files:
        if verbose:
            print(f"  Searching {pdf_path.name}...")
        
        try:
            # Run the search in a subprocess with timeout using the worker script
            result = subprocess.run(
                [sys.executable, str(worker_script), str(pdf_path), search_term],
                capture_output=True,
                text=True,
                timeout=timeout_per_pdf
            )
            
            output = result.stdout.strip()
            if output.startswith("RESULT:"):
                result_data = json.loads(output[7:])
                results.append(result_data)
            elif output.startswith("ERROR:"):
                if verbose:
                    print(f"  ⚠️ Error in {pdf_path.name}: {output[6:]}")
        except subprocess.TimeoutExpired:
            if verbose:
                print(f"  ⏱️ Timeout on {pdf_path.name} (skipping)")
            skipped += 1
        except Exception as e:
            if verbose:
                print(f"  ⚠️ Error in {pdf_path.name}: {e}")
    
    if skipped > 0:
        print(f"  ⏱️ Skipped {skipped} PDF(s) due to timeout/corruption")
    
    # Sort by match count
    results.sort(key=lambda x: x['match_count'], reverse=True)
    
    if not results:
        print(f"❌ No PDFs found containing '{search_term}'")
        return
    
    print(f"✅ Found '{search_term}' in {len(results)} PDF(s):\n")
    
    for r in results:
        pages_str = ", ".join(str(p) for p in r['pages'][:10])
        if len(r['pages']) > 10:
            pages_str += f" ... ({len(r['pages'])} pages)"
        print(f"📄 {r['filename']}")
        print(f"   📍 Page {pages_str}")
        print(f"   🔢 {r['match_count']} match(es)")
        print()
    
    return results  # Return for use by pdf-import


def extract_pdf_content(pdf_path: Path, max_pages: int = 10, max_chars: int = 3000, timeout_sec: int = 5) -> str:
    """Extract actual text content from a PDF with timeout using subprocess."""
    import subprocess
    
    # Path to worker script
    worker_script = Path(__file__).parent / "pdf_extract_worker.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(worker_script), str(pdf_path), str(max_pages), str(max_chars)],
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        if result.returncode != 0:
            print(f"  ⚠️ Error extracting: {result.stderr.strip()}")
            return None
        content = result.stdout
        return content if content.strip() else None
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ Timeout extracting {pdf_path.name} (skipping)")
        return None
    except Exception as e:
        print(f"  ⚠️ Error extracting: {e}")
        return None


def auto_tag_content(content: str, existing_tags: str = "") -> str:
    """
    Auto-generate tags based on content keywords.
    Uses simple keyword matching - can be upgraded to AI later.
    """
    # Topic keywords to detect
    topic_keywords = {
        "python": ["python", "pygame", "pandas", "django", "flask", "pip", "venv", "pipenv"],
        "rust": ["rust", "cargo", "rustc", "ownership", "borrow", "lifetime", "trait"],
        "iot": ["esp32", "esp8266", "arduino", "sensor", "gpio", "i2c", "spi", "microcontroller"],
        "web": ["http", "html", "css", "javascript", "api", "rest", "json", "ajax"],
        "database": ["sql", "mysql", "postgresql", "sqlite", "mongodb", "redis", "query"],
        "ai": ["machine learning", "neural", "tensorflow", "pytorch", "ai", "deep learning", "model"],
        "network": ["tcp", "udp", "socket", "http", "dns", "ip", "router", "firewall"],
        "security": ["encryption", "hash", "auth", "password", "ssl", "tls", "certificate"],
        "linux": ["bash", "shell", "terminal", "sudo", "apt", "yum", "cron", "systemd"],
        "docker": ["docker", "container", "kubernetes", "k8s", "pod", "image", "registry"],
        "git": ["git", "commit", "branch", "merge", "pull", "push", "repository"],
        "async": ["async", "await", "asyncio", "coroutine", "promise", "event loop"],
    }
    
    content_lower = content.lower()
    detected_topics = []
    
    for topic, keywords in topic_keywords.items():
        for kw in keywords:
            if kw in content_lower:
                detected_topics.append(topic)
                break  # Only add topic once
    
    # Combine with existing tags
    existing = set(t.strip() for t in existing_tags.split(",") if t.strip())
    detected = set(detected_topics)
    all_tags = existing | detected
    
    return ",".join(sorted(all_tags)) if all_tags else existing_tags


def find_duplicates(threshold: float = 0.7) -> list:
    """
    Find duplicate or very similar notes using simple text similarity.
    Returns list of (id1, id2, similarity_score) tuples.
    """
    import math
    from collections import Counter
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, content FROM notes")
    notes = c.fetchall()
    conn.close()
    
    if len(notes) < 2:
        return []
    
    # Simple word-based similarity (Jaccard index)
    def get_words(text):
        return set(text.lower().split())
    
    def jaccard_similarity(set1, set2):
        if not set1 or not set2:
            return 0
        return len(set1 & set2) / len(set1 | set2)
    
    duplicates = []
    
    for i in range(len(notes)):
        id1, title1, content1 = notes[i]
        words1 = get_words(content1 or "")
        
        for j in range(i + 1, len(notes)):
            id2, title2, content2 = notes[j]
            words2 = get_words(content2 or "")
            
            # Check title similarity too
            title_sim = jaccard_similarity(get_words(title1 or ""), get_words(title2 or ""))
            content_sim = jaccard_similarity(words1, words2)
            
            # Combined score
            similarity = (title_sim * 0.4) + (content_sim * 0.6)
            
            if similarity >= threshold:
                duplicates.append((id1, title1, id2, title2, round(similarity, 2)))
    
    return duplicates


def deduplicate(dry_run: bool = True):
    """Find and optionally merge duplicate notes."""
    print("🔍 Finding duplicate notes...")
    
    duplicates = find_duplicates(threshold=0.7)
    
    if not duplicates:
        print("✅ No duplicates found!")
        return []
    
    print(f"📋 Found {len(duplicates)} potential duplicates:\n")
    
    for id1, title1, id2, title2, score in duplicates[:10]:  # Show first 10
        print(f"  #{id1}: {title1[:40]}")
        print(f"  #{id2}: {title2[:40]}")
        print(f"  Similarity: {score:.0%}")
        print()
    
    if len(duplicates) > 10:
        print(f"  ... and {len(duplicates) - 10} more")
    
    if dry_run:
        print("\n⚠️ This is a dry run. Use --confirm to merge.")
        print("   Merging keeps the newest note and deletes the older one.")
    
    return duplicates


def find_backlinks(max_notes: int = 10) -> list:
    """
    Find explicit references between notes.
    Looks for patterns like: "note #5", "see #12", "related to note X"
    Returns list of (source_id, target_id, context) tuples.
    """
    import re
    
    # Patterns to detect references to other notes
    patterns = [
        r'note\s*#?(\d+)',
        r'see\s*#?(\d+)',
        r'related\s*to\s*#?(\d+)',
        r'refer\s*to\s*#?(\d+)',
        r'as\s*shown\s*in\s*note\s*#?(\d+)',
    ]
    
    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, content FROM notes")
    notes = c.fetchall()
    conn.close()
    
    backlinks = []
    
    for note_id, title, content in notes:
        if not content:
            continue
        
        for pattern in compiled:
            matches = pattern.findall(content)
            for target_id in matches:
                try:
                    target_id = int(target_id)
                    if target_id != note_id:  # Don't link to self
                        # Get context
                        match = pattern.search(content)
                        if match:
                            start = max(0, match.start() - 20)
                            end = min(len(content), match.end() + 20)
                            context = content[start:end].replace('\n', ' ')
                            backlinks.append((note_id, title[:30], target_id, context))
                except ValueError:
                    continue
    
    return backlinks[:max_notes]  # Limit results


def show_backlinks():
    """Display all backlinks found in notes."""
    print("🔗 Finding backlinks between notes...")
    
    backlinks = find_backlinks(max_notes=20)
    
    if not backlinks:
        print("ℹ️ No explicit backlinks found.")
        print("   Add references like 'see note #5' or 'related to #12'")
        return
    
    print(f"📋 Found {len(backlinks)} backlinks:\n")
    
    for source_id, source_title, target_id, context in backlinks:
        print(f"  #{source_id} ({source_title}...) → #{target_id}")
        print(f"    \"...{context}...\"")
        print()
    
    return backlinks


def search_graph(keyword: str, limit: int = 10):
    """
    Search notes and transcripts by keyword.
    Shows matching items with their connections.
    """
    conn = get_db()
    c = conn.cursor()
    
    # Search notes
    c.execute("""
        SELECT id, title, content, tags, 'note' as type 
        FROM notes 
        WHERE content LIKE ? OR title LIKE ? OR tags LIKE ?
        LIMIT ?
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))
    
    notes = c.fetchall()
    
    # Search transcripts
    c.execute("""
        SELECT id, title, content, tags, 'transcript' as type 
        FROM transcripts 
        WHERE content LIKE ? OR title LIKE ? OR tags LIKE ?
        LIMIT ?
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))
    
    transcripts = c.fetchall()
    conn.close()
    
    total = len(notes) + len(transcripts)
    
    if total == 0:
        print(f"❌ No results found for '{keyword}'")
        return []
    
    print(f"🔍 Search results for '{keyword}': {total} found\n")
    
    print("📝 Notes:")
    for note in notes[:limit]:
        note_id, title, content, tags, note_type = note
        preview = (content or "")[:100].replace('\n', ' ')
        print(f"  #{note_id}: {title[:40]}")
        print(f"      Tags: {tags or 'none'}")
        print(f"      Preview: {preview}...")
        print()
    
    if transcripts:
        print("\n📹 Transcripts:")
        for trans in transcripts[:limit]:
            trans_id, title, content, tags, trans_type = trans
            preview = (content or "")[:100].replace('\n', ' ')
            print(f"  #{trans_id}: {title[:40]}")
            print(f"      Preview: {preview}...")
            print()
    
    return notes, transcripts


def find_related_by_source(limit: int = 5) -> list:
    """
    Find notes that share the same source (PDF or YouTube).
    Links notes from the same book/video together.
    """
    conn = get_db()
    c = conn.cursor()
    
    # Get all notes with their content
    c.execute("SELECT id, title, content, source FROM notes WHERE content LIKE '%PDF Search:%'")
    pdf_notes = c.fetchall()
    
    # Group by PDF filename
    from collections import defaultdict
    pdf_groups = defaultdict(list)
    
    for note_id, title, content, source in pdf_notes:
        # Extract filename from content
        if content and "File:" in content:
            try:
                for line in content.split('\n'):
                    if line.startswith("File:"):
                        filename = line.replace("File:", "").strip()
                        pdf_groups[filename].append((note_id, title))
                        break
            except:
                pass
    
    # Find groups with 2+ notes (potential links)
    related = []
    for filename, notes in pdf_groups.items():
        if len(notes) >= 2:
            related.append((filename, notes))
    
    conn.close()
    
    return related[:limit]


def find_related_by_embedding(limit: int = 10, similarity_threshold: float = 0.7) -> list:
    """
    Find semantically related notes using embeddings (AI).
    Uses nomic-embed-text to find notes with similar content.
    This will use GPU when running on a machine with CUDA.
    """
    import subprocess
    import numpy as np
    
    print("🔗 Finding related notes using AI embeddings...")
    
    # Get notes with content
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, content FROM notes WHERE length(content) > 50")
    notes = c.fetchall()
    conn.close()
    
    if len(notes) < 2:
        print("⚠️ Not enough notes to compare")
        return []
    
    # Generate embeddings for each note
    embeddings = []
    valid_notes = []
    
    print(f"   Generating embeddings for {len(notes)} notes...")
    
    for note_id, title, content in notes:
        # Truncate content to first 1000 chars for embedding
        content_snippet = content[:1000] if content else ""
        if not content_snippet:
            continue
            
        # Get embedding from Ollama
        try:
            result = subprocess.run(
                ["ollama", "run", "nomic-embed-text", f"Find related notes: {content_snippet}"],
                capture_output=True, text=True, timeout=30
            )
            # Parse embedding from output (Ollama returns JSON with embedding)
            import json
            try:
                data = json.loads(result.stdout)
                embedding = data.get('embedding', [])
                if embedding:
                    embeddings.append(np.array(embedding))
                    valid_notes.append((note_id, title, content_snippet[:200]))
            except:
                # Try parsing as direct embedding
                pass
        except Exception as e:
            print(f"   ⚠️ Error embedding note {note_id}: {e}")
            continue
    
    if len(embeddings) < 2:
        print("⚠️ Could not generate enough embeddings")
        return []
    
    # Calculate cosine similarity
    print("   Calculating similarities...")
    embeddings = np.array(embeddings)
    
    # Normalize
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized = embeddings / norms
    
    # Similarity matrix
    similarity = np.dot(normalized, normalized.T)
    
    # Find pairs above threshold
    related = []
    for i in range(len(valid_notes)):
        for j in range(i + 1, len(valid_notes)):
            if similarity[i][j] >= similarity_threshold:
                related.append((
                    valid_notes[i][1][:50],  # title 1
                    valid_notes[j][1][:50],  # title 2
                    float(similarity[i][j])  # similarity score
                ))
    
    # Sort by similarity
    related.sort(key=lambda x: x[2], reverse=True)
    
    print(f"   Found {len(related)} related note pairs")
    return related[:limit]


def find_orphans() -> list:
    """
    Find notes that have no connections to other notes.
    Uses the current graph to determine connectivity.
    """
    import re
    
    # Get all node IDs from current graph
    graph_file = BRAIN_DIR / "graph.html"
    if not graph_file.exists():
        print("⚠️ No graph found - run 'brain.py graph-viz' first")
        return []
    
    content = graph_file.read_text()
    
    # Extract all node IDs that have connections
    connected = set()
    links = re.findall(r'"source":\s*"([nt]\d+)",\s*"target":\s*"([nt]\d+)"', content)
    for source, target in links:
        connected.add(source)
        connected.add(target)
    
    # Get all notes
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, tags FROM notes")
    all_notes = c.fetchall()
    conn.close()
    
    # Find orphans (notes not in any connection)
    orphans = []
    for note_id, title, tags in all_notes:
        node_id = f"n{note_id}"
        if node_id not in connected:
            orphans.append((note_id, title, tags))
    
    return orphans


def show_orphans(limit: int = 20):
    """Display orphan notes (notes with no connections)."""
    print("🔍 Finding orphan notes...")
    
    orphans = find_orphans()
    
    if not orphans:
        print("✅ No orphans found! All notes are connected.")
        return []
    
    print(f"📋 Found {len(orphans)} orphan notes:\n")
    
    for note_id, title, tags in orphans[:limit]:
        print(f"  #{note_id}: {title[:50]}")
        print(f"      Tags: {tags or 'none'}")
        print()
    
    if len(orphans) > limit:
        print(f"  ... and {len(orphans) - limit} more")
    
    print(f"\n💡 Tip: Add content or link to other notes to connect them!")
    
    return orphans


def cluster_by_time(limit: int = 10):
    """
    Cluster notes by creation date.
    Shows notes grouped by day/week.
    """
    from collections import defaultdict
    from datetime import datetime
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, created_at, tags FROM notes ORDER BY created_at DESC")
    notes = c.fetchall()
    conn.close()
    
    # Group by date
    by_date = defaultdict(list)
    for note_id, title, created_at, tags in notes:
        date = created_at[:10] if created_at else "unknown"
        by_date[date].append((note_id, title, tags))
    
    print(f"📅 Time Clustering: {len(notes)} notes\n")
    
    # Show clusters
    for date, notes_list in sorted(by_date.items(), reverse=True)[:limit]:
        print(f"  📆 {date} ({len(notes_list)} notes)")
        for note_id, title, tags in notes_list[:3]:
            print(f"      → #{note_id}: {title[:40]}")
        if len(notes_list) > 3:
            print(f"      ... and {len(notes_list) - 3} more")
        print()
    
    if len(by_date) > limit:
        print(f"  ... and {len(by_date) - limit} more days")
    
    return by_date


def export_json(output_file: str = None):
    """Export all Brain data as JSON."""
    import json
    from datetime import datetime
    
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"/media/tony/Drive2/Brain/export_{timestamp}.json"
    
    conn = get_db()
    c = conn.cursor()
    
    # Get all notes
    c.execute("SELECT id, title, content, author, source, created_at, tags FROM notes")
    notes = c.fetchall()
    
    # Get all transcripts
    c.execute("SELECT id, title, url, content, author, source, duration, created_at, tags FROM transcripts")
    transcripts = c.fetchall()
    
    conn.close()
    
    # Build export data
    data = {
        "exported_at": datetime.now().isoformat(),
        "notes": [
            {
                "id": n[0], "title": n[1], "content": n[2], "author": n[3],
                "source": n[4], "created_at": n[5], "tags": n[6]
            } for n in notes
        ],
        "transcripts": [
            {
                "id": t[0], "title": t[1], "url": t[2], "content": t[3],
                "author": t[4], "source": t[5], "duration": t[6], "created_at": t[7], "tags": t[8]
            } for t in transcripts
        ],
        "stats": {
            "total_notes": len(notes),
            "total_transcripts": len(transcripts)
        }
    }
    
    # Also export to brain.json for browser
    browser_file = BRAIN_DIR / "brain.json"
    with open(browser_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"📄 Browser data: {browser_file}")
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Exported to: {output_file}")
    print(f"   Notes: {len(notes)}")
    print(f"   Transcripts: {len(transcripts)}")
    
    return output_file


def show_stats():
    """Show Brain statistics and insights."""
    import json
    from collections import Counter
    from datetime import datetime
    
    conn = get_db()
    c = conn.cursor()
    
    # Basic counts
    c.execute("SELECT COUNT(*) FROM notes")
    note_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM transcripts")
    transcript_count = c.fetchone()[0]
    
    # Get all tags
    c.execute("SELECT tags FROM notes WHERE tags IS NOT NULL AND tags != ''")
    all_tags = []
    for row in c.fetchall():
        if row[0]:
            all_tags.extend([t.strip() for t in row[0].split(',')])
    
    # Get all tags from transcripts too
    c.execute("SELECT tags FROM transcripts WHERE tags IS NOT NULL AND tags != ''")
    for row in c.fetchall():
        if row[0]:
            all_tags.extend([t.strip() for t in row[0].split(',')])
    
    # Tag counts
    tag_counts = Counter(all_tags).most_common(10)
    
    # Sources
    c.execute("SELECT source, COUNT(*) FROM notes GROUP BY source")
    sources = c.fetchall()
    
    # Recent activity
    c.execute("SELECT created_at FROM notes ORDER BY created_at DESC LIMIT 1")
    latest_note = c.fetchone()
    
    c.execute("SELECT created_at FROM transcripts ORDER BY created_at DESC LIMIT 1")
    latest_transcript = c.fetchone()
    
    conn.close()
    
    # Print stats
    print("🧠 Brain Statistics")
    print("=" * 40)
    print(f"\n📊 Overview:")
    print(f"   Notes: {note_count}")
    print(f"   Transcripts: {transcript_count}")
    print(f"   Total items: {note_count + transcript_count}")
    
    print(f"\n🏷️ Top Tags:")
    for tag, count in tag_counts:
        print(f"   {tag}: {count}")
    
    print(f"\n📁 Sources:")
    for source, count in sources:
        print(f"   {source}: {count}")
    
    print(f"\n🕐 Latest:")
    if latest_note:
        print(f"   Note: {latest_note[0][:16] if latest_note[0] else 'unknown'}")
    if latest_transcript:
        print(f"   Transcript: {latest_transcript[0][:16] if latest_transcript[0] else 'unknown'}")
    
    print()
    return {
        "notes": note_count,
        "transcripts": transcript_count,
        "tags": dict(tag_counts)
    }


def edit_note(note_id: int = None, new_content: str = None, new_title: str = None, new_tags: str = None):
    """Edit an existing note."""
    if not note_id:
        print("❌ Please provide a note ID")
        print("   Usage: brain.py edit <note_id> [--content 'new content'] [--title 'new title'] [--tags 'tag1,tag2']")
        return
    
    conn = get_db()
    c = conn.cursor()
    
    # Check if note exists
    c.execute("SELECT id, title, content, tags FROM notes WHERE id = ?", (note_id,))
    note = c.fetchone()
    
    if not note:
        print(f"❌ Note #{note_id} not found")
        conn.close()
        return
    
    old_title, old_content, old_tags = note[1], note[2], note[3]
    
    # Update fields
    title = new_title if new_title else old_title
    content = new_content if new_content else old_content
    tags = new_tags if new_tags else old_tags
    
    c.execute("UPDATE notes SET title = ?, content = ?, tags = ? WHERE id = ?",
              (title, content, tags, note_id))
    conn.commit()
    conn.close()
    
    print(f"✅ Updated note #{note_id}")
    print(f"   Title: {title[:50]}")
    print(f"   Tags: {tags}")
    
    return True


def merge_notes(keep_id: int, delete_id: int, dry_run: bool = True):
    """Merge note B into note A, keeping A and deleting B."""
    conn = get_db()
    c = conn.cursor()
    
    # Get both notes
    c.execute("SELECT id, title, content, tags FROM notes WHERE id = ?", (keep_id,))
    keep_note = c.fetchone()
    
    c.execute("SELECT id, title, content, tags FROM notes WHERE id = ?", (delete_id,))
    delete_note = c.fetchone()
    
    if not keep_note:
        print(f"❌ Note #{keep_id} not found")
        conn.close()
        return
    
    if not delete_note:
        print(f"❌ Note #{delete_id} not found")
        conn.close()
        return
    
    # Merge content
    merged_content = f"{keep_note[2]}\n\n---\n\n[Merged from note #{delete_id}: {delete_note[1]}]\n{delete_note[2]}"
    
    # Merge tags
    tags1 = set(t.strip() for t in (keep_note[3] or "").split(",") if t.strip())
    tags2 = set(t.strip() for t in (delete_note[3] or "").split(",") if t.strip())
    merged_tags = ",".join(sorted(tags1 | tags2))
    
    if dry_run:
        print(f"🔍 Dry run - would merge:")
        print(f"   Keep: #{keep_id} - {keep_note[1][:40]}")
        print(f"   Delete: #{delete_id} - {delete_note[1][:40]}")
        print(f"\n   Merged title: {keep_note[1][:40]}")
        print(f"   Merged tags: {merged_tags}")
        print(f"\n⚠️ Use --confirm to actually merge")
    else:
        # Update the keep note
        c.execute("UPDATE notes SET content = ?, tags = ? WHERE id = ?",
                 (merged_content, merged_tags, keep_id))
        
        # Delete the other note
        c.execute("DELETE FROM notes WHERE id = ?", (delete_id,))
        
        conn.commit()
        print(f"✅ Merged note #{delete_id} into #{keep_id}")
        print(f"   Tags: {merged_tags}")
    
    conn.close()
    return not dry_run


def random_note(tag_filter: str = None):
    """Show a random note for review."""
    import random
    
    conn = get_db()
    c = conn.cursor()
    
    if tag_filter:
        c.execute("SELECT id, title, content, tags FROM notes WHERE tags LIKE ?", (f"%{tag_filter}%",))
    else:
        c.execute("SELECT id, title, content, tags FROM notes")
    
    notes = c.fetchall()
    conn.close()
    
    if not notes:
        print("❌ No notes found")
        return
    
    note = random.choice(notes)
    
    print("=" * 50)
    print(f"📝 Note #{note[0]}: {note[1]}")
    print(f"   Tags: {note[3] or 'none'}")
    print("-" * 50)
    print(note[2][:800])
    if len(note[2] or "") > 800:
        print("\n[...]")
    print("=" * 50)
    print(f"\n💡 Tip: Use 'brain.py get {note[0]}' to view full note")
    
    return note


def chat_with_brain(question: str, collection: str = "notes", model: str = "qwen3:8b"):
    """Answer a question using QMD semantic search + Ollama."""
    import subprocess
    
    print(f"🤔 Question: {question}")
    print("-" * 50)
    
    # Search using QMD
    try:
        result = subprocess.run(
            ["qmd", "search", question, "-c", collection, "-n", "3"],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode != 0:
            print(f"❌ Search error: {result.stderr}")
            return None
        
        output = result.stdout
        if not output.strip():
            print("❌ No relevant notes found")
            return None
        
        # Extract content from results - parse QMD output
        lines = output.split('\n')
        context_parts = []
        titles = []
        
        in_content = False
        current_content = []
        
        for line in lines:
            if 'Title:' in line:
                title = line.split('Title:')[1].strip()
                titles.append(title)
            elif line.startswith('@@'):
                in_content = True
                current_content = []
            elif in_content:
                if line.strip() and not line.startswith('==='):
                    current_content.append(line.strip())
                elif line.startswith('==='):
                    if current_content:
                        context_parts.append(' '.join(current_content[:5]))
                    in_content = False
        
        context = "\n\n".join(context_parts[:3])
        
        if not context:
            # Fallback: just use raw output
            context = output[:1500]
        
        if len(context) < 50:
            print("❌ Not enough relevant content found")
            print("   Try a different question or add more notes")
            return None
        
        # Use Ollama to answer
        print(f"📚 Searching knowledge base...")
        print(f"🤖 Using {model} to answer...\n")
        
        prompt = f"""You are a helpful assistant. Answer the question based ONLY on the provided notes from the user's knowledge base.

Notes from knowledge base:
{context}

Question: {question}

Instructions:
- Answer based ONLY on the notes provided
- If the notes don't contain enough information, say so
- Be concise but helpful

Answer:"""

        # Run Ollama
        ollama_result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=120
        )
        
        print("=" * 50)
        print("📖 ANSWER:")
        print("=" * 50)
        print(ollama_result.stdout)
        print("=" * 50)
        
        # Show sources
        print("\n📚 Sources found:")
        for t in titles[:3]:
            print(f"  • {t}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Search timed out. Try a simpler question.")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def multi_search(question: str):
    """Search across PDFs, notes, transcripts, and web simultaneously."""
    import subprocess
    import threading
    
    results = {"notes": None, "transcripts": None, "pdfs": None, "web": None}
    errors = []
    
    def search_notes():
        try:
            result = subprocess.run(
                ["qmd", "search", question, "-c", "notes", "-n", "3"],
                capture_output=True, text=True, timeout=15
            )
            results["notes"] = result.stdout if result.returncode == 0 else ""
        except Exception as e:
            errors.append(f"Notes: {e}")
    
    def search_transcripts():
        try:
            result = subprocess.run(
                ["qmd", "search", question, "-c", "transcripts", "-n", "3"],
                capture_output=True, text=True, timeout=15
            )
            results["transcripts"] = result.stdout if result.returncode == 0 else ""
        except Exception as e:
            errors.append(f"Transcripts: {e}")
    
    def search_pdfs():
        try:
            # Search PDFs
            result = subprocess.run(
                ["python3", "/media/tony/Drive2/Programs/brain/brain.py", "pdf", question, "/media/tony/Drive2/python3/"],
                capture_output=True, text=True, timeout=30
            )
            results["pdfs"] = result.stdout if result.returncode == 0 else ""
        except Exception as e:
            errors.append(f"PDFs: {e}")
    
    def search_web():
        try:
            # Use web_search via OpenClaw
            from tools import web_search
            r = web_search({"query": question, "count": 3})
            if r and "results" in r:
                results["web"] = "\n".join([f"• {item.get('title', 'No title')}" for item in r["results"]])
        except Exception as e:
            errors.append(f"Web: {e}")
    
    print(f"🔍 Multi-source search: {question}")
    print("=" * 50)
    
    # Run all searches in parallel
    threads = [
        threading.Thread(target=search_notes),
        threading.Thread(target=search_transcripts),
        threading.Thread(target=search_pdfs),
    ]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    # Display results
    print("\n📚 NOTES:")
    if results["notes"]:
        print(results["notes"][:500])
    else:
        print("  (no results)")
    
    print("\n📹 TRANSCRIPTS:")
    if results["transcripts"]:
        print(results["transcripts"][:500])
    else:
        print("  (no results)")
    
    print("\n📄 PDFs:")
    if results["pdfs"]:
        print(results["pdfs"][:500])
    else:
        print("  (no results)")
    
    if errors:
        print(f"\n⚠️ Some searches failed: {errors}")
    
    print("\n" + "=" * 50)
    print("💡 Use 'brain.py chat \"question\"' for AI answer from notes")
    print("   Or 'brain.py pdf \"term\" /path/' for detailed PDF search")
    
    return results


def hybrid_search(query: str):
    """Search using keyword + semantic + graph all together."""
    import subprocess
    
    print(f"🔍 Hybrid search: {query}")
    print("=" * 50)
    
    results = {}
    
    # 1. Keyword search (QMD)
    try:
        result = subprocess.run(
            ["qmd", "search", query, "-c", "notes", "-n", "3", "--no-rerank"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            results["keyword"] = result.stdout[:400]
    except:
        pass
    
    # 2. Semantic search (QMD with embeddings)
    try:
        result = subprocess.run(
            ["qmd", "vsearch", query, "-c", "notes", "-n", "3"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            results["semantic"] = result.stdout[:400]
    except:
        pass
    
    # 3. Graph connections (from brain)
    try:
        result = subprocess.run(
            ["python3", "/media/tony/Drive2/Programs/brain/brain.py", "search", query],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            results["graph"] = result.stdout[:400]
    except:
        pass
    
    # Display combined results
    print("\n🔑 KEYWORD (BM25):")
    print(results.get("keyword", "  (no results)")[:200])
    
    print("\n🧠 SEMANTIC (Vectors):")
    print(results.get("semantic", "  (no results)")[:200])
    
    print("\n🕸️ GRAPH (Connections):")
    print(results.get("graph", "  (no results)")[:200])
    
    print("\n" + "=" * 50)
    print("💡 Use 'brain.py chat \"question\"' for combined AI answer")
    
    return results


def summarize_note(note_id: int = None, model: str = "qwen3:8b"):
    """Summarize a note using AI."""
    import subprocess
    
    if not note_id:
        print("❌ Please provide a note ID")
        print("   Usage: brain.py summarize <note_id>")
        return
    
    # Get note content
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT title, content FROM notes WHERE id = ?", (note_id,))
    note = c.fetchone()
    conn.close()
    
    if not note:
        print(f"❌ Note #{note_id} not found")
        return
    
    title, content = note
    content = (content or "")[:2000]  # Limit for AI
    
    print(f"📝 Summarizing: {title}")
    print("-" * 40)
    
    prompt = f"""Summarize the following note concisely. Include the main points and key takeaways.

Note Title: {title}

Note Content:
{content}

Provide a 2-3 sentence summary:"""

    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=60
        )
        
        print("=" * 50)
        print("📖 SUMMARY:")
        print("=" * 50)
        print(result.stdout)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def get_note(note_id: int = None):
    """Get a single note by ID."""
    if not note_id:
        print("❌ Please provide a note ID")
        return
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, content, author, source, created_at, tags FROM notes WHERE id = ?", (note_id,))
    note = c.fetchone()
    conn.close()
    
    if not note:
        print(f"❌ Note #{note_id} not found")
        return
    
    print(f"\n📝 Note #{note[0]}: {note[1]}")
    print(f"   Author: {note[3]} | Source: {note[4]}")
    print(f"   Created: {note[5]}")
    print(f"   Tags: {note[6]}")
    print(f"\n{'-' * 40}")
    print(note[2][:500] + ("..." if len(note[2] or "") > 500 else ""))
    
    return note


def show_related_by_source():
    """Display notes related by shared source."""
    print("🔗 Finding related notes by source...")
    
    related = find_related_by_source(limit=10)
    
    if not related:
        print("ℹ️ No related notes found by source.")
        print("   Import more PDFs to see connections.")
        return []
    
    print(f"📋 Found {len(related)} sources with multiple notes:\n")
    
    for filename, notes in related:
        print(f"  📄 {filename[:50]}...")
        for note_id, title in notes:
            print(f"      → #{note_id}: {title[:40]}")
        print()
    
    return related


def import_pdf_search_to_notes(search_term: str, directory: str, tags: str = "pdf,imported", max_pdfs: int = 10, extract_content: bool = True):
    """Import PDF search results as notes to Brain."""
    results = search_pdfs(search_term, directory, verbose=False)
    
    if not results:
        print("❌ No results to import")
        return
    
    # Limit results
    results = results[:max_pdfs]
    print(f"\n📥 Importing up to {len(results)} results to Brain...")
    
    for r in results:
        content_parts = []
        
        # Basic info
        content_parts.append(f"""PDF Search: "{search_term}"

**File:** {r['filename']}
**Pages:** {', '.join(map(str, r['pages'][:15]))}
**Matches:** {r['match_count']}
**Location:** {r['filepath']}

---""")
        
        # Extract actual content if requested
        if extract_content:
            print(f"  📄 Extracting content from: {r['filename'][:40]}...")
            pdf_content = extract_pdf_content(Path(r['filepath']), max_pages=3, max_chars=1500)
            
            if pdf_content:
                content_parts.append(f"\n**Content Preview:**\n{pdf_content}")
                # Auto-tag based on content
                auto_tags = auto_tag_content(pdf_content, f"{tags},{search_term}")
                if auto_tags != f"{tags},{search_term}":
                    tags = auto_tags
                    print(f"  🏷️ Auto-detected tags: {tags}")
            else:
                content_parts.append("\n[Content extraction unavailable]")
        
        full_content = '\n'.join(content_parts)
        
        # Extract clean title from filename
        title = r['filename'].replace('_', ' ').replace('.pdf', '')
        
        add_note(full_content, title=title, author="Brain", tags=f"{tags},{search_term}")
    
    print(f"✅ Imported {len(results)} PDF notes with content!")
    print("💡 Run 'brain.py graph-viz' to see new connections")


def sync_external_sources():
    """Sync from bookmarks and notes programs."""
    imported_count = 0
    
    # Sync from bookmarks_manager
    bm_path = Path("/media/tony/Drive2/Programs/bookmarks_manager/bookmarks.json")
    if bm_path.exists():
        print("📚 Syncing bookmarks...")
        try:
            import json
            with open(bm_path) as f:
                bookmarks = json.load(f)
            
            for bm in bookmarks.get("bookmarks", []):
                # Check if already imported (by URL)
                conn = get_db()
                c = conn.cursor()
                c.execute("SELECT id FROM notes WHERE source = ? AND content LIKE ?", 
                         ("bookmark", f"%{bm.get('url', '')}%"))
                if not c.fetchone():
                    content = f"URL: {bm.get('url', '')}\n\n{bm.get('description', '')}"
                    add_note(content, title=bm.get("title", "Bookmark"), 
                            author="sync", tags=f"bookmark,{bm.get('category', '')}")
                    imported_count += 1
                conn.close()
        except Exception as e:
            print(f"⚠️ Bookmarks sync error: {e}")
    
    # Sync from notes_cli
    notes_path = Path("/media/tony/Drive2/Programs/notes_cli/notes.json")
    if notes_path.exists():
        print("📝 Syncing notes_cli...")
        try:
            import json
            with open(notes_path) as f:
                notes_data = json.load(f)
            
            for note in notes_data.get("notes", []):
                conn = get_db()
                c = conn.cursor()
                c.execute("SELECT id FROM notes WHERE title = ? AND source = ?", 
                         (note.get("title", ""), "notes_cli"))
                if not c.fetchone():
                    add_note(note.get("content", ""), title=note.get("title", "Note"),
                            author="sync", tags=note.get("tags", ""))
                    imported_count += 1
                conn.close()
        except Exception as e:
            print(f"⚠️ Notes sync error: {e}")
    
    # Also check for markdown notes in Programs folder
    programs_notes = Path("/media/tony/Drive2/Programs")
    for md_file in programs_notes.glob("*/README.md"):
        try:
            content = md_file.read_text()[:2000]  # Limit size
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT id FROM notes WHERE title = ?", (md_file.stem,))
            if not c.fetchone():
                add_note(content[:500], title=f"Program: {md_file.stem}", 
                         author="sync", tags="program,documentation")
                imported_count += 1
            conn.close()
        except:
            pass
    
    if imported_count > 0:
        print(f"✅ Synced {imported_count} new items!")
        print("💡 Run 'brain.py graph-viz' to see new connections")
    else:
        print("ℹ️ No new items to sync")


def generate_flashcards(note_id: int = None, count: int = 5, model: str = "qwen3:8b"):
    """Generate flashcards from a note using AI."""
    import subprocess
    
    if not note_id:
        print("❌ Please provide a note ID")
        print("   Usage: brain.py flashcard <note_id>")
        return
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT title, content FROM notes WHERE id = ?", (note_id,))
    note = c.fetchone()
    conn.close()
    
    if not note:
        print(f"❌ Note #{note_id} not found")
        return
    
    title, content = note
    content = (content or "")[:2500]
    
    print(f"📝 Generating flashcards from: {title}")
    
    prompt = f"""Generate {count} flashcards (Q&A) from this note.

Note: {title}
{content}

Format:
Q: question
A: answer"""

    try:
        result = subprocess.run(["ollama", "run", model, prompt], capture_output=True, text=True, timeout=120)
        
        print("=" * 50)
        print("📇 FLASHCARDS:")
        print("=" * 50)
        print(result.stdout)
        print("=" * 50)
        
        with open(f"/media/tony/Drive2/Brain/flashcards_{note_id}.txt", 'w') as f:
            f.write(f"# Flashcards: {title}\n\n{result.stdout}")
        print(f"\n💾 Saved to flashcards_{note_id}.txt")
    except Exception as e:
        print(f"❌ Error: {e}")


def flashcards_random(count: int = 5, model: str = "qwen3:8b"):
    """Generate flashcards from random note."""
    import random
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM notes")
    notes = [r[0] for r in c.fetchall()]
    conn.close()
    
    if notes:
        generate_flashcards(random.choice(notes), count, model)
    else:
        print("❌ No notes found")


def writing_assist(prompt: str, model: str = "qwen3:8b"):
    """Help write something using your knowledge base."""
    import subprocess
    
    if not prompt:
        print("❌ Please provide a writing prompt")
        print("   Usage: brain.py write \"Write an email about Python\"")
        return
    
    print(f"✍️ Writing assist: {prompt}")
    print("-" * 40)
    
    # Search for relevant context
    try:
        result = subprocess.run(
            ["qmd", "search", prompt, "-c", "notes", "-n", "3"],
            capture_output=True, text=True, timeout=15
        )
        
        context = ""
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Title:' in line:
                    context += f"\n{line}\n"
                elif line.startswith('# '):
                    context += f"{line[2:]}\n"
        
        if not context:
            context = "No relevant notes found."
        
    except:
        context = "Could not search notes."
    
    full_prompt = f"""You are a helpful writing assistant. Use the user's knowledge base to help write something.

User's request: {prompt}

Relevant knowledge:
{context}

Instructions:
- Write based on the user's request
- Incorporate relevant info from their knowledge if helpful
- Be concise and helpful

Write:"""

    try:
        result = subprocess.run(
            ["ollama", "run", model, full_prompt],
            capture_output=True, text=True, timeout=120, bufsize=1
        )
        
        print("=" * 50)
        print("✍️ WRITING:")
        print("=" * 50)
        
        # Stream output
        print(result.stdout)
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def streaming_chat(question: str, model: str = "qwen3:8b"):
    """Chat with streaming responses."""
    import subprocess
    
    print(f"🤔 Question: {question}")
    print("-" * 50)
    
    # Get context
    try:
        result = subprocess.run(
            ["qmd", "search", question, "-c", "notes", "-n", "3"],
            capture_output=True, text=True, timeout=15
        )
        
        context = ""
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Title:' in line:
                    context += f"{line}\n"
                elif line.startswith('# '):
                    context += f"{line[2:]}\n"
        
        if not context:
            context = "No relevant notes found."
            
    except:
        context = "Could not search notes."
    
    full_prompt = f"""Answer the question based ONLY on the user's notes.

Question: {question}

Notes:
{context}

Answer:"""

    print("📖 Answer (streaming):\n")
    
    try:
        # Stream the response
        process = subprocess.Popen(
            ["ollama", "run", model, full_prompt],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line, end='', flush=True)
        
        process.wait()
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Brain")
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("voice", help="Record voice")
    yt_p = subparsers.add_parser("youtube", help="YouTube import"); yt_p.add_argument("url", nargs="?", default=""); yt_p.add_argument("--urls", dest="urls", action="append", default=[])
    
    note_p = subparsers.add_parser("note", help="Add note"); note_p.add_argument("content"); note_p.add_argument("--title", default=""); note_p.add_argument("--author", default="Tony"); note_p.add_argument("--tags", default="")
    list_p = subparsers.add_parser("list", help="List"); list_p.add_argument("--limit",type=int,default=10)
    pdf_p = subparsers.add_parser("pdf", help="Search PDFs"); pdf_p.add_argument("query", nargs="?", default=""); pdf_p.add_argument("directory", nargs="?", default="/media/tony/Drive2/python3/"); pdf_p.add_argument("-v", "--verbose", action="store_true")
    
    # New: PDF import command
    pdf_imp_p = subparsers.add_parser("pdf-import", help="Import PDF search results as notes")
    pdf_imp_p.add_argument("query", nargs="?", default="")
    pdf_imp_p.add_argument("directory", nargs="?", default="/media/tony/Drive2/python3/")
    pdf_imp_p.add_argument("--tags", default="pdf,imported")
    pdf_imp_p.add_argument("--limit", type=int, default=10, help="Max PDFs to import (default: 10)")
    pdf_imp_p.add_argument("--no-content", action="store_true", help="Skip content extraction (import metadata only)")
    
    # New: Sync command
    subparsers.add_parser("sync", help="Sync from bookmarks and notes programs")
    
    # New: Dedupe command
    dedupe_p = subparsers.add_parser("dedupe", help="Find duplicate notes")
    dedupe_p.add_argument("--threshold", type=float, default=0.7, help="Similarity threshold 0-1 (default: 0.7)")
    dedupe_p.add_argument("--confirm", action="store_true", help="Actually merge duplicates (default is dry-run)")
    
    # New: Backlinks command
    subparsers.add_parser("backlinks", help="Find explicit references between notes")
    
    # New: Search command
    search_p = subparsers.add_parser("search", help="Search notes and transcripts")
    search_p.add_argument("query", nargs="?", default="")
    search_p.add_argument("--limit", type=int, default=10)
    
    # New: Related command
    subparsers.add_parser("related", help="Find notes related by source (same PDF/video)")
    
    # New: AI-Related command (uses embeddings - GPU powered!)
    ai_related_p = subparsers.add_parser("ai-related", help="Find related notes using AI embeddings (GPU)")
    ai_related_p.add_argument("--limit", type=int, default=10, help="Number of pairs to find")
    ai_related_p.add_argument("--threshold", type=float, default=0.7, help="Similarity threshold 0-1")
    
    # New: Orphans command
    subparsers.add_parser("orphans", help="Find notes with no connections")
    
    # New: Cluster command
    subparsers.add_parser("cluster", help="Group notes by time")
    
    # New: Export command
    export_p = subparsers.add_parser("export", help="Export Brain data as JSON")
    export_p.add_argument("--output", default=None, help="Output file path")
    
    # New: Stats command
    subparsers.add_parser("stats", help="Show Brain statistics")
    
    # New: Get command
    get_p = subparsers.add_parser("get", help="Get a note by ID")
    get_p.add_argument("note_id", type=int, nargs="?", help="Note ID to retrieve")
    
    # New: Edit command
    edit_p = subparsers.add_parser("edit", help="Edit a note")
    edit_p.add_argument("note_id", type=int, nargs="?", help="Note ID to edit")
    edit_p.add_argument("--content", default=None, help="New content")
    edit_p.add_argument("--title", default=None, help="New title")
    edit_p.add_argument("--tags", default=None, help="New tags (comma-separated)")
    
    # New: Merge command
    merge_p = subparsers.add_parser("merge", help="Merge two notes")
    merge_p.add_argument("keep_id", type=int, help="ID of note to keep")
    merge_p.add_argument("delete_id", type=int, help="ID of note to delete")
    merge_p.add_argument("--confirm", action="store_true", help="Actually merge (default is dry-run)")
    
    # New: Random command
    random_p = subparsers.add_parser("random", help="Show random note for review")
    random_p.add_argument("--tag", default=None, help="Filter by tag")
    
    # New: Chat command
    chat_p = subparsers.add_parser("chat", help="Ask a question (RAG)")
    chat_p.add_argument("question", nargs="?", default="", help="Question to ask")
    chat_p.add_argument("--collection", default="notes", help="Collection to search (notes, transcripts)")
    chat_p.add_argument("--model", default="qwen3:8b", help="Ollama model to use")
    
    # New: Multi-search command
    multi_p = subparsers.add_parser("multi", help="Search multiple sources")
    multi_p.add_argument("query", nargs="?", default="", help="Search query")
    
    # Hybrid search
    hybrid_p = subparsers.add_parser("hybrid", help="Search keyword + semantic + graph")
    hybrid_p.add_argument("query", nargs="?", default="", help="Search query")
    
    # Summarize
    summarize_p = subparsers.add_parser("summarize", help="Summarize a note with AI")
    summarize_p.add_argument("note_id", type=int, nargs="?", help="Note ID to summarize")
    summarize_p.add_argument("--random", action="store_true", help="Summarize random note")
    summarize_p.add_argument("--model", default="qwen3:8b", help="Ollama model")
    
    # Flashcards
    flash_p = subparsers.add_parser("flashcard", help="Generate flashcards from note")
    flash_p.add_argument("note_id", type=int, nargs="?", help="Note ID")
    flash_p.add_argument("--random", action="store_true", help="Random note")
    flash_p.add_argument("--count", type=int, default=5, help="Number of flashcards")
    
    # Writing assist
    write_p = subparsers.add_parser("write", help="Writing assistant")
    write_p.add_argument("prompt", nargs="?", default="", help="What to write")
    write_p.add_argument("--model", default="qwen3:8b", help="Ollama model")
    
    # Streaming chat
    stream_p = subparsers.add_parser("stream", help="Chat with streaming")
    stream_p.add_argument("question", nargs="?", default="", help="Question")
    stream_p.add_argument("--model", default="qwen3:8b", help="Ollama model")
    
    subparsers.add_parser("graph", help="Graph")
    subparsers.add_parser("graph-viz", help="Graph viz")
    
    args = parser.parse_args()
    init_db()
    
    if args.command == "note": add_note(args.content, args.title, args.author, args.tags)
    elif args.command == "list": list_notes(args.limit)
    elif args.command == "graph": show_graph()
    elif args.command == "graph-viz": show_graph_html()
    elif args.command == "pdf":
        if not args.query:
            print("❌ Please provide a search term")
            print("   Usage: brain.py pdf <search_term> [directory]")
            print("   Example: brain.py pdf 'class' /media/tony/Drive2/python3/")
        else:
            search_pdfs(args.query, args.directory, args.verbose)
    elif args.command == "pdf-import":
        if not args.query:
            print("❌ Please provide a search term")
            print("   Usage: brain.py pdf-import <search_term> [directory]")
            print("   Example: brain.py pdf-import 'esp32' /media/tony/Drive2/IOT/")
            print("   With limit: brain.py pdf-import 'esp32' /media/tony/Drive2/IOT/ --limit 5")
            print("   No content: brain.py pdf-import 'esp32' /media/tony/Drive2/IOT/ --no-content")
        else:
            extract = not args.no_content
            import_pdf_search_to_notes(args.query, args.directory, args.tags, args.limit, extract_content=extract)
    elif args.command == "sync":
        sync_external_sources()
    elif args.command == "dedupe":
        duplicates = deduplicate(dry_run=not args.confirm)
        if duplicates and args.confirm:
            print("⚠️ Merge not yet implemented - run manually to review")
    elif args.command == "backlinks":
        show_backlinks()
    elif args.command == "search":
        if not args.query:
            print("❌ Please provide a search term")
            print("   Usage: brain.py search <keyword>")
            print("   Example: brain.py search python")
        else:
            search_graph(args.query, args.limit)
    elif args.command == "related":
        show_related_by_source()
    elif args.command == "ai-related":
        results = find_related_by_embedding(limit=args.limit, similarity_threshold=args.threshold)
        if results:
            print("\n🔗 AI-Related Notes (GPU-powered!):")
            print("-" * 60)
            for title1, title2, score in results:
                print(f"  {title1}")
                print(f"  ↔ {title2}")
                print(f"  Similarity: {score:.2%}")
                print()
        else:
            print("No related notes found above threshold.")
    elif args.command == "orphans":
        show_orphans()
    elif args.command == "cluster":
        cluster_by_time()
    elif args.command == "export":
        export_json(args.output)
    elif args.command == "stats":
        show_stats()
    elif args.command == "get":
        get_note(args.note_id)
    elif args.command == "edit":
        if not args.note_id:
            print("❌ Please provide a note ID")
            print("   Usage: brain.py edit <note_id> [--content 'content'] [--title 'title'] [--tags 'tag1,tag2']")
        else:
            edit_note(args.note_id, args.content, args.title, args.tags)
    elif args.command == "merge":
        merge_notes(args.keep_id, args.delete_id, dry_run=not args.confirm)
    elif args.command == "random":
        random_note(args.tag)
    elif args.command == "chat":
        if not args.question:
            print("❌ Please provide a question")
            print("   Usage: brain.py chat \"What is Python asyncio?\"")
            print("   Search transcripts: brain.py chat \"SQL tutorial\" --collection transcripts")
        else:
            chat_with_brain(args.question, args.collection, args.model)
    elif args.command == "multi":
        if not args.query:
            print("❌ Please provide a search query")
            print("   Usage: brain.py multi \"search term\"")
        else:
            multi_search(args.query)
    elif args.command == "hybrid":
        if not args.query:
            print("❌ Please provide a search query")
            print("   Usage: brain.py hybrid \"search term\"")
        else:
            hybrid_search(args.query)
    elif args.command == "summarize":
        if args.random:
            summarize_random(args.model)
        elif args.note_id:
            summarize_note(args.note_id, args.model)
        else:
            print("❌ Provide note ID or use --random")
    elif args.command == "flashcard":
        if args.random:
            flashcards_random(args.count)
        elif args.note_id:
            generate_flashcards(args.note_id, args.count)
        else:
            print("❌ Provide note ID or use --random")
    elif args.command == "write":
        if not args.prompt:
            print("❌ Provide a writing prompt")
            print("   Usage: brain.py write \"Write an email about Python\"")
        else:
            writing_assist(args.prompt, args.model)
    elif args.command == "stream":
        if not args.question:
            print("❌ Provide a question")
            print("   Usage: brain.py stream \"What is asyncio?\"")
        else:
            streaming_chat(args.question, args.model)
    elif args.command == "youtube":
        urls = [args.url] if args.url else []
        urls.extend(args.urls)
        if not urls:
            print("❌ Please provide YouTube URL(s)")
            print("   Usage: brain.py youtube <url>")
            print("   Or: brain.py youtube --urls <url1> --urls <url2>")
        else:
            for u in urls:
                import_youtube(u)
    else: parser.print_help()

if __name__ == "__main__":
    main()
