from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HarnessProjection:
    id: str
    source: Path
    target: Path
    kind: str
    description: str
    component: str
    exclude_prefixes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Harness:
    name: str
    projections: tuple[HarnessProjection, ...]
    managed_roots: tuple[Path, ...]
