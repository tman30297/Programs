# RemindMe Daemon

Background daemon for RemindMe. Checks for due reminders every 10 seconds and sends desktop notifications.

## How It Works

- Runs in background, checks SQLite database every 10 seconds
- Sends desktop notifications via `notify-send` when reminder is due
- Uses lock file to prevent multiple instances
- Marks reminders as notified after sending

## Started Automatically

The daemon is typically started via `remindme -d start`. See `../remindme/README.md` for usage.
