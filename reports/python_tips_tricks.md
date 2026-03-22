# Python Tips & Tricks - Research Notes
## 2026-03-14

---

## Advanced Python Features

### 1. List Comprehensions
```python
# Basic
squares = [x**2 for x in range(10)]

# With condition
evens = [x for x in range(20) if x % 2 == 0]

# Nested
matrix = [[j for j in range(3)] for i in range(3)]
```

### 2. Dictionary Operations
```python
# Dict comprehension
{name: len(name) for name in ['alice', 'bob', 'charlie']}

# Merge dicts (Python 3.9+)
d1 = {'a': 1}
d2 = {'b': 2}
merged = d1 | d2

# Get with default
value = my_dict.get('key', 'default')
```

### 3. Collections Module
```python
from collections import Counter, defaultdict, OrderedDict

# Counter - count elements
Counter(['a', 'b', 'a', 'c', 'a'])

# defaultdict - default values
d = defaultdict(list)
d['key'].append(1)

# OrderedDict - maintains order (Python 3.7+ dicts do too)
```

### 4. Itertools
```python
import itertools

# Infinite iterators
count(10)      # 10, 11, 12, ...
cycle([1,2,3]) # 1, 2, 3, 1, 2, ...
repeat(5)      # 5, 5, 5, ...

# Combinatorics
combinations([1,2,3], 2)  # (1,2), (1,3), (2,3)
permutations([1,2,3])     # all permutations
product([1,2], [3,4])      # cartesian product
```

### 5. Functools
```python
from functools import lru_cache, partial, wraps

# Memoization
@lru_cache(maxsize=128)
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)

# Partial functions
def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)
```

### 6. Context Managers
```python
# Class-based
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

# Using contextlib
from contextlib import contextmanager

@contextmanager
def temp_file(filename):
    f = open(filename, 'w')
    try:
        yield f
    finally:
        f.close()
```

### 7. Decorators
```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end-start:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
```

### 8. Lambda Functions
```python
# Sorting with lambda
students = [('Alice', 90), ('Bob', 80), ('Charlie', 85)]
sorted_by_grade = sorted(students, key=lambda x: x[1], reverse=True)

# Map and filter
doubled = list(map(lambda x: x*2, numbers))
evens = list(filter(lambda x: x%2==0, numbers))

# Composing
from functools import reduce
sum_of_squares = reduce(lambda acc, x: acc + x**2, numbers, 0)
```

### 9. Walrus Operator (Python 3.8+)
```python
# Assign and use in same expression
if (n := len(data)) > 10:
    print(f"List has {n} elements")

# List comprehension with side effects
[y := f(x) for x in items if (y := g(x)) > 0]
```

### 10. Pattern Matching (Python 3.10+)
```python
def http_status(status):
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case int() as code if 400 <= code < 600:
            return f"Client/Server Error: {code}"
        case _:
            return "Unknown"

# Structural pattern matching
def point_classify(point):
    match point:
        case (0, 0):
            return "Origin"
        case (x, 0):
            return f"On X-axis: {x}"
        case (0, y):
            return f"On Y-axis: {y}"
        case (x, y) if x == y:
            return "Diagonal"
        case _:
            return "Arbitrary point"
```

### 11. Type Hints
```python
from typing import List, Dict, Optional, Union, Callable

def process_items(items: List[int]) -> Dict[str, int]:
    return {
        'sum': sum(items),
        'count': len(items),
        'avg': sum(items) / len(items)
    }

# Union types (Python 3.10+ can use |)
def greet(name: str | None) -> str:
    return f"Hello, {name or 'Anonymous'}"

# Callable types
def apply_func(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)
```

### 12. Exception Handling Best Practices
```python
# Multiple exceptions
try:
    risky_operation()
except (ValueError, TypeError) as e:
    log_error(e)

# Else clause (runs if no exception)
try:
    result = divide(a, b)
except ZeroDivisionError:
    print("Cannot divide by zero")
else:
    print(f"Result: {result}")

# Finally (always runs)
try:
    file = open('data.txt')
finally:
    file.close()  # Always executes
```

### 13. Generators
```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Generator expression
gen = (x**2 for x in range(10))

# itertools for generators
from itertools import islice
first_10 = islice(fibonacci(100), 10)
```

### 14. dataclasses (Python 3.7+)
```python
from dataclasses import dataclass, field

@dataclass
class Person:
    name: str
    age: int
    email: str = ""
    tags: list = field(default_factory=list)

person = Person("Alice", 30, "alice@example.com")
```

### 15. f-strings (Python 3.6+)
```python
name = "Alice"
age = 30

# Basic
f"Hello, {name}!"

# Expressions
f"In 5 years: {age + 5}"

# Formatting
f"Pi: {3.14159:.2f}"

# Debugging
f"{name=}, {age=}"
```

---

## Performance Tips

### Use Built-ins
- `sum()`, `min()`, `max()` are optimized in C
- Use `list comprehension` over `map()` unless necessary
- Use `in` operator for membership testing (set/dict are O(1))

### Avoid
- Global variables (slow lookup)
- Dot operations in loops (cache attribute lookups)
- String concatenation in loops (use join)

### Profiling
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# code to profile
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

---

## Useful Standard Library Modules

| Module | Use Case |
|--------|----------|
| `os` | OS operations |
| `sys` | System parameters |
| `pathlib` | Path manipulation |
| `json` | JSON handling |
| `re` | Regular expressions |
| `datetime` | Date/time |
| `collections` | Specialized containers |
| `itertools` | Iterator functions |
| `functools` | Higher-order functions |
| `typing` | Type hints |

---

*Last Updated: 2026-03-14*
