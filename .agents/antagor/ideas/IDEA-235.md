---
id: IDEA-235
title: 'Step help names the add-in: is-typo says ''!SEMTools dictionary'''
created: '2026-10-17T20:34:14+00:00'
source_project: semkit
source_path: /Users/bolandau/Work/tools/semkit
status: new
for_path: /Users/bolandau/Work/tools/semkit
---

semkit read IN is-typo --help (v0.1.23) says 'a wordform the !SEMTools dictionary or pymorphy3 knows'. Product text must not name the add-in (ADR 0006). Say 'the bundled dictionary'. Check every step help and --ai for '!SEMTools' / 'SEMTools' and add the word to the help leak test of tests/steps.
