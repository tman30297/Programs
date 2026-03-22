# Modern CLI Tools - 2026 Research

## Shell Enhancements

### Fish Shell (Friendly Interactive Shell)
- Autosuggestions based on history
- Syntax highlighting out of the box
- Web-based configuration
- Script compatibility with bash

### Nushell
- Structured data (tables, lists) as first-class citizens
- Pipeline data can query JSON, YAML, CSV
- Modern plugin system
- Cross-platform

### Zsh with Oh My Zsh
- Most customizable
- Massive plugin ecosystem
- Slightly higher learning curve

## Terminal Multiplexers

### tmux
- Standard for session management
- Split panes, windows, detach/attach
- Many plugins (tmuxinator for sessions)

### Zellij
- Rust-based, modern alternative
- Simpler UX than tmux
- Built-in layouts

## Productivity Tools

### fzf (Fuzzy Finder)
- Blazing fast fuzzy search
- Works with any CLI tool
- Preview pane support

### skim
- Rust rewrite of fzf
- Even faster for large datasets
- Similar interface

### bat (cat clone)
- Syntax highlighting
- Git integration
- Line numbers
- File paging

### exa (ls replacement)
- Colors for file types
- Git integration
- Tree view
- Icons support

### ripgrep (rg)
- Faster than grep/ack
- Respect .gitignore
- Multi-threaded

### fd (find alternative)
- Faster, simpler syntax
- Colored output
- Default ignore patterns

## Rich CLI UIs

### Textual
- Python framework for TUI
- Rich interactive interfaces
- Similar to React for terminals

### Bubbly
- Shell prompt framework
- Status bars, widgets

### Charcoaly
- Fast, minimal prompt

## Practical Combinations

```bash
# Recommended setup
fish + tmux + fzf + bat + exa + ripgrep + fd
```

## Resources
- github.com/junegunn/fzf
- github.com/sharkdp/bat
- github.com/sharkdp/fd
- github.com/BurntSushi/ripgrep
- github.com/ogham/exa
- github.com/nushell/nushell
