import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import asyncio

from src.config import CRAWL_LOG_FILE, FAILED_URLS_FILE, META_DIR, QUEUE_STATE_FILE, SITEMAP_FILE, VISITED_URLS_FILE
from src.crawl_logging.crawl_logger import logger
from src.crawler.queue_manager import ScraperQueueManager


def clear_state():
    """Removes all crawl persistence state files to trigger a completely fresh run."""
    logger.info("Clearing all resume and state files to start fresh...")
    state_files = [
        VISITED_URLS_FILE,
        FAILED_URLS_FILE,
        CRAWL_LOG_FILE,
        SITEMAP_FILE,
        QUEUE_STATE_FILE,
        META_DIR / "scraped_links.txt",
        META_DIR / "queue_links.txt",
    ]
    for file in state_files:
        if file.exists():
            try:
                file.unlink()
                logger.info(f"Successfully deleted {file.name}")
            except Exception as e:
                logger.error(f"Failed to delete {file.name}: {e}")


async def run_scraper(limit: int, use_sitemap: bool, base_url: str = None):
    """Initializes queue manager and runs crawling task."""
    logger.info("Starting crawler engine...")
    manager = ScraperQueueManager(base_url=base_url)

    try:
        # Execute crawl loop with limit and sitemap settings
        await manager.start_crawl(max_pages=limit, use_sitemap=use_sitemap)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Crawl execution paused by user request. Persisting state...")
        manager.persist_state()
    except Exception as e:
        logger.critical(f"Unhandled critical crash in crawler: {e}", exc_info=True)
        manager.persist_state()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Production-grade Unreal Engine Documentation -> Obsidian Vault Scraper"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Target limit for total successfully crawled pages before stopping"
    )
    parser.add_argument("--no-sitemap", action="store_true", help="Skip searching and reading sitemaps first")
    parser.add_argument(
        "--fresh", action="store_true", help="Clear all existing visited history, queue, and log files before starting"
    )

    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Custom base starting URL to scope the recursive crawl to a specific topic",
    )

    args = parser.parse_args()

    if args.fresh:
        clear_state()

    # Windows-specific event loop policy setup to ensure stable subprocess close
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(run_scraper(limit=args.limit, use_sitemap=not args.no_sitemap, base_url=args.base_url))
    except KeyboardInterrupt:
        logger.info("Crawl process shutdown cleanly.")


if __name__ == "__main__":
    main()
