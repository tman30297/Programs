# macOS Automation with Hammerspoon - 2026

## What is Hammerspoon?
**Hammerspoon** is a powerful macOS desktop automation tool that bridges the operating system and Lua scripting. It's 228 points on Hacker News and gaining popularity for power users.

## Key Features
- **Lua-based scripting** - Easy to learn, powerful
- **System API access** - Control windows, menus, keyboard, mouse
- **Extension ecosystem** - Rich set of plugins for various tasks
- **Open source** - Free and community-driven

## Common Use Cases

### Window Management
- Snap windows to specific screen regions
- Multi-monitor setups made easy
- Window pooling across applications

### Keyboard Shortcuts
- Create custom global hotkeys
- App-specific shortcuts
- Text expansion

### Automation
- Connect app behaviors to system events
- Auto-launch app groupings
- Menu bar integrations

### System Control
- Display brightness/volume control
- WiFi/Bluetooth management
- File system monitoring

## Installation
```bash
# Via Homebrew
brew install hammerspoon --cask

# Or manual
# Download from https://github.com/Hammerspoon/hammerspoon/releases
# Drag to Applications folder
```

## Getting Started

### 1. Create init.lua
```lua
-- ~/.hammerspoon/init.lua

-- Example: Hyper key (Caps Lock) for shortcuts
hyper = {"Cmd", "Alt", "Ctrl", "Shift"}

-- Window snap bindings
hs.hotkey.bind(hyper, "H", function()
  hs.window.focusedWindow():moveToUnit(hs.layout.left50)
end)

hs.hotkey.bind(hyper, "L", function()
  hs.window.focusedWindow():moveToUnit(hs.layout.right50)
end)
```

### 2. Useful Extensions
```lua
-- Window management
hs.window.animationDuration = 0
hs.window.setShadows(false)

-- App launcher
hs.application.enableSpotlightUsage(true)

-- Clipboard history
hs.clipboard.historyCount = 100

-- Auto-reload config
hsreload = require("hsreload")
hsreload.cliAndConfig()
```

## Popular Configs to Explore
- [Sample Configurations Wiki](https://github.com/Hammerspoon/hammerspoon/wiki/Sample-Configurations)
- **Spoon** plugins - Pre-built utility packages

## Alternative: BetterTouchTool
- More GUI-focused
- Paid ($10 one-time)
- Easier for beginners but less flexible

## Alternative: Raycast (for macOS)
- Modern, free
- Command palette like Spotlight
- Extension store

## When to Use Hammerspoon
✅ Complex window management workflows  
✅ Tighter system integration needs  
✅ Custom automation pipelines  
✅ Free and open source preference  

❌ Simple hotkeys only (use Karabiner-Elements)  
❌ If you need mobile companion app  

---
*Generated: 2026-03-14*
*Source: Hacker News, GitHub*
