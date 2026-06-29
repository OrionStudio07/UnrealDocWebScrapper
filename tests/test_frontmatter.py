from src.metadata.frontmatter import append_related_pages, generate_frontmatter, infer_tags


def test_infer_tags_cplusplus():
    # Should infer cplusplus
    url = "https://dev.epicgames.com/documentation/en-us/unreal-engine/programming-guide"
    title = "C++ Coding Standards"
    headings = ["Overview", "Uproperty Specifiers", "Ufunction Details"]
    tags = infer_tags(url, title, headings)
    assert "cplusplus" in tags

    # Verify editor tag is inferred when editor keywords are present
    headings.append("Custom Editor tools plugins")
    tags_with_editor = infer_tags(url, title, headings)
    assert "editor" in tags_with_editor


def test_infer_tags_rendering_niagara():
    url = "https://dev.epicgames.com/documentation/en-us/unreal-engine/visual-effects"
    title = "Niagara Particles Guide"
    headings = ["Niagara System Overview"]
    tags = infer_tags(url, title, headings)
    assert "niagara" in tags

    # Verify rendering tag is inferred when rendering keywords are present
    headings.append("Materials shader lighting")
    tags_with_rendering = infer_tags(url, title, headings)
    assert "rendering" in tags_with_rendering


def test_generate_frontmatter():
    title = "Actors in Unreal"
    url = "https://dev.epicgames.com/documentation/actor"
    inferred = ["gameplay"]

    frontmatter = generate_frontmatter(title, url, inferred)

    assert frontmatter.startswith("---\n")
    assert "title: Actors in Unreal\n" in frontmatter
    assert "source: https://dev.epicgames.com/documentation/actor\n" in frontmatter
    assert "tags:\n" in frontmatter
    assert "  - unreal-engine\n" in frontmatter
    assert "  - ue5\n" in frontmatter
    assert "  - gameplay\n" in frontmatter
    assert frontmatter.endswith("---\n\n")


def test_append_related_pages_no_links():
    content = "Some text with no wiki links."
    assert append_related_pages(content) == content


def test_append_related_pages_with_links():
    content = "Here is an [[Actor]] and another [[Pawn|Pawn Actor]]."
    result = append_related_pages(content)

    assert "## Related Pages" in result
    assert "* [[Actor]]" in result
    assert "* [[Pawn]]" in result  # Piped link anchor should be extracted as just the target slug
