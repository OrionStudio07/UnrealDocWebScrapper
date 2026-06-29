import re
from urllib.parse import urlparse

from src.config import TARGET_DOMAIN
from src.storage.vault_storage import sanitize_filename


def convert_links_to_wikilinks(markdown_text: str) -> str:
    """
    Scans the markdown text for links pointing to the target documentation
    domain and replaces them with Obsidian wiki-links.

    Example:
    [Actor](https://dev.epicgames.com/documentation/en-us/unreal-engine/actor) -> [[actor|Actor]]
    """
    # Pattern to match standard Markdown links: [Anchor Text](URL)
    # Group 1: Anchor Text, Group 2: URL
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    def link_replace(match):
        anchor = match.group(1).strip()
        url = match.group(2).strip()

        is_in_scope = False
        slug = None

        try:
            parsed = urlparse(url)

            # Check absolute URLs
            if parsed.netloc == TARGET_DOMAIN:
                if "/documentation/" in parsed.path:
                    is_in_scope = True
                    parts = [p for p in parsed.path.split("/") if p]
                    if parts:
                        slug = parts[-1]

            # Check domain-relative URLs (e.g. /documentation/en-us/unreal-engine/actor)
            elif parsed.netloc == "" and parsed.path.startswith("/documentation/"):
                is_in_scope = True
                parts = [p for p in parsed.path.split("/") if p]
                if parts:
                    slug = parts[-1]

            # Check relative URLs (e.g. ../actor or gameplay-framework)
            elif parsed.netloc == "" and not parsed.path.startswith("/") and parsed.path != "":
                is_in_scope = True
                parts = [p for p in parsed.path.split("/") if p]
                if parts:
                    slug = parts[-1]
        except Exception:
            pass

        if is_in_scope and slug:
            # Clean anchors or query params out of slug
            slug = slug.split("?")[0].split("#")[0]
            proper_slug = slug.replace("-", " ").replace("_", " ").title()
            sanitized_slug = sanitize_filename(proper_slug)

            if not sanitized_slug:
                return match.group(0)

            # If anchor is clean and matches the slug name, make it simple [[slug]]
            # Otherwise, use the piped syntax: [[slug|Anchor]]
            clean_anchor = re.sub(r"\s+", " ", anchor).strip()
            if sanitized_slug.lower() == clean_anchor.lower():
                return f"[[{sanitized_slug}]]"
            else:
                return f"[[{sanitized_slug}|{clean_anchor}]]"

        return match.group(0)

    return link_pattern.sub(link_replace, markdown_text)
