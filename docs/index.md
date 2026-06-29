# UnrealDocWebScrapper

Welcome to the official documentation site for **UnrealDocWebScrapper**!

UnrealDocWebScrapper is a production-grade, highly optimized asynchronous web crawler and semantic knowledge-base generator. It is designed to index, parse, and clean Epic Games' Unreal Engine documentation, converting it into a clean, inter-linked, structured **Obsidian Vault** layout.

This vault serves as a high-fidelity local **Knowledge Layer** for downstream systems, specifically enabling AI agent platforms (like your **Orion Collab** project) to read, traverse, and verify workflows with zero runtime compilation or API lookup errors.

---

## Key Capabilities

*   **⚡ 100x Speedup Sitemap Discovery:** Bypasses heavy browser rendering by fetching and parsing sitemaps concurrently in Python thread pools.
*   **🕷️ Playwright Hydration Crawling:** Utilizes async browser workers to render Javascript SPA content, dismiss cookie consent banners, and capture dynamic HTML elements.
*   **🛡️ Anti-Bot Evasion:** Configured with browser spoofing parameters, native host contexts, and rate throttling to avoid Akamai 403 access blocks.
*   **🔗 Semantic Wiki-Link Converter:** Transforms page links into standardized Obsidian double-bracket wiki-links (`[[slug|Anchor]]`), building a local, navigable knowledge graph.
*   **🏷️ Categorization & Metadata Enrichment:** Routes files into functional folders (like `Blueprints/`, `Cplusplus/`, `Rendering/`) and automatically infers tags to append to the Markdown frontmatter.
*   **🔄 Queue Management & Persistence:** Automatically serializes pending queue states, logs, and visited registries to resume crawls instantly after a pause or crash.

---

## Quick Navigation

*   **[Getting Started](getting_started.md):** Setup instructions and first crawl guide.
*   **[Configuration Guide](configuration.md):** Customize concurrency, wait delays, categories, and browser settings.
*   **[System Architecture](architecture.md):** Dive deep into how the crawler pipeline works and integrates with the **Orion Collab** AI agents.
*   **[Developer & Contributor Guide](development.md):** Standards, testing, and contribution protocols.
