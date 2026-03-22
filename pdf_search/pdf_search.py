#!/usr/bin/env python3
"""
PDF Text Search Tool

A CLI tool that searches for keywords across multiple PDF files
and shows which documents contain the search term, on which pages.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import subprocess

# Try to import pypdf, install if missing
try:
    from pypdf import PdfReader
except ImportError:
    print("Installing pypdf...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    from pypdf import PdfReader


def find_pdfs(directory: Path) -> List[Path]:
    """Recursively find all PDF files in a directory."""
    return sorted(directory.rglob("*.pdf"))


def search_pdf(pdf_path: Path, search_term: str, verbose: bool = False) -> Tuple[bool, List[int], int]:
    """
    Search for a term in a PDF file.
    
    Returns: (has_matches, list_of_page_numbers, total_matches)
    """
    try:
        reader = PdfReader(str(pdf_path))
        matches_per_page = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text()
                if text:
                    # Case-insensitive search
                    text_lower = text.lower()
                    search_lower = search_term.lower()
                    count = text_lower.count(search_lower)
                    if count > 0:
                        matches_per_page.append((page_num, count))
            except Exception as e:
                if verbose:
                    print(f"  Warning: Error extracting text from page {page_num}: {e}")
                continue
        
        total_matches = sum(count for _, count in matches_per_page)
        has_matches = len(matches_per_page) > 0
        
        return has_matches, [page for page, _ in matches_per_page], total_matches
        
    except Exception as e:
        if verbose:
            print(f"  Error reading {pdf_path.name}: {e}")
        return False, [], 0


def format_results(results: List[Dict], search_term: str) -> None:
    """Format and display search results."""
    if not results:
        print(f"\nNo PDFs found containing '{search_term}'")
        return
    
    print(f"\nFound '{search_term}' in {len(results)} PDF(s):\n")
    
    for result in results:
        pages_str = ", ".join(str(p) for p in result['pages'])
        print(f"Found in: {result['filename']}")
        print(f"  Page {pages_str} - ({result['match_count']} match{'es' if result['match_count'] != 1 else ''})")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Search for text across multiple PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pdf_search.py "python" /media/tony/Drive2/python3/
  pdf_search.py "class" --verbose
  pdf_search.py "import" /media/tony/Drive2/Rust/
        """
    )
    
    parser.add_argument(
        "search_term",
        help="Text string to search for"
    )
    
    parser.add_argument(
        "directory",
        nargs="?",
        default="/media/tony/Drive2/python3/",
        help="Directory to search (default: /media/tony/Drive2/python3/)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress and errors"
    )
    
    args = parser.parse_args()
    
    search_dir = Path(args.directory).expanduser().resolve()
    
    if not search_dir.exists():
        print(f"Error: Directory not found: {search_dir}")
        sys.exit(1)
    
    if not search_dir.is_dir():
        print(f"Error: Not a directory: {search_dir}")
        sys.exit(1)
    
    if args.verbose:
        print(f"Searching for '{args.search_term}' in: {search_dir}")
        print("Finding PDF files...")
    
    pdf_files = find_pdfs(search_dir)
    
    if not pdf_files:
        print(f"No PDF files found in {search_dir}")
        sys.exit(0)
    
    if args.verbose:
        print(f"Found {len(pdf_files)} PDF file(s)\n")
    
    results = []
    
    for i, pdf_path in enumerate(pdf_files, 1):
        if args.verbose:
            print(f"[{i}/{len(pdf_files)}] Searching {pdf_path.name}...")
        
        has_matches, pages, match_count = search_pdf(pdf_path, args.search_term, args.verbose)
        
        if has_matches:
            results.append({
                'filename': pdf_path.name,
                'filepath': pdf_path,
                'pages': pages,
                'match_count': match_count
            })
    
    # Sort by match count (most matches first)
    results.sort(key=lambda x: x['match_count'], reverse=True)
    
    # Display results
    format_results(results, args.search_term)
    
    if args.verbose and results:
        total_matches = sum(r['match_count'] for r in results)
        print(f"Total: {total_matches} match(es) across {len(results)} file(s)")


if __name__ == "__main__":
    main()
