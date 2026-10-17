"""The declension area: everything that declines in each phrase of the core, to the genitive."""

from __future__ import annotations

import rb_semkit as sk

DATA_OPERATIONS = {"decline": lambda phrases: sk.decline(phrases, "genitive")}
