#!/usr/bin/env python3
"""
PDF Auto-Processor
Extracts text and generates AI summaries for all PDFs
Tracks progress to resume where left off
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

PDF_DIRS = [
    "/media/tony/Drive2/python3/",
    "/media/tony/Drive2/Rust/",
    "/media/tony/Drive2/IOT/",
    "/media/tony/Drive2/Full_Stack_Dev/",
    "/media/tony/Drive2/Robot_OS/",
    "/media/tony/Drive2/Android/",
    "/media/tony/Drive2/FPGA/",
    "/media/tony/Drive2/IOS/",
]

PROGRESS_FILE = "/media/tony/Drive2/Programs/pdf_to_text/progress.json"
LOG_FILE = "/media/tony/Drive2/Programs/pdf_to_text/process.log"

MODEL = "llama3.2:latest"  # Fast and reliable

def log(msg):
    """Log to file and stdout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_progress():
    """Load processing progress"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {
        "text_extracted": [],  # PDFs with .txt files
        "summarized": [],       # PDFs with summaries
        "errors": [],
        "last_run": None
    }

def save_progress(progress):
    """Save processing progress"""
    progress["last_run"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

def get_all_pdfs():
    """Get all PDFs from directories"""
    pdfs = []
    for directory in PDF_DIRS:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for f in files:
                    if f.endswith(".pdf"):
                        pdfs.append(os.path.join(root, f))
    return pdfs

# Central extracted text directory (for PDFs in folders we can't write to)
EXTRACTED_DIR = "/media/tony/Drive2/Programs/pdf_to_text/extracted/"

def get_txt_path(pdf_path):
    """Get corresponding txt path - use central extracted folder for write-protected dirs"""
    pdf_dir = os.path.dirname(pdf_path)
    filename = os.path.basename(pdf_path).replace(".pdf", ".txt")
    
    # Check if we can write to the PDF's directory
    test_file = os.path.join(pdf_dir, ".write_test")
    try:
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        # Can write - use same directory
        return pdf_path.replace(".pdf", ".txt")
    except PermissionError:
        # Can't write - use central extracted folder
        return os.path.join(EXTRACTED_DIR, filename)

def needs_text_extraction(pdf_path, progress):
    """Check if PDF needs text extraction"""
    # Use the correct txt path (central folder for write-protected dirs)
    txt_path = get_txt_path(pdf_path)
    # Need extraction if no .txt file OR .txt is older than .pdf
    if not os.path.exists(txt_path):
        return True
    try:
        if os.path.getmtime(pdf_path) > os.path.getmtime(txt_path):
            return True
    except OSError:
        return True
    return False

def needs_summary(pdf_path, progress):
    """Check if PDF needs summary"""
    # Need summary if not in summarized list
    return pdf_path not in progress.get("summarized", [])

def extract_text(pdf_path):
    """Extract text from PDF"""
    import subprocess
    txt_path = get_txt_path(pdf_path)
    # Pass output path to pdf_to_text.py
    cmd = ["python3", "/media/tony/Drive2/Programs/pdf_to_text/pdf_to_text.py", pdf_path, txt_path]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.returncode == 0

def summarize_pdf(pdf_path):
    """Generate AI summary for PDF"""
    import subprocess
    cmd = ["python3", "/media/tony/Drive2/Programs/pdf_to_text/pdf_summarize.py", pdf_path, MODEL, "detailed", "--save-brain"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return result.returncode == 0

def process_batch(max_text=20, max_summary=15):
    """Process a batch of PDFs - tuned for speed (55 min/hr, 5 min break)"""
    progress = load_progress()
    all_pdfs = get_all_pdfs()
    
    log(f"Found {len(all_pdfs)} total PDFs")
    
    # First: Text extraction
    text_count = 0
    for pdf in all_pdfs:
        if text_count >= max_text:
            break
        if pdf in progress["errors"]:
            continue
        if needs_text_extraction(pdf, progress):
            log(f"TEXT: {os.path.basename(pdf)}")
            try:
                if extract_text(pdf):
                    progress["text_extracted"].append(pdf)
                    text_count += 1
                else:
                    log(f"ERROR extracting: {pdf}")
                    progress["errors"].append(pdf)
            except Exception as e:
                log(f"ERROR: {e}")
                progress["errors"].append(pdf)
            save_progress(progress)
    
    # Second: Summaries
    sum_count = 0
    for pdf in all_pdfs:
        if sum_count >= max_summary:
            break
        if pdf in progress["errors"]:
            continue
        if needs_summary(pdf, progress):
            log(f"SUMMARY: {os.path.basename(pdf)}")
            try:
                if summarize_pdf(pdf):
                    progress["summarized"].append(pdf)
                    sum_count += 1
                else:
                    log(f"ERROR summarizing: {pdf}")
                    progress["errors"].append(pdf)
            except Exception as e:
                log(f"ERROR: {e}")
                progress["errors"].append(pdf)
            save_progress(progress)
    
    # Summary stats
    done_text = len(progress["text_extracted"])
    done_sum = len(progress["summarized"])
    total = len(all_pdfs)
    
    log(f"=== PROGRESS: {done_text}/{total} text, {done_sum}/{total} summarized, {len(progress['errors'])} errors ===")
    
    return progress

if __name__ == "__main__":
    # Process a batch each run - tuned for speed
    # Runs constantly, 5 min break each hour handled by cron
    process_batch(max_text=15, max_summary=10)
