---
id: IDEA-238
title: Split the describe.json and help snapshots by step
created: '2026-10-17T23:01:02+00:00'
source_project: semkit
source_path: /Users/bolandau/Work/tools/semkit
status: new
for_path: /Users/bolandau/Work/tools/semkit
---

Every new step or option changes the one snapshot tests/snapshots/describe.json (and shared help snapshots like read.txt, tests/steps/areas.py), so parallel tasks wait for each other on scope_held (E-005..E-007, 2026-10-18: 035, 036, 042, 043, 044 serialized on it). Store describe output per step (one file per step, like the help snapshots), so a task that adds a step touches only its own files.
