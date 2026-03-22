#!/usr/bin/env python3
"""
PDF Q&A (ChatPDF-style)
Ask questions about PDF content and get AI answers using Ollama
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Import our pdf_to_text function
sys.path.insert(0, '/media/tony/Drive2/Programs/pdf_to_text')
from pdf_to_text import pdf_to_text


def ask_ollama(question, context, model="qwen3:latest", max_context=12000):
    """Ask Ollama a question with context from the PDF."""
    
    # Truncate context if too long
    if len(context) > max_context:
        context = context[:max_context] + "\n\n[... document continues ...]"
    
    prompt = f"""You are a helpful AI assistant answering questions about a document.

Document content:
---
{context}
---

Question: {question}

Instructions:
- Answer based ONLY on the document content provided
- If the answer is not in the document, say "I don't find that information in the document"
- Be specific and reference relevant sections when possible
- If the question is unclear, ask for clarification

Answer:"""

    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/generate",
             "-d", json.dumps({
                 "model": model,
                 "prompt": prompt,
                 "stream": False,
                 "options": {"temperature": 0.3}
             })],
            capture_output=True, text=True, timeout=120
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            return {
                "success": True,
                "answer": response.get("response", "").strip(),
                "model": model
            }
        else:
            return {
                "success": False,
                "error": f"Ollama error: {result.stderr}"
            }
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Ollama request timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def pdf_qa(pdf_path, question, model="qwen3:latest", verbose=False):
    """Full pipeline: PDF -> text -> ask question."""
    
    # Step 1: Extract text
    if verbose:
        print(f"📄 Loading: {pdf_path}")
    
    result = pdf_to_text(pdf_path, verbose=False)  # Silent extraction
    
    if not result["success"]:
        return {"success": False, "error": result["error"]}
    
    # Read the extracted text
    text_path = result["output"]
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    if verbose:
        print(f"📝 Loaded {len(text)} characters")
        print(f"🤖 Asking: {question[:50]}...")
    
    # Step 2: Ask question
    answer_result = ask_ollama(question, text, model=model)
    
    if answer_result["success"]:
        return {
            "success": True,
            "pdf": pdf_path,
            "pages": result["pages"],
            "question": question,
            "answer": answer_result["answer"],
            "model": model
        }
    else:
        return {
            "success": False,
            "error": answer_result["error"]
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF Q&A - Ask questions about PDFs")
    parser.add_argument("pdf_file", help="Path to PDF file")
    parser.add_argument("question", help="Question to ask about the PDF")
    parser.add_argument("model", nargs="?", default="qwen3:latest", help="Ollama model")
    
    args = parser.parse_args()
    
    result = pdf_qa(args.pdf_file, args.question, model=args.model, verbose=True)
    
    if result["success"]:
        print(f"\n{'='*60}")
        print(f"❓ QUESTION: {result['question']}")
        print('='*60)
        print(result["answer"])
        print('='*60)
        print(f"\n✅ Answer from {result['model']} (PDF: {result['pages']} pages)")
    else:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
