# Getting Started

This guide walks you through setting up UnrealDocWebScrapper and running your first documentation crawl.

## Prerequisites

*   Python 3.11 or higher
*   Operating System: Windows, macOS, or Linux

## Setup Instructions

1.  **Clone and Enter Repository:**
    ```bash
    git clone https://github.com/your-username/UnrealDocWebScrapper.git
    cd UnrealDocWebScrapper
    ```

2.  **Initialize Virtual Environment:**
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Install Package Dependencies:**
    Install core dependencies along with optional development dependencies:
    ```bash
    pip install -e .[dev]
    ```

4.  **Install Playwright Browser Binaries:**
    The scraper requires Chromium to render Javascript hydrated single-page applications. Install them via:
    ```bash
    playwright install chromium
    ```

---

## Running the Scraper

The primary entry point is `src/main.py`. The scraper offers several execution flags to control limits, sitemaps, and state resumption.

### 1. Fresh Run with XML Sitemaps
Discovers index lists and starts a crawl session up to a specific limit of pages:
```bash
python src/main.py --limit 100 --fresh
```

### 2. Fast Crawl skipping Sitemap checks
Directly begins crawl recursion starting from the landing documentation page:
```bash
python src/main.py --limit 10 --no-sitemap --fresh
```

### 3. Sub-section Target Crawl
Scope the crawling process to a specific sub-topic or directory by setting `--base-url`:
```bash
python src/main.py --limit 50 --base-url "https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-framework" --fresh
```

### 4. Resume an Interrupted Crawl
If a crawl session is interrupted or hits its page limit, omit the `--fresh` flag to automatically reload the serialized states:
```bash
python src/main.py --limit 200
```

---

## Verifying Scraper Outputs

Once crawled, outputs are saved into your vault directory:
1.  **Observidian Vault:** Look in `UE5_Obsidian_Vault/` directory. Files are organized into folders like `Blueprints/`, `Cplusplus/`, `Rendering/` etc.
2.  **State Logs:** The files `visited_urls.json` and `crawl_log.json` inside the `UE5_Obsidian_Vault/Meta` directory record all crawled page states and timestamps.
3.  **Wiki Links:** Open any generated markdown file in a text editor or Obsidian. Note standard double-bracket internal wiki links like `[[Actors In Unreal Engine|Actor]]` linking various files.
