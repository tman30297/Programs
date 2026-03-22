# Disk Analyzer

Find large files and directories.

## Usage

```bash
# Analyze current directory
python disk_analyzer.py

# Analyze specific path
python disk_analyzer.py /home/user

# Top 30 results
python disk_analyzer.py /home/user -n 30
```

## How It Works

1. Scans directory recursively
2. Calculates size of each item
3. Returns top N largest files/directories
4. Shows human-readable sizes
