# New Programming Languages - Research Notes
## 2026-03-14

---

## 1. Systems Programming

### Rust
```rust
fn main() {
    let x = 5;
    let y = &x;  // Immutable reference
    
    println!("The value is: {}", y);
}

// Ownership example
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;  // s1 is moved to s2
    
    // println!("{}", s1);  // Error: s1 no longer valid
    println!("{}", s2);  // Works
}
```

**Key Features:**
- Memory safety without GC
- Zero-cost abstractions
- Fearless concurrency
- Pattern matching
- Type inference

### Zig
```zig
const std = @import("std");

pub fn main() void {
    const stdout = std.io.getStdOut().writer();
    stdout.print("Hello, {}!\n", .{"World"}) catch unreachable;
}
```

**Key Features:**
- No hidden memory allocation
- Manual memory management
- C interop
- Comptime (compile-time execution)

---

## 2. Web Assembly

### AssemblyScript
```typescript
export function fibonacci(n: i32): i32 {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}
```

### Rust (WASM)
```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}
```

---

## 3. Modern Alternatives

### Carbon
- C++ successor by Google
- Interoperable with C++
- Modern syntax
- Memory safety

### Mojo
- Python superset
- AI/ML optimization
- High performance
- Compatible with Python

---

## 4. Functional Languages

### Elixir
```elixir
defmodule Math do
  def factorial(0), do: 1
  def factorial(n) when n > 0 do
    n * factorial(n - 1)
  end
end
```

### Gleam
- Type-safe Erlang
- No runtime errors
- Friendly compiler

---

## 5. Scripting & Automation

### Lua
```lua
-- Simple function
function factorial(n)
  if n == 0 then
    return 1
  else
    return n * factorial(n - 1)
  end
end
```

### Julia
```julia
function fibonacci(n)
    if n <= 1
        return n
    else
        return fibonacci(n-1) + fibonacci(n-2)
    end
end

# Multiple dispatch
foo(x::String) = "string"
foo(x::Int) = "int"
```

---

## 6. Compiled Languages

### Go
```go
package main

import "fmt"

func main() {
    message := "Hello, World!"
    fmt.Println(message)
}

// Concurrency
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        results <- j * 2
    }
}
```

### Swift
```swift
func greet(name: String) -> String {
    return "Hello, \(name)!"
}

// Optionals
var name: String? = nil
let greeting = name ?? "Anonymous"
```

---

## 7. Niche Languages

### Raku (Perl 6)
```raku
sub factorial(Int $n) {
    $n <= 1 ?? 1 !! $n * factorial($n - 1)
}
```

### Nim
```nim
proc factorial(n: int): int =
  if n <= 1: 1
  else: n * factorial(n - 1)
```

---

## 8. Language Trends 2026

### Most Popular
| Language | Use Case |
|----------|----------|
| Python | AI/ML, automation |
| JavaScript | Web development |
| TypeScript | Type-safe JS |
| Rust | Systems programming |
| Go | Cloud-native |

### Growing Fast
- Rust (memory safety)
- TypeScript (web development)
- Go (simplicity, concurrency)
- Swift (Apple ecosystem)
- Kotlin (Android)

---

## 9. Comparison

### Performance
| Language | Speed | Memory |
|----------|-------|--------|
| Rust | Very Fast | Manual |
| Go | Fast | GC |
| C/C++ | Very Fast | Manual |
| Java | Fast | GC |
| Python | Slow | GC |

### Learning Curve
| Language | Difficulty |
|----------|------------|
| Python | Easy |
| Go | Easy |
| JavaScript | Medium |
| Rust | Hard |
| C++ | Hard |

---

## 10. Resources

### Learning
- rust-lang.org/learn
- golang.org/doc
- ziglang.org/learn
- mojo.ai

### Practice
- Exercism.io
- LeetCode
- Codewars

---

*Last Updated: 2026-03-14*
