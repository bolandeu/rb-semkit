"""The CLI pipeline: `semkit read IN STEP … write OUT` (ADR 0008).

`group` chains the steps (Click chain), `commands` makes a command of each entry of the step table, `items` resolves
the list arguments, `state` runs the steps over the current table, `tables` reads and writes through dataio (ADR 0001).
"""
