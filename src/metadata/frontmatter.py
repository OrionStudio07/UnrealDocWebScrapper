import re
from datetime import datetime


def infer_tags(url: str, title: str, headings: list) -> list:
    """
    Automatically infers specific tags based on keywords in the URL, title,
    and page headings. Returns a list of inferred tags.
    """
    inferred = set()

    # Text sources to inspect
    text_content = f"{url} {title} {' '.join(headings)}".lower()

    # Keyword to Tag Mapping Rules
    mapping = {
        "blueprints": ["blueprint", "visual-scripting", "wbp_"],
        "cplusplus": ["c++", "cpp", "cplusplus", "uproperty", "ufunction", "ustruct"],
        "rendering": [
            "rendering",
            "materials",
            "shaders",
            "lighting",
            "shadowing",
            "graphics",
            "nanite",
            "lumen",
            "textures",
        ],
        "gameplay": ["actor", "pawn", "character", "component", "gameplay-framework"],
        "ai": ["ai", "artificial-intelligence", "behavior-tree", "navmesh", "navigation", "state-tree"],
        "networking": ["networking", "replication", "multiplayer", "online", "replicated"],
        "niagara": ["niagara", "particle", "vfx", "visual-effects"],
        "sequencer": ["sequencer", "cinematic", "movie-render"],
        "ui": ["umg", "slate", "widget", "hud"],
        "physics": ["physics", "collision", "chaos", "rigidbody"],
        "audio": ["audio", "sound", "soundscape", "music", "synthesizer"],
        "editor": ["editor", "tools", "plugins", "unreal-editor"],
    }

    for tag, keywords in mapping.items():
        for keyword in keywords:
            # If the keyword contains non-alphanumeric characters (like c++), do a direct substring check
            if not keyword.isalnum():
                if keyword in text_content:
                    inferred.add(tag)
            elif len(keyword) <= 3:
                # Use regex word boundaries for short alphanumeric terms like 'ai' or 'cpp'
                if re.search(r"\b" + re.escape(keyword) + r"\b", text_content):
                    inferred.add(tag)
            else:
                if keyword in text_content:
                    inferred.add(tag)

    return sorted(list(inferred))


def generate_frontmatter(title: str, url: str, inferred_tags: list) -> str:
    """Generates the Obsidian-compatible YAML frontmatter header block."""
    tags_list = ["unreal-engine", "ue5", "documentation"] + inferred_tags
    timestamp = datetime.utcnow().isoformat() + "Z"

    frontmatter = "---\n"
    frontmatter += f"title: {title}\n"
    frontmatter += f"source: {url}\n"
    frontmatter += "tags:\n"
    for tag in tags_list:
        frontmatter += f"  - {tag}\n"
    frontmatter += f"created: {timestamp}\n"
    frontmatter += "---\n\n"

    return frontmatter


def append_related_pages(markdown_content: str) -> str:
    """
    Scans the markdown content for internal wiki-links and appends a
    'Related Pages' section at the end if links are discovered.
    """
    # Find all [[WikiLinks]] or [[WikiLinks|Anchor]]
    wiki_link_pattern = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
    found_links = wiki_link_pattern.findall(markdown_content)

    # Deduplicate and limit to top 5 unique links
    unique_links = []
    seen = set()
    for link in found_links:
        link_clean = link.strip()
        if link_clean.lower() not in seen:
            seen.add(link_clean.lower())
            unique_links.append(link_clean)

    if not unique_links:
        return markdown_content

    related_section = "\n## Related Pages\n\n"
    for link in unique_links[:5]:
        related_section += f"* [[{link}]]\n"

    return markdown_content.rstrip() + "\n" + related_section
