---
id: IDEA-268
title: Timing tests fail the gate under load
created: '2026-10-19T14:41:08+00:00'
source_project: semkit
source_path: /Users/bolandau/Work/tools/semkit
status: dropped
for_path: /Users/bolandau/Work/tools/semkit
triage:
  serves: []
  risks: []
  why: The gate fails under machine load (SEMKIT-065 attempt 1) on timed tests; every
    accept and clean-clone check is at risk
  score: 6.0
  route: task
  at: '2026-10-19T15:31:47+00:00'
reason: Done as task SEMKIT-067
---

SEMKIT-065 attempt 1: Antagor's gate run took 17 min under load and failed at pytest; the same commit passed twice in ~4 min. Suspects: tests/pipeline/test_speed.py (xlsx < 5 s), tests/lists/test_lists.py::test_a_million_rows_run_in_seconds (< 30 s), tests/test_detach.py (10–15 s waits). Move speed tests out of the gate (a marker) or make the limits relative.
