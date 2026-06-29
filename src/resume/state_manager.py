import json
from pathlib import Path

from src.config import FAILED_URLS_FILE, META_DIR, QUEUE_STATE_FILE, SITEMAP_FILE, VISITED_URLS_FILE
from src.crawl_logging.crawl_logger import logger


def load_json_file(file_path: Path, default_value):
    """Safely loads a JSON file. Returns default_value if empty or missing."""
    if not file_path.exists():
        return default_value
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    except Exception as e:
        logger.warning(f"Error loading {file_path.name}: {e}. Starting fresh for this state.")
    return default_value


def save_json_file(file_path: Path, data):
    """Saves data to a JSON file, ensuring the parent directories exist."""
    try:
        META_DIR.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving {file_path.name}: {e}")


def load_crawl_state() -> tuple[set, dict, list, list]:
    """
    Loads all saved crawl states to resume progress.
    Returns (visited_set, failed_dict, sitemap_list, queue_list).
    """
    scraped_txt_path = META_DIR / "scraped_links.txt"
    queue_txt_path = META_DIR / "queue_links.txt"

    visited = set()
    if scraped_txt_path.exists():
        try:
            with open(scraped_txt_path, "r", encoding="utf-8") as f:
                visited = {line.strip() for line in f if line.strip()}
        except Exception as e:
            logger.warning(f"Error loading scraped_links.txt: {e}")

    if not visited:
        visited = set(load_json_file(VISITED_URLS_FILE, []))

    queue = []
    if queue_txt_path.exists():
        try:
            with open(queue_txt_path, "r", encoding="utf-8") as f:
                queue = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.warning(f"Error loading queue_links.txt: {e}")

    if not queue:
        queue = load_json_file(QUEUE_STATE_FILE, [])

    failed = load_json_file(FAILED_URLS_FILE, {})
    sitemap = load_json_file(SITEMAP_FILE, [])

    return visited, failed, sitemap, queue


def save_crawl_state(visited_set: set, failed_dict: dict, sitemap_list: list, queue_list: list):
    """Persists current crawl state to disk."""
    save_json_file(VISITED_URLS_FILE, sorted(list(visited_set)))
    save_json_file(FAILED_URLS_FILE, failed_dict)
    save_json_file(SITEMAP_FILE, sitemap_list)
    save_json_file(QUEUE_STATE_FILE, queue_list)

    # Also write plain text list of scraped and queued links
    try:
        with open(META_DIR / "scraped_links.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(list(visited_set))))
        with open(META_DIR / "queue_links.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(queue_list))
    except Exception as e:
        logger.error(f"Error saving plain text logs: {e}")
