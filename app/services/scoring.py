from __future__ import annotations

from app.services.career import combined_career_score
from app.services.childcare import childcare_costs
from app.services.col import col_costs
from app.services.commute import couple_commute_tier
from app.services.commute_scoring import commute_feasibility
from app.services.data_loader import load_metros, get_metro_cost_map
from app.services.employers import get_top_employers
from app.services.housing import housing_costs

DEFAULT_WEIGHTS = {
    "career": 3,
    "housing": 3,
    "col": 2,
    "commute": 2,
    "childcare": 2,
}


def inverse_cost_score(value: float, min_value: float, max_value: float) -> float:
    if max_value == min_value:
        return 100.0
    return 100.0 * (max_value - value) / (max_value - min_value)


def average_weights(partner1_weights: dict[str, int], partner2_weights: dict[str, int]) -> dict[str, float]:
    keys = DEFAULT_WEIGHTS.keys()
    averaged = {key: (partner1_weights.get(key, DEFAULT_WEIGHTS[key]) + partner2_weights.get(key, DEFAULT_WEIGHTS[key])) / 2 for key in keys}
    total = sum(averaged.values()) or 1
    return {key: value / total for key, value in averaged.items()}


def rank_metros(preferences: dict) -> list[dict]:
    metros = load_metros()
    cost_map = get_metro_cost_map()
    tier = couple_commute_tier(preferences["partner1_commute"], preferences["partner2_commute"])
    has_kids = preferences.get("has_kids", False)

    raw_results = []
    for metro in metros:
        metro_cost = cost_map[metro["id"]]
        housing = housing_costs(metro_cost, tier)
        col = col_costs(metro_cost, tier)
        childcare = childcare_costs(metro_cost)
        career = combined_career_score(metro_cost, preferences["partner1_field"], preferences["partner2_field"])
        commute = commute_feasibility(
            metro_cost,
            preferences["partner1_field"],
            preferences["partner1_commute"],
            preferences["partner2_field"],
            preferences["partner2_commute"],
        )
        raw_results.append(
            {
                "metro": metro,
                "tier": tier,
                "housing": housing,
                "col": col,
                "childcare": childcare,
                "career_raw": career,
                "commute_raw": commute,
            }
        )

    housing_values = [item["housing"]["burden"] for item in raw_results]
    col_values = [item["col"]["total"] for item in raw_results]
    childcare_values = [item["childcare"]["total"] for item in raw_results]

    housing_min, housing_max = min(housing_values), max(housing_values)
    col_min, col_max = min(col_values), max(col_values)
    childcare_min, childcare_max = min(childcare_values), max(childcare_values)

    weights = average_weights(preferences["partner1_weights"], preferences["partner2_weights"])
    if not has_kids:
        childcare_weight = weights.pop("childcare", 0)
        if childcare_weight:
            redistribute = childcare_weight / len(weights)
            weights = {key: value + redistribute for key, value in weights.items()}

    ranked = []
    for item in raw_results:
        category_scores = {
            "career": round(item["career_raw"], 1),
            "housing": round(inverse_cost_score(item["housing"]["burden"], housing_min, housing_max), 1),
            "col": round(inverse_cost_score(item["col"]["total"], col_min, col_max), 1),
            "commute": round(item["commute_raw"]["score"], 1),
            "childcare": round(inverse_cost_score(item["childcare"]["total"], childcare_min, childcare_max), 1),
        }
        overall = round(sum(category_scores[key] * weights[key] for key in weights), 1)
        employers = get_top_employers(
            item["metro"]["id"],
            preferences["partner1_field"],
            preferences["partner2_field"],
        )
        ranked.append(
            {
                "metro": item["metro"],
                "tier": item["tier"],
                "housing": item["housing"],
                "col": item["col"],
                "childcare": item["childcare"],
                "commute": item["commute_raw"],
                "employers": employers,
                "category_scores": category_scores,
                "overall_score": overall,
                "weights": weights,
            }
        )

    ranked.sort(key=lambda row: row["overall_score"], reverse=True)
    return ranked
