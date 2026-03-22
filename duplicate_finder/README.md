# Duplicate Finder

Find duplicate files in a directory by comparing content hashes.

## Usage

```bash
# Scan current directory
python duplicate_finder.py

# Scan specific directory
python duplicate_finder.py /home/user/downloads

# Only scan specific extensions
python duplicate_finder.py /home/user/photos -e .jpg .png .raw

# Delete duplicates (keeps newest)
python duplicate_finder.py /home/user/photos --delete

# Delete, keep oldest
python duplicate_finder.py /home/user/photos --delete --oldest
```

## Options

| Flag | Description |
|------|-------------|
| `path` | Directory to scan |
| `-e, --extensions` | File extensions to include |
| `-d, --delete` | Delete duplicates (keeps one) |
| `-o, --oldest` | Keep oldest instead of newest |
| `-q, --quiet` | Quiet mode |

## How It Works

1. Scans all files in directory
2. Calculates MD5 hash of each file
3. Groups files by hash
4. Reports duplicates with space wasted
5. Optionally deletes duplicates
