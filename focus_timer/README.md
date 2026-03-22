# Focus Timer

A simple productivity timer with Pomodoro support.

## Usage

```bash
# Default 25-minute timer
python focus_timer.py

# Custom time (10 minutes)
python focus_timer.py 10

# Short break
python focus_timer.py 5 --break

# Pomodoro technique
python focus_timer.py --pomodoro

# Custom pomodoro (30min work, 10min break, 3 cycles)
python focus_timer.py --pomodoro -w 30 -r 10 -c 3
```

## Options

| Flag | Description |
|------|-------------|
| `minutes` | Minutes for timer (default: 25) |
| `-p, --pomodoro` | Run Pomodoro technique |
| `-b, --break` | Short break timer |
| `-w, --work` | Work minutes (default: 25) |
| `-r, --rest` | Break minutes (default: 5) |
| `-c, --cycles` | Number of cycles (default: 4) |

## Pomodoro Technique

Default: 4 cycles of 25min work + 5min break, then a longer 15min break.

Sends desktop notifications when timer completes.
