from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files

DESCRIPTIONS: dict[str, str] = {
    "index.md": "Prefixed UUID's for Python with Pydantic & SQLAlchemy support.",
}


def on_page_markdown(
    markdown: str, page: Page, config: MkDocsConfig, files: Files
) -> str:
    """Inject a description into page metadata if not already present."""

    if page.meta.get("description"):
        return markdown

    if description := DESCRIPTIONS.get(page.file.src_path):
        page.meta["description"] = description

    return markdown
