# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-29

### Added
- Created modernized enterprise repository structure, renaming repository configuration reference to `UnrealDocWebScrapper`.
- Established standard tool configuration files: `.gitignore` and `pyproject.toml` supporting `pytest` and `ruff`.
- Setup GitHub Actions CI workflow to run linters and unit tests automatically on PRs and merges to `main`.
- Added standard community documentation templates: `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`.
- Added new documentation site configurations with `mkdocs.yml` and extensive architectural documentation explaining the integration with the `orion collab` agentic framework.
- Formulated a standard unit testing suite inside the `tests/` directory covering wiki linking, vault classification, and tag/metadata generation.
- Added a `samples/` directory with representative files to provide immediate formatting guidance for downstream consumption on GitHub without committing the full scraped vault.
