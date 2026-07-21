from __future__ import annotations


def commute_feasibility(
    metro_cost: dict,
    partner1_field: str,
    partner1_max: int,
    partner2_field: str,
    partner2_max: int,
) -> dict:
    minutes1 = metro_cost["commute_minutes"].get(partner1_field, 35)
    minutes2 = metro_cost["commute_minutes"].get(partner2_field, 35)
    partner1_ok = minutes1 <= partner1_max
    partner2_ok = minutes2 <= partner2_max
    both_ok = partner1_ok and partner2_ok

    if both_ok:
        score = 100.0
    elif partner1_ok or partner2_ok:
        score = 55.0
    else:
        over1 = max(0, minutes1 - partner1_max)
        over2 = max(0, minutes2 - partner2_max)
        penalty = min(50, (over1 + over2) * 2)
        score = max(0.0, 45.0 - penalty)

    return {
        "score": score,
        "both_ok": both_ok,
        "partner1_minutes": minutes1,
        "partner2_minutes": minutes2,
        "partner1_ok": partner1_ok,
        "partner2_ok": partner2_ok,
    }
