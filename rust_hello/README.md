# Rust Hello World

A beginner-friendly Rust program demonstrating basic Rust syntax and concepts.

## What It Does

- Prints "Hello, World!" style messages
- Demonstrates Rust variables (mutable vs immutable)
- Shows function definitions and return values
- Illustrates Rust's ownership model (move vs borrow)
- Includes while and for loop examples

## How to Run

### Prerequisites

Install Rust if not already installed:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Compile and Run

```bash
cd /media/tony/Drive2/Programs/rust_hello
rustc main.rs
./main
```

Or use Cargo (recommended for larger projects):
```bash
cd /media/tony/Drive2/Programs/rust_hello
cargo run
```

## Requirements

- Rust toolchain (rustc, cargo)
- Install via: https://rustup.rs/

## Concepts Demonstrated

1. **Variables** - Immutable by default, use `mut` for mutable
2. **Functions** - Return values without `return` keyword
3. **Ownership** - Move semantics vs borrowing with references
4. **Loops** - While loops and for-each iteration
5. **Strings** - `String` type with heap allocation

## Learning Reference

This program is based on learning Rust syntax, focusing on:
- Variable declarations
- Function definitions
- Ownership and borrowing
- Control flow (loops)
