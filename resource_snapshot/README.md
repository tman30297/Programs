# Resource Snapshot

Capture and compare system resource snapshots (CPU, memory, GPU, disk, network).

## Requirements

```bash
pip install psutil gputil
```

## Usage

```bash
# Take a snapshot
python resource_snapshot.py --take

# List snapshots
python resource_snapshot.py --list

# Show latest snapshot
python resource_snapshot.py --latest

# Compare two snapshots
python resource_snapshot.py --compare 1 2

# Watch continuously
python resource_snapshot.py --watch

# Verbose output
python resource_snapshot.py --latest -v
```

## Options

| Flag | Description |
|------|-------------|
| `--take` | Take a snapshot |
| `-l, --list` | List all snapshots |
| `--latest` | Show latest snapshot |
| `--compare` | Compare two snapshots |
| `-w, --watch` | Continuous monitoring |
| `-v, --verbose` | Verbose output |
| `-i, --interval` | Watch interval (default: 2s) |
| `-c, --count` | Iterations for watch mode |

Captures CPU, memory, GPU, disk, network, processes, and battery info.
