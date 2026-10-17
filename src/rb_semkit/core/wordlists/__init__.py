"""Word lists: the bundled ones (Bukvarix, the add-in's) and the Human's own, found by name.

`resolve(name)` gives the items, `names()` every list with its source, size and description, `describe(name)` one of
them; `word_list(name)` is the public name for Python users. A step that takes items resolves `@name` through these.
"""

from . import store as store
from .catalog import describe as describe
from .catalog import names as names
from .catalog import resolve as resolve
from .catalog import word_list

__all__ = ["word_list"]
