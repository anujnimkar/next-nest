from __future__ import annotations

from app.services.data_loader import load_commute_tiers


def tier_for_commute(max_commute_minutes: int) -> dict:
    for tier in load_commute_tiers():
        if tier["min_minutes"] <= max_commute_minutes <= tier["max_minutes"]:
            return tier
    return load_commute_tiers()[-1]


def couple_commute_tier(partner1_max: int, partner2_max: int) -> dict:
    restrictive = min(partner1_max, partner2_max)
    return tier_for_commute(restrictive)
