# Backup Utility

Incremental backups with rotation.

## Usage

```bash
# Create backup
backup_util.py backup /path/to/source /path/to/backup

# With name
backup_util.py backup /home/user /backups -n myfiles

# Exclude patterns
backup_util.py backup /home/user /backups -e "*.log" -e "node_modules"

# Dry run
backup_util.py backup /home/user /backups --dry-run

# Restore
backup_util.py restore /backups/myfiles_20240101 /path/to/restore
```

## Features

- Incremental backups (only changes)
- File hash tracking
- Exclude patterns
- Dry-run mode
- Restore capability
