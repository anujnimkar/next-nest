#!/usr/bin/env python3
"""Generate metro employer data with roles and pay ranges."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.role_templates import PAY_TIER_MULTIPLIERS, ROLE_TEMPLATES

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "app" / "data"

METRO_TIERS = {
    "nyc": 1, "sf": 1, "san_jose": 1,
    "la": 2, "boston": 2, "seattle": 2, "dc": 2, "san_diego": 2,
    "chicago": 3, "philadelphia": 3, "miami": 3, "denver": 3, "baltimore": 3,
    "minneapolis": 3, "portland": 3, "sacramento": 3, "austin": 3, "providence": 3, "hartford": 3,
    "dfw": 4, "houston": 4, "atlanta": 4, "phoenix": 4, "riverside": 4, "detroit": 4,
    "tampa": 4, "stlouis": 4, "orlando": 4, "charlotte": 4, "san_antonio": 4, "pittsburgh": 4,
    "las_vegas": 4, "cincinnati": 4, "kansas_city": 4, "columbus": 4, "indianapolis": 4,
    "cleveland": 4, "nashville": 4, "virginia_beach": 4, "milwaukee": 4, "jacksonville": 4,
    "raleigh": 4, "richmond": 4, "new_orleans": 4, "salt_lake_city": 4,
    "oklahoma_city": 5, "memphis": 5, "louisville": 5, "buffalo": 5, "birmingham": 5,
}

METRO_EMPLOYERS: dict[str, list[tuple[str, list[str]]]] = {
    "nyc": [
        ("JPMorgan Chase", ["finance", "business_intelligence", "data_analytics"]),
        ("Google", ["software_tech", "data_engineering", "data_analytics"]),
        ("Mount Sinai Health System", ["healthcare", "biotech"]),
        ("Deloitte", ["consulting", "business_intelligence", "data_analytics"]),
        ("Bloomberg", ["software_tech", "data_engineering", "finance"]),
    ],
    "sf": [
        ("Salesforce", ["software_tech", "data_engineering", "business_intelligence"]),
        ("Apple", ["software_tech", "hardware_engineering", "data_engineering"]),
        ("Uber", ["software_tech", "data_analytics", "data_engineering"]),
        ("Wells Fargo", ["finance", "business_intelligence"]),
        ("Genentech", ["biotech", "data_analytics", "healthcare"]),
    ],
    "san_jose": [
        ("Apple", ["hardware_engineering", "software_tech", "data_engineering"]),
        ("Google", ["software_tech", "data_engineering", "data_analytics"]),
        ("Intel", ["hardware_engineering", "engineering", "manufacturing"]),
        ("Adobe", ["software_tech", "data_analytics", "marketing"]),
        ("Cisco", ["hardware_engineering", "software_tech", "data_engineering"]),
    ],
    "la": [
        ("Disney", ["media", "marketing", "software_tech"]),
        ("Northrop Grumman", ["engineering", "hardware_engineering", "manufacturing"]),
        ("UCLA Health", ["healthcare", "biotech"]),
        ("Snap", ["software_tech", "data_analytics", "marketing"]),
        ("SpaceX", ["engineering", "hardware_engineering", "manufacturing"]),
    ],
    "seattle": [
        ("Amazon", ["software_tech", "data_engineering", "business_intelligence"]),
        ("Microsoft", ["software_tech", "data_engineering", "data_analytics"]),
        ("Boeing", ["engineering", "hardware_engineering", "manufacturing"]),
        ("Expedia Group", ["software_tech", "data_analytics", "marketing"]),
        ("Providence Health", ["healthcare", "data_analytics"]),
    ],
    "boston": [
        ("Mass General Brigham", ["healthcare", "biotech", "data_analytics"]),
        ("State Street", ["finance", "business_intelligence", "data_engineering"]),
        ("Biogen", ["biotech", "data_analytics", "healthcare"]),
        ("Wayfair", ["software_tech", "data_engineering", "business_intelligence"]),
        ("Boston Consulting Group", ["consulting", "business_intelligence", "data_analytics"]),
    ],
    "dc": [
        ("Lockheed Martin", ["engineering", "hardware_engineering", "government"]),
        ("Capital One", ["finance", "software_tech", "data_analytics"]),
        ("Amazon Web Services", ["software_tech", "data_engineering", "business_intelligence"]),
        ("MedStar Health", ["healthcare", "data_analytics"]),
        ("Deloitte", ["consulting", "government", "business_intelligence"]),
    ],
    "chicago": [
        ("United Airlines", ["engineering", "software_tech", "data_analytics"]),
        ("Abbott", ["healthcare", "biotech", "engineering"]),
        ("Allstate", ["finance", "data_analytics", "business_intelligence"]),
        ("McDonald's", ["marketing", "business_intelligence", "software_tech"]),
        ("Accenture", ["consulting", "data_engineering", "business_intelligence"]),
    ],
    "dfw": [
        ("American Airlines", ["engineering", "software_tech", "data_analytics"]),
        ("AT&T", ["software_tech", "hardware_engineering", "data_engineering"]),
        ("Texas Health Resources", ["healthcare", "data_analytics"]),
        ("JPMorgan Chase", ["finance", "business_intelligence", "data_analytics"]),
        ("Toyota North America", ["manufacturing", "engineering", "business_intelligence"]),
    ],
    "houston": [
        ("ExxonMobil", ["engineering", "manufacturing", "data_analytics"]),
        ("MD Anderson Cancer Center", ["healthcare", "biotech", "data_analytics"]),
        ("Halliburton", ["engineering", "manufacturing", "hardware_engineering"]),
        ("Memorial Hermann", ["healthcare", "business_intelligence"]),
        ("Sysco", ["sales", "business_intelligence", "data_engineering"]),
    ],
    "atlanta": [
        ("Delta Air Lines", ["engineering", "software_tech", "data_analytics"]),
        ("Home Depot", ["business_intelligence", "data_engineering", "software_tech"]),
        ("Coca-Cola", ["marketing", "business_intelligence", "data_analytics"]),
        ("UPS", ["engineering", "manufacturing", "data_engineering"]),
        ("Emory Healthcare", ["healthcare", "biotech", "data_analytics"]),
    ],
    "austin": [
        ("Apple", ["hardware_engineering", "software_tech", "data_engineering"]),
        ("Tesla", ["engineering", "hardware_engineering", "manufacturing"]),
        ("Dell Technologies", ["software_tech", "hardware_engineering", "sales"]),
        ("Oracle", ["software_tech", "data_engineering", "business_intelligence"]),
        ("Indeed", ["software_tech", "data_analytics", "data_engineering"]),
    ],
    "denver": [
        ("Lockheed Martin Space", ["engineering", "hardware_engineering", "government"]),
        ("Centura Health", ["healthcare", "data_analytics"]),
        ("Arrow Electronics", ["sales", "business_intelligence", "data_engineering"]),
        ("Slalom", ["consulting", "data_analytics", "business_intelligence"]),
        ("Palantir", ["software_tech", "data_engineering", "government"]),
    ],
    "raleigh": [
        ("Red Hat", ["software_tech", "data_engineering", "business_intelligence"]),
        ("Epic Games", ["software_tech", "data_analytics", "marketing"]),
        ("Duke Health", ["healthcare", "biotech", "data_analytics"]),
        ("Cisco", ["hardware_engineering", "software_tech", "data_engineering"]),
        ("Fidelity Investments", ["finance", "business_intelligence", "data_analytics"]),
    ],
    "phoenix": [
        ("Intel", ["hardware_engineering", "engineering", "manufacturing"]),
        ("Banner Health", ["healthcare", "data_analytics"]),
        ("American Express", ["finance", "software_tech", "data_analytics"]),
        ("Honeywell", ["engineering", "hardware_engineering", "manufacturing"]),
        ("Carvana", ["software_tech", "data_engineering", "sales"]),
    ],
}

DEFAULT_EMPLOYER_POOL = [
    ("Regional Health System", ["healthcare", "data_analytics"]),
    ("State University", ["education", "data_analytics"]),
    ("Manufacturing Corp", ["manufacturing", "engineering"]),
    ("Financial Services Group", ["finance", "business_intelligence"]),
    ("Tech Solutions Inc", ["software_tech", "data_engineering"]),
]


def scale_pay(value: int, tier: int) -> int:
    return round(value * PAY_TIER_MULTIPLIERS[tier])


def build_roles(fields: list[str], tier: int, limit: int = 3) -> list[dict]:
    roles = []
    seen_titles = set()
    for field in fields:
        for title, pay_min, pay_max in ROLE_TEMPLATES.get(field, []):
            if title in seen_titles:
                continue
            seen_titles.add(title)
            roles.append(
                {
                    "title": title,
                    "field": field,
                    "pay_min": scale_pay(pay_min, tier),
                    "pay_max": scale_pay(pay_max, tier),
                }
            )
            if len(roles) >= limit:
                return roles
    return roles


def employers_for_metro(metro_id: str) -> list[dict]:
    tier = METRO_TIERS.get(metro_id, 4)
    entries = METRO_EMPLOYERS.get(metro_id, DEFAULT_EMPLOYER_POOL)
    return [
        {
            "name": name,
            "fields": fields,
            "roles": build_roles(fields, tier),
        }
        for name, fields in entries[:5]
    ]


def main() -> None:
    metros = json.loads((DATA_DIR / "metros.json").read_text())
    payload = []
    for metro in metros:
        payload.append(
            {
                "metro_id": metro["id"],
                "employers": employers_for_metro(metro["id"]),
            }
        )
    output = DATA_DIR / "metro_employers.json"
    output.write_text(json.dumps(payload, indent=2))
    print(f"Wrote employer data for {len(payload)} metros to {output}")


if __name__ == "__main__":
    main()
