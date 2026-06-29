# Developer & Contributing Guide

This guide details development workflows, testing requirements, and styling guidelines for UnrealDocWebScrapper.

---

## Developer Environment Setup

1.  **Activate Virtual Environment:**
    ```bash
    # Windows:
    .venv\Scripts\activate
    # macOS/Linux:
    source .venv/bin/activate
    ```

2.  **Install Editable Developer Mode:**
    Ensure requirements and development packages are installed:
    ```bash
    pip install -e .[dev]
    ```

3.  **Install Playwright Browser Drivers:**
    Ensure the browser executable binaries are updated:
    ```bash
    playwright install chromium
    ```

---

## Code Quality & Formatting

We use **Ruff** to enforce code quality, standards, imports ordering, and formatting guidelines.

### 1. Style Checks
Run Ruff to check linting issues across all directories:
```bash
ruff check .
```

### 2. Auto-Fix Linting Issues
Ruff can automatically fix common style errors:
```bash
ruff check --fix .
```

### 3. Check Code Formatting
Verify that formatting matches styling rules:
```bash
ruff format --check .
```

### 4. Apply Code Formatting
Format files automatically:
```bash
ruff format .
```

---

## Unit Testing

All modifications must include corresponding unit tests. We use **Pytest** to manage tests.

### 1. Run Complete Test Suite
```bash
pytest
```

### 2. Run Specific Test File
```bash
pytest tests/test_wiki_linker.py
```

### 3. Run Tests with Code Coverage Reports
```bash
pytest --cov=src tests/
```

### 4. Writing Tests
Place all tests inside the `tests/` directory with filenames starting with `test_` (e.g. `tests/test_parser.py`).
Mock dynamic network requests or browser instances to ensure that the test suite runs offline and executes in under 2 seconds.
