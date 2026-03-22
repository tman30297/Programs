#!/usr/bin/env python3
"""
brain_all - Unified search across Brain, PDFs, and Memory with AI summarization

Usage:
    python3 brain_all.py "search term"
    python3 brain_all.py "search term" --smart        # Brain first, fallback to PDFs
    python3 brain_all.py "search term" --summarize    # AI summary of results
    python3 brain_all.py --gui                        # Launch web GUI
"""

import argparse
import subprocess
import json
import sys
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

# Configuration
BRAIN_CMD = ["python3", "/media/tony/Drive2/Programs/brain/brain.py"]
PDF_CMD = ["python3", "/media/tony/Drive2/Programs/pdf_search/pdf_search.py"]
MEMORY_DIR = "/home/tony/.openclaw/workspace/memory"

# PDF folders to search
PDF_FOLDERS = [
    "/media/tony/Drive2/python3/",
    "/media/tony/Drive2/Rust/",
    "/media/tony/Drive2/IOT/",
    "/media/tony/Drive2/Full_Stack_Dev/",
    "/media/tony/Drive2/Robot_OS/",
    "/media/tony/Drive2/Android/",
]

def search_brain(query, limit=5):
    """Search Brain using hybrid search"""
    try:
        result = subprocess.run(
            BRAIN_CMD + ["multi", query],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return {"source": "Brain", "results": result.stdout.strip(), "success": True}
        return {"source": "Brain", "results": "No results found", "success": False}
    except Exception as e:
        return {"source": "Brain", "results": f"Error: {str(e)}", "success": False}

def search_pdfs(query, limit=5):
    """Search PDFs in all folders"""
    all_results = []
    
    for folder in PDF_FOLDERS:
        if not os.path.exists(folder):
            continue
        try:
            result = subprocess.run(
                PDF_CMD + ["pdf", query, folder],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines[:limit]:
                    if line.strip():
                        all_results.append(line.strip())
        except Exception:
            continue
    
    if all_results:
        return {"source": "PDFs", "results": "\n".join(all_results[:limit]), "success": True}
    return {"source": "PDFs", "results": "No PDFs found", "success": False}

def search_memory(query, limit=5):
    """Search memory files"""
    try:
        result = subprocess.run(
            ["grep", "-r", "-i", query, MEMORY_DIR, "--include=*.md"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')[:limit]
            return {"source": "Memory", "results": "\n".join(lines), "success": True}
        return {"source": "Memory", "results": "No memory results found", "success": False}
    except Exception as e:
        return {"source": "Memory", "results": f"Error: {str(e)}", "success": False}

def smart_search(query, limit=5):
    """Smart search: Brain first, fallback to PDFs if needed"""
    print("🧠 Running smart search...")
    
    # First, search Brain
    brain_results = search_brain(query, limit)
    print(f"   Brain: {'✓' if brain_results['success'] else '✗'}")
    
    # Check if we have enough results
    has_brain = brain_results['success'] and "No results" not in brain_results['results']
    
    if has_brain:
        # Good Brain results, optionally add PDFs
        print("   ✓ Brain has results. Add PDFs? (use --include-pdfs)")
        return brain_results
    else:
        # No Brain results, try PDFs
        print("   ✗ No Brain results. Trying PDFs...")
        pdf_results = search_pdfs(query, limit)
        print(f"   PDFs: {'✓' if pdf_results['success'] else '✗'}")
        return pdf_results

def summarize_results(query, results):
    """Use AI to summarize search results"""
    print("\n🤖 Getting AI summary...")
    
    # Combine all results into context
    context = f"Search query: {query}\n\n"
    for source, content in results.items():
        if isinstance(content, dict):
            content = content.get('results', 'No results')
        context += f"\n=== {source} ===\n{content}\n"
    
    prompt = f"""Based on the following search results for "{query}", provide a brief summary of what was found across all sources. Focus on the most relevant information.

{context}

Summary:"""
    
    try:
        result = subprocess.run(
            BRAIN_CMD + ["chat", prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "Could not generate summary"
    except Exception as e:
        return f"Error: {str(e)}"

def run_gui():
    """Launch a simple web GUI"""
    port = 8768
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>brain_all Search</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px; margin: 0 auto; padding: 20px;
            background: #1a1a2e; color: #eee;
        }
        h1 { color: #00d9ff; text-align: center; }
        .search-box { display: flex; gap: 10px; margin-bottom: 20px; }
        input { 
            flex: 1; padding: 15px; font-size: 16px; border: none; border-radius: 8px;
            background: #16213e; color: #fff;
        }
        button { 
            padding: 15px 30px; font-size: 16px; border: none; border-radius: 8px;
            background: #00d9ff; color: #1a1a2e; cursor: pointer; font-weight: bold;
        }
        button:hover { background: #00b8d4; }
        .options { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .checkbox { display: flex; align-items: center; gap: 5px; }
        .checkbox input { width: auto; }
        #results { background: #16213e; border-radius: 8px; padding: 20px; }
        .source { margin-top: 20px; }
        .source h3 { color: #00d9ff; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .source pre { white-space: pre-wrap; word-wrap: break-word; max-height: 300px; overflow-y: auto; }
        .summary { 
            background: #0f3460; border-left: 4px solid #00d9ff; 
            padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0;
        }
        .loading { text-align: center; color: #888; }
        .error { color: #ff6b6b; }
    </style>
</head>
<body>
    <h1>🧠 brain_all Search</h1>
    <div class="search-box">
        <input type="text" id="query" placeholder="Search Brain, PDFs, Memory..." autofocus>
        <button onclick="doSearch()">Search</button>
    </div>
    <div class="options">
        <label class="checkbox"><input type="checkbox" id="smart" checked> Smart Search</label>
        <label class="checkbox"><input type="checkbox" id="summarize"> AI Summary</label>
        <label class="checkbox"><input type="checkbox" id="brain" checked> Brain</label>
        <label class="checkbox"><input type="checkbox" id="pdfs" checked> PDFs</label>
        <label class="checkbox"><input type="checkbox" id="memory" checked> Memory</label>
    </div>
    <div id="results"></div>
    
    <script>
    async function doSearch() {
        const query = document.getElementById('query').value.trim();
        if (!query) {
            alert('Please enter a search query');
            return;
        }
        
        const options = {
            smart: document.getElementById('smart').checked,
            summarize: document.getElementById('summarize').checked,
            sources: []
        };
        if (document.getElementById('brain').checked) options.sources.push('brain');
        if (document.getElementById('pdfs').checked) options.sources.push('pdf');
        if (document.getElementById('memory').checked) options.sources.push('memory');
        
        document.getElementById('results').innerHTML = '<div class="loading">Searching...</div>';
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, options })
            });
            const data = await response.json();
            if (data.error) {
                document.getElementById('results').innerHTML = '<div class="error">' + data.error + '</div>';
                return;
            }
            displayResults(data);
        } catch (e) {
            document.getElementById('results').innerHTML = '<div class="error">Error: ' + e + '</div>';
        }
    }
    
    function displayResults(data) {
        let html = '';
        
        if (data.summary) {
            html += '<div class="summary"><strong>🤖 AI Summary:</strong><br><br>' + data.summary + '</div>';
        }
        
        for (const [source, content] of Object.entries(data.results)) {
            if (content && content !== 'No results found' && !content.startsWith('Error')) {
                html += '<div class="source"><h3>' + source + '</h3><pre>' + content + '</pre></div>';
            }
        }
        
        if (!html) html = 'No results found.';
        document.getElementById('results').innerHTML = html;
    }
    
    document.getElementById('query').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') doSearch();
    });
    </script>
</body>
</html>"""
    
    # Write HTML to temp file
    html_file = "/tmp/brain_all_gui.html"
    with open(html_file, 'w') as f:
        f.write(html)
    
    # Start server
    class Handler(SimpleHTTPRequestHandler):
        def do_POST(self):
            if self.path == '/search':
                content_type = self.headers.get('Content-Type', '')
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Handle JSON or form data
                if 'application/json' in content_type:
                    data = json.loads(post_data.decode('utf-8'))
                    query = data.get('query', '')
                    opts = data.get('options', {})
                else:
                    params = parse_qs(post_data.decode('utf-8'))
                    query = params.get('query', [''])[0]
                    opts = json.loads(params.get('options', ['{}'])[0])
                
                if not query:
                    response = json.dumps({'error': 'Please provide a search query', 'results': {}})
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(response.encode())
                    return
                
                # Run search
                results = {}
                sources = opts.get('sources', ['brain', 'pdf', 'memory'])
                
                if 'brain' in sources:
                    if opts.get('smart'):
                        results['🧠 Brain'] = search_brain(query)['results']
                        if 'No results' in results.get('🧠 Brain', ''):
                            results['📄 PDFs'] = search_pdfs(query)['results']
                    else:
                        results['🧠 Brain'] = search_brain(query)['results']
                
                if 'pdf' in sources and not opts.get('smart'):
                    results['📄 PDFs'] = search_pdfs(query)['results']
                
                if 'memory' in sources:
                    results['📝 Memory'] = search_memory(query)['results']
                
                summary = None
                if opts.get('summarize'):
                    summary = summarize_results(query, results)
                
                response = json.dumps({'results': results, 'summary': summary})
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
            else:
                self.send_response(404)
                self.end_headers()
        
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            super().end_headers()
    
    # Get local IP
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname) if hostname else "localhost"
    
    server = HTTPServer(('0.0.0.0', port), Handler)
    url = f"http://localhost:{port}/brain_all_gui.html"
    
    print(f"\n🌐 Opening GUI at: {url}")
    print(f"   Or from another device: http://{local_ip}:{port}/brain_all_gui.html")
    print(f"\n   Press Ctrl+C to stop server\n")
    
    # Change to /tmp so it can find the HTML file
    os.chdir('/tmp')
    
    webbrowser.open(url)
    server.serve_forever()

def main():
    parser = argparse.ArgumentParser(description="Search Brain, PDFs, and Memory")
    parser.add_argument("query", nargs="?", help="Search term")
    parser.add_argument("--limit", type=int, default=5, help="Max results per source")
    parser.add_argument("--sources", default="brain,pdf,memory", help="Comma-separated sources")
    parser.add_argument("--smart", action="store_true", help="Smart search: Brain first, fallback to PDFs")
    parser.add_argument("--summarize", action="store_true", help="Get AI summary of results")
    parser.add_argument("--gui", action="store_true", help="Launch web GUI")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.gui:
        run_gui()
        return
    
    if not args.query:
        parser.print_help()
        return
    
    sources = [s.strip().lower() for s in args.sources.split(',')]
    results = {}
    
    print(f"\n🔍 Searching for: \"{args.query}\"")
    if args.smart:
        print("   Mode: Smart (Brain first → PDFs fallback)")
    if args.summarize:
        print("   Mode: AI Summary enabled")
    print(f"   Sources: {', '.join(sources)}\n")
    
    if args.smart:
        # Smart search
        if "brain" in sources:
            results["brain"] = search_brain(args.query, args.limit)
            if results["brain"]["success"]:
                if "pdf" in sources:
                    results["pdf"] = search_pdfs(args.query, args.limit)
        elif "pdf" in sources:
            results["pdf"] = search_pdfs(args.query, args.limit)
    else:
        # Regular parallel search
        if "brain" in sources:
            results["brain"] = search_brain(args.query, args.limit)
        if "pdf" in sources:
            results["pdf"] = search_pdfs(args.query, args.limit)
        if "memory" in sources:
            results["memory"] = search_memory(args.query, args.limit)
    
    # Print results
    for source, data in results.items():
        print(f"\n{'='*60}")
        print(f"  {source.upper()}")
        print(f"{'='*60}")
        print(data["results"])
    
    # AI Summary
    if args.summarize:
        summary = summarize_results(args.query, {k: v["results"] for k, v in results.items()})
        print(f"\n{'='*60}")
        print("  🤖 AI SUMMARY")
        print(f"{'='*60}")
        print(summary)
    
    print(f"\n{'='*60}")
    print(f"  Search complete for: \"{args.query}\"")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
