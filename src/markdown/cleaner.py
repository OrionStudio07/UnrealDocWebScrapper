import markdownify
from bs4 import BeautifulSoup


def clean_html_dom(html_content: str) -> str:
    """
    Parses raw HTML, strips away boilerplate elements (headers, footers,
    cookie banners, sidebars), and isolates the core documentation page body.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # CSS selectors for common elements that do not contain main documentation text
    boilerplate_selectors = [
        "header",
        "footer",
        "nav",
        "#header",
        "#footer",
        ".header",
        ".footer",
        ".sidebar",
        ".sidebar-container",
        "#sidebar",
        ".toc-container",
        ".breadcrumbs",
        ".breadcrumb-container",
        ".breadcrumb-wrapper",
        "#onetrust-consent-sdk",
        ".onetrust-pc-dark",
        ".feedback-container",
        ".edit-button",
        ".edit-btn",
        ".cookie-banner",
        ".cookie-consent",
        ".search-container",
        "#search-container",
        ".epic-header",
        ".nav-header",
    ]

    # Remove unwanted elements
    for selector in boilerplate_selectors:
        for element in soup.select(selector):
            element.decompose()

    # Remove image elements since they are excluded
    for img in soup.find_all("img"):
        img.decompose()

    # Attempt to locate the main content wrapper
    main_content = soup.select_one(".documentation-page") or soup.select_one("main") or soup.select_one("#main-content")
    if main_content:
        return str(main_content)

    return str(soup)


def convert_html_to_markdown_fallback(html_content: str) -> str:
    """
    Converts HTML content to clean markdown using markdownify as a fallback
    when trafilatura fails to extract content.
    """
    cleaned_html = clean_html_dom(html_content)

    # Configure markdownify to preserve tables, code blocks, list structures, links, and headings
    markdown_text = markdownify.markdownify(
        cleaned_html,
        heading_style="ATX",
        convert=[
            "p",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ul",
            "ol",
            "li",
            "table",
            "tr",
            "td",
            "th",
            "pre",
            "code",
            "span",
            "strong",
            "em",
            "a",
        ],
    )

    return markdown_text.strip()
