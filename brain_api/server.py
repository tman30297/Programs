#!/usr/bin/env python3
"""
Brain API Server - REST API for the Brain AI System
Provides HTTP access to Brain functionality for external applications.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add Brain to path
BRAIN_DIR = Path("/media/tony/Drive2/Programs/brain")
sys.path.insert(0, str(BRAIN_DIR))

# Try to import FastAPI, fallback to Flask
try:
    from fastapi import FastAPI, HTTPException, Query, Body
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FRAMEWORK = "fastapi"
except ImportError:
    from flask import Flask, request, jsonify
    FRAMEWORK = "flask"

# Configuration
BRAIN_PATH = "/media/tony/Drive2/Programs/brain/brain.py"
HOST = "0.0.0.0"
PORT = 8081
DEBUG = False

app = FastAPI() if FRAMEWORK == "fastapi" else Flask(__name__)

# CORS for FastAPI
if FRAMEWORK == "fastapi":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def run_brain_command(args: List[str], timeout: int = 60) -> Dict[str, Any]:
    """Execute a brain.py command and return parsed JSON output."""
    cmd = ["python3", BRAIN_PATH] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(BRAIN_DIR)
        )
        
        # Try to parse as JSON first
        try:
            if result.stdout.strip():
                return {"success": True, "data": json.loads(result.stdout)}
            return {"success": True, "output": result.stdout}
        except json.JSONDecodeError:
            # Return as text if not JSON
            return {
                "success": True,
                "output": result.stdout,
                "stderr": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_brain_chat(prompt: str, stream: bool = False) -> Dict[str, Any]:
    """Execute chat command."""
    cmd = ["python3", BRAIN_PATH, "chat", prompt]
    if stream:
        cmd.insert(3, "--stream")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(BRAIN_DIR)
        )
        
        if result.returncode == 0:
            return {"success": True, "response": result.stdout}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== API Routes ====================

@app.get("/")
def root():
    """API root endpoint."""
    return {
        "name": "Brain API Server",
        "version": "1.0.0",
        "framework": FRAMEWORK,
        "endpoints": {
            "notes": "/notes (GET, POST)",
            "search": "/search (GET)",
            "chat": "/chat (POST)",
            "stats": "/stats (GET)",
            "random": "/random (GET)",
            "get_note": "/notes/{note_id} (GET)",
            "youtube": "/youtube (POST)",
            "pdf_search": "/pdf/search (GET)",
            "export": "/export (GET)",
        }
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "framework": FRAMEWORK}


# ----- Notes API -----

@app.get("/notes")
def list_notes(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tag: Optional[str] = None
):
    """List all notes with optional filtering."""
    args = ["list", "--limit", str(limit), "--offset", str(offset)]
    if tag:
        args.extend(["--tag", tag])
    
    result = run_brain_command(args)
    if result.get("success"):
        return result
    raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))


@app.get("/notes/{note_id}")
def get_note(note_id: str):
    """Get a specific note by ID."""
    result = run_brain_command(["get", note_id])
    if result.get("success"):
        data = result.get("data", result.get("output", {}))
        if isinstance(data, str):
            # Try to parse the output
            try:
                data = json.loads(data) if data.startswith("{") else {"content": data}
            except:
                data = {"content": data}
        return data
    raise HTTPException(status_code=404, detail=f"Note {note_id} not found")


@app.post("/notes")
def add_note(
    content: str = Body(...),
    title: Optional[str] = Body(None),
    tags: Optional[str] = Body(None)
):
    """Add a new note."""
    args = ["note", content]
    if title:
        args.extend(["--title", title])
    if tags:
        args.extend(["--tags", tags])
    
    result = run_brain_command(args)
    if result.get("success"):
        return {"success": True, "message": "Note added", "output": result.get("output", "")}
    raise HTTPException(status_code=500, detail=result.get("error", "Failed to add note"))


@app.put("/notes/{note_id}")
def edit_note(note_id: str, content: str = Body(...)):
    """Edit an existing note."""
    result = run_brain_command(["edit", note_id, content])
    if result.get("success"):
        return {"success": True, "message": f"Note {note_id} updated"}
    raise HTTPException(status_code=500, detail=result.get("error", "Failed to edit note"))


@app.delete("/notes/{note_id}")
def delete_note(note_id: str):
    """Delete a note (if supported)."""
    # Brain may not have delete, so we return a message
    return {"success": False, "message": "Delete not implemented in Brain"}


# ----- Search API -----

@app.get("/search")
def search_notes(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Search notes."""
    result = run_brain_command(["search", query, "--limit", str(limit)])
    if result.get("success"):
        return result.get("data", {"results": result.get("output", "")})
    raise HTTPException(status_code=500, detail=result.get("error", "Search failed"))


