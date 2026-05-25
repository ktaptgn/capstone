from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def load_log_entry_schema(schema_path: str | Path) -> dict[str, Any]:
    with Path(schema_path).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def validate_log_entry(entry: dict[str, Any], schema: dict[str, Any]) -> None:
    Draft202012Validator(schema).validate(entry)


def write_policy_log(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2)


def read_policy_log(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as stream:
        return json.load(stream)
