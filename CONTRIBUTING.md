# Contributing to the Mother-Baby Program Paradigm

Thank you for your interest in contributing to this project!  
The Mother-Baby Program Paradigm is an open framework created and maintained by **Cherry Computer Ltd.**

We welcome contributions of all kinds: code, documentation, examples, design ideas, bug reports, and philosophical extensions of the paradigm.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Types of Contributions](#types-of-contributions)
- [Pull Request Process](#pull-request-process)
- [Branching Strategy](#branching-strategy)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Cherry Computer Ltd. Core Team](#cherry-computer-ltd-core-team)

---

## Code of Conduct

By participating in this project, you agree to uphold the following principles:

1. **Respect**: Treat all contributors with dignity and professionalism
2. **Clarity**: Write code and documentation that others can understand
3. **Openness**: Welcome diverse perspectives and approaches
4. **Quality**: Prioritize correctness, readability, and maintainability over speed
5. **Attribution**: Credit others' contributions fairly

---

## How to Contribute

### 1. Fork the Repository

```bash
git clone https://github.com/Infinite-Networker/The-Mother-Baby-Program-Paradigm.git
cd The-Mother-Baby-Program-Paradigm
git checkout -b feature/your-feature-name
```

### 2. Set Up Development Environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Make Your Changes

Follow the coding standards below.

### 4. Test Your Changes

```bash
python -m pytest tests/ -v
```

### 5. Submit a Pull Request

Push your branch and open a PR against `main`.

---

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- A virtual environment tool (`venv`, `conda`, etc.)

### Installing Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies (linting, testing, formatting)
pip install -r requirements-dev.txt
```

### Project Structure

```
The-Mother-Baby-Program-Paradigm/
├── src/
│   ├── mother/          # MotherProgram, Spawner, Evaluator, Supervisor
│   ├── baby/            # BabyProgram, WorkerBaby, AIBaby, SensorBaby
│   ├── communication/   # MessageBus, Message
│   ├── lifecycle/       # LifecycleManager
│   └── utils/           # Logger, helpers
├── tests/
│   ├── unit/            # Unit tests for individual modules
│   └── integration/     # Full pipeline tests
├── examples/
│   ├── basic/           # Simple usage examples
│   ├── advanced/        # Complex multi-baby pipelines
│   └── ai_agents/       # AI-powered baby examples
├── docs/
│   ├── diagrams/        # Architecture diagrams (ASCII + SVG)
│   ├── guides/          # How-to guides
│   ├── PHILOSOPHY.md    # The paradigm's conceptual foundation
│   └── ARCHITECTURE.md  # Technical architecture reference
└── assets/
    └── designs/         # Visual design assets (SVG, PNG)
```

---

## Coding Standards

### Python Style

- Follow **PEP 8** with a line length of **100 characters**
- Use **type hints** for all function signatures
- Use **dataclasses** for configuration and data transfer objects
- Use **ABC** for abstract base classes
- Use **`logging`** via the provided `get_logger()` utility (never `print` in production code)

### Docstrings

All public classes and functions must have docstrings:

```python
def spawn_baby(
    self,
    baby_class: Type[BabyProgram],
    task: Optional[str] = None,
    config: Optional[dict] = None,
) -> Optional[str]:
    """
    Spawn a new Baby Program.

    Args:
        baby_class: The BabyProgram subclass to instantiate.
        task: A human-readable description of the baby's purpose.
        config: Optional configuration dict to pass to the baby.

    Returns:
        The baby's unique ID string, or None if capacity is reached.

    Example:
        >>> baby_id = mother.spawn_baby(WorkerBaby, task="process_csv")
    """
```

### Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Classes | PascalCase | `MotherProgram`, `WorkerBaby` |
| Functions/Methods | snake_case | `spawn_baby()`, `report_metrics()` |
| Constants | UPPER_SNAKE_CASE | `MAX_BABIES`, `DEFAULT_HEALTH` |
| Private attributes | `_underscore_prefix` | `_babies`, `_lock` |
| Files | snake_case | `mother_program.py`, `worker_baby.py` |

---

## Types of Contributions

### 🐛 Bug Reports

Open a GitHub Issue with:
- Python version and OS
- Minimal reproducible example
- Expected vs. actual behavior
- Full stack trace if applicable

### ✨ New Baby Types

Create a new file in `src/baby/`:
- Extend `BabyProgram`
- Implement `execute()` and `report_metrics()`
- Add to `src/baby/__init__.py`
- Write unit tests in `tests/unit/`
- Add an example in `examples/`

### 🧠 New Spawn Policies

Add a new `SpawnPolicy` subclass to `src/mother/spawner.py`:
- Implement `should_spawn(mother_status)` → `bool`
- Document when the policy is appropriate

### 📚 Documentation

- Fix typos or unclear explanations in any `.md` file
- Add guides to `docs/guides/`
- Add architecture diagrams to `docs/diagrams/`
- Add code examples to `examples/`

### 🎨 Design Assets

- SVG diagrams for documentation
- Flowcharts, sequence diagrams
- Visual representations of the paradigm

---

## Pull Request Process

1. **Branch naming**: `feature/description`, `fix/description`, `docs/description`
2. **Title format**: `feat: Add TimeBasedSpawnPolicy` / `fix: Handle empty task queue` / `docs: Add SensorBaby guide`
3. **Description**: Include what you changed, why, and how to test it
4. **Tests**: All new code must include tests (≥80% coverage)
5. **Docs**: Update relevant documentation files
6. **Review**: At least one review from the Cherry Computer Ltd. core team
7. **CI**: All automated checks must pass

---

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable, released code |
| `develop` | Integration branch for next release |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `docs/*` | Documentation updates |
| `experiment/*` | Experimental / research ideas |

---

## Testing Requirements

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v

# With coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Standards

- Every new class must have a corresponding test file
- Unit tests must be independent (no shared state between tests)
- Use `setUp` / `tearDown` for Mother Program lifecycle in tests
- Integration tests should test complete data-flow scenarios
- Mock external services (APIs, DBs) — never call real services in tests

---

## Documentation Standards

- All docs are written in **Markdown**
- Code examples must be runnable (test them before submitting)
- Link between related docs where appropriate
- Include the **Cherry Computer Ltd.** attribution in all new docs

---

## Cherry Computer Ltd. Core Team

The Mother-Baby Program Paradigm is created and maintained by:

**Cherry Computer Ltd.**  
*Pioneering bio-inspired software architectures since 2024*

For questions, reach out via GitHub Issues or Discussions.

---

*Thank you for contributing to the future of bio-inspired software! 🌱*

*© 2024 Cherry Computer Ltd. — MIT License*
