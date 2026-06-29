# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### In Progress
- Full scrape of Unreal Engine 5 documentation (knowledge graph is being incrementally expanded with each crawl session).
- MkDocs documentation site deployment via GitHub Pages.

### Completed
- Orion Collab agent integration for live vault traversal and constraint verification.

## [1.0.0] - 2026-06-29

### Added
- Core asynchronous crawler engine with Playwright Chromium browser automation.
- Multithreaded sitemap XML discovery with 100× speedup over browser-based fetching.
- Obsidian wiki-link transformer with whitespace normalization and backlinks engine.
- YAML frontmatter generation with regex-inferred metadata tags.
- Intelligent content-aware directory categorization (`Blueprints/`, `Rendering/`, `AI/`, etc.).
- Crash-resilient state resume via JSON serialization of queue, visited URLs, and failures.
- Enterprise repository structure: CI pipeline, issue/PR templates, community docs.
- Unit test suite (15 tests) covering wiki-linking, vault storage, and frontmatter generation.
- Sample output files under `samples/` for reference without committing the full vault.
