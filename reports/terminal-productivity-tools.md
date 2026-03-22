# Terminal Productivity Tools Report

## Overview
A curated list of essential terminal tools to boost productivity in the command line.

---

## Terminal Multiplexers

### Zellij
**Modern terminal workspace**

- **Website:** zellij.dev
- **Philosophy:** "Terminal Workspace with Batteries Included"
- **Language:** Rust
- **Key Features:**
  - Panes, tabs, and layouts
  - Built-in status bar
  - Scrolling support
  - Easy session sharing
  - Try without installing: `bash <(curl -L https://zellij.dev/launch)`

- **Best For:** Users wanting modern tmux alternative with better defaults

```bash
# Install
cargo install zellij

# Key shortcuts
Ctrl + p + n  # Switch panes
Ctrl + p + d  # Detach
```

### tmux
**The classic**

- **Standard:** Terminal multiplexer for 15+ years
- **Key Features:**
  - Sessions, windows, panes
  - Highly customizable
  - Scriptable
  - Massive plugin ecosystem (TPM)

- **Best For:** Power users who need maximum flexibility

```bash
# Key bindings
Ctrl+b %      # Split vertically
Ctrl+b "      # Split horizontally
Ctrl+b d      # Detach
Ctrl+b [      # Scroll mode
```

### Screen
**The original**

- Older than tmux
- Still widely used
- Less feature-rich but stable

---

## Shell Enhancements

### Starship
**Cross-shell prompt**

- **Website:** starship.rs
- **Fast:** Written in Rust
- **Minimal:** Low resource usage
- **Features:**
  - Git status
  - Runtime versions (Node, Python, etc.)
  - Customizable
  - Works with bash, zsh, fish, powershell

```bash
# Install
curl -sS https://starship.rs/install.sh | sh

# Add to .bashrc
eval "$(starship init bash)"
```

### Oh My Zsh
**Zsh framework**

- **Website:** ohmyz.sh
- **Plugins:** 100s available
- **Themes:** Hundreds of options
- **Best For:** Zsh users wanting better DX

### Fish Shell
**User-friendly shell**

- **Website:** fishshell.com
- **Philosophy:** "The user-friendly shell"
- **Features:**
  - Syntax highlighting out of the box
  - Autosuggestions
  - Web-based configuration
  - No configuration needed

---

## CLI Utilities

### fzf
**Fuzzy finder**

- **Website:** github.com/junegunn/fzf
- **Use:** Fuzzy search in terminal
- **Works with:** Files, commands, process IDs, git branches

```bash
# Install
git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
~/.fzf/install

# Usage
Ctrl + T   # Search files
Alt + C    # cd into directory
```

### bat
**Better cat**

- **Website:** github.com/sharkdp/bat
- **Alternatives:** cat with syntax highlighting, line numbers, git diff

```bash
# Install
cargo install bat

# Usage
bat main.py
```

### eza
**Modern ls**

- **Website:** github.com/eza-community/eza
- **Features:**
  - Icons
  - Git status
  - Colors
  - Long format improvements

```bash
# Install
cargo install eza

# Usage
eza -la --icons --git
```

### dust
**Better du**

- **Website:** github.com/bootandy/dust
- **Visualize:** Directory sizes with nice charts

### bottom
**System monitor**

- **Website:** github.com/ClementTsang/bottom
- **Like:** htop but cross-platform and modern

### tldr
**Simplified man pages**

- **Website:** tldr.sh
- **Examples:** Practical examples instead of comprehensive docs

```bash
# Install
npm install -g tldr

# Usage
tldr tar
```

### httpie
**HTTP client**

- **Website:** httpie.io
- **Like:** curl but human-friendly

```bash
# Install
pip install httpie

# Usage
http GET api.example.com/users
```

### tldr-pages
**Simplified manual pages**
- Community-driven simplified man pages

---

## Git CLI Tools

### lazygit
**TUI for git**

- **Website:** jesseduffield.com/lazygit
- **Features:**
  - Visual git operations
  - Easy staging, committing, pushing
  - Merge conflict resolution

```bash
# Install
cargo install lazygit

# Run
lazygit
```

### gh CLI
**GitHub CLI**

- **Website:** cli.github.com
- **Features:**
  - PRs, issues, releases from CLI
  - GitHub Actions management
  - Gist management

```bash
# Install
brew install gh

# Create PR
gh pr create
```

### gitui
**Fast git TUI**

- **Website:** github.com/extrawurst/gitui
- **Written in:** Rust
- **Fast:** Blazing fast git operations

---

## Database Clients

### pgcli
**PostgreSQL CLI**

- **Website:** pgcli.com
- **Features:**
  - Auto-completion
  - Syntax highlighting
  - Multi-line support

```bash
# Install
pip install pgcli

# Usage
pgcli -h localhost -U postgres -d mydb
```

### mycli
**MySQL/MariaDB CLI**

- Similar to pgcli for MySQL

---

## Network Tools

### curlie
**HTTP client**

- **Website:** rscurlie.github.io/rscurlie
- **Front-end:** for curlb with power

### httpie
**Human-friendly HTTP**

- See CLI Utilities above

---

## Productivity Tips

### 1. Master Your Multiplexer
- Use Zellij or tmux daily
- Keep sessions persistent
- Use layouts for different workflows

### 2. Fuzzy Finding Everywhere
- fzf for files, commands, git
- Integrate into shell

### 3. Aliases and Functions
```bash
# Add to .bashrc/.zshrc
alias ll='eza -la --icons --git'
alias cat='bat'
alias find='fzf'
```

### 4. Starship Prompt
- Install once, use everywhere
- Shows context automatically

### 5. Learn Keyboard Shortcuts
- Ctrl+r (reverse search)
- Ctrl+a/e (line start/end)
- Ctrl+w (delete word)
- Ctrl+u (clear line)

---

## Installation Quick Reference

```bash
# macOS
brew install zellij starship fzf bat eza dust bottom tldr lazygit gh gitui pgcli

# Linux (cargo)
cargo install zellij starship fzf bat eza dust bottom tldr lazygit gitui

# Python
pip install httpie pgcli mycli
```

---

## Summary

| Category | Recommended Tools |
|----------|-------------------|
| Multiplexer | Zellij (modern) or tmux (classic) |
| Prompt | Starship |
| File ops | eza, bat, fzf |
| System | bottom, dust |
| Git | lazygit, gh |
| Database | pgcli, mycli |

---

*Report generated: 2026-03-14*
*Location: /media/tony/Drive2/Programs/reports/*
