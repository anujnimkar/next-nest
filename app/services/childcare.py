from __future__ import annotations


def childcare_costs(metro_cost: dict) -> dict:
    childcare = metro_cost["childcare"]
    items = {key: round(value) for key, value in childcare.items()}
    total = sum(items.values())
    return {"breakdown": items, "total": total}
