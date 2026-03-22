# Python Advanced Concepts - Additional Research
## 2026-03-14

---

## 1. Abstract Base Classes (abc)

```python
import abc

class PluginBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def load(self, input):
        """Retrieve data from input source."""
        pass
    
    @abc.abstractmethod
    def save(self, output, data):
        """Save data to output."""
        pass

# Register implementation
@PluginBase.register
class MyPlugin:
    def load(self, input):
        return input.read()
    
    def save(self, output, data):
        return output.write(data)

# Check implementation
print(isinstance(MyPlugin(), PluginBase))  # True
```

---

## 2. Context Managers

```python
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    yield
    end = time.time()
    print(f"Time: {end - start:.2f}s")

# Usage
with timer():
    # code to time
    sum(range(1000000))
```

---

## 3. Descriptors

```python
class Descriptor:
    def __get__(self, obj, objtype=None):
        return getattr(obj, '_value', 0)
    
    def __set__(self, obj, value):
        obj._value = max(0, value)  # Always positive
    
    def __delete__(self, obj):
        del obj._value

class MyClass:
    value = Descriptor()

obj = MyClass()
obj.value = 10
print(obj.value)  # 10
obj.value = -5
print(obj.value)  # 0 (clamped)
```

---

## 4. Metaclasses

```python
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        namespace['created_at'] = '2026-01-01'
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=Meta):
    pass

print(MyClass.created_at)  # 2026-01-01
```

---

## 5. Data Classes

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Employee:
    name: str
    department: str
    salary: int = 0
    skills: List[str] = field(default_factory=list)
    
    def total_compensation(self):
        return self.salary

emp = Employee("Alice", "Engineering", skills=["Python", "Go"])
```

---

## 6. Named Tuples

```python
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
print(p.x, p.y)  # 10 20
print(p._fields)  # ('x', 'y')

# Methods
print(p._asdict())  # {'x': 10, 'y': 20}
p2 = p._replace(x=15)
```

---

## 7. Enums

```python
from enum import Enum, auto

class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

# Or with values
class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

print(Color.RED.name)  # RED
print(Status.PENDING.value)  # pending
```

---

## 8. Property Decorators

```python
class Temperature:
    def __init__(self):
        self._celsius = 0
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        self._celsius = value
    
    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self._celsius = (value - 32) * 5/9
```

---

## 9. Slots

```python
class WithoutSlots:
    def __init__(self, name):
        self.name = name

class WithSlots:
    __slots__ = ['name']
    def __init__(self, name):
        self.name = name

# With slots uses less memory
import sys
print(sys.getsizeof(WithoutSlots("test")))  # Larger
print(sys.getsizeof(WithSlots("test")))     # Smaller
```

---

## 10. Weak References

```python
import weakref

class Callbacks:
    def __init__(self):
        self.callbacks = []
    
    def add(self, callback):
        # Use weak reference to avoid memory leaks
        self.callbacks.append(weakref.ref(callback))
    
    def execute(self):
        for ref in self.callbacks:
            callback = ref()
            if callback:
                callback()
```

---

## 11. Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers(min_value=0, max_value=100)))
def test_sorting(numbers):
    sorted_nums = sorted(numbers)
    assert sorted_nums == numbers or sorted_nums == numbers[::-1]
    # This will fail - demonstrating property-based testing
```

---

## 12. Async/Await Deep Dive

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return {"data": "result"}

async def main():
    # Sequential
    result = await fetch_data()
    
    # Concurrent
    results = await asyncio.gather(
        fetch_data(),
        fetch_data(),
        fetch_data()
    )

asyncio.run(main())
```

---

## 13. Generators Deep Dive

```python
# Generator function
def count_up_to(n):
    i = 1
    while i <= n:
        yield i
        i += 1

# Generator expression
squares = (x**2 for x in range(10))

# Pipeline
def filter_even(numbers):
    for n in numbers:
        if n % 2 == 0:
            yield n

def double(numbers):
    for n in numbers:
        yield n * 2

result = double(filter_even(range(10)))
```

---

## 14. Coroutines

```python
async def coroutine_example():
    print("Starting")
    await asyncio.sleep(1)
    print("Middle")
    await asyncio.sleep(1)
    print("Done")

# Send values
async def bounded_counter():
    value = 0
    while True:
        new_value = yield value
        if new_value is not None:
            value = new_value
        else:
            value += 1

async def main():
    counter = bounded_counter()
    print(await counter.asend(None))    # 0 (initial)
    print(await counter.asend(10))       # 10 (set)
    print(await counter.asend(None))      # 11 (increment)
```

---

## 15. Type Hints Advanced

```python
from typing import TypeVar, Generic, Protocol, Union, Literal

T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, value: T):
        self.value = value

# Protocol (structural subtyping)
class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Circle")

# Literal types
def move(direction: Literal["up", "down", "left", "right"]) -> None:
    pass

# Union types
def process(value: int | str) -> str:
    return str(value)
```

---

*Last Updated: 2026-03-14*
