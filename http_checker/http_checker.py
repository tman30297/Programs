#!/usr/bin/env python3
"""
HTTP Server Checker - Check HTTP/HTTPS server status and response times
Usage: python http_checker.py <url> [options]

Examples:
    python http_checker.py https://google.com          Check a single URL
    python http_checker.py https://google.com -v      Verbose output
    python http_checker.py urls.txt                   Check URLs from file
    python http_checker.py google.com facebook.com -c 5  Check with 5 concurrent
"""

import argparse
import socket
import time
import concurrent.futures
import urllib.request
import urllib.error
import sys
from datetime import datetime


DEFAULT_TIMEOUT = 5
COMMON_PORTS = {80: 'http', 443: 'https', 8080: 'http-alt', 8443: 'https-alt'}


def check_url(url, timeout=DEFAULT_TIMEOUT, follow_redirects=True):
    """Check a URL and return status information."""
    result = {
        'url': url,
        'status': 'unknown',
        'status_code': None,
        'response_time': None,
        'error': None,
        'server': None,
        'content_type': None,
        'content_length': None
    }
    
    # Ensure URL has scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    start_time = time.time()
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; HTTP-Checker/1.0)'
        })
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result['response_time'] = (time.time() - start_time) * 1000  # ms
            result['status_code'] = response.status
            result['status'] = 'up'
            result['server'] = response.headers.get('Server', 'Unknown')
            result['content_type'] = response.headers.get('Content-Type', 'Unknown')
            result['content_length'] = response.headers.get('Content-Length', 'Unknown')
            
    except urllib.error.HTTPError as e:
        result['response_time'] = (time.time() - start_time) * 1000
        result['status_code'] = e.code
        result['status'] = 'error'
        result['error'] = str(e)
        
    except urllib.error.URLError as e:
        result['error'] = str(e.reason)
        result['status'] = 'down'
        
    except socket.timeout:
        result['status'] = 'timeout'
        result['error'] = 'Connection timed out'
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result


def check_port(host, port, timeout=3):
    """Quick port check using socket."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def extract_host(url):
    """Extract host from URL."""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.split(':')[0]
    except:
        return url


def format_response_time(ms):
    """Format response time for display."""
    if ms is None:
        return "---"
    if ms < 1000:
        return f"{ms:.0f}ms"
    return f"{ms/1000:.2f}s"


def print_result(result, verbose=False):
    """Print a single check result."""
    status_symbols = {
        'up': '✓',
        'down': '✗',
        'error': '!',
        'timeout': '⌛',
        'unknown': '?'
    }
    
    symbol = status_symbols.get(result['status'], '?')
    
    if result['status'] == 'up':
        print(f"  {symbol} {result['url']}")
        print(f"      Status: {result['status_code']} | Time: {format_response_time(result['response_time'])}")
        if verbose and result['server']:
            print(f"      Server: {result['server']}")
    else:
        print(f"  {symbol} {result['url']}")
        print(f"      Status: {result['status']}")
        if result.get('error'):
            print(f"      Error: {result['error']}")


def main():
    parser = argparse.ArgumentParser(
        description='HTTP Server Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python http_checker.py https://google.com
  python http_checker.py google.com facebook.com twitter.com
  python http_checker.py urls.txt
  python http_checker.py google.com -v
        '''
    )
    
    parser.add_argument('targets', nargs='+', help='URLs or hosts to check')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show verbose output')
    parser.add_argument('-t', '--timeout', type=int, default=DEFAULT_TIMEOUT,
                        help=f'Request timeout in seconds (default: {DEFAULT_TIMEOUT})')
    parser.add_argument('-c', '--concurrency', type=int, default=5,
                        help='Number of concurrent checks (default: 5)')
    parser.add_argument('--no-https', action='store_true',
                        help='Use HTTP instead of HTTPS')
    
    args = parser.parse_args()
    
    # Collect URLs
    urls = []
    for target in args.targets:
        # Check if it's a file
        if target.endswith('.txt'):
            try:
                with open(target, 'r') as f:
                    urls.extend(line.strip() for line in f if line.strip() and not line.startswith('#'))
            except FileNotFoundError:
                print(f"Error: File not found: {target}")
            except Exception as e:
                print(f"Error reading {target}: {e}")
        else:
            urls.append(target)
    
    if not urls:
        print("No URLs to check")
        return
    
    # Build URL list with proper scheme
    url_list = []
    for url in urls:
        if args.no_https:
            url = url.replace('https://', 'http://')
        url_list.append(url)
    
    print(f"\n{'='*60}")
    print("  HTTP SERVER CHECKER")
    print(f"{'='*60}")
    print(f"Checking {len(url_list)} URL(s)...")
    print(f"Concurrency: {args.concurrency} | Timeout: {args.timeout}s")
    print(f"{'='*60}\n")
    
    # Check URLs in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {executor.submit(check_url, url, args.timeout): url for url in url_list}
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print_result(result, args.verbose)
    
    # Summary
    up_count = sum(1 for r in results if r['status'] == 'up')
    down_count = sum(1 for r in results if r['status'] == 'down')
    error_count = sum(1 for r in results if r['status'] not in ['up', 'down'])
    
    response_times = [r['response_time'] for r in results if r['response_time']]
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total checked: {len(results)}")
    print(f"  ✓ Up: {up_count}")
    print(f"  ✗ Down: {down_count}")
    print(f"  ! Errors: {error_count}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        print(f"\nResponse times:")
        print(f"  Min: {format_response_time(min_time)}")
        print(f"  Avg: {format_response_time(avg_time)}")
        print(f"  Max: {format_response_time(max_time)}")


if __name__ == '__main__':
    main()
