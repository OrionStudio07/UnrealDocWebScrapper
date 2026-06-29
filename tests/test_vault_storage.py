from src.storage.vault_storage import determine_category, sanitize_filename


def test_sanitize_filename():
    assert sanitize_filename("Normal Name") == "Normal Name"
    assert sanitize_filename("Name/With:Illegal?Chars") == "Name_With_Illegal_Chars"
    assert sanitize_filename("  Whitespace Trim  ") == "Whitespace Trim"
    assert sanitize_filename('Name <With> "Quotes" | Pipes') == "Name _With_ _Quotes_ _ Pipes"


def test_determine_category_by_url():
    # URL contains "blueprint" -> Blueprints category
    url = "https://dev.epicgames.com/documentation/en-us/unreal-engine/visual-scripting/blueprints-overview"
    assert determine_category(url) == "Blueprints"


def test_determine_category_by_title():
    # Title contains "materials" -> Rendering category
    url = "https://dev.epicgames.com/documentation/en-us/unreal-engine/some-page"
    assert determine_category(url, title="Materials Interface Guide") == "Rendering"


def test_determine_category_by_content_fallback():
    # Content contains "replication" -> Networking category
    url = "https://dev.epicgames.com/documentation/en-us/unreal-engine/some-page"
    assert (
        determine_category(
            url, title="General Guide", content="This page discusses network replication of variables..."
        )
        == "Networking"
    )


def test_determine_category_fallback_meta():
    # Matches nothing -> Meta category
    url = "https://dev.epicgames.com/documentation/en-us/unreal-engine/miscellaneous"
    assert determine_category(url, title="Unknown Page", content="Some text here that matches no keywords.") == "Meta"
