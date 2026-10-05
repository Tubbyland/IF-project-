"""Strategy registry.

A seat is given as a spec string:
    honest | helper | drifter | anchor | opportunist | careful_drifter
    adaptive                    default adaptive parameters
    adaptive:path/to/params.json  tuned parameters saved by `tune`
    bluffer                     solo-seeker that hides its run (bluffer.py)
    bluffer:path/to/params.json

To add a strategy, subclass `Bot` (see base.py) and add it to STRATEGIES.
"""
import json

from .adaptive import Adaptive, Params
from .base import Bot
from .bluffer import Bluffer, BluffParams
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
    "bluffer": Bluffer,
}


def make_bot(spec: str) -> Bot:
    name, _, arg = spec.partition(":")
    if name not in STRATEGIES:
        raise ValueError(f"unknown strategy {name!r}; "
                         f"choose from {sorted(STRATEGIES)}")
    if name in ("adaptive", "bluffer") and arg:
        with open(arg) as f:
            data = json.load(f)
        cls, pcls = ((Adaptive, Params) if name == "adaptive"
                     else (Bluffer, BluffParams))
        return cls(pcls.from_dict(data.get("params", data)),
                   label=data.get("label", name))
    return STRATEGIES[name]()


def make_table(specs) -> list[Bot]:
    return [make_bot(s) if isinstance(s, str) else s for s in specs]
