SEMKIT-023 attempt 1 (file docstring) done: I applied every note. The gate passes, and `scripts/check_command_docstrings.py` passes.

1. src/rb_semkit/cli.py: a new module docstring. It says the root command registers every module of the commands package by name, and --ai adds each `ai_section()`.
2. src/rb_semkit/commands/read.py: a new module docstring. It names the pipeline command, read, the steps from `steps.areas()`, write and `ai_section()`.
3. src/rb_semkit/core/errors.py: a new module docstring. It says what a CliError carries and that InvalidArguments is a usage error (exit 2).
4. src/rb_semkit/core/frame.py: the docstring now names `text_columns`.
5. src/rb_semkit/core/markers/lists.py: the docstring now names `phrases` (used by pipeline/items.py for `@name`).
6. src/rb_semkit/core/text/base.py: the docstring now names `verbs` (used by steps/text.py).

No code changed, only docstrings.
