# QuickLook

Unified lookup tool: dictionary, Wikipedia, unit conversion, calculator, weather.

## Requirements

```bash
pip install requests currency-converter
```

## Usage

```bash
# Dictionary lookup
quicklook.py elucidate

# Wikipedia lookup
quicklook.py wikipedia python

# Unit conversion
quicklook.py convert 100 km to mi
quicklook.py convert 50 kg to lb
quicklook.py convert 72 f to c

# Calculator
quicklook.py calc 2+2
quicklook.py calc sqrt(144)

# Weather
quicklook.py weather new york

# History
quicklook.py history
```

## Features

- Dictionary (Free Dictionary API)
- Wikipedia summaries
- Unit conversion (length, weight, volume, data, time, temp)
- Calculator with math functions
- Weather via wttr.in
- Query history
