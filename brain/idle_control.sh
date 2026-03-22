#!/bin/bash
# Brain Idle Monitor Control

PID_FILE="/tmp/idle_brain.pid"
LOG_FILE="/tmp/idle_brain.log"

case "$1" in
    start)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "Idle monitor already running (PID: $PID)"
                exit 1
            fi
        fi
        nohup python3 /media/tony/Drive2/Programs/brain/idle_monitor.py > $LOG_FILE 2>&1 &
        echo "Started idle monitor"
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            kill $(cat "$PID_FILE") 2>/dev/null
            rm -f "$PID_FILE"
            echo "Stopped idle monitor"
        else
            echo "Idle monitor not running"
        fi
        ;;
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "Running (PID: $PID)"
            else
                echo "Not running (stale PID file)"
            fi
        else
            echo "Not running"
        fi
        ;;
    log)
        tail -20 $LOG_FILE
        ;;
    *)
        echo "Usage: $0 {start|stop|status|log}"
        ;;
esac
