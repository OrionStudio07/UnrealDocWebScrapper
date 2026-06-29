import re
from pathlib import Path
from urllib.parse import urlparse

from src.config import CATEGORY_MAPPING, META_DIR, VAULT_DIR


def initialize_vault():
    """Create all standard vault subfolders and the Meta directory if they do not exist."""
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    META_DIR.mkdir(parents=True, exist_ok=True)
    for folder in CATEGORY_MAPPING.keys():
        (VAULT_DIR / folder).mkdir(parents=True, exist_ok=True)


def sanitize_filename(name: str) -> str:
    """Replace illegal OS characters in filenames with underscores."""
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", name)
    return sanitized.strip()


def determine_category(url: str, title: str = "", content: str = "") -> str:
    """
    Decide the vault folder based on URL slug keywords, title, or content indicators.
    Falls back to 'Meta' if no matches are found.
    """
    parsed = urlparse(url)
    path_lower = parsed.path.lower()
    title_lower = title.lower()

    # 1. Match categories based on path or title keywords
    for category, keywords in CATEGORY_MAPPING.items():
        for keyword in keywords:
            if keyword in path_lower or keyword in title_lower:
                return category

    # 2. Match based on the initial segment of content as fallback
    content_lower = content.lower()[:2000]
    for category, keywords in CATEGORY_MAPPING.items():
        for keyword in keywords:
            if keyword in content_lower:
                return category

    return "Meta"


def save_page_markdown(url: str, title: str, markdown_content: str) -> Path:
    """Categorize and save markdown content to the appropriate folder in the vault."""
    initialize_vault()

    category = determine_category(url, title, markdown_content)

    # Extract slug from url path
    parsed = urlparse(url)
    path_parts = [part for part in parsed.path.split("/") if part]

    if path_parts:
        slug = path_parts[-1]
    else:
        slug = "index"

    # Format slug as a proper Title Case name by replacing hyphens and underscores with spaces
    proper_slug = slug.replace("-", " ").replace("_", " ").title()
    sanitized_slug = sanitize_filename(proper_slug)
    if not sanitized_slug:
        sanitized_slug = "Documentation Page"

    filename = f"{sanitized_slug}.md"
    target_path = VAULT_DIR / category / filename

    # Write UTF-8 markdown file
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    return target_path
