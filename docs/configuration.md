# Configuration Guide

All configuration options are defined in the central configuration file [src/config.py](file:///d:/CVT%20Antrigravity%20Plan/UnrealScrap/src/config.py). You can adjust crawler speeds, browser modes, vault targets, URL exclusion rules, and automated folder mapping tags.

---

## Central Configuration Parameters

### Crawler Concurrency & Speeds

*   `CONCURRENT_REQUESTS` (Default: `16`): The maximum number of concurrent page fetching tasks across all running browsers. Setting this higher speeds up crawling but increases the risk of triggering Akamai blocking limits.
*   `NUM_BROWSERS` (Default: `3`): The number of independent Playwright Chromium browser windows spawned by the async orchestrator. Spreading concurrent tasks across multiple browsers distributes system load.
*   `REQUEST_DELAY` (Default: `1.0`): Politeness delay in seconds between sequential requests. Increasing this value acts as a safeguard against IP blocks.

### Browser Automation Modes

*   `PLAYWRIGHT_HEADLESS` (Default: `False`): Set to `False` to run the browser headfully (visible interface). **Running headfully is highly recommended** on desktop systems because it bypasses many security and Akamai bot detection signatures.
*   `PLAYWRIGHT_TIMEOUT` (Default: `60000`): Timeout in milliseconds (minimum `60000`) for loading hydrated SPA documents.

### Storage & Vault Destinations

*   `VAULT_DIR` (Default: `Path("UE5_Obsidian_Vault")`): Root path for the generated Obsidian Vault folder.
*   `META_DIR` (Default: `VAULT_DIR / "Meta"`): Folder containing serialized tracking indexes, crawl history logs, and failed tasks.

---

## URL Exclusion Filters

The list `EXCLUDED_SUBSTRINGS` filters out noise URLs:
```python
EXCLUDED_SUBSTRINGS = [
    "#",
    "?session=",
    "?application_version=",
    "/forums/",
    "/community/",
    "/marketplace/",
    "/fab/",
    "/blog/",
]
```
Add any additional URL substrings here to ignore matching segments during recursive crawling.

---

## Category Mapping & Folder Routing

The dictionary `CATEGORY_MAPPING` maps folder destinations in your Obsidian Vault to lists of target keywords found in the page path, heading titles, or body contents:

```python
CATEGORY_MAPPING = {
    "Blueprints": ["blueprint", "visual-scripting", "subsystem"],
    "Rendering": ["rendering", "materials", "graphics", "niagara", "lighting", "shadowing", "textures", "post-processing", "render"],
    "GameplayFramework": ["gameplay", "actor", "pawn", "character", "component", "framework"],
    "AI": ["ai-", "artificial-intelligence", "behavior-tree", "navigation", "mass-entity"],
    "Networking": ["networking", "replication", "multiplayer", "online", "replication"],
    "Animation": ["animation", "skeletal-mesh", "control-rig", "mover", "blend-space", "mocap"],
    "Physics": ["physics", "collision", "chaos"],
    "Audio": ["audio", "sound", "music", "audioinsights"],
    "Editor": ["editor", "tools", "pipelines", "uproperty"],
    "Cplusplus": ["cplusplus", "cpp", "programming", "automation", "api-reference", "c-plus-plus"],
}
```

If a crawled URL, title, or body text matches one of the listed keywords, the document is routed directly into that subdirectory (e.g. `Blueprints/`). Files that match no keywords are placed in the `Meta/` directory as a fallback.
