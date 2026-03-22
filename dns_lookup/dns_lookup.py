#!/usr/bin/env python3
"""DNS Lookup Tool - Query DNS records for any domain"""

import socket
import sys
from datetime import datetime

RECORD_TYPES = {
    'A': socket.AF_INET,      # IPv4 address
    'AAAA': socket.AF_INET6,  # IPv6 address
    'CNAME': None,            # Canonical name
    'MX': None,               # Mail exchange
    'NS': None,               # Name server
    'TXT': None,              # Text record
    'SOA': None,              # Start of authority
    'PTR': None,              # Pointer (reverse DNS)
}

def lookup_record(domain: str, record_type: str = 'A') -> list:
    """Look up DNS records for a domain"""
    try:
        if record_type == 'A':
            return socket.getaddrinfo(domain, None, socket.AF_INET)
        elif record_type == 'AAAA':
            return socket.getaddrinfo(domain, None, socket.AF_INET6)
        elif record_type == 'CNAME':
            return [(socket.gethostbyname(domain),)]
        elif record_type == 'PTR':
            # Reverse lookup
            addr = socket.gethostbyname(domain)
            return [(socket.gethostbyaddr(addr)[0],)]
        else:
            # Try using socket for common types
            try:
                if record_type == 'MX':
                    import dns.resolver
                    answers = dns.resolver.resolve(domain, 'MX')
                    return [(str(rdata.exchange), rdata.preference) for rdata in answers]
                else:
                    # Fallback to basic lookup
                    result = socket.gethostbyname(domain)
                    return [(result,)]
            except ImportError:
                # No dns.resolver, just do basic lookup
                result = socket.gethostbyname(domain)
                return [(result,)]
    except socket.gaierror as e:
        return [f"Error: {e}"]
    except Exception as e:
        return [f"Error: {e}"]

def main():
    print("🔍 DNS Lookup Tool")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        domain = sys.argv[1]
        rtype = sys.argv[2].upper() if len(sys.argv) > 2 else 'A'
    else:
        domain = input("Enter domain: ").strip()
        rtype = input("Record type (A/AAAA/CNAME/MX/NS/TXT/PTR): ").strip().upper() or 'A'
    
    if not domain:
        print("Error: No domain provided")
        return
    
    # Add scheme if missing
    if not domain.startswith(('http://', 'https://', '.')):
        pass  # assume it's a bare domain
    
    # Remove scheme if present
    domain = domain.replace('https://', '').replace('http://', '').rstrip('/')
    
    print(f"\n📋 Looking up {rtype} records for: {domain}")
    print("-" * 40)
    
    results = lookup_record(domain, rtype)
    
    for i, result in enumerate(results, 1):
        if isinstance(result, tuple):
            print(f"  {i}. {' | '.join(str(r) for r in result)}")
        else:
            print(f"  {i}. {result}")
    
    print("-" * 40)
    print(f"Queried at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
