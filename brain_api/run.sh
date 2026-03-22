#!/bin/bash
# Brain API Server Launcher
# Usage: ./run.sh [--debug] [--port 8081]

PORT=8081
DEBUG=""
HOST="0.0.0.0"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            DEBUG="--debug"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Starting Brain API Server on http://$HOST:$PORT"
python3 server.py --host "$HOST" --port "$PORT" $DEBUG