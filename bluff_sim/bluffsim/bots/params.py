"""Shared machinery for tunable parameter sets.

A subclass is a dataclass with a class attribute BOUNDS mapping each field
to (low, high, is_int). The genetic search only uses the methods here, so
any strategy with such a parameter set can be tuned.
"""
from __future__ import annotations

import random
from dataclasses import asdict, fields


class TunableParams:
    BOUNDS: dict = {}

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict):
        names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in names})

    def clipped(self):
        out = {}
        for k, v in self.to_dict().items():
            lo, hi, is_int = self.BOUNDS[k]
            v = min(hi, max(lo, v))
            out[k] = int(round(v)) if is_int else round(float(v), 3)
        return type(self)(**out)

    @classmethod
    def random(cls, rng: random.Random):
        return cls(**{k: rng.uniform(lo, hi) for k, (lo, hi, _)
                      in cls.BOUNDS.items()}).clipped()

    def mutate(self, rng: random.Random, rate=0.3, scale=0.15):
        d = self.to_dict()
        for k, (lo, hi, _) in self.BOUNDS.items():
            if rng.random() < rate:
                d[k] = d[k] + rng.gauss(0, scale * (hi - lo))
        return type(self)(**d).clipped()

    @classmethod
    def crossover(cls, a, b, rng: random.Random):
        da, db = a.to_dict(), b.to_dict()
        return cls(**{k: (da[k] if rng.random() < 0.5 else db[k])
                      for k in da}).clipped()

    def distance(self, other) -> float:
        """Mean absolute difference, each parameter scaled to 0-1."""
        da, db = self.to_dict(), other.to_dict()
        return sum(abs(da[k] - db[k]) / (hi - lo)
                   for k, (lo, hi, _) in self.BOUNDS.items()) / len(self.BOUNDS)
