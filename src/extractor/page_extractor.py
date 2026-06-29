import trafilatura
from playwright.async_api import async_playwright

from src.config import NUM_BROWSERS, PLAYWRIGHT_HEADLESS, PLAYWRIGHT_TIMEOUT
from src.markdown.cleaner import clean_html_dom, convert_html_to_markdown_fallback


class PageExtractor:
    """
    Playwright-based browser rendering wrapper that loads dynamic JS pages,
    dismisses banners implicitly, and extracts structured content.
    """

    def __init__(self):
        self.playwright = None
        self.browsers = []
        self.contexts = []
        self.pages = {}

    async def start(self):
        """Launch configured number of Playwright browsers, set up browser contexts, and block assets."""
        self.playwright = await async_playwright().start()

        async def block_assets(route):
            if route.request.resource_type in ["stylesheet", "font", "image", "media"]:
                await route.abort()
            else:
                await route.continue_()

        for _i in range(NUM_BROWSERS):
            browser = await self.playwright.chromium.launch(
                headless=PLAYWRIGHT_HEADLESS, args=["--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            await context.route("**/*", block_assets)
            self.browsers.append(browser)
            self.contexts.append(context)

    async def fetch_page(self, url: str, worker_id: int = 1) -> dict:
        """
        Navigates to URL, waits for network idle state, extracts fully hydrated HTML,
        and converts it into markdown.
        """
        if not self.contexts:
            await self.start()

        context_idx = (worker_id - 1) % len(self.contexts)
        context = self.contexts[context_idx]

        # Keep 5 persistent tabs (pages) open per context/window.
        # Check if we already have an open page for this worker, otherwise create one.
        if worker_id not in self.pages or self.pages[worker_id].is_closed():
            self.pages[worker_id] = await context.new_page()

        page = self.pages[worker_id]
        try:
            page.set_default_timeout(PLAYWRIGHT_TIMEOUT)

            # Navigate to URL, waiting for network idle to ensure React/Next hydration is complete
            response = await page.goto(url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)

            if not response or response.status != 200:
                status = response.status if response else "NoResponse"
                return {"url": url, "success": False, "status_code": status, "error": f"HTTP status code: {status}"}

            html = await page.content()
            title = await page.title()

            # Strip developer community branding from titles
            title = title.replace(" | Epic Developer Community", "").replace(" | Unreal Engine", "").strip()

            # Extract content from the cleaned HTML
            cleaned_html = clean_html_dom(html)

            markdown = trafilatura.extract(
                cleaned_html, output_format="markdown", include_links=True, include_images=False, include_tables=True
            )

            # Fallback if trafilatura extraction is empty
            if not markdown or len(markdown.strip()) < 50:
                markdown = convert_html_to_markdown_fallback(html)

            # Extract all anchor href links for recursive crawler link discovery
            discovered_links = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a'))
                    .map(a => a.href)
                    .filter(href => href && href.startsWith('http'));
            }""")

            # Extract headings for tag inference
            headings = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('h1, h2, h3, h4'))
                    .map(h => h.textContent.trim())
                    .filter(t => t.length > 0);
            }""")

            return {
                "url": page.url,
                "success": True,
                "status_code": response.status,
                "title": title,
                "markdown": markdown,
                "raw_html": html,
                "discovered_links": discovered_links,
                "headings": headings,
            }

        except Exception as e:
            return {"url": url, "success": False, "status_code": "Exception", "error": str(e)}

    async def close(self):
        """Close browser resources."""
        for page in list(self.pages.values()):
            try:
                await page.close()
            except Exception:
                pass
        self.pages.clear()

        for context in self.contexts:
            try:
                await context.close()
            except Exception:
                pass
        for browser in self.browsers:
            try:
                await browser.close()
            except Exception:
                pass
        if self.playwright:
            await self.playwright.stop()
