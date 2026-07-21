from __future__ import annotations


def col_costs(metro_cost: dict, tier: dict) -> dict:
    col = metro_cost["col"]
    multiplier = tier["col_multiplier"]
    items = {
        key: round(value * multiplier)
        for key, value in col.items()
    }
    total = sum(items.values())
    return {"breakdown": items, "total": total}
