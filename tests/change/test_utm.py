"""UTM tags of a URL: removed in any case of «utm_», or one extracted as its decoded value."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk


def test_removal_takes_every_utm_tag_and_keeps_the_query_valid() -> None:
    urls = pd.Series(
        [
            "https://site.ru/?UTM_Source=ya&utm_medium=cpc&id=5#top",
            "https://site.ru/page?utm_source=ya",
            "https://site.ru/?id=5&utm_term=x&page=2",
            "https://site.ru/page",
        ]
    )

    assert sk.remove_utm(urls).tolist() == [
        "https://site.ru/?id=5#top",
        "https://site.ru/page",
        "https://site.ru/?id=5&page=2",
        "https://site.ru/page",
    ]


def test_extract_gives_the_url_decoded_value_only() -> None:
    urls = pd.Series(
        [
            "?utm_source=%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81",
            "https://site.ru/?UTM_SOURCE=ya&utm_medium=cpc",
            "https://site.ru/?utm_term=купить+диван#top",
            "https://site.ru/?id=5",
        ]
    )

    assert sk.extract_utm(urls, "source").tolist() == ["Яндекс", "ya", "", ""]
    assert sk.extract_utm(urls, "term").tolist() == ["", "", "купить диван", ""]


def test_a_tag_in_the_fragment_is_no_utm_tag_for_both_functions() -> None:
    url = pd.Series(["https://site.ru/?utm_source=vk#utm_medium=x"])

    assert sk.extract_utm(url, "medium").tolist() == [""]
    assert sk.remove_utm(url).tolist() == ["https://site.ru/#utm_medium=x"]
    assert sk.extract_utm(url, "source").tolist() == ["vk"]
