"""Typed configuration for the package-research pipeline.

Modeled on the proven job-scout architecture: a single pydantic config object
loaded from explicit arguments and/or environment variables. Secrets (the
Anthropic API key) are NEVER hardcoded — they are read from the environment.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _env_int(name: str, raw: str) -> int:
    """Parse an integer env var, naming the variable on failure (REVIEW.md L3)."""
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"environment variable {name} must be an integer, got {raw!r}") from exc


class Config(BaseModel):
    """Pipeline configuration.

    Construct directly, or use :meth:`from_env` to pull defaults from the
    environment. The API key is intentionally not part of the model — it is
    resolved at call-time from ``ANTHROPIC_API_KEY`` so it never lands in a
    serialized config or a log line.
    """

    input_dir: Path = Field(..., description="Folder of source notes (.md/.txt) to ingest.")
    output_dir: Path = Field(
        default=Path("./kpm-out"),
        description="Where the produced KPM package will be written.",
    )
    model: str = Field(
        default="claude-sonnet-4-6",
        description="Anthropic model used for the LLM-backed stages.",
    )
    max_sources: int = Field(
        default=200,
        ge=1,
        description="Cap on the number of source files ingested.",
    )
    max_chunk_chars: int = Field(
        default=1500,
        ge=100,
        description="Target maximum characters per ingested passage/chunk.",
    )
    max_tokens: int = Field(
        default=4096,
        ge=256,
        description="Response token cap for LLM calls; hitting it raises TruncationError instead of silently dropping output.",
    )
    distill_batch_size: int = Field(
        default=40,
        ge=1,
        description="Candidates per distill LLM call (batched so large corpora can't overflow one response).",
    )

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("input_dir", "output_dir", mode="before")
    @classmethod
    def _coerce_path(cls, v: object) -> Path:
        return Path(v) if not isinstance(v, Path) else v

    @classmethod
    def from_env(
        cls,
        input_dir: Optional[os.PathLike | str] = None,
        output_dir: Optional[os.PathLike | str] = None,
        **overrides: object,
    ) -> "Config":
        """Build a Config from explicit args, falling back to env vars.

        Recognized env vars: ``PR_INPUT_DIR``, ``PR_OUTPUT_DIR``, ``PR_MODEL``,
        ``PR_MAX_SOURCES``. Explicit arguments win over env vars, which win over
        the model defaults.
        """
        data: dict[str, object] = {}

        resolved_input = input_dir or os.environ.get("PR_INPUT_DIR")
        if resolved_input is None:
            raise ValueError("input_dir is required (pass it explicitly or set PR_INPUT_DIR)")
        data["input_dir"] = resolved_input

        resolved_output = output_dir or os.environ.get("PR_OUTPUT_DIR")
        if resolved_output is not None:
            data["output_dir"] = resolved_output

        if (m := os.environ.get("PR_MODEL")) is not None:
            data["model"] = m
        if (ms := os.environ.get("PR_MAX_SOURCES")) is not None:
            data["max_sources"] = _env_int("PR_MAX_SOURCES", ms)
        if (mt := os.environ.get("PR_MAX_TOKENS")) is not None:
            data["max_tokens"] = _env_int("PR_MAX_TOKENS", mt)
        if (bs := os.environ.get("PR_DISTILL_BATCH_SIZE")) is not None:
            data["distill_batch_size"] = _env_int("PR_DISTILL_BATCH_SIZE", bs)

        data.update(overrides)
        return cls(**data)

    @staticmethod
    def resolve_api_key() -> str:
        """Resolve the Anthropic API key from the environment.

        Never stored on the Config object. Raises if missing so failures are
        explicit rather than silent.
        """
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Export it before running the LLM-backed stages (distill/score/verify)."
            )
        return key
