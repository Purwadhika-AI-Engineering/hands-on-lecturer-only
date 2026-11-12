"""Guardrail layers for AcmeBot.

The five files in this package are the ONLY files you need to edit in the lab
(plus app/prompts.py for one finding). Each file is one layer of defense in depth:

    input_guard.py    Layer 1  what may reach the model
    data_guard.py     Layer 2  what documents may enter / be retrieved / how they are shown
    tool_guard.py     Layer 3  what the agent may DO
    output_guard.py   Layer 4  what may leave the system
    runtime_guard.py  Layer 5  how much, how fast, how long

Every layer ships as a pass-through stub. Your job: make the attack suite fail to hurt us.
"""
from dataclasses import dataclass


@dataclass
class GuardResult:
    """Return value of input / data / output / runtime guards."""

    allowed: bool = True
    reason: str = ""
    text: str | None = None  # sanitized replacement text, if the guard rewrote it


@dataclass
class ToolDecision:
    """Return value of tool_guard.authorize()."""

    allow: bool = True
    reason: str = ""
    needs_approval: bool = False  # True = queue for a human instead of executing
