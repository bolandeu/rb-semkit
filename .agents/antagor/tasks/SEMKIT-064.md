---
id: SEMKIT-064
title: docs --out reports success again (lost in the v1.18.2 template merge)
status: queue
attempts: 1
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: architect
worker: claude-code
type: bugfix
owns_paths:
- src/rb_semkit/commands/docs.py
- tests/docs_cmd/
test_paths:
- tests/docs_cmd/
docs: none
tools: []
worker_args: null
class: mechanical
decision: false
visual: null
depends_on:
- SEMKIT-063
budget_usd: null
epic: null
spec_refs: []
checks:
- uv run --extra vectors pytest
resident: null
tool: null
pr: null
translation: semkit docs --out снова сообщает об успехе (строка потерялась при слиянии
  шаблона v1.18.2).
---

In the v1.18.2 template merge (SEMKIT-063) src/rb_semkit/commands/docs.py lost the line after out.write_text: output.emit_success(ctx, {"path": str(out)}, lambda data: output.human.echo(f"Wrote {data['path']}")). Now 'semkit docs --out FILE' prints nothing and gives no JSON envelope. Restore it after the try block; keep the template's OSError -> InvalidArguments. Add the test.

## Read first

- `src/rb_semkit/commands/docs.py` — the command

## Out of scope

- The document itself.

## Acceptance

- Given semkit docs --out FILE, When it runs, Then it prints 'Wrote FILE'; with --json it prints the success envelope with path [check: tests/docs_cmd/]

## How to test

Integration through the CLI runner, a file in tmp_path.

## Basis

SEMKIT-063 merge of commands/docs.py: keep the template's OSError -> InvalidArguments.

## Feedback

### Attempt 1: checks failed

- `uv run --extra vectors pytest` (exit 1)

```
sed database in <sqlite3.Connection object at 0x135cd9a80>
  return compile(source, filename, mode, flags,
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/ast.py:46: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1368b89a0>
  return compile(source, filename, mode, flags,
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/ast.py:46: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x133fdf4c0>
  return compile(source, filename, mode, flags,
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/ast.py:46: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x13638a110>
  return compile(source, filename, mode, flags,
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/ast.py:46: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x12ffbe3e0>
  return compile(source, filename, mode, flags,
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/ast.py:46: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x12abf5d50>
  return compile(source, filename, mode, flags,
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/ast.py:46: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x140298c70>
  return compile(source, filename, mode, flags,
ResourceWarning: Enable tracemalloc to get the object allocation traceback
```
