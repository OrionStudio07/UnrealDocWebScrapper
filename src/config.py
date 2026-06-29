from pathlib import Path

# Scraper configuration settings
TARGET_DOMAIN = "dev.epicgames.com"
BASE_URL = "https://dev.epicgames.com/documentation/en-us/unreal-engine"
CONCURRENT_REQUESTS = 16  # Total concurrent page workers (10 per browser)
NUM_BROWSERS = 3  # Number of browser windows (instances)
REQUEST_DELAY = 1.0  # Seconds between requests (politeness delay to avoid blocks)
PLAYWRIGHT_TIMEOUT = 60000  # ms (minimum 60000 ms)
PLAYWRIGHT_HEADLESS = False  # Set to False to run headful (helps bypass Akamai 403 blocks)

# Vault Directory Settings
VAULT_DIR = Path("UE5_Obsidian_Vault")
META_DIR = VAULT_DIR / "Meta"

# State Tracking Files
VISITED_URLS_FILE = META_DIR / "visited_urls.json"
FAILED_URLS_FILE = META_DIR / "failed_urls.json"
CRAWL_LOG_FILE = META_DIR / "crawl_log.json"
SITEMAP_FILE = META_DIR / "sitemap.json"
QUEUE_STATE_FILE = META_DIR / "queue_state.json"

# Exclusion patterns for URLs
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

# Vault Subfolders Routing Rules
# Maps Obsidian folders to URL slug/content keywords
CATEGORY_MAPPING = {
    "Blueprints": ["blueprint", "visual-scripting", "subsystem"],
    "Rendering": [
        "rendering",
        "materials",
        "graphics",
        "niagara",
        "lighting",
        "shadowing",
        "textures",
        "post-processing",
        "render",
    ],
    "GameplayFramework": ["gameplay", "actor", "pawn", "character", "component", "framework"],
    "AI": ["ai-", "artificial-intelligence", "behavior-tree", "navigation", "mass-entity"],
    "Networking": ["networking", "replication", "multiplayer", "online", "replication"],
    "Animation": ["animation", "skeletal-mesh", "control-rig", "mover", "blend-space", "mocap"],
    "Physics": ["physics", "collision", "chaos"],
    "Audio": ["audio", "sound", "music", "audioinsights"],
    "Editor": ["editor", "tools", "pipelines", "uproperty"],
    "Cplusplus": ["cplusplus", "cpp", "programming", "automation", "api-reference", "c-plus-plus"],
}
