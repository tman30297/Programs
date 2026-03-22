#!/usr/bin/env python3
"""
aiassist - Local AI CLI Assistant
Uses Ollama for on-device AI assistance
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

DEFAULT_MODEL = "llama3.2:3b"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_SYSTEM = "You are a helpful, concise CLI assistant. Give short, practical answers."

MODELS_CACHE = None


def check_ollama():
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def get_models():
    global MODELS_CACHE
    if MODELS_CACHE is not None:
        return MODELS_CACHE
    
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            MODELS_CACHE = [m["name"] for m in data.get("models", [])]
            return MODELS_CACHE
    except Exception:
        return []


def list_models():
    models = get_models()
    if not models:
        print("No models found. Pull one with: ollama pull <model>")
        return
    print("Available models:")
    for m in models:
        print(f"  * {m}")


def chat(prompt, model=None, system=None, stream=True):
    model = model or DEFAULT_MODEL
    system = system or DEFAULT_SYSTEM
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "stream": stream
    }
    
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            if stream:
                for line in resp:
                    if line:
                        data = json.loads(line)
                        msg = data.get("message", {})
                        content = msg.get("content", "")
                        if content:
                            print(content, end="", flush=True)
                        if data.get("done", False):
                            print()
            else:
                data = json.loads(resp.read())
                return data.get("message", {}).get("content", "")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def summarize_file(filepath):
    try:
        with open(filepath, "r") as f:
            content = f.read(8000)
            if len(content) >= 8000:
                content += "\n[... file truncated ...]"
        
        suffix = Path(filepath).suffix
        prompt = f"Summarize this file in a few sentences:\n\n```{suffix}\n{content}```"
        return chat(prompt)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return None


def explain_code(code):
    prompt = f"Explain what this code does:\n\n```{code}```"
    return chat(prompt)


def translate_text(text, target_lang="Spanish"):
    prompt = f"Translate to {target_lang}: {text}"
    return chat(prompt)


def bash_exec(command):
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout or result.stderr
        if not output:
            output = "(no output)"
        
        prompt = f"I ran this command: {command}\n\nOutput:\n{output}\n\nExplain what happened and if there were any errors."
        return chat(prompt)
    except subprocess.TimeoutExpired:
        print("Command timed out", file=sys.stderr)
        return None


def complete(text):
    payload = {
        "model": DEFAULT_MODEL,
        "prompt": text,
        "stream": True
    }
    
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            for line in resp:
                if line:
                    data = json.loads(line)
                    resp_text = data.get("response", "")
                    if resp_text:
                        print(resp_text, end="", flush=True)
                    if data.get("done", False):
                        print()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def interactive_mode():
    print(f"AI Assist (using {DEFAULT_MODEL}). Type 'exit' to quit, 'clear' to reset.")
    
    messages = [{"role": "system", "content": DEFAULT_SYSTEM}]
    
    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ("exit", "quit"):
            break
        if user_input.lower() == "clear":
            messages = [{"role": "system", "content": DEFAULT_SYSTEM}]
            print("Conversation cleared.")
            continue
        
        messages.append({"role": "user", "content": user_input})
        
        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "stream": True
        }
        
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                print("\n", end="")
                for line in resp:
                    if line:
                        data = json.loads(line)
                        msg = data.get("message", {})
                        content = msg.get("content", "")
                        if content:
                            print(content, end="", flush=True)
                        if data.get("done", False):
                            print()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="AI CLI Assistant using local Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aiassist "What is Python?"
  aiassist -f /path/to/file
  aiassist --explain "print('hello')"
  aiassist --translate "Hello world" Spanish
  aiassist --exec "ls -la"
  aiassist --completion "def hello"
  aiassist --list
  aiassist -i
        """
    )
    
    parser.add_argument("prompt", nargs="?", help="Prompt/question")
    parser.add_argument("-m", "--model", help="Model to use")
    parser.add_argument("-s", "--system", help="System prompt")
    parser.add_argument("-f", "--file", help="Summarize file")
    parser.add_argument("--explain", help="Explain code")
    parser.add_argument("--translate", nargs="?", const="Spanish", help="Translate text")
    parser.add_argument("--exec", dest="command", help="Execute and explain command")
    parser.add_argument("--completion", help="Generate completion")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--list", action="store_true", help="List available models")
    parser.add_argument("--check", action="store_true", help="Check Ollama status")
    
    args = parser.parse_args()
    
    if not check_ollama():
        print("Ollama not running. Start with: ollama serve", file=sys.stderr)
        sys.exit(1)
    
    if args.check:
        print("Ollama is running")
        models = get_models()
        print(f"  Models: {len(models)}")
        return
    
    if args.list:
        list_models()
        return
    
    if args.interactive:
        interactive_mode()
        return
    
    if args.file:
        summarize_file(args.file)
        return
    
    if args.explain:
        explain_code(args.explain)
        return
    
    if args.translate:
        translate_text(args.prompt or "", args.translate)
        return
    
    if args.command:
        bash_exec(args.command)
        return
    
    if args.completion:
        complete(args.completion)
        return
    
    if args.prompt:
        chat(args.prompt, model=args.model, system=args.system)
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()