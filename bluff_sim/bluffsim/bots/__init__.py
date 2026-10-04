"""Strategy registry.

A seat is given as a spec string:
    honest | helper | drifter | anchor | opportunist | careful_drifter
    adaptive                    default adaptive parameters
    adaptive:path/to/params.json  tuned parameters saved by `tune`

To add a strategy, subclass `Bot` (see base.py) and add it to STRATEGIES.
"""
import json

from .adaptive import Adaptive, Params
from .base import Bot
from .simple import (Anchor, CarefulDrifter, Drifter, GroupHelper, Honest,
                     Opportunist)

STRATEGIES = {
    "honest": Honest,
    "helper": GroupHelper,
    "drifter": Drifter,
    "anchor": Anchor,
    "opportunist": Opportunist,
    "careful_drifter": CarefulDrifter,
    "adaptive": Adaptive,
}


def make_bot(spec: str) -> Bot:
    name, _, arg = spec.partition(":")
    if name not in STRATEGIES:
        raise ValueError(f"unknown strategy {name!r}; "
                         f"choose from {sorted(STRATEGIES)}")
    if name == "adaptive" and arg:
        with open(arg) as f:
            data = json.load(f)
        return Adaptive(Params.from_dict(data.get("params", data)),
                        label=data.get("label", "adaptive"))
    return STRATEGIES[name]()


def make_table(specs) -> list[Bot]:
    return [make_bot(s) if isinstance(s, str) else s for s in specs]
