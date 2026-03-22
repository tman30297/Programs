#!/usr/bin/env python3
"""Standalone PDF search script - can be killed if it hangs."""
import sys
import json
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: pdf_search_worker.py <pdf_path> <search_term>")
    sys.exit(1)

pdf_path = sys.argv[1]
search_term = sys.argv[2].lower()

try:
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    matches = []
    
    for page_num, page in enumerate(reader.pages[:50], start=1):
        try:
            text = page.extract_text()
            if text:
                count = text.lower().count(search_term)
                if count > 0:
                    matches.append((page_num, count))
        except:
            continue
    
    if matches:
        result = {
            "filename": Path(pdf_path).name,
            "filepath": pdf_path,
            "pages": [p for p, _ in matches],
            "match_count": sum(c for _, c in matches)
        }
        print("RESULT:" + json.dumps(result))
    else:
        print("NO_MATCH")
except Exception as e:
    print("ERROR:" + str(e))
