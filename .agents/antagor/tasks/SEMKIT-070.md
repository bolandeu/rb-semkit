---
id: SEMKIT-070
title: 'Help and describe snapshots are generated files: tests/snapshots/** linguist-generated'
status: done
attempts: 1
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: human
worker: claude-code
type: chore
owns_paths:
- .gitattributes
- tests/markers/test_build_markers.py
- uv.lock
test_paths:
- tests/markers/test_build_markers.py
docs: none
tools: []
worker_args: null
class: mechanical
decision: false
visual: null
depends_on: []
budget_usd: null
epic: null
spec_refs: []
checks:
- 'sh -c ''uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed
  -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check'''
resident: null
tool: null
pr: null
translation: 'Пометить снимки справки tests/snapshots/** как linguist-generated в
  .gitattributes (правило Человека 20.10): обновление шаблона больше не упирается
  в max_files.'
---

The Human's rule (2026-10-20): generated files go to .gitattributes as linguist-generated, so Antagor counts them by file. tests/snapshots/ holds 326 files written by `pytest --snapshot-update`; a template update that refreshes the help of the 145 pipeline steps goes over max_files = 150.

1. Add one line to .gitattributes: `tests/snapshots/** linguist-generated`, with a short comment above it in the style of the file (written by pytest --snapshot-update, read in review as a diff).
2. The gate ends with 'release: gate passed'.

## Read first

- `.gitattributes`
- `tests/snapshots/help/run.txt` — one of the snapshots, read only

## Acceptance

- Given .gitattributes, When git check-attr linguist-generated runs on tests/snapshots/help/run.txt, Then it says set, and the gate ends with 'release: gate passed' [check: sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check']

## Out of scope

- The snapshots themselves.

## Feedback

### Attempt 1: checks failed

- `sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check'` (exit 3)

```
-version` = 0.1.58.post4.dev0+dd3faff; `semkit --help` ok)
release: standard: commands ... ok (156 commands and 7 groups answer --help)
release: standard: json ... ok (156 commands accept --json (the root lists it))
release: standard: errors ... ok (an unknown option: exit 2 and the error envelope, in 156 commands)
release: standard: health ... ok (doctor --json and auth status --json give the envelope)
release: standard: docs ... ok (README.md, AGENTS.md)
release: standard: ci ... ok (.gitea/workflows/ci.yml runs rb-release check)
release: vulnerability audit ... FAILED
   Updating https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git (v1.23.1)
    Updated https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git (8fa0241305775587de2c6c03822d880715219ff2)

release: gate step 'vulnerability audit' failed:
$ /opt/homebrew/bin/osv-scanner --lockfile=uv.lock
Starting filesystem walk for root: /
Scanned /Users/bolandau/Work/tools/semkit.worktrees/SEMKIT-070/uv.lock file and found 120 packages
End status: 0 dirs visited, 1 inodes visited, 1 Extract calls, 13.555459ms elapsed, 13.556ms wall time
Filtered 1 local/unscannable package/s from the scan.

Total 1 package affected by 1 known vulnerability (1 Critical, 0 High, 0 Medium, 0 Low, 0 Unknown) from 1 ecosystem.
1 vulnerability can be fixed.

+-------------------------------------+------+-----------+---------+-----------+---------------+---------+
| OSV URL                             | CVSS | ECOSYSTEM | PACKAGE | VERSION   | FIXED VERSION | SOURCE  |
+-------------------------------------+------+-----------+---------+-----------+---------------+---------+
| https://osv.dev/PYSEC-2026-4320     | 9.1  | PyPI      | certifi | 2026.7.22 | 2026.10.19    | uv.lock |
| https://osv.dev/GHSA-6q48-6c7w-9gw2 |      |           |         |           |               |         |
+-------------------------------------+------+-----------+---------+-----------+---------------+---------+
release: audit failed
```
