SEMKIT-023 round 2 done: I applied the Architect's answers to inbox #1–#4. The gate passes, and `scripts/check_command_docstrings.py` passes.

1. #1, the error envelope: it keeps `action`. Nothing changed.
2. #2, the first required argument: it is now positional and is also accepted as `--NAME`. The other arguments stay options.
   - `drop-words @minus/universal`, `remove-chars punctuation` and `remove-words --items купить` all work.
   - A value given in both forms is refused: exit 2, and the message names the step and both forms. A value given in neither form is refused the same way.
   - The pipeline group now cuts the command line at each word that names a step, but not at the value of an option. So a step's options and its positional value can come in any order.
   - A word after IN that names no step is refused with Typer's «No such command», which suggests near names.
   - The Example lines of the step help now use the positional form.
3. #3: no change in this round. docs/plan.md §3.2 was already updated in round 1.
4. #4: pyproject now pins `typer>=0.27,<0.28`, with a comment that names pipeline/group.py.

New tests in tests/pipeline, red before the code:
- the epic line with positional arguments
- the positional form and the option form give the same rows
- a value given twice is refused
- a missing value names both forms
- an unknown word after a step is refused, naming it

Help snapshots are refreshed, because the steps now show an Arguments panel.
