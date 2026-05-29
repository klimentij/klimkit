from __future__ import annotations

from .base import Harness, HarnessProjection
from .codex import CODEX_HARNESS


SUPPORTED_HARNESSES = {
    CODEX_HARNESS.name: CODEX_HARNESS,
}


def enabled_harnesses(*, codex_enabled: bool) -> list[Harness]:
    return [CODEX_HARNESS] if codex_enabled else []


def harness_by_name(name: str) -> Harness:
    try:
        return SUPPORTED_HARNESSES[name]
    except KeyError as exc:
        raise ValueError(f"Unsupported harness: {name}") from exc
