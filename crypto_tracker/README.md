# Crypto Tracker CLI

A command-line tool to track cryptocurrency prices and manage your portfolio.

## Features

- **Price Lookup**: Get current price and 24h change for any cryptocurrency
- **Top Coins**: View top cryptocurrencies by market cap
- **Search**: Find cryptocurrencies by name or symbol
- **Portfolio**: Track your holdings with current values

## Installation

```bash
cd /media/tony/Drive2/Programs/crypto_tracker
./install.sh
```

Add to PATH if needed:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Usage

### Get Price
```bash
crypto price bitcoin
crypto price ethereum
crypto price solana --currency eur
```

### Top Cryptocurrencies
```bash
crypto top
crypto top --limit 20
crypto top --currency eur
```

### Search
```bash
crypto search doge
crypto search bitcoin
```

### Portfolio
```bash
# Add holdings
crypto portfolio add bitcoin 0.5
crypto portfolio add ethereum 2.0

# Remove holdings
crypto portfolio remove bitcoin 0.1

# View portfolio
crypto portfolio show

# Clear portfolio
crypto portfolio clear
```

## Examples

```
$ crypto price bitcoin
BITCOIN
  Price: $67,432.50
  24h:   ▲ 2.34%

$ crypto top
Top Cryptocurrencies
------------------------------------------------------------
#  Coin               Price           24h %      
------------------------------------------------------------
1  BTC                $67,432.50      ▲ 2.34%    
2  ETH                $3,521.80       ▼ 1.22%    
3  SOL                $142.50         ▲ 5.67%    
...

$ crypto portfolio show
Your Portfolio
----------------------------------------------------------------------
Coin             Amount          Price           Value            24h       
----------------------------------------------------------------------
BITCOIN          0.500000        $67,432.50      $33,716.25       ▲ 2.34%   
ETHEREUM         2.000000        $3,521.80       $7,043.60       ▼ 1.22%   
----------------------------------------------------------------------
Total Value:                                        $40,759.85
```

## API

Uses [CoinGecko API](https://www.coingecko.com/en/api) (free, no API key required).
