from __future__ import annotations

from app.services.career import combined_career_score
from app.services.childcare import childcare_costs
from app.services.col import col_costs
from app.services.commute import couple_commute_tier
from app.services.commute_scoring import commute_feasibility
from app.services.data_loader import load_metros, get_metro_cost_map
from app.services.employers import get_top_employers
from app.services.housing import housing_costs

COST_PREFERENCE_MAX = 10_000
SALARY_PREFERENCE_MAX = 100_000


def inverse_cost_score(value: float, min_value: float, max_value: float) -> float:
    """Retained for compatibility with existing callers and tests."""
    if max_value == min_value:
        return 100.0
    return 100.0 * (max_value - value) / (max_value - min_value)


def budget_match_score(monthly_cost: float, budgets: list[int]) -> float:
    """Score each partner's maximum monthly budget, then average the results."""
    scores = []
    for budget in budgets:
        if budget <= 0:
            scores.append(100.0 if monthly_cost == 0 else 0.0)
        elif monthly_cost <= budget:
            scores.append(100.0)
        else:
            scores.append(max(0.0, 100.0 * budget / monthly_cost))
    return sum(scores) / len(scores)


def salary_match_score(employers: list[dict], field_id: str, monthly_target: int) -> float:
    """Return how well a metro's listed roles meet one partner's salary target."""
    if monthly_target <= 0:
        return 100.0

    matching_roles = [
        role
        for employer in employers
        for role in employer["roles"]
        if role["field"] == field_id
    ]
    if not matching_roles:
        return 0.0

    best_monthly_pay = max(role["pay_max"] / 12 for role in matching_roles)
    return min(100.0, 100.0 * best_monthly_pay / monthly_target)


def normalized_dollar_weight(amount: float, maximum: float) -> float:
    """Use a stated dollar value as a bounded category weight."""
    return 0.25 + min(max(amount, 0) / maximum, 1.0)


def build_weights(preferences: dict, has_kids: bool) -> dict[str, float]:
    partner1 = preferences["partner1_preferences"]
    partner2 = preferences["partner2_preferences"]
    averages = {
        key: (partner1[key] + partner2[key]) / 2
        for key in ("career_importance", "housing", "col", "childcare")
    }

    weights = {
        "career": 0.25 + averages["career_importance"] / 10,
        "housing": normalized_dollar_weight(averages["housing"], COST_PREFERENCE_MAX),
        "col": normalized_dollar_weight(averages["col"], COST_PREFERENCE_MAX),
        "commute": 1.0,
    }
    if has_kids:
        weights["childcare"] = normalized_dollar_weight(
            averages["childcare"],
            COST_PREFERENCE_MAX,
        )

    total = sum(weights.values())
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
        partner1_salary_score = salary_match_score(
            employers,
            preferences["partner1_field"],
            partner1_preferences["salary"],
        )
        partner2_salary_score = salary_match_score(
            employers,
            preferences["partner2_field"],
            partner2_preferences["salary"],
        )
        salary_score = (partner1_salary_score + partner2_salary_score) / 2
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
