# TUI Studio - Visual Terminal UI Design Tool

*Research: March 14, 2026*

## Overview
**TUI Studio** is a Figma-like visual editor for building TUI (Text User Interface) applications. Currently trending on Hacker News (566 points).

## What is a TUI?
Terminal User Interface - interactive apps that run entirely in the terminal (like htop, lazygit, k9s). Built from characters, colors, and ANSI escape codes.

## Features

### Visual Canvas
- Drag-and-drop components onto live canvas
- Real-time ANSI preview
- Configurable zoom levels

### 20+ Built-in Components
- Screen, Box, Button, TextInput
- Checkbox, Radio, Select, Toggle
- Text, Spinner, ProgressBar
- Table, List, Tree, Menu
- Tabs, Modal, Popover, Tooltip

### Layout Engine
- Absolute positioning
- Flexbox layout
- Grid layout
- Full property control (like CSS)

### 8 Color Themes
- Dracula, Nord, Solarized
- Monokai, Gruvbox
- Tokyo Night, Nightfox, Sonokai
- Live preview when switching

### Export to 6 Frameworks
⚠️ **Alpha:** Code export not yet functional
- **Ink** - TypeScript/React for terminal
- **BubbleTea** - Go, Elm-architecture
- **Blessed** - JavaScript/Node.js
- **Textual** - Python, modern TUI framework
- **OpenTUI** - TypeScript
- **Tview** - Go, widget-based

## Project Files
- Saved as portable `.tui` JSON files
- No account/cloud required
- Git-friendly, shareable

## Platform Status
- **macOS:** Gatekeeper blocks - need "Open Anyway"
- **Windows:** SmartScreen blocks - need "Run anyway"  
- **Linux:** Works out of the box (dpkg -i)

## Pricing
- Core editor: **Free** (early access)
- Pro tier: Planned (team features, cloud sync, priority support)

## Use Case for Tony
Great tool for building Python TUIs using **Textual** framework. Could be useful for:
- System monitoring dashboards
- CLI tool interfaces
- Developer productivity tools

---
*Source: tui.studio | Hacker News trending #13*
