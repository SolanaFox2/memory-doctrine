"""Shared score clamps — the ONE canonical pair (REVIEW.md M3).

``score``, ``verify``, and the CLI all clamp model-supplied scores into the
doctrine's bounds (confidence in [0, 1], generativity in 1..5). Three local
copies had drifted: the CLI's generativity clamp used ``int(value)``, so a
numeric string like ``"4.0"`` raised and collapsed to 1 (REVIEW.md M2). Every
caller imports these; the only per-caller variation is the documented fallback.
"""

from __future__ import annotations


def clamp_confidence(value: object, fallback: float = 0.0) -> float:
    """Coerce ``value`` to a float clamped to [0, 1]; ``fallback`` on garbage.

    Callers pass the fallback their stage documents: score and the CLI use the
    default 0.0 (garbage earns no confidence), verify passes the idea's prior.
    """
    try:
        c = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return fallback
    if c < 0.0:
        return 0.0
    if c > 1.0:
        return 1.0
    return c


def clamp_generativity(value: object, fallback: int = 1) -> int:
    """Coerce ``value`` to an int clamped to 1..5; ``fallback`` on garbage.

    Accepts numeric strings via ``round(float(...))`` so a stringly-typed score
    like ``"4.0"`` keeps its value instead of collapsing to the floor.
    """
    try:
        g = int(round(float(value)))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return fallback
    if g < 1:
        return 1
    if g > 5:
        return 5
    return g
