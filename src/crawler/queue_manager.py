import asyncio
import re
import urllib.request
from urllib.parse import urlparse

from src.config import BASE_URL, CONCURRENT_REQUESTS, EXCLUDED_SUBSTRINGS, REQUEST_DELAY, TARGET_DOMAIN
from src.crawl_logging.crawl_logger import log_event, logger
from src.extractor.page_extractor import PageExtractor
from src.linking.wiki_linker import convert_links_to_wikilinks
from src.metadata.frontmatter import append_related_pages, generate_frontmatter, infer_tags
from src.resume.state_manager import load_crawl_state, save_crawl_state
from src.storage.vault_storage import save_page_markdown


class ScraperQueueManager:
    """
    Manages the crawling queue, sitemaps, worker task concurrency,
    politeness pacing, and state preservation.
    """

    def __init__(self, base_url: str = None):
        self.queue = asyncio.Queue()
        self.visited_urls = set()
        self.failed_urls = {}
        self.sitemap_urls = []
        self.extractor = PageExtractor()
        from src.config import NUM_BROWSERS

        self.rate_limit_locks = [asyncio.Lock() for _ in range(NUM_BROWSERS)]
        self.last_request_times = [0.0 for _ in range(NUM_BROWSERS)]
        self.base_url = base_url or BASE_URL

    def is_url_in_scope(self, url: str) -> bool:
        """Checks if the URL is within the allowed domain and path scope, and not excluded."""
        # Clean URL (strip query parameters and anchors for consistency)
        clean_url = url.split("#")[0].split("?")[0].strip()

        # Normalize by removing locale segments (like /en-us/) to match redirects
        normalized_url = re.sub(r"/documentation/[a-zA-Z]{2}-[a-zA-Z]{2}/", "/documentation/", clean_url)
        normalized_base = re.sub(r"/documentation/[a-zA-Z]{2}-[a-zA-Z]{2}/", "/documentation/", self.base_url)

        # Check domain-relative documentation root
        normalized_doc_root = "https://dev.epicgames.com/documentation/unreal-engine"
        if not normalized_url.startswith(normalized_doc_root):
            return False

        # If we are targeting a specific topic page rather than the documentation root, filter by category keywords
        normalized_base_lower = normalized_base.lower()
        if not normalized_base_lower.endswith("/unreal-engine"):
            from src.config import CATEGORY_MAPPING

            matched_category = None
            for category, keywords in CATEGORY_MAPPING.items():
                if any(k in normalized_base_lower for k in keywords):
                    matched_category = category
                    break

            if matched_category:
                allowed_keywords = list(CATEGORY_MAPPING[matched_category])
                # Add topic-specific structural helpers for Blueprints
                if matched_category == "Blueprints":
                    allowed_keywords += [
                        "anatomy",
                        "node",
                        "graph",
                        "communication",
                        "dispatcher",
                        "interface",
                        "namespaces",
                        "debugger",
                    ]

                url_lower = normalized_url.lower()
                if not any(k in url_lower for k in allowed_keywords):
                    return False

        parsed = urlparse(clean_url)
        if parsed.netloc != TARGET_DOMAIN:
            return False

        clean_url_lower = clean_url.lower()
        for substring in EXCLUDED_SUBSTRINGS:
            if substring in clean_url_lower:
                return False

        # Filter specific paths
        if any(p in clean_url_lower for p in ["/login", "/search", "/api/", "/signin"]):
            return False

        return True

    async def throttle(self, worker_id: int):
        """Ensures that requests on the same browser instance are spaced by at least REQUEST_DELAY seconds."""
        from src.config import NUM_BROWSERS

        browser_idx = (worker_id - 1) % NUM_BROWSERS
        async with self.rate_limit_locks[browser_idx]:
            now = asyncio.get_event_loop().time()
            elapsed = now - self.last_request_times[browser_idx]
            if elapsed < REQUEST_DELAY:
                await asyncio.sleep(REQUEST_DELAY - elapsed)
            self.last_request_times[browser_idx] = asyncio.get_event_loop().time()

    async def parse_sitemap(self, sitemap_url: str):
        """Recursively parses sitemap.xml files to find target documentation links."""
        logger.info(f"Checking sitemap for URLs: {sitemap_url}")
        try:

            def fetch_sitemap_sync(url):
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    },
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    return response.read().decode("utf-8", errors="ignore")

            raw_html = await asyncio.to_thread(fetch_sitemap_sync, sitemap_url)

            # Locate all <loc>...</loc> tags in sitemap XML content
            locs = re.findall(r"<loc>(.*?)</loc>", raw_html, re.IGNORECASE | re.DOTALL)

            for loc in locs:
                loc = loc.strip()
                # If loc contains another sitemap XML, parse it recursively
                loc_lower = loc.lower()
                if loc.endswith(".xml") or "sitemap" in loc_lower:
                    if ("unreal" in loc_lower or "documentation" in loc_lower) and "fortnite" not in loc_lower:
                        if loc not in self.sitemap_urls:
                            self.sitemap_urls.append(loc)
                            # Spawn background task to parse nested sitemap
                            asyncio.create_task(self.parse_sitemap(loc))
                else:
                    if self.is_url_in_scope(loc) and loc not in self.visited_urls:
                        self.sitemap_urls.append(loc)

            logger.info(f"Discovered {len(self.sitemap_urls)} total URLs in sitemaps so far.")
        except Exception as e:
            logger.error(f"Error parsing sitemap {sitemap_url}: {e}")

    async def initialize_state(self, sitemap_fallback: bool = True):
        """Loads previous state if resuming, otherwise initializes sitemaps."""
        visited, failed, sitemap_list, queue_list = load_crawl_state()

        self.visited_urls = visited
        self.failed_urls = failed

        if queue_list or visited:
            logger.info(f"Resuming crawl. Loaded {len(visited)} visited and {len(queue_list)} queued URLs.")
            for url in queue_list:
                await self.queue.put(url)
        else:
            logger.info("No previous state detected. Starting fresh crawl.")
            if sitemap_fallback:
                # Target typical sitemap locations
                sitemaps_to_try = [
                    "https://dev.epicgames.com/documentation/sitemap.xml",
                    "https://dev.epicgames.com/sitemap.xml",
                ]
                for s_url in sitemaps_to_try:
                    await self.parse_sitemap(s_url)

                # Give sitemap parser tasks a moment to start
                await asyncio.sleep(2.0)

            # Put the entry point URL in queue
            if self.base_url not in self.visited_urls:
                await self.queue.put(self.base_url)

    def persist_state(self):
        """Saves current queue and visited state to JSON files."""
        # Convert queue to list
        queue_list = []
        # We temporarily copy elements out of queue to read it safely
        temp_list = []
        while not self.queue.empty():
            item = self.queue.get_nowait()
            queue_list.append(item)
            temp_list.append(item)
        for item in temp_list:
            self.queue.put_nowait(item)

        save_crawl_state(self.visited_urls, self.failed_urls, self.sitemap_urls, queue_list)

    async def crawl_worker(self, worker_id: int):
        """Worker loop that fetches, extracts, cleans, and saves documentation pages."""
        logger.info(f"Worker-{worker_id} started.")
        while True:
            try:
                url = await self.queue.get()
            except asyncio.CancelledError:
                break

            if url in self.visited_urls:
                self.queue.task_done()
                continue

            logger.info(f"Worker-{worker_id} fetching: {url}")
            await self.throttle(worker_id)

            # Fetch and extract page contents
            retries = 3
            page_data = None
            for attempt in range(retries):
                page_data = await self.extractor.fetch_page(url, worker_id=worker_id)
                if page_data.get("success"):
                    break
                logger.warning(f"Worker-{worker_id} attempt {attempt + 1} failed for {url}: {page_data.get('error')}")
                await asyncio.sleep(2.0 * (attempt + 1))

            if page_data and page_data.get("success"):
                resolved_url = page_data.get("url", url)
                title = page_data.get("title", "Untitled Page")
                markdown = page_data.get("markdown", "")
                headings = page_data.get("headings", [])
                discovered_links = page_data.get("discovered_links", [])

                # 1. Convert links in markdown to Obsidian wiki-links
                converted_markdown = convert_links_to_wikilinks(markdown)

                # 2. Append Related Pages backlinks block
                markdown_with_relations = append_related_pages(converted_markdown)

                # 3. Generate frontmatter metadata header
                inferred_tags = infer_tags(resolved_url, title, headings)
                frontmatter = generate_frontmatter(title, resolved_url, inferred_tags)

                final_content = frontmatter + markdown_with_relations

                # 4. Save markdown to the organized folder
                try:
                    saved_path = save_page_markdown(resolved_url, title, final_content)
                    self.visited_urls.add(url)
                    if resolved_url != url:
                        self.visited_urls.add(resolved_url)
                    log_event("SCRAPE_SUCCESS", resolved_url, f"Saved page: {saved_path.name}", 200)
                    logger.info(f"Worker-{worker_id} successfully saved: {saved_path.name}")
                except Exception as e:
                    logger.error(f"Worker-{worker_id} failed to save file: {e}")
                    log_event("SAVE_ERROR", resolved_url, str(e), 500)

                # 5. Enqueue newly discovered in-scope links
                enqueued_count = 0
                logger.info(f"Worker-{worker_id} found {len(discovered_links)} raw links on page.")
                for link in discovered_links:
                    # Clean anchors
                    clean_link = link.split("#")[0].split("?")[0].strip()
                    in_scope = self.is_url_in_scope(clean_link)
                    visited = clean_link in self.visited_urls
                    if in_scope and not visited:
                        # Put in queue
                        await self.queue.put(clean_link)
                        enqueued_count += 1
                logger.info(f"Worker-{worker_id} enqueued {enqueued_count} new links.")
            else:
                error_msg = page_data.get("error", "Unknown error") if page_data else "No response received"
                self.failed_urls[url] = error_msg
                log_event("SCRAPE_FAILED", url, error_msg, page_data.get("status_code") if page_data else None)
                logger.error(f"Worker-{worker_id} permanently failed URL {url}: {error_msg}")

            # Periodically dump state to keep resume data synchronized
            self.persist_state()
            self.queue.task_done()

    async def start_crawl(self, max_pages: int = None, use_sitemap: bool = True):
        """Starts the crawling process orchestrating workers."""
        await self.extractor.start()
        await self.initialize_state(sitemap_fallback=use_sitemap)

        # Start crawl workers
        workers = []
        for i in range(CONCURRENT_REQUESTS):
            task = asyncio.create_task(self.crawl_worker(i + 1))
            workers.append(task)

        # Add a monitor to stop crawling if page limit is met
        monitor_task = None
        main_task = asyncio.current_task()
        if max_pages is not None:

            async def limit_monitor():
                while len(self.visited_urls) < max_pages:
                    await asyncio.sleep(1.0)
                logger.info(f"Crawl limit of {max_pages} reached. Stopping scraper.")
                main_task.cancel()

            monitor_task = asyncio.create_task(limit_monitor())

        # Wait for the queue to empty
        try:
            await self.queue.join()
        except asyncio.CancelledError:
            pass
        finally:
            if monitor_task:
                monitor_task.cancel()
            for worker in workers:
                worker.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            await self.extractor.close()
            self.persist_state()
            logger.info("Crawl completed and state persisted.")
