"""Pages as HTML: the zones of a page as columns, and its heading structure."""

from .headings import headings
from .parse import parse_html

__all__ = ["headings", "parse_html"]
