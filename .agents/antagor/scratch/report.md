SEMKIT-023 done: the gate passes (`uv run scripts/release.py --check`, 1.7 min) and `scripts/check_command_docstrings.py` passes.

What is built:
1. `semkit read IN [--column C] [--whole] [--trace FILE] STEP… write OUT [--overwrite]` in `src/rb_semkit/pipeline/` and `src/rb_semkit/commands/read.py`.
   Typer 0.27 ships a Click without chained groups, so `PipelineGroup` chains the steps itself. It parses every step first, then reads the input.
2. The step table is in `src/rb_semkit/steps/` (one module per area: text, dupes, analysis), and `areas()` discovers the modules. The generator in `pipeline/commands.py` makes one command per entry from the signature and the docstring.
3. The text steps are `<verb>-<matcher>` for the verbs the matcher class supports (`core.text.base.verbs`), plus `keep-`/`drop-<matcher>`: 55 steps. Also `dupes` (`--action drop` is a filter), `ngrams` and `bigrams`.
4. To give the generator Literal choices, the choice arguments of the matchers and of `dupes` (and `compare_lists` kind) are now `Literal` types. The runtime checks read their allowed values from the same Literal.
5. `cli.py` registers every module of the commands package. `--ai` prints SKILL.md, then each module's `ai_section()`.
6. rb-dataio is a required dependency, pinned to the homeserver repo at tag v0.1.21 (the GitHub URL in plan §3 does not exist).
7. The bench part `scripts/bench_parts/cli.py` runs 1M phrases through 5 cleaning steps from parquet to parquet in 6.25 s (the budget is 120 s). `tests/pipeline/test_speed.py` (marker `speed`) runs it.

Red run before the code: 35 failed in tests/pipeline (no read command).

Changed existing tests:
- tests/test_help.py: a step's help is rendered as `read IN <step> --help`, and its snapshot is at steps/<area>/<step>.txt. The Example check accepts `semkit read IN … <step>`.
- tests/test_describe.py::test_options_are_the_real_ones: it uses the same help argv.
- tests/test_cli.py::test_bare_group_shows_help_and_exits_zero: `read` is added.
- tests/snapshots/describe.json: the new commands. The root command order is now alphabetical, by module discovery.

Open questions in the inbox: #1 is `hint` vs `action` in the error envelope (I kept `action`). #2 is the epic's positional `drop-words @list` vs the task's `--items` (I implemented options).
Findings: #3 is the ADR 0001 wording about the [io] extra. #4 is about Typer internals imported by the pipeline group.
