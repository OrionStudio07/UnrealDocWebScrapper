# Contributing to UnrealDocWebScrapper

Thank you for your interest in contributing to UnrealDocWebScrapper! As an enterprise-grade project, we follow rigorous guidelines to ensure code quality, compliance, and robustness.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

To get started with local development:

1. Clone the repository:
   ```bash
   git clone https://github.com/OrionStudio07/UnrealDocWebScrapper.git
   cd UnrealDocWebScrapper
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. Install requirements and development dependencies in editable mode:
   ```bash
   pip install -e .[dev]
   ```

4. Install Playwright browser binaries:
   ```bash
   playwright install chromium
   ```

## Development Guidelines

### Code Style & Formatting

We use **Ruff** for linting and formatting. Ensure your changes conform before opening a PR:

- Check style:
  ```bash
  ruff check .
  ```
- Format code:
  ```bash
  ruff format .
  ```

### Testing

All additions or bug fixes must include unit tests. We use **Pytest** for our test suite.

- Run unit tests:
  ```bash
  pytest
  ```
- Run tests with coverage:
  ```bash
  pytest --cov=src tests/
  ```

### Submitting Pull Requests

1. Create a new topic branch from the main branch.
2. Ensure linting passes and all unit tests succeed.
3. Write clean, commit messages following standard conventions.
4. Open a pull request using the provided [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).
5. Link any related issues solved by the pull request.
