# Additional Research Topics - 2026-03-14

---

## 1. Cybersecurity Fundamentals

### OWASP Top 10 (2021)
1. **A01: Broken Access Control**
2. **A02: Cryptographic Failures**
3. **A03: Injection**
4. **A04: Insecure Design**
5. **A05: Security Misconfiguration**
6. **A06: Vulnerable Components**
7. **A07: Auth Failures**
8. **A08: Data Integrity Failures**
9. **A09: Logging Failures**
10. **A10: SSRF**

---

## 2. Encryption

### Symmetric
- AES (Advanced Encryption Standard)
- DES (Data Encryption Standard)
- ChaCha20

### Asymmetric
- RSA
- ECC (Elliptic Curve Cryptography)
- DSA

### Hashing
- SHA-256
- SHA-3
- Bcrypt (for passwords)
- Argon2

---

## 3. Network Protocols

### Application Layer
- HTTP/HTTPS
- DNS
- FTP
- SSH
- SMTP

### Transport Layer
- TCP
- UDP
- DCCP
- SCTP

### Network Layer
- IP (IPv4/IPv6)
- ICMP
- IGMP

---

## 4. Cloud Computing

### Service Models
| Model | Description | Examples |
|-------|-------------|----------|
| IaaS | Infrastructure | AWS EC2, GCP Compute |
| PaaS | Platform | Heroku, AWS Beanstalk |
| SaaS | Software | Gmail, Office 365 |

### Major Providers
- AWS (Amazon Web Services)
- Microsoft Azure
- Google Cloud Platform
- DigitalOcean
- Linode

---

## 5. Container Technology

### Docker Basics
```bash
# Build image
docker build -t myapp .

# Run container
docker run -d -p 8080:80 myapp

# List containers
docker ps -a

# Logs
docker logs container_id

# Exec into container
docker exec -it container_id bash
```

### Docker Compose
```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/code
  redis:
    image: redis
```

### Kubernetes
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: myapp
    image: myapp:latest
    ports:
    - containerPort: 8080
```

---

## 6. Git Best Practices

### Commands
```bash
# Branch management
git checkout -b feature/new-feature
git merge main
git rebase main

# Stashing
git stash
git stash pop
git stash list

# History
git log --oneline --graph --all
git diff HEAD~1

# Undo
git reset --soft HEAD~1
git revert HEAD
```

### Workflows
- Git Flow
- GitHub Flow
- Trunk-Based Development

---

## 7. Regular Expressions

### Common Patterns
```python
import re

# Email
email = r'^[\w\.-]+@[\w\.-]+\.\w+$'

# Phone
phone = r'^\+?1?\d{10}$'

# URL
url = r'https?://[\w\.-]+(?:/[\w\.-]*)*'

# IP Address
ip = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# Usage
pattern = re.compile(email)
result = pattern.match('user@example.com')
```

---

## 8. Data Structures

### Time Complexities
| Operation | List | Dict | Set |
|-----------|------|------|-----|
| Access | O(1) | O(1) | N/A |
| Search | O(n) | O(1) | O(n) |
| Insert | O(1)* | O(1) | O(1) |
| Delete | O(n) | O(1) | O(1) |

*Amortized

### Use Cases
- **List**: Ordered collection, index access
- **Dict**: Key-value pairs, fast lookup
- **Set**: Unique elements, membership test
- **Tuple**: Immutable sequences
- **Deque**: Fast append/pop from both ends

---

## 9. Algorithms

### Sorting
```python
# Python's built-in (Timsort)
sorted_list = sorted(items)
items.sort()

# Custom
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```

### Searching
- Binary search (sorted data)
- Linear search (unsorted)
- BFS/DFS (graphs)

---

## 10. Design Patterns

### Creational
- Singleton
- Factory
- Builder
- Prototype

### Structural
- Adapter
- Bridge
- Composite
- Decorator
- Facade
- Proxy

### Behavioral
- Observer
- Strategy
- Command
- Iterator
- State
- Template Method

---

## 11. APIs

### REST
- Resource-based URLs
- HTTP methods (GET, POST, PUT, DELETE)
- JSON responses
- Stateless

### GraphQL
- Single endpoint
- Query exactly what you need
- Strongly typed schema

### gRPC
- Protocol Buffers
- Fast binary serialization
- Bidirectional streaming

---

## 12. Authentication

### Methods
- **Basic Auth** - Username/password
- **API Keys** - Token-based
- **OAuth 2.0** - Delegated authorization
- **JWT** - JSON Web Tokens
- **SAML** - Enterprise SSO

### Implementation
```python
# JWT
import jwt

token = jwt.encode({'user': 'alice'}, 'secret', algorithm='HS256')
payload = jwt.decode(token, 'secret', algorithms=['HS256'])
```

---

## 13. Logging

### Python Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

### Log Levels
- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

---

## 14. Error Handling

### Best Practices
```python
# Specific exceptions
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
else:
    # Runs if no exception
    print(result)
finally:
    # Always runs
    cleanup()
```

### Custom Exceptions
```python
class CustomError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code
```

---

## 15. Performance Optimization

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

### Tips
- Use built-in functions
- Avoid globals in loops
- Use list comprehensions
- Cache expensive operations
- Use appropriate data structures

---

*Last Updated: 2026-03-14*
