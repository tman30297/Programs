#!/usr/bin/env python3
"""
PDF Librarian API - FastAPI Service

FastAPI wrapper for PDF search.
"""

import os
import io
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pypdf import PdfReader

app = FastAPI(title="PDF Librarian API", version="1.0.0")

# Configuration
PDF_DIR = os.environ.get("PDF_DIR", "/media/tony/Drive2/")
PROG_DIRS = ["/media/tony/Drive2/python3/", "/media/tony/Drive2/Rust/"]
DEFAULT_LIMIT = 10

class SearchRequest(BaseModel):
    query: str
    directory: Optional[str] = None
    limit: int = DEFAULT_LIMIT
    verbose: bool = False

def find_pdfs(directory: Path) -> List[Path]:
    return sorted(directory.rglob("*.pdf"))

def is_valid_pdf(file_path: Path) -> bool:
    """Check if file starts with PDF header."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(5)
        return header == b'%PDF-'
    except:
        return False

def search_pdf(pdf_path: Path, search_term: str, verbose: bool = False):
    if not is_valid_pdf(pdf_path):
        return []
    try:
        reader = PdfReader(str(pdf_path))
        matches = []
        for page_num, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text()
                if text and search_term.lower() in text.lower():
                    matches.append(page_num)
            except:
                continue
        return matches
    except:
        return []

@app.get("/")
async def root():
    return {"service": "PDF Librarian API", "version": "1.0.0"}

@app.get("/status")
async def status():
    return {"status": "ok", "pdf_dir": PDF_DIR}

@app.post("/search/prog")
async def search_prog(req: SearchRequest):
    """Search programming-focused PDFs only."""
    results = []
    for prog_dir in PROG_DIRS:
        dir_path = Path(prog_dir)
        if not dir_path.exists():
            continue
        pdfs = find_pdfs(dir_path)
        for pdf_path in pdfs:
            pages = search_pdf(pdf_path, req.query, req.verbose)
            if pages:
                results.append({
                    "filename": pdf_path.name,
                    "path": str(pdf_path),
                    "pages": pages[:5],
                    "match_count": len(pages)
                })
                if len(results) >= req.limit:
                    break
        if len(results) >= req.limit:
            break
    
    log_search(req.query, len(results))
    return {"query": req.query, "results": results[:req.limit], "total_found": len(results)}

# Import audit log
import sys
sys.path.insert(0, str(Path(__file__).parent))
from search_log import log_search

@app.post("/search")
async def search_pdfs(req: SearchRequest):
    pdf_dir = req.directory or PDF_DIR
    dir_path = Path(pdf_dir)
    
    if not dir_path.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {pdf_dir}")
    
    results = []
    pdfs = find_pdfs(dir_path)
    
    for pdf_path in pdfs:
        pages = search_pdf(pdf_path, req.query, req.verbose)
        if pages:
            results.append({
                "filename": pdf_path.name,
                "path": str(pdf_path),
                "pages": pages,
                "match_count": len(pages)
            })
            if len(results) >= req.limit:
                break
    
    # Log the search
    log_search(req.query, len(results))
    
    return {"query": req.query, "results": results, "total_found": len(results)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)