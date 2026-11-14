from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import urlparse


@dataclass
class EnvAssertError(Exception):
    missing: list[str]
    invalid: list[tuple[str, str]]

    def __str__(self) -> str:  # pragma: no cover - trivial
        parts: list[str] = []
        if self.missing:
            parts.append(f"missing: {', '.join(self.missing)}")
        if self.invalid:
            parts.append(
                "invalid: "
                + ", ".join(f"{name} ({reason})" for name, reason in self.invalid)
            )
        return f"Environment validation failed ({'; '.join(parts)})"


def _parse_bool(raw: str) -> bool | None:
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return None


def assert_env(
    schema: Mapping[str, Mapping[str, Any]],
    source: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Validate environment variables.

    Schema keys are env names. Each value is a dict with optional keys:
    ``type`` (string|int|float|bool|url|enum), ``required``, ``default``,
    ``min``, ``max``, ``values`` (for enum).
    """
    env = source if source is not None else os.environ
    missing: list[str] = []
    invalid: list[tuple[str, str]] = []
    out: dict[str, Any] = {}

    for name, spec in schema.items():
        raw = env.get(name)
        required = spec.get("required", True)
        if "default" in spec:
            required = False

        if raw is None or raw == "":
            if "default" in spec:
                out[name] = spec["default"]
            elif required:
                missing.append(name)
            else:
                out[name] = None
            continue

        kind = spec.get("type", "string")
        if kind == "string":
            out[name] = raw
        elif kind == "int":
            try:
                number = int(raw.strip())
            except ValueError:
                invalid.append((name, "expected integer"))
                continue
            if "min" in spec and number < spec["min"]:
                invalid.append((name, f"expected >= {spec['min']}"))
                continue
            if "max" in spec and number > spec["max"]:
                invalid.append((name, f"expected <= {spec['max']}"))
                continue
            out[name] = number
        elif kind == "float":
            try:
                number = float(raw)
            except ValueError:
                invalid.append((name, "expected number"))
                continue
            if "min" in spec and number < spec["min"]:
                invalid.append((name, f"expected >= {spec['min']}"))
                continue
            if "max" in spec and number > spec["max"]:
                invalid.append((name, f"expected <= {spec['max']}"))
                continue
            out[name] = number
        elif kind == "bool":
            parsed = _parse_bool(raw)
            if parsed is None:
                invalid.append((name, "expected boolean (true/false/1/0)"))
                continue
            out[name] = parsed
        elif kind == "url":
            parsed_url = urlparse(raw)
            if not parsed_url.scheme or not parsed_url.netloc:
                invalid.append((name, "expected URL"))
                continue
            out[name] = raw
        elif kind == "enum":
            values = list(spec.get("values", []))
            if raw not in values:
                invalid.append((name, f"expected one of: {', '.join(values)}"))
                continue
            out[name] = raw
        else:
            invalid.append((name, "unknown type"))

    if missing or invalid:
        raise EnvAssertError(missing, invalid)
    return out


__all__ = ["EnvAssertError", "assert_env"]
