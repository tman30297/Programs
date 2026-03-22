# Awesome Python Libraries - Research Notes
## 2026-03-14

---

## Categories of Python Libraries

### Web Frameworks
| Library | Description |
|---------|-------------|
| Django | Full-stack web framework |
| Flask | Lightweight WSGI framework |
| FastAPI | Modern, fast web framework for APIs |
| Pyramid | General-purpose web framework |
| Tornado | Async web framework |

### API & HTTP
- **requests** - HTTP library
- **httpx** - Async HTTP client
- **urllib3** - HTTP client
- **aiohttp** - Async HTTP client

### Data Science & ML
| Library | Use Case |
|---------|----------|
| NumPy | Numerical computing |
| Pandas | Data analysis |
| SciPy | Scientific computing |
| Scikit-learn | Machine learning |
| TensorFlow | Deep learning |
| PyTorch | Deep learning |
| Keras | Neural networks API |
| Matplotlib | Plotting/charting |
| Seaborn | Statistical visualization |

### Computer Vision
- **OpenCV** - Computer vision
- **Pillow** - Image processing
- **Scikit-image** - Image processing
- **PyTorchVision** - Vision models

### NLP
- **NLTK** - Natural language toolkit
- **SpaCy** - Industrial NLP
- **Transformers** - Hugging Face transformers
- **TextBlob** - NLP made easy

### Database
| Driver | Database |
|--------|----------|
| psycopg2 | PostgreSQL |
| pymysql | MySQL |
| sqlite3 | SQLite (built-in) |
| pymongo | MongoDB |
| redis | Redis |

### ORM
- **SQLAlchemy** - Database ORM
- **Django ORM** - Django's ORM
- **Peewee** - Lightweight ORM
- **Tortoise** - Async ORM

### Testing
- **pytest** - Testing framework
- **unittest** - Built-in testing
- **nose2** - Test discovery
- **hypothesis** - Property-based testing

### Async Programming
- **asyncio** - Built-in async
- **aiohttp** - Async HTTP
- **aioredis** - Async Redis
- **uvloop** - Fast event loop

### GUI
- **PyQt** - Qt bindings
- **PySide** - Qt bindings (official)
- **Tkinter** - Built-in GUI
- **Kivy** - Cross-platform GUI
- **CustomTkinter** - Modern tkinter

### Automation & DevOps
- **Fabric** - Remote execution
- **Ansible** - Configuration management
- **Salt** - Configuration management
- **Paramiko** - SSH client
- **Invoke** - Task execution

### Network Tools
- **Scapy** - Packet manipulation
- **netaddr** - Network addresses
- **dnspython** - DNS client
- **ipython** - Enhanced shell

### Security
- **cryptography** - Cryptography
- **pyOpenSSL** - SSL/TLS
- **passlib** - Password hashing
- **python-jose** - JWT handling

### CLI
- **Click** - CLI framework
- **Typer** - CLI with type hints
- **argparse** - CLI (built-in)
- **rich** - Rich terminal output

### Async Frameworks
- **FastAPI** - Async API framework
- **Starlette** - ASGI framework
- **Tornado** - Async web

---

## Package Management

### pip
```bash
pip install package
pip freeze > requirements.txt
pip install -r requirements.txt
```

### poetry
```bash
poetry new project
poetry add package
poetry install
```

### pipenv
```bash
pipenv install package
pipenv shell
```

---

## Development Tools

### Linters
- **flake8** - Style guide
- **pylint** - Code analysis
- **black** - Code formatter
- **isort** - Import sorting

### Type Checking
- **mypy** - Static type checker
- **pyright** - Microsoft's type checker

### IDEs
- **VS Code** - Visual Studio Code
- **PyCharm** - JetBrains IDE
- **Vim/Neovim** - Terminal editors
- **Emacs** - Extensible editor

---

## Resources

- **Awesome Python**: github.com/vinta/awesome-python
- **Python Docs**: docs.python.org/3/
- **PyPI**: pypi.org

---

*Last Updated: 2026-03-14*
