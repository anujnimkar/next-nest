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

    def individual_score(estimated_minutes: int, maximum_minutes: int) -> float:
        if estimated_minutes <= maximum_minutes:
            return 100.0
        return max(0.0, 100.0 * maximum_minutes / estimated_minutes)

    # The lower partner score determines feasibility for a shared location.
    score = min(
        individual_score(minutes1, partner1_max),
        individual_score(minutes2, partner2_max),
    )

    return {
        "score": score,
        "both_ok": both_ok,
        "partner1_minutes": minutes1,
        "partner2_minutes": minutes2,
        "partner1_ok": partner1_ok,
        "partner2_ok": partner2_ok,
    }
