"""The marker steps: each verb of the marker matcher, and the keep and drop filters (ADR 0004)."""

from __future__ import annotations

from ..core.markers.matcher import markers
from .text import matcher_steps

STEPS = matcher_steps(markers)
