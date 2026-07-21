from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from flask import current_app


@lru_cache(maxsize=1)
def _data_dir() -> Path:
    return Path(current_app.config["DATA_DIR"])


def _load_json(filename: str):
    path = _data_dir() / filename
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_metros() -> list[dict]:
    return _load_json("metros.json")


def load_commute_tiers() -> list[dict]:
    return _load_json("commute_tiers.json")


def load_career_fields() -> list[dict]:
    return _load_json("career_fields.json")


def load_metro_costs() -> list[dict]:
    return _load_json("metro_costs.json")


def load_metro_employers() -> list[dict]:
    return _load_json("metro_employers.json")


def get_metro_cost_map() -> dict[str, dict]:
    return {item["id"]: item for item in load_metro_costs()}


def get_career_field_map() -> dict[str, dict]:
    return {item["id"]: item for item in load_career_fields()}


def get_metro_employer_map() -> dict[str, list[dict]]:
    return {item["metro_id"]: item["employers"] for item in load_metro_employers()}


def clear_cache() -> None:
    _data_dir.cache_clear()
