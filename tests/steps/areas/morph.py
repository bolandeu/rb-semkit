"""The command line of each step of the morph area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "lemmatize": ["phrases.csv", "lemmatize"],
    "part-of-speech": ["phrases.csv", "part-of-speech"],
    "wordforms": ["phrases.csv", "wordforms", "диван"],
}
