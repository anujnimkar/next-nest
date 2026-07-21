from __future__ import annotations

ROLE_TEMPLATES: dict[str, list[tuple[str, int, int]]] = {
    "software_tech": [
        ("Software Engineer", 95000, 155000),
        ("Full Stack Developer", 90000, 145000),
    ],
    "hardware_engineering": [
        ("Hardware Engineer", 90000, 145000),
        ("Systems Architect", 100000, 160000),
    ],
    "business_intelligence": [
        ("BI Analyst", 80000, 125000),
        ("Analytics Manager", 95000, 140000),
    ],
    "data_analytics": [
        ("Data Analyst", 75000, 120000),
        ("Analytics Consultant", 85000, 130000),
    ],
    "data_engineering": [
        ("Data Engineer", 95000, 150000),
        ("ETL Developer", 90000, 140000),
    ],
    "finance": [
        ("Financial Analyst", 75000, 115000),
        ("Investment Associate", 90000, 140000),
    ],
    "healthcare": [
        ("Registered Nurse", 65000, 95000),
        ("Clinical Coordinator", 70000, 105000),
    ],
    "engineering": [
        ("Mechanical Engineer", 75000, 115000),
        ("Project Engineer", 80000, 120000),
    ],
    "education": [
        ("Instructional Designer", 55000, 85000),
        ("School Administrator", 65000, 95000),
    ],
    "legal": [
        ("Associate Attorney", 90000, 150000),
        ("Legal Counsel", 110000, 170000),
    ],
    "marketing": [
        ("Marketing Manager", 70000, 115000),
        ("Brand Strategist", 65000, 105000),
    ],
    "sales": [
        ("Account Executive", 70000, 130000),
        ("Business Development Manager", 75000, 125000),
    ],
    "consulting": [
        ("Management Consultant", 85000, 140000),
        ("Strategy Analyst", 80000, 125000),
    ],
    "biotech": [
        ("Research Scientist", 80000, 125000),
        ("Clinical Research Associate", 70000, 105000),
    ],
    "government": [
        ("Policy Analyst", 60000, 95000),
        ("Program Manager", 70000, 105000),
    ],
    "remote_hybrid": [
        ("Remote Program Manager", 80000, 125000),
        ("Customer Success Lead", 65000, 105000),
    ],
    "manufacturing": [
        ("Operations Manager", 70000, 110000),
        ("Production Supervisor", 60000, 90000),
    ],
    "media": [
        ("Content Producer", 55000, 90000),
        ("Digital Media Manager", 65000, 105000),
    ],
    "real_estate": [
        ("Project Manager", 70000, 110000),
        ("Commercial Broker", 65000, 120000),
    ],
    "hospitality": [
        ("Hotel Operations Manager", 55000, 85000),
        ("Food & Beverage Director", 60000, 90000),
    ],
}

PAY_TIER_MULTIPLIERS = {
    1: 1.35,
    2: 1.15,
    3: 1.0,
    4: 0.92,
    5: 0.85,
}
