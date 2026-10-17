"""Wrong arguments raise InvalidArguments naming the argument and the allowed values; the input stays as it was."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core.errors import InvalidArguments

TABLE = pd.DataFrame({"phrase": ["Купить диван"], "count": [5]})


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (
            lambda: sk.change_case(TABLE, "title", column="nope"),
            r"column: 'nope' is not in the table; allowed: 'phrase'",
        ),
        (lambda: sk.change_case(TABLE, "camel", column="phrase"), r"kind='camel'; allowed: 'lower', 'upper', 'title'"),
        (lambda: sk.change_case(TABLE, "list_upper", column="phrase"), r"words: not given; allowed: one word"),
        (lambda: sk.replace_words(TABLE, {}, column="phrase"), r"pairs=\{\}; allowed: a non-empty mapping"),
        (lambda: sk.replace_text(TABLE, {"": "x"}, column="phrase"), r"pairs: the empty text ''; allowed: a non-empty"),
        (lambda: sk.replace_text(TABLE, {"(": "x"}, by="regex", column="phrase"), r"pairs='\(';.*a valid regular"),
        (lambda: sk.replace_text(TABLE, {"a": "x"}, by="cell", column="phrase"), r"by='cell'; allowed: 'substring'"),
        (lambda: sk.match_type(TABLE, "exact", column="phrase"), r"kind='exact'; allowed: 'broad'"),
        (lambda: sk.match_type(TABLE, "stopword_modifier", modifier="*", column="phrase"), r"modifier='\*'; allowed"),
        (lambda: sk.extract_utm(TABLE, "id", column="phrase"), r"tag='id'; allowed: 'source', 'medium'"),
        (lambda: sk.hash_text(TABLE, algorithm="sha1", column="phrase"), r"algorithm='sha1'; allowed: 'md5', 'sha256'"),
        (lambda: sk.translit(TABLE, to="de", column="phrase"), r"to='de'; allowed: 'en', 'ru'"),
        (
            lambda: sk.move_words(TABLE, [], column="phrase"),
            r"words: an empty list; allowed: one word or a list of single words",
        ),
        (lambda: sk.insert(TABLE, column="phrase"), r"before, after: neither given; allowed: a text"),
        (lambda: sk.fix_word_order(TABLE, form="neuter", column="phrase"), r"form='neuter'; allowed: 'masculine'"),
        (lambda: sk.fix_word_order(TABLE, main_word="два слова", column="phrase"), r"main_word='два слова'; allowed"),
    ],
)
def test_a_wrong_argument_is_named_with_the_allowed_values(call, message: str) -> None:
    before = TABLE.copy()

    with pytest.raises(InvalidArguments, match=message):
        call()
    pd.testing.assert_frame_equal(TABLE, before)
