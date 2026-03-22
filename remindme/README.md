# RemindMe

Natural language reminder tool with desktop notifications.

## Usage

```bash
# Remind in X minutes/hours
remindme in 30 minutes "Call mom"
remindme in 2 hours "Meeting starts"

# Remind at specific time
remindme at 5pm "Check email"
remindme at 9am "Standup"

# Tomorrow
remindme tomorrow 9am "Standup"

# List reminders
remindme -l

# Clear all reminders
remindme -c

# Clear specific reminder
remindme -c 1

# Daemon management
remindme -d start   # Start background daemon
remindme -d stop    # Stop daemon
remindme -d status  # Check daemon status
```

## Features

- Natural language parsing
- Desktop notifications (notify-send)
- Background daemon for reliable reminders
- SQLite storage
- List, clear, and manage reminders
