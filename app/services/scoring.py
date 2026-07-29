from __future__ import annotations

import math

from app.services.career import career_score_for_partner
from app.services.childcare import childcare_costs
from app.services.col import col_costs
from app.services.commute import couple_commute_tier
from app.services.commute_scoring import commute_feasibility
from app.services.data_loader import load_metros, get_metro_cost_map
from app.services.employers import get_top_employers
from app.services.housing import housing_costs

def inverse_cost_score(value: float, min_value: float, max_value: float) -> float:
    """Retained for compatibility with existing callers and tests."""
    if max_value == min_value:
        return 100.0
    return 100.0 * (max_value - value) / (max_value - min_value)


def budget_match_score(monthly_cost: float, budgets: list[int]) -> float:
    """Score a shared expense against the couple's combined soft budget."""
    household_budget = sum(budgets)
    if household_budget <= 0:
        return 100.0 if monthly_cost == 0 else 0.0
    if monthly_cost <= household_budget:
        return 100.0
    return max(0.0, 100.0 * household_budget / monthly_cost)


def best_monthly_pay(employers: list[dict], field_id: str) -> float:
    matching_roles = [
        role
        for employer in employers
        for role in employer["roles"]
        if role["field"] == field_id
    ]
    if not matching_roles:
        return 0.0
    return max(role["pay_max"] / 12 for role in matching_roles)


def salary_match_score(monthly_pay: float, monthly_target: int) -> float:
    """Return how well a monthly salary estimate meets one partner's target."""
    if monthly_target <= 0:
        return 100.0
    return min(100.0, 100.0 * monthly_pay / monthly_target)


def geometric_mean(left: float, right: float) -> float:
    """Prevent one partner's strong outcome from hiding the other's weak one."""
    return math.sqrt(max(left, 0.0) * max(right, 0.0))


def build_weights(preferences: dict, has_kids: bool) -> dict[str, float]:
    partner1 = preferences["partner1_preferences"]
    partner2 = preferences["partner2_preferences"]
    weights = {
        # At 5, career has equal weight to each fixed category. At 0 it is
        # omitted; at 10 it receives double the fixed category weight.
        "career": (partner1["career_importance"] + partner2["career_importance"]) / 10,
        "housing": 1.0,
        "col": 1.0,
        "commute": 1.0,
    }
    if has_kids:
        weights["childcare"] = 1.0

    total = sum(weights.values())
    if total == 0:
        return {key: 1 / len(weights) for key in weights}
    return {key: value / total for key, value in weights.items()}


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
        partner1_career = career_score_for_partner(
            metro_cost,
            preferences["partner1_field"],
        )
        partner2_career = career_score_for_partner(
            metro_cost,
            preferences["partner2_field"],
        )
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
                "career_raw": geometric_mean(partner1_career, partner2_career),
                "commute_raw": commute,
            }
        )

    partner1_preferences = preferences["partner1_preferences"]
    partner2_preferences = preferences["partner2_preferences"]
    weights = build_weights(preferences, has_kids)

    ranked = []
    for item in raw_results:
        employers = get_top_employers(
            item["metro"]["id"],
            preferences["partner1_field"],
            preferences["partner2_field"],
        )
        partner1_monthly_pay = best_monthly_pay(
            employers,
            preferences["partner1_field"],
        )
        partner2_monthly_pay = best_monthly_pay(
            employers,
            preferences["partner2_field"],
        )
        partner1_salary_score = salary_match_score(
            partner1_monthly_pay,
            partner1_preferences["salary"],
        )
        partner2_salary_score = salary_match_score(
            partner2_monthly_pay,
            partner2_preferences["salary"],
        )
        individual_salary_score = geometric_mean(
            partner1_salary_score,
            partner2_salary_score,
        )
        household_salary_score = salary_match_score(
            partner1_monthly_pay + partner2_monthly_pay,
            partner1_preferences["salary"] + partner2_preferences["salary"],
        )
        salary_score = 0.7 * individual_salary_score + 0.3 * household_salary_score
        category_scores = {
            "career": round(0.6 * item["career_raw"] + 0.4 * salary_score, 1),
            "housing": round(
                budget_match_score(
                    item["housing"]["burden"],
                    [partner1_preferences["housing"], partner2_preferences["housing"]],
                ),
                1,
            ),
            "col": round(
                budget_match_score(
                    item["col"]["total"],
                    [partner1_preferences["col"], partner2_preferences["col"]],
                ),
                1,
            ),
            "commute": round(item["commute_raw"]["score"], 1),
            "childcare": round(
                budget_match_score(
                    item["childcare"]["total"],
                    [partner1_preferences["childcare"], partner2_preferences["childcare"]],
                ),
                1,
            ),
        }
        overall = round(sum(category_scores[key] * weights[key] for key in weights), 1)
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
