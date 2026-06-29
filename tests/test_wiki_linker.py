from src.linking.wiki_linker import convert_links_to_wikilinks


def test_convert_absolute_links_in_scope():
    # Standard absolute URL inside target domain
    text = "Check the [Actor](https://dev.epicgames.com/documentation/en-us/unreal-engine/actor) guidelines."
    expected = "Check the [[Actor]] guidelines."
    assert convert_links_to_wikilinks(text) == expected


def test_convert_absolute_links_in_scope_piped():
    # Piped absolute URL inside target domain with different anchor text
    text = "Read about [Custom Actors](https://dev.epicgames.com/documentation/en-us/unreal-engine/actor)."
    expected = "Read about [[Actor|Custom Actors]]."
    # Wait, the code replaces '-' with ' ' and runs title():
    # "actor" -> "Actor". The clean anchor is "Custom Actors".
    # Since "Actor" != "Custom Actors", it returns [[Actor|Custom Actors]]
    assert expected == convert_links_to_wikilinks(text)


def test_convert_domain_relative_links():
    # Domain-relative URL starting with /documentation/
    text = "Refer to the [Gameplay Framework](/documentation/en-us/unreal-engine/gameplay-framework) sections."
    expected = "Refer to the [[Gameplay Framework]] sections."
    assert convert_links_to_wikilinks(text) == expected


def test_convert_relative_links():
    # Relative URL
    text = "Details on [Tick](../actor-ticking-in-unreal-engine)."
    expected = "Details on [[Actor Ticking In Unreal Engine|Tick]]."
    assert convert_links_to_wikilinks(text) == expected


def test_ignore_out_of_scope_links():
    # Link pointing to outside domain should not be converted
    text = "Go to [Google](https://www.google.com)."
    assert convert_links_to_wikilinks(text) == text