@app.get("/hybrid")
def hybrid_search(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Hybrid search (keyword + semantic + graph)."""
    result = run_brain_command(["hybrid", query, "--limit", str(limit)])
    if result.get("success"):
        return result.get("data", {"results": result.get("output", "")})
    raise HTTPException(status_code=500, detail=result.get("error", "Search failed"))


@app.get("/multi")
def multi_search(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Search multiple sources (notes, transcripts, PDFs)."""
    result = run_brain_command(["multi", query, "--limit", str(limit)])
    if result.get("success"):
        return result.get("data", {"results": result.get("output", "")})
    raise HTTPException(status_code=500, detail=result.get("error", "Search failed"))


# ----- Chat API -----

@app.post("/chat")
def chat(
    prompt: str = Body(...),
    stream: bool = Body(False)
):
    """Ask the Brain a question (RAG)."""
    result = run_brain_chat(prompt, stream=stream)
    if result.get("success"):
        return {"response": result.get("response", "")}
    raise HTTPException(status_code=500, detail=result.get("error", "Chat failed"))


@app.post("/stream")
def chat_stream(prompt: str = Body(...)):
    """Stream chat response."""
    return chat(prompt, stream=True)


# ----- YouTube API -----

@app.post("/youtube")
def import_youtube(url: str = Body(...)):
    """Import YouTube video and transcribe."""
    result = run_brain_command(["youtube", url], timeout=300)
    if result.get("success"):
        return {"success": True, "output": result.get("output", "YouTube import started")}
    raise HTTPException(status_code=500, detail=result.get("error", "YouTube import failed"))


# ----- PDF API -----

@app.get("/pdf/search")
def pdf_search(
    query: str = Query(..., min_length=1),
    path: str = Query("/media/tony/Drive2"),
    limit: int = Query(10, ge=1, le=50)
):
    """Search PDFs."""
    result = run_brain_command(["pdf", query, path, "--limit", str(limit)])
    if result.get("success"):
        return {"results": result.get("output", "")}
    raise HTTPException(status_code=500, detail=result.get("error", "PDF search failed"))


@app.post("/pdf/import")
def pdf_import(
    query: str = Body(...),
    path: str = Body("/media/tony/Drive2")
):
    """Import PDF search results as notes."""
    result = run_brain_command(["pdf-import", query, path])
    if result.get("success"):
        return {"success": True, "output": result.get("output", "")}
    raise HTTPException(status_code=500, detail=result.get("error", "PDF import failed"))


# ----- Stats API -----

@app.get("/stats")
def get_stats():
    """Get Brain statistics."""
    result = run_brain_command(["stats"])
    if result.get("success"):
        return result.get("data", {"stats": result.get("output", "")})
    raise HTTPException(status_code=500, detail=result.get("error", "Failed to get stats"))


@app.get("/random")
def random_note():
    """Get a random note for review."""
    result = run_brain_command(["random"])
    if result.get("success"):
        return {"note": result.get("output", "")}
    raise HTTPException(status_code=500, detail=result.get("error", "Failed to get random note"))


# ----- Export API -----

@app.get("/export")
def export_data():
    """Export all Brain data as JSON."""
    result = run_brain_command(["export"])
    if result.get("success"):
        try:
            data = json.loads(result.get("output", "{}"))
            return data
        except:
            return {"export": result.get("output", "")}
    raise HTTPException(status_code=500, detail=result.get("error", "Export failed"))


# ----- Graph API -----

@app.get("/graph")
def get_graph():
    """Get knowledge graph data."""
    result = run_brain_command(["graph"])
    if result.get("success"):
        return result.get("data", {"graph": result.get("output", "")})
    raise HTTPException(status_code=500, detail=result.get("error", "Failed to get graph"))


# ----- Summarize/Flashcard API -----

@app.get("/summarize/{note_id}")
def summarize_note(note_id: str):
    """Summarize a note with AI."""
    result = run_brain_command(["summarize", note_id])
    if result.get("success"):
        return {"summary": result.get("output", "")}
    raise HTTPException(status_code=500, detail=result.get("error", "Summarize failed"))


@app.get("/flashcard/{note_id}")
def flashcard_note(note_id: str):
    """Generate flashcards from a note."""
    result = run_brain_command(["flashcard", note_id])
    if result.get("success"):
        return {"flashcards": result.get("output", "")}
    raise HTTPException(status_code=500, detail=result.get("error", "Flashcard failed"))


# ==================== Flask Routes (fallback) ====================

if FRAMEWORK == "flask":
    # Map FastAPI-style routes to Flask
    @app.route("/", methods=["GET"])
    def flask_root():
        return jsonify(root())
    
    @app.route("/health", methods=["GET"])
    def flask_health():
        return jsonify(health())
    
    @app.route("/notes", methods=["GET"])
    def flask_list_notes():
        limit = request.args.get("limit", 20, type=int)
        offset = request.args.get("offset", 0, type=int)
        tag = request.args.get("tag")
        return jsonify(list_notes(limit, offset, tag))
    
    @app.route("/notes", methods=["POST"])
    def flask_add_note():
        data = request.json
        return jsonify(add_note(data.get("content", ""), data.get("title"), data.get("tags")))
    
    @app.route("/notes/<note_id>", methods=["GET"])
    def flask_get_note(note_id):
        return jsonify(get_note(note_id))
    
    @app.route("/search", methods=["GET"])
    def flask_search():
        query = request.args.get("query", "")
        limit = request.args.get("limit", 10, type=int)
        return jsonify(search_notes(query, limit))
    
    @app.route("/chat", methods=["POST"])
    def flask_chat():
        data = request.json
        return jsonify(chat(data.get("prompt", ""), data.get("stream", False)))
    
    @app.route("/stats", methods=["GET"])
    def flask_stats():
        return jsonify(get_stats())
    
    @app.route("/random", methods=["GET"])
    def flask_random():
        return jsonify(random_note())
    
    @app.route("/export", methods=["GET"])
    def flask_export():
        return jsonify(export_data())
    
    @app.route("/graph", methods=["GET"])
    def flask_graph():
        return jsonify(get_graph())


# ==================== Main ====================

def main():
    parser = argparse.ArgumentParser(description="Brain API Server")
    parser.add_argument("--host", default=HOST, help="Host to bind to")
    parser.add_argument("--port", type=int, default=PORT, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--framework", choices=["fastapi", "flask", "auto"], default="auto",
                        help="Web framework to use")
    args = parser.parse_args()
    
    global DEBUG
    DEBUG = args.debug
    
    # Determine framework
    framework = args.framework
    if framework == "auto":
        framework = FRAMEWORK
    
    print(f"Starting Brain API Server on {args.host}:{args.port}")
    print(f"Using framework: {framework}")
    print(f"Brain path: {BRAIN_PATH}")
    print(f"\nAPI available at: http://{args.host}:{args.port}")
    print(f"Documentation: http://{args.host}:{args.port}/")
    
    if framework == "fastapi":
        uvicorn.run(app, host=args.host, port=args.port, log_level="debug" if args.debug else "info")
    else:
        app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()