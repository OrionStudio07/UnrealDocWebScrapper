import json
import logging
from datetime import datetime

from src.config import CRAWL_LOG_FILE, META_DIR

# Set up terminal logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ue_scraper")


def log_event(event_type: str, url: str, message: str, status_code=None):
    """
    Appends a structured JSON log entry to crawl_log.json.
    """
    META_DIR.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event_type,
        "url": url,
        "status_code": status_code,
        "message": message,
    }

    # Read existing or start fresh
    entries = []
    if CRAWL_LOG_FILE.exists():
        try:
            with open(CRAWL_LOG_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    entries = json.loads(content)
        except Exception as e:
            logger.warning(f"Failed to read crawl_log.json: {e}. Reinitializing.")

    entries.append(log_entry)

    try:
        with open(CRAWL_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to write to crawl_log.json: {e}")
