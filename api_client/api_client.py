#!/usr/bin/env python3
"""
API Client Wrapper - A flexible HTTP API client with CLI and library support.
Supports GET, POST, PUT, DELETE, PATCH methods with authentication, headers, and JSON handling.
"""

import argparse
import json
import sys
from typing import Any, Optional
from urllib.parse import urlparse

try:
    import requests
    from requests.auth import HTTPBasicAuth, HTTPDigestAuth
except ImportError:
    print("Error: 'requests' library required. Install with: pip install requests")
    sys.exit(1)


class APIClient:
    """Flexible API client with authentication and request management."""
    
    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url.rstrip('/') if base_url else ""
        self.timeout = timeout
        self.session = requests.Session()
        self.default_headers = {}
    
    def set_header(self, key: str, value: str):
        """Set a default header for all requests."""
        self.default_headers[key] = value
    
    def set_auth(self, auth_type: str, username: str, password: str):
        """Set authentication. Types: basic, digest, bearer."""
        if auth_type == "basic":
            self.session.auth = HTTPBasicAuth(username, password)
        elif auth_type == "digest":
            self.session.auth = HTTPDigestAuth(username, password)
        elif auth_type == "bearer":
            self.set_header("Authorization", f"Bearer {password}")
        elif auth_type == "api_key":
            self.set_header("X-API-Key", password)
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
        if self.base_url:
            return f"{self.base_url}/{endpoint.lstrip('/')}"
        return endpoint
    
    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an HTTP request."""
        url = self._build_url(endpoint)
        headers = {**self.default_headers, **kwargs.pop('headers', {})}
        
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                timeout=kwargs.pop('timeout', self.timeout),
                **kwargs
            )
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            sys.exit(1)
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("PATCH", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, **kwargs)


def print_response(response: requests.Response, verbose: bool = False):
    """Print formatted response."""
    if verbose:
        print(f"\n{'='*50}")
        print(f"Status: {response.status_code} {response.reason}")
        print(f"Headers: {dict(response.headers)}")
        print(f"{'='*50}")
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError:
        print(response.text)


def main():
    parser = argparse.ArgumentParser(
        description="API Client Wrapper - HTTP API testing tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s GET https://api.example.com/users
  %(prog)s POST https://api.example.com/users -d '{"name":"John"}'
  %(prog)s GET https://api.example.com/protected -a basic user pass
  %(prog)s GET https://api.example.com/data -H "X-Custom: value"
        """
    )
    
    parser.add_argument('method', choices=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                        help='HTTP method')
    parser.add_argument('url', help='API endpoint URL')
    parser.add_argument('-d', '--data', help='JSON data to send')
    parser.add_argument('-H', '--header', action='append', dest='headers',
                        help='Custom headers (can be repeated)')
    parser.add_argument('-a', '--auth', nargs=3, metavar=('TYPE', 'USER', 'PASS'),
                        help='Auth type: basic, digest, bearer, api_key')
    parser.add_argument('-b', '--base-url', help='Base URL for relative endpoints')
    parser.add_argument('-t', '--timeout', type=int, default=30, help='Request timeout')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Build client
    client = APIClient(base_url=args.base_url or "", timeout=args.timeout)
    
    # Add headers
    if args.headers:
        for header in args.headers:
            if ':' in header:
                key, value = header.split(':', 1)
                client.set_header(key.strip(), value.strip())
    
    # Add auth
    if args.auth:
        auth_type, username, password = args.auth
        client.set_auth(auth_type, username, password)
    
    # Prepare request
    kwargs = {}
    if args.data:
        try:
            kwargs['json'] = json.loads(args.data)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --data")
            sys.exit(1)
    
    # Make request
    response = client.request(args.method, args.url, **kwargs)
    print_response(response, args.verbose)


if __name__ == "__main__":
    main()
