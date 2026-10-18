"""The steps of each area of the step table, one module per area (the pipeline core's areas are in tests/pipeline).

A module holds `COMMANDS`: a command line for each step of the area. A new step is one line in the module of its area,
a new area one new module; no file is shared by the areas.
"""

from __future__ import annotations

import importlib
import pkgutil

_MODULES = {
    module.name: importlib.import_module(f"{__name__}.{module.name}") for module in pkgutil.iter_modules(__path__)
}
COMMANDS_BY_AREA = {area: module.COMMANDS for area, module in _MODULES.items()}
AREAS = {area: sorted(commands) for area, commands in COMMANDS_BY_AREA.items()}
COMMANDS = {step: argv for commands in COMMANDS_BY_AREA.values() for step, argv in commands.items()}
