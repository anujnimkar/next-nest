from __future__ import annotations

from app.services.data_loader import get_career_field_map, get_metro_employer_map


def _relevance_score(employer: dict, partner_fields: set[str]) -> int:
    overlap = len(set(employer["fields"]) & partner_fields)
    return overlap


def _prioritize_roles(roles: list[dict], partner_fields: set[str]) -> list[dict]:
    matching = [role for role in roles if role["field"] in partner_fields]
    if matching:
        return matching[:3]
    return roles[:3]


def get_top_employers(
    metro_id: str,
    partner1_field: str,
    partner2_field: str,
    limit: int = 5,
) -> list[dict]:
    partner_fields = {partner1_field, partner2_field}
    employers = get_metro_employer_map().get(metro_id, [])
    ranked = sorted(
        employers,
        key=lambda employer: (_relevance_score(employer, partner_fields), employer["name"]),
        reverse=True,
    )
    results = []
    for employer in ranked[:limit]:
        roles = _prioritize_roles(employer["roles"], partner_fields)
        results.append(
            {
                "name": employer["name"],
                "roles": roles,
                "matches_partner_fields": bool(set(employer["fields"]) & partner_fields),
            }
        )
    return results


def get_field_label(field_id: str) -> str:
    field = get_career_field_map().get(field_id)
    return field["label"] if field else field_id.replace("_", " ").title()
