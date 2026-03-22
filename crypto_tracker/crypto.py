#!/usr/bin/env python3
"""
Crypto Tracker CLI - Track cryptocurrency prices and portfolio
Uses CoinGecko API (free, no API key required)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Optional

# Try to import requests, install if missing
try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

API_URL = "https://api.coingecko.com/api/v3"
PORTFOLIO_FILE = os.path.expanduser("~/.crypto_portfolio.json")

COLORS = {
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "cyan": "\033[96m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def colorize(text: str, color: str) -> str:
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def get_price(coin_id: str, vs_currency: str = "usd") -> Optional[dict]:
    """Fetch current price for a cryptocurrency"""
    try:
        url = f"{API_URL}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currency,
            "include_24hr_change": "true",
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def get_prices(coin_ids: list, vs_currency: str = "usd") -> Optional[dict]:
    """Fetch prices for multiple cryptocurrencies"""
    try:
        url = f"{API_URL}/simple/price"
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": vs_currency,
            "include_24hr_change": "true",
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return None


def search_coin(query: str) -> Optional[list]:
    """Search for a cryptocurrency by name or symbol"""
    try:
        url = f"{API_URL}/search"
        params = {"query": query}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("coins", [])[:5]
    except Exception as e:
        print(f"Error searching: {e}")
        return None


def format_price(price: float) -> str:
    """Format price with appropriate decimal places"""
    if price >= 1:
        return f"${price:,.2f}"
    else:
        return f"${price:.6f}"


def format_change(change: float) -> str:
    """Format price change with color"""
    if change is None:
        return "N/A"
    arrow = "▲" if change >= 0 else "▼"
    color = "green" if change >= 0 else "red"
    return f"{colorize(arrow, color)} {abs(change):.2f}%"


def show_price(coin_id: str, vs_currency: str = "usd"):
    """Display price for a single cryptocurrency"""
    data = get_price(coin_id, vs_currency)
    if not data or coin_id not in data:
        print(f"Coin '{coin_id}' not found")
        return

    price = data[coin_id].get(vs_currency, 0)
    change = data[coin_id].get(f"{vs_currency}_24h_change")

    print(f"\n{colorize(coin_id.upper(), 'bold')}")
    print(f"  Price: {colorize(format_price(price), 'cyan')}")
    print(f"  24h:   {format_change(change)}")


def show_top(limit: int = 10, vs_currency: str = "usd"):
    """Display top cryptocurrencies by market cap"""
    try:
        url = f"{API_URL}/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": "false",
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        coins = resp.json()

        print(f"\n{colorize('Top Cryptocurrencies', 'bold')}")
        print("-" * 60)
        print(f"{'#':<3} {'Coin':<20} {'Price':<15} {'24h %':<10}")
        print("-" * 60)

        for i, coin in enumerate(coins, 1):
            name = coin["symbol"].upper()
            price = coin["current_price"]
            change = coin["price_change_percentage_24h"]
            print(
                f"{i:<3} {name:<20} {format_price(price):<15} {format_change(change):<10}"
            )
    except Exception as e:
        print(f"Error fetching top coins: {e}")


def load_portfolio() -> dict:
    """Load portfolio from file"""
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {}


def save_portfolio(portfolio: dict):
    """Save portfolio to file"""
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)


def portfolio_add(coin_id: str, amount: float):
    """Add holdings to portfolio"""
    portfolio = load_portfolio()
    if coin_id in portfolio:
        portfolio[coin_id] += amount
    else:
        portfolio[coin_id] = amount
    save_portfolio(portfolio)
    print(f"Added {amount} {coin_id.upper()} to portfolio")


def portfolio_remove(coin_id: str, amount: float):
    """Remove holdings from portfolio"""
    portfolio = load_portfolio()
    if coin_id not in portfolio:
        print(f"{coin_id.upper()} not in portfolio")
        return
    if portfolio[coin_id] < amount:
        print(f"Insufficient {coin_id.upper()} in portfolio")
        return
    portfolio[coin_id] -= amount
    if portfolio[coin_id] <= 0:
        del portfolio[coin_id]
    save_portfolio(portfolio)
    print(f"Removed {amount} {coin_id.upper()} from portfolio")


def portfolio_show(vs_currency: str = "usd"):
    """Display portfolio with current values"""
    portfolio = load_portfolio()
    if not portfolio:
        print("Portfolio is empty. Use 'portfolio add <coin> <amount>' to add holdings.")
        return

    coin_ids = list(portfolio.keys())
    prices = get_prices(coin_ids, vs_currency)

    if not prices:
        print("Error fetching prices")
        return

    print(f"\n{colorize('Your Portfolio', 'bold')}")
    print("-" * 70)
    print(f"{'Coin':<15} {'Amount':<15} {'Price':<15} {'Value':<15} {'24h':<10}")
    print("-" * 70)

    total_value = 0
    for coin_id, amount in portfolio.items():
        if coin_id not in prices:
            continue
        price = prices[coin_id].get(vs_currency, 0)
        change = prices[coin_id].get(f"{vs_currency}_24h_change")
        value = amount * price
        total_value += value

        print(
            f"{coin_id.upper():<15} {amount:<15.6f} {format_price(price):<15} "
            f"{format_price(value):<15} {format_change(change):<10}"
        )

    print("-" * 70)
    print(f"{colorize('Total Value:', 'bold')} {colorize(format_price(total_value), 'cyan')}")


def portfolio_clear():
    """Clear the entire portfolio"""
    if os.path.exists(PORTFOLIO_FILE):
        os.remove(PORTFOLIO_FILE)
        print("Portfolio cleared")


def search(query: str):
    """Search for cryptocurrencies"""
    results = search_coin(query)
    if not results:
        print(f"No results for '{query}'")
        return

    print(f"\n{colorize('Search Results', 'bold')}")
    for coin in results:
        print(f"  {coin['symbol'].upper():<10} - {coin['name']}")
        print(f"  ID: {coin['id']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Crypto Tracker CLI - Track cryptocurrency prices and portfolio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  crypto price bitcoin          Show BTC price
  crypto price ethereum         Show ETH price
  crypto top                    Show top 10 cryptos
  crypto search doge            Search for dogecoin
  crypto portfolio add bitcoin 0.5   Add 0.5 BTC to portfolio
  crypto portfolio show         Show portfolio with values
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Price command
    price_parser = subparsers.add_parser("price", help="Get price of a cryptocurrency")
    price_parser.add_argument("coin", help="Coin ID (e.g., bitcoin, ethereum)")
    price_parser.add_argument(
        "--currency", "-c", default="usd", help="Vs currency (usd, eur, etc)"
    )

    # Top command
    top_parser = subparsers.add_parser("top", help="Show top cryptocurrencies")
    top_parser.add_argument(
        "--limit", "-n", type=int, default=10, help="Number of coins to show"
    )
    top_parser.add_argument(
        "--currency", "-c", default="usd", help="Vs currency (usd, eur, etc)"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for a cryptocurrency")
    search_parser.add_argument("query", help="Search query")

    # Portfolio command
    portfolio_parser = subparsers.add_parser("portfolio", help="Manage portfolio")
    portfolio_sub = portfolio_parser.add_subparsers(dest="portfolio_action")

    portfolio_add_parser = portfolio_sub.add_parser("add", help="Add to portfolio")
    portfolio_add_parser.add_argument("coin", help="Coin ID")
    portfolio_add_parser.add_argument("amount", type=float, help="Amount")

    portfolio_remove_parser = portfolio_sub.add_parser(
        "remove", help="Remove from portfolio"
    )
    portfolio_remove_parser.add_argument("coin", help="Coin ID")
    portfolio_remove_parser.add_argument("amount", type=float, help="Amount")

    portfolio_sub.add_parser("show", help="Show portfolio")
    portfolio_sub.add_parser("clear", help="Clear portfolio")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "price":
        show_price(args.coin, args.currency)
    elif args.command == "top":
        show_top(args.limit, args.currency)
    elif args.command == "search":
        search(args.query)
    elif args.command == "portfolio":
        if args.portfolio_action == "add":
            portfolio_add(args.coin, args.amount)
        elif args.portfolio_action == "remove":
            portfolio_remove(args.coin, args.amount)
        elif args.portfolio_action == "show":
            portfolio_show()
        elif args.portfolio_action == "clear":
            portfolio_clear()
        else:
            portfolio_show()


if __name__ == "__main__":
    main()
