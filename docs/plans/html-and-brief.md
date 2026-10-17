# HTML pages and the copywriter brief: what semkit lacks

Found on 2026-10-18 against the full text analysis of Miratext (the page of an analysis of five competitors, saved by
the Human). semkit already has: text metrics against competitors (text-stats, compare-stats), word and n-gram density
of competitors with the median and the number of sites (compare-grams), phrase occurrences (coverage), bm25.

## Gaps

1. HTML input: the zones of a page (text, links, both), title, description, H1-H6; leaving out noindex, alt and title
   attributes. Fetching pages stays outside semkit; parsing a given HTML is text analysis.
2. Meta tags of the competitors and the top words in them.
3. The heading structure H1-H6 of each competitor, in order.
4. The recommended number of occurrences of a word for a target text size: how many to add or remove.
5. The copywriter brief by a template («фраза (3)», «[4]», «- 2*», «,6*»), grouped by the kind of occurrence.
6. Kinds of occurrence: diluted (other words between, same order), reversed, reversed diluted, morphological diluted,
   clean and direct; coverage has exact, lemmas and any_order.
7. Leaving out numbers and a list of the Human's words in compare-grams and text-stats.

Proposed: an epic «HTML input» (1-3), an epic «copywriter brief» (4-5), a task for 6-7. The Human, 2026-10-18: HTML
input first.

## HTML input: clarification

The Human, 2026-10-18: the input is pages (first of all the pages of the Human's own site), given as HTML by the
Human; fetching stays outside semkit. Competitors are one scenario of the same commands, not the purpose.

Proposed (round 1, waiting for the Human):
- `parse-html`: a change step on a column of HTML (one page: `read page.html --whole`; many: a table url, html); adds
  url (when known), text (visible text without links), links (link text), all, main (the main content without menus,
  header and footer), title, description, h1. The columns match the `--pages` table of the vector steps (url, text,
  title, h1), so parsed pages go straight to assign-pages, nearest, coverage, coverage-meaning, text-stats.
- `headings`: a report, one row per heading (url, order, level H1-H6, text).
- Defaults count noindex text and alt and title attributes, as Miratext; `--drop-noindex`, `--drop-attributes` leave
  them out; scripts, styles and hidden elements are always left out.
- A ready library under a thin wrapper (selectolax or lxml for zones and headings, trafilatura for main), chosen by a
  comparison on real pages before the card.
- The average over a list of pages (the Human): `summary`, a report over any table: per numeric column the mean,
  median, min, max and count (parse-html → text-stats → summary gives the table «all URLs: mean, median» of
  Miratext); compare-grams gets the mean density beside the median.
- One page against the average of a list (the Human): compare-stats and compare-grams already compare mine with the
  median; both get a mean column and `--norm mean|median` for the verdict (default median, as now).
- Words in meta tags: no step; compare-grams on the title or description column (a scenario).

## The recommended number of occurrences (the Human, 2026-10-18)

Taken from the measure over several URLs: per gram, the mean (or median, `--norm`) density over the list of pages x the
size in words (my page by default, `--words N` for a target size), rounded: the column «need»; beside it «have» and
«add/remove». Columns of compare-grams, no new step.

## Keyword occurrence check (the Human, 2026-10-18)

semkit gives bricks, not the house. The eight named kinds of Miratext are four parameters of one search: word forms
(as given / any: coverage exact, lemmas), order (as given / any: any_order), punctuation inside, words inserted
between. Only the insertions are missing and useful: natural text writes «купить недорогие пластиковые окна».
Decided: coverage gets `--gap N` (up to N words between the words of the phrase, default 0). No named kinds, no
`--kinds`, no column per kind, no stricter exact: the existing exact stays as it is.

## HTML libraries: measured (2026-10-18)

Seven real pages (the five competitors of the Miratext analysis, two ost-term pages; the import page is the Human's
test page), Python 3.12, mean of 3 runs per page.

| library | role | words p3 (Miratext 1683) | time per page | main of the test page |
|---|---|---|---|---|
| selectolax 1.0 (lexbor) | zones, title, description, H1-H6, noindex | 1688 | ~1 ms | — |
| lxml 6.1 | the same | 1688 | 1-5 ms | — |
| html-text 0.7 | visible text | 1697 | 3-7 ms | — |
| BeautifulSoup 4.15 | visible text | 1697 | 8-23 ms | — |
| inscriptis 2.7 | visible text by layout | 1706 | 5-13 ms | — |
| trafilatura 2.3 (favor_recall) | main content | — | 9-29 ms | 13 of 14 sections, no menu or footer |
| justext 3.0 | main content | — | 8-24 ms | 8 of 14 sections |
| readability-lxml 0.9 | main content | — | 10-107 ms | 0 of 14 (took a wrong block) |

Chosen: selectolax for the zones, meta tags, headings and noindex (the fastest, CSS selectors, its all-text word count
matches Miratext within 0.3 % on a page without JavaScript); trafilatura with favor_recall for main. A page built by
JavaScript (di-project: 6 words) has no text in its HTML: the Human gives the rendered HTML.

The Human, 2026-10-18: the copywriter brief (gap 5, templates, targets) is not done: a complex scenario.
