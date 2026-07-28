from app.services.commute import couple_commute_tier, tier_for_commute
from app.services.housing import housing_costs, monthly_mortgage
from app.services.scoring import budget_match_score, inverse_cost_score, rank_metros


def test_tier_for_commute_boundaries(app):
    with app.app_context():
        assert tier_for_commute(15)["tier"] == 1
        assert tier_for_commute(25)["tier"] == 2
        assert tier_for_commute(40)["tier"] == 3
        assert tier_for_commute(60)["tier"] == 4


def test_couple_uses_shorter_commute(app):
    with app.app_context():
        tier = couple_commute_tier(20, 45)
        assert tier["tier"] == 1


def test_monthly_mortgage_positive():
    payment = monthly_mortgage(400000)
    assert 2500 < payment < 3500


def test_inverse_cost_score():
    assert inverse_cost_score(50, 0, 100) == 50
    assert inverse_cost_score(0, 0, 100) == 100
    assert inverse_cost_score(100, 0, 100) == 0


def test_budget_match_score_rewards_costs_within_budget():
    assert budget_match_score(2000, [2500, 3000]) == 100
    assert budget_match_score(4000, [2000, 4000]) == 75


def test_rank_metros_returns_fifty(app):
    with app.app_context():
        preferences = {
            "partner1_field": "software_tech",
            "partner1_commute": 35,
            "partner2_field": "healthcare",
            "partner2_commute": 30,
            "has_kids": True,
            "partner1_preferences": {"career_importance": 5, "salary": 10000, "housing": 3000, "col": 1500, "childcare": 2000},
            "partner2_preferences": {"career_importance": 5, "salary": 10000, "housing": 3000, "col": 1500, "childcare": 2000},
        }
        ranked = rank_metros(preferences)
        assert len(ranked) == 50
        assert ranked[0]["overall_score"] >= ranked[-1]["overall_score"]


def test_expensive_metros_lower_housing_score_for_tech(app):
    with app.app_context():
        preferences = {
            "partner1_field": "software_tech",
            "partner1_commute": 20,
            "partner2_field": "software_tech",
            "partner2_commute": 20,
            "has_kids": False,
            "partner1_preferences": {"career_importance": 1, "salary": 5000, "housing": 1500, "col": 1000, "childcare": 1000},
            "partner2_preferences": {"career_importance": 1, "salary": 5000, "housing": 1500, "col": 1000, "childcare": 1000},
        }
        ranked = rank_metros(preferences)
        by_id = {row["metro"]["id"]: row for row in ranked}
        assert by_id["birmingham"]["category_scores"]["housing"] > by_id["sf"]["category_scores"]["housing"]


def test_housing_costs_respect_tier(app):
    with app.app_context():
        from app.services.data_loader import get_metro_cost_map

        metro = get_metro_cost_map()["austin"]
        tier1 = tier_for_commute(15)
        tier4 = tier_for_commute(60)
        high = housing_costs(metro, tier1)
        low = housing_costs(metro, tier4)
        assert low["rent"] < high["rent"]


def test_full_flow(client):
    response = client.get("/")
    assert response.status_code == 200

    response = client.post(
        "/?step=1",
        data={"career_field": "software_tech", "max_commute": 35},
        follow_redirects=False,
    )
    assert response.status_code == 302

    response = client.post(
        "/?step=2",
        data={"career_field": "healthcare", "max_commute": 30},
        follow_redirects=False,
    )
    assert response.status_code == 302

    response = client.post(
        "/?step=3",
        data={
            "has_kids": "yes",
            "partner1_career_importance": 5,
            "partner1_salary": 10000,
            "partner1_housing": 3000,
            "partner1_col": 1500,
            "partner1_childcare": 2000,
            "partner2_career_importance": 5,
            "partner2_salary": 10000,
            "partner2_housing": 3000,
            "partner2_col": 1500,
            "partner2_childcare": 2000,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Ranked metro areas" in response.data
    assert response.data.count(b'class="result-card"') == 50
    assert b"Top employers in this area" in response.data


def test_ranked_metros_include_employers(app):
    with app.app_context():
        preferences = {
            "partner1_field": "software_tech",
            "partner1_commute": 35,
            "partner2_field": "data_engineering",
            "partner2_commute": 30,
            "has_kids": False,
            "partner1_preferences": {"career_importance": 5, "salary": 10000, "housing": 3000, "col": 1500, "childcare": 2000},
            "partner2_preferences": {"career_importance": 5, "salary": 10000, "housing": 3000, "col": 1500, "childcare": 2000},
        }
        ranked = rank_metros(preferences)
        seattle = next(row for row in ranked if row["metro"]["id"] == "seattle")
        assert len(seattle["employers"]) == 5
        assert seattle["employers"][0]["roles"]
        assert "pay_min" in seattle["employers"][0]["roles"][0]
