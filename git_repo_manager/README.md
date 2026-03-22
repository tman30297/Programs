# Git Repo Manager

Manage multiple git repositories at once.

## Usage

```bash
# Show status of all repos
python git_repo_manager.py status

# Pull all repos
python git_repo_manager.py pull

# Fetch all repos
python git_repo_manager.py fetch

# List all repos
python git_repo_manager.py list

# Show recent commits
python git_repo_manager.py recent

# Show current branch
python git_repo_manager.py branch

# Show dirty repos
python git_repo_manager.py dirty

# Backup all repos
python git_repo_manager.py backup -d /path/to/backup
```

## Commands

| Command | Description |
|---------|-------------|
| `status` | Show status of all repos |
| `pull` | Pull all repos |
| `fetch` | Fetch all repos |
| `list` | List all repos found |
| `recent` | Show recent commits |
| `branch` | Show current branch |
| `dirty` | Show repos with uncommitted changes |
| `backup` | Create bare clones backup |

## Configuration

Edit `REPO_DIRS` in the script to add directories to scan:
```python
REPO_DIRS = [
    "/media/tony/Drive2/Programs",
    "/home/tony/.openclaw/workspace",
    "/home/tony/projects",
]
```
