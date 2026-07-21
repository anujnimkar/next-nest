from __future__ import annotations

from app.services.data_loader import get_career_field_map


def career_score_for_partner(metro_cost: dict, field_id: str) -> float:
    field = get_career_field_map()[field_id]
    concentration = metro_cost["career_scores"].get(field_id, 50)
    growth = field["growth_rate"]
    growth_score = min(growth / 15 * 100, 100)
    return 0.65 * concentration + 0.35 * growth_score


def combined_career_score(metro_cost: dict, partner1_field: str, partner2_field: str) -> float:
    score1 = career_score_for_partner(metro_cost, partner1_field)
    score2 = career_score_for_partner(metro_cost, partner2_field)
    return (score1 + score2) / 2
