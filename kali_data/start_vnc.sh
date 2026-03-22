#!/bin/bash
# Start VNC and noVNC for Kali container

# Start Xvfb (virtual display)
Xvfb :0 -screen 0 1024x768x24 &
sleep 2

# Start x11vnc
x11vnc -display :0 -forever -shared -rfbport 6080 -bg &
sleep 2

# Start websockify for noVNC
cd /usr/share/novnc
./utils/websockify --web /usr/share/novnc 6080 localhost:6080 &

echo "VNC services started"
