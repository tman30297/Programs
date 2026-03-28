#!/usr/bin/env python3
"""
PDF Librarian API - FastAPI Service

FastAPI wrapper around pdf_search for HTTP access.
Provides semantic and keyword search across PDF library.
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pdf_search"))
from pdf_search import search_pdf, find_pdfs

app = FastAPI(title="PDF Librarian API", version="1.0.0")

# Configuration
PDF_DIR = os.environ.get("PDF_DIR", "/media/tony/Drive2/")
DEFAULT_LIMIT = 10

class SearchQuery(BaseModel):
    query: str
    directory: Optional[str] = None
    limit: Optional[int] = DEFAULT_LIMIT
    verbose: Optional[bool] = False

class SearchResult(BaseModel):
    filename: str
    path: str
    pages: List[int]
    match_count: int

@app.get("/")
async def root():
    return {"service": "PDF Librarian API", "version": "1.0.0", "docs": "/docs"}

@app.get("/status")
async def status():
    return {"status": "ok", "pdf_dir": PDF_DIR}

class SearchRequest(BaseModel):
    query: str
    directory: Optional[str] = None
    limit: int = DEFAULT_LIMIT

@app.post("/search")
async def search_pdfs(req: SearchRequest):
    """Search PDFs for a query string."""
    pdf_dir = req.directory or PDF_DIR
    dir_path = Path(pdf_dir)
    
    if not dir_path.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {pdf_dir}")
    
    results = []
    pdfs = find_pdfs(dir_path)
    
    for pdf_path in pdfs:
        has_matches, pages, count = search_pdf(pdf_path, req.query, req.verbose)
        if has_matches:
            results.append({
                "filename": pdf_path.name,
                "path": str(pdf_path),
                "pages": pages,
                "match_count": count
            })
            if len(results) >= req.limit:
                break
    
    return {"query": req.query, "results": results, "total_found": len(results)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)