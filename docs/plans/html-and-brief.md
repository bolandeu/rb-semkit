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
- Words in meta tags: no step; compare-grams on the title or description column (a scenario).
