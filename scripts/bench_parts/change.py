"""The change area: translit both ways and ЧПУ, which read the package tables."""

from __future__ import annotations

import rb_semkit as sk

DATA_OPERATIONS = {
    "translit_en": lambda phrases: sk.translit(phrases, to="en"),
    "translit_ru": lambda phrases: sk.translit(phrases, to="ru"),
    "chpu": lambda phrases: sk.chpu(phrases),
}
