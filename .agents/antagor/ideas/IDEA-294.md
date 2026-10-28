---
id: IDEA-294
title: 'Template v1.23.0: the gate through uvx from cli-generator, rb-cli-core gone'
created: '2026-10-20T13:04:46+00:00'
source_project: semkit
source_path: /Users/bolandau/Work/tools/semkit
status: taken
for_path: /Users/bolandau/Work/tools/semkit
triage:
  serves: []
  risks: []
  why: ''
  score: null
  route: task
  at: '2026-10-20T13:04:50+00:00'
task: SEMKIT-068
taken_project: semkit
---

From cli-generator (the Human said to send it), 2026-10-20: move semkit to template v1.23.0; the gate is uvx --from git+…/cli-generator.git@<template tag>#subdirectory=gate rb-release check; adopt_core, rb-cli-core and release.py are gone; the gate checks the Standard's mandatory rules (standard.md). Release, then send the version to cli-generator.
