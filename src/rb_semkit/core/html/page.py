"""One page of HTML read into its parts: the zones of text, the meta tags and the headings.

The parsing is a thin wrapper over selectolax (lexbor) for the zones, the meta tags, the headings and noindex, and
trafilatura (favor_recall) for the main content. Scripts, styles, noscript, templates and hidden elements are never
counted. The text of <noindex> (the tag and the <!--noindex--> comments) and the alt and title attributes count unless
the caller leaves them out.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

import trafilatura
from selectolax.lexbor import LexborHTMLParser, LexborNode

NEVER_COUNTED = "script, style, noscript, template, [hidden], input[type=hidden]"
HIDDEN_STYLE = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden", re.IGNORECASE)
NOINDEX_COMMENTS = re.compile(r"<!--\s*noindex\s*-->.*?<!--\s*/noindex\s*-->", re.IGNORECASE | re.DOTALL)
HAS_TAG = re.compile(r"<[a-zA-Z!/]")
SPACES = re.compile(r"\s+")
ATTRIBUTES = ("alt", "title")
VOID_TAGS = {"img", "input", "area", "br", "hr", "embed", "source", "track", "wbr"}


@dataclass(frozen=True)
class Page:
    """The parts of a page; every part is a string, empty when the page has none."""

    text: str = ""
    links: str = ""
    all: str = ""
    main: str = ""
    title: str = ""
    description: str = ""
    h1: str = ""


def is_html(cell: str) -> bool:
    """True when the cell holds a tag."""
    return bool(HAS_TAG.search(cell))


def squeeze(text: str) -> str:
    """The text with each run of whitespace as one space, no space at the edges."""
    return SPACES.sub(" ", text).strip()


def _text_of(node: LexborNode | None) -> str:
    return squeeze(node.text(separator=" ")) if node is not None else ""


def _description(tree: LexborHTMLParser) -> str:
    for meta in tree.css("meta[name]"):
        if (meta.attributes.get("name") or "").strip().lower() == "description":
            return squeeze(meta.attributes.get("content") or "")
    return ""


def _remove_hidden(tree: LexborHTMLParser) -> None:
    for node in tree.css(NEVER_COUNTED):
        node.decompose()
    for node in tree.css("[style], [aria-hidden=true]"):
        style = node.attributes.get("style") or ""
        if HIDDEN_STYLE.search(style) or node.attributes.get("aria-hidden") == "true":
            node.decompose()


def _add_attribute_text(tree: LexborHTMLParser) -> None:
    """The alt and title of each element as text next to it (inside it for a link, so the link keeps it)."""
    for node in tree.css("[alt], [title]"):
        for name in ATTRIBUTES:
            value = squeeze(node.attributes.get(name) or "")
            if value:
                piece = f" {html.escape(value)} "
                if node.tag in VOID_TAGS:
                    node.insert_after(piece)
                else:
                    node.insert_child(piece)


def parse_page(source: str, *, drop_noindex: bool, drop_attributes: bool) -> Page:
    """The parts of the page `source`."""
    if drop_noindex:
        source = NOINDEX_COMMENTS.sub(" ", source)
    tree = LexborHTMLParser(source)
    title, description = _text_of(tree.css_first("head title")), _description(tree)
    if drop_noindex:
        for node in tree.css("noindex"):
            node.decompose()
    _remove_hidden(tree)
    main = trafilatura.extract(tree.html or "", favor_recall=True) or ""
    if not drop_attributes:
        _add_attribute_text(tree)
    body = tree.body
    if body is None:
        return Page(title=title, description=description)
    h1 = _text_of(body.css_first("h1"))
    everything = _text_of(body)
    links = squeeze(" ".join(_text_of(link) for link in body.css("a")))
    for link in body.css("a"):
        link.decompose()
    return Page(_text_of(body), links, everything, squeeze(main), title, description, h1)


def parse_headings(source: str) -> list[tuple[int, str]]:
    """The level and the text of each heading of the page `source`, in page order; a heading without text is skipped."""
    tree = LexborHTMLParser(source)
    _remove_hidden(tree)
    _add_attribute_text(tree)
    found = ((int(str(node.tag)[1]), _text_of(node)) for node in tree.css("h1, h2, h3, h4, h5, h6"))
    return [(level, text) for level, text in found if text]
