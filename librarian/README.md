# PDF Librarian API

FastAPI service providing HTTP access to PDF search functionality.

## Files

- `librarian_api.py` - FastAPI service

## Setup

```bash
pip install fastapi uvicorn pypdf
```

## Run

```bash
cd /media/tony/Drive2/Programs/librarian
python3 librarian_api.py
```

Service runs on **port 8083** (default; configurable)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/status` | GET | Status check |
| `/search` | POST | Search PDFs |

## Search Request

```bash
curl -X POST http://localhost:8081/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python", "limit": 5}'
```

Response:

```json
{
  "query": "python",
  "results": [
    {"filename": "book.pdf", "path": "/path/to/book.pdf", "pages": [1, 5, 10], "match_count": 3}
  ],
  "total_found": 1
}
```

## OpenClaw Integration

Add to skill definition:

```json
{
  "name": "pdf_librarian",
  "description": "Search PDF library for technical information",
  "tools": [
    {
      "name": "search_pdfs",
      "parameters": {"query": "search term"}
    }
  ]
}
```

Bridge code calls `http://localhost:8081/search` with POST payload.

---

# Project Vault (Later List)

## Files

- `project_vault.py` - Python wrapper for CSV management

## Setup

```bash
pip install pandas
```

## Run

```bash
python3 /media/tony/Drive2/Programs/librarian/project_vault.py add "Project Name" "Stack" "Notes"
python3 /media/tony/Drive2/Programs/librarian/project_vault.py list
python3 /media/tony/Drive2/Programs/librarian/project_vault.py aging
```

## CSV Location

`/media/tony/Drive2/Programs/librarian/later_list.csv`

## Obsidian Dataview

Add to Obsidian note:

```dataviewjs
dv.table(["Project Name", "Stack", "Status", "Date Added"],
  dv.io.csv("/media/tony/Drive2/Programs/librarian/later_list.csv")
  .sort(p => p["Date Added"], 'desc'))
```

## Fields

| Field | Description |
|-------|-------------|
| Project Name | Project title |
| Stack | Tech stack (comma-separated) |
| Notes | Description |
| Status | Saved for Later, Active, Archived |
| Date Added | YYYY-MM-DD |
| Days Active | Auto-calculated |

## Aging Status

- 🟢 Fresh: 0-30 days
- 🟡 Medium: 31-60 days  
- 🔴 High: 60+ days

---

# Git Auto-Sync

## Files

- `autocommit.sh` - Bash script to commit CSV changes

## Setup

```bash
chmod +x /media/tony/Drive2/Programs/librarian/autocommit.sh
```

## Cron (Optional)

```bash
# Run every hour
0 * * * * /media/tony/Drive2/Programs/librarian/autocommit.sh
```

Or use systemd path unit (see systemd docs).

---

# Weekly Report

## Files

- `weekly_report.qmd` - Quarto template

## Run

```bash
quarto render /media/tony/Drive2/Programs/librarian/weekly_report.qmd
```

Output: `weekly_report.md`

## Systemd Timer (Optional)

Create service + timer units in `/etc/systemd/system/` for automatic weekly execution.