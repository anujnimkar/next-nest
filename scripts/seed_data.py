#!/usr/bin/env python3
"""Generate curated metro cost data for the relocation advisor app.

Run once to refresh app/data/metro_costs.json. Optionally set HUD_API_TOKEN
in .env to pull 2BR FMR values from the HUD API.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "app" / "data"

# Base cost profiles keyed by cost tier (1=expensive, 5=affordable)
COST_PROFILES = {
    1: {  # Very expensive (SF, NYC, SJ)
        "rent_2br": 3200, "price_1800": 950000,
        "groceries": 650, "gas": 180, "parking": 350, "electricity": 160, "water": 50,
        "daycare": 2800, "nutrition": 450, "hobbies": 280,
    },
    2: {  # Expensive (LA, Boston, Seattle, DC, SD)
        "rent_2br": 2400, "price_1800": 650000,
        "groceries": 550, "gas": 170, "parking": 250, "electricity": 140, "water": 45,
        "daycare": 2200, "nutrition": 400, "hobbies": 240,
    },
    3: {  # Above average (Denver, Austin, Miami, Chicago)
        "rent_2br": 1900, "price_1800": 480000,
        "groceries": 480, "gas": 160, "parking": 180, "electricity": 130, "water": 40,
        "daycare": 1700, "nutrition": 350, "hobbies": 200,
    },
    4: {  # Average (Atlanta, Dallas, Phoenix, Charlotte)
        "rent_2br": 1500, "price_1800": 350000,
        "groceries": 420, "gas": 150, "parking": 120, "electricity": 120, "water": 35,
        "daycare": 1300, "nutrition": 320, "hobbies": 175,
    },
    5: {  # Affordable (Memphis, Birmingham, Buffalo, OKC)
        "rent_2br": 1100, "price_1800": 240000,
        "groceries": 380, "gas": 140, "parking": 80, "electricity": 110, "water": 30,
        "daycare": 950, "nutrition": 280, "hobbies": 150,
    },
}

# Metro -> cost tier + career/commute modifiers
METRO_CONFIG = {
    "nyc": (1, {"software_tech": (95, 35), "finance": (98, 30), "healthcare": (90, 25), "engineering": (75, 40),
                "education": (85, 30), "legal": (95, 25), "marketing": (88, 30), "sales": (85, 30),
                "consulting": (92, 30), "biotech": (80, 35), "government": (70, 35), "remote_hybrid": (90, 20),
                "manufacturing": (60, 45), "media": (95, 30), "real_estate": (85, 30), "hospitality": (80, 25)}),
    "la": (2, {"software_tech": (88, 40), "finance": (82, 35), "healthcare": (85, 35), "engineering": (78, 40),
               "education": (75, 35), "legal": (85, 35), "marketing": (90, 35), "sales": (82, 35),
               "consulting": (80, 35), "biotech": (75, 40), "government": (65, 40), "remote_hybrid": (85, 25),
               "manufacturing": (70, 45), "media": (95, 35), "real_estate": (80, 35), "hospitality": (85, 30)}),
    "chicago": (3, {"software_tech": (82, 30), "finance": (90, 25), "healthcare": (88, 30), "engineering": (80, 35),
                    "education": (80, 30), "legal": (88, 25), "marketing": (82, 30), "sales": (80, 30),
                    "consulting": (85, 28), "biotech": (72, 35), "government": (70, 30), "remote_hybrid": (80, 20),
                    "manufacturing": (75, 35), "media": (78, 30), "real_estate": (75, 30), "hospitality": (78, 28)}),
    "dfw": (4, {"software_tech": (78, 35), "finance": (75, 30), "healthcare": (82, 35), "engineering": (72, 35),
                "education": (72, 35), "legal": (70, 30), "marketing": (72, 35), "sales": (78, 30),
                "consulting": (75, 32), "biotech": (55, 40), "government": (60, 35), "remote_hybrid": (75, 20),
                "manufacturing": (70, 35), "media": (65, 35), "real_estate": (78, 30), "hospitality": (72, 30)}),
    "houston": (4, {"software_tech": (70, 35), "finance": (72, 30), "healthcare": (90, 30), "engineering": (85, 35),
                    "education": (70, 35), "legal": (68, 30), "marketing": (68, 35), "sales": (72, 30),
                    "consulting": (70, 32), "biotech": (65, 35), "government": (55, 35), "remote_hybrid": (72, 20),
                    "manufacturing": (80, 35), "media": (60, 35), "real_estate": (72, 30), "hospitality": (70, 28)}),
    "dc": (2, {"software_tech": (85, 35), "finance": (80, 30), "healthcare": (88, 30), "engineering": (78, 35),
               "education": (78, 30), "legal": (90, 25), "marketing": (78, 32), "sales": (75, 32),
               "consulting": (88, 28), "biotech": (75, 35), "government": (95, 20), "remote_hybrid": (88, 20),
               "manufacturing": (55, 40), "media": (72, 32), "real_estate": (72, 30), "hospitality": (70, 28)}),
    "philadelphia": (3, {"software_tech": (75, 30), "finance": (78, 28), "healthcare": (90, 28), "engineering": (72, 32),
                         "education": (82, 28), "legal": (80, 28), "marketing": (72, 30), "sales": (70, 30),
                         "consulting": (75, 28), "biotech": (78, 32), "government": (65, 30), "remote_hybrid": (78, 20),
                         "manufacturing": (65, 35), "media": (68, 30), "real_estate": (68, 28), "hospitality": (72, 28)}),
    "miami": (3, {"software_tech": (72, 35), "finance": (78, 30), "healthcare": (82, 30), "engineering": (65, 35),
                  "education": (68, 32), "legal": (75, 28), "marketing": (80, 30), "sales": (82, 28),
                  "consulting": (72, 30), "biotech": (60, 35), "government": (60, 32), "remote_hybrid": (78, 20),
                  "manufacturing": (55, 38), "media": (75, 30), "real_estate": (82, 28), "hospitality": (88, 25)}),
    "atlanta": (4, {"software_tech": (82, 35), "finance": (78, 30), "healthcare": (85, 30), "engineering": (72, 35),
                    "education": (72, 32), "legal": (72, 28), "marketing": (78, 32), "sales": (80, 28),
                    "consulting": (80, 30), "biotech": (65, 35), "government": (62, 32), "remote_hybrid": (80, 18),
                    "manufacturing": (68, 35), "media": (78, 30), "real_estate": (75, 28), "hospitality": (75, 28)}),
    "boston": (2, {"software_tech": (92, 30), "finance": (88, 25), "healthcare": (95, 25), "engineering": (85, 30),
                   "education": (92, 25), "legal": (88, 25), "marketing": (80, 28), "sales": (75, 28),
                   "consulting": (88, 25), "biotech": (95, 28), "government": (70, 30), "remote_hybrid": (88, 18),
                   "manufacturing": (60, 35), "media": (78, 28), "real_estate": (72, 28), "hospitality": (75, 25)}),
    "phoenix": (4, {"software_tech": (72, 35), "finance": (68, 32), "healthcare": (82, 32), "engineering": (68, 35),
                    "education": (68, 35), "legal": (65, 32), "marketing": (70, 35), "sales": (72, 32),
                    "consulting": (68, 32), "biotech": (55, 38), "government": (58, 35), "remote_hybrid": (75, 18),
                    "manufacturing": (65, 35), "media": (62, 35), "real_estate": (78, 30), "hospitality": (75, 28)}),
    "sf": (1, {"software_tech": (98, 35), "finance": (92, 30), "healthcare": (85, 30), "engineering": (88, 35),
               "education": (78, 30), "legal": (88, 28), "marketing": (85, 30), "sales": (80, 30),
               "consulting": (90, 28), "biotech": (92, 30), "government": (65, 35), "remote_hybrid": (95, 18),
               "manufacturing": (55, 40), "media": (82, 30), "real_estate": (78, 30), "hospitality": (78, 28)}),
    "riverside": (4, {"software_tech": (55, 45), "finance": (52, 40), "healthcare": (72, 38), "engineering": (58, 42),
                       "education": (62, 38), "legal": (55, 38), "marketing": (55, 40), "sales": (58, 38),
                       "consulting": (55, 40), "biotech": (45, 45), "government": (52, 38), "remote_hybrid": (65, 22),
                       "manufacturing": (62, 38), "media": (50, 40), "real_estate": (65, 35), "hospitality": (60, 32)}),
    "detroit": (4, {"software_tech": (65, 32), "finance": (62, 30), "healthcare": (82, 30), "engineering": (78, 32),
                    "education": (68, 32), "legal": (65, 28), "marketing": (62, 32), "sales": (65, 30),
                    "consulting": (62, 30), "biotech": (55, 35), "government": (58, 30), "remote_hybrid": (68, 18),
                    "manufacturing": (82, 30), "media": (58, 32), "real_estate": (62, 28), "hospitality": (65, 28)}),
    "seattle": (2, {"software_tech": (95, 30), "finance": (78, 28), "healthcare": (85, 28), "engineering": (82, 30),
                    "education": (75, 28), "legal": (75, 28), "marketing": (78, 28), "sales": (72, 28),
                    "consulting": (82, 28), "biotech": (80, 30), "government": (65, 30), "remote_hybrid": (92, 15),
                    "manufacturing": (70, 32), "media": (72, 28), "real_estate": (72, 28), "hospitality": (72, 25)}),
    "minneapolis": (3, {"software_tech": (78, 28), "finance": (82, 25), "healthcare": (90, 25), "engineering": (75, 30),
                        "education": (78, 28), "legal": (72, 25), "marketing": (72, 28), "sales": (72, 28),
                        "consulting": (78, 25), "biotech": (72, 30), "government": (62, 28), "remote_hybrid": (80, 18),
                        "manufacturing": (72, 28), "media": (68, 28), "real_estate": (68, 25), "hospitality": (68, 25)}),
    "san_diego": (2, {"software_tech": (82, 32), "finance": (72, 28), "healthcare": (88, 28), "engineering": (78, 32),
                      "education": (75, 30), "legal": (72, 28), "marketing": (75, 30), "sales": (72, 28),
                      "consulting": (75, 28), "biotech": (85, 30), "government": (68, 30), "remote_hybrid": (82, 18),
                      "manufacturing": (65, 35), "media": (70, 30), "real_estate": (75, 28), "hospitality": (78, 25)}),
    "tampa": (4, {"software_tech": (68, 35), "finance": (68, 32), "healthcare": (82, 30), "engineering": (62, 35),
                  "education": (65, 32), "legal": (65, 30), "marketing": (70, 32), "sales": (72, 30),
                  "consulting": (68, 32), "biotech": (55, 38), "government": (58, 32), "remote_hybrid": (72, 18),
                  "manufacturing": (58, 35), "media": (62, 32), "real_estate": (72, 28), "hospitality": (78, 28)}),
    "denver": (3, {"software_tech": (82, 30), "finance": (72, 28), "healthcare": (82, 28), "engineering": (72, 30),
                   "education": (72, 28), "legal": (68, 28), "marketing": (72, 30), "sales": (70, 28),
                   "consulting": (75, 28), "biotech": (65, 32), "government": (62, 28), "remote_hybrid": (82, 18),
                   "manufacturing": (62, 32), "media": (65, 30), "real_estate": (72, 28), "hospitality": (72, 25)}),
    "baltimore": (3, {"software_tech": (72, 32), "finance": (72, 28), "healthcare": (92, 25), "engineering": (72, 30),
                      "education": (78, 28), "legal": (75, 25), "marketing": (68, 30), "sales": (68, 28),
                      "consulting": (72, 28), "biotech": (78, 30), "government": (78, 25), "remote_hybrid": (75, 18),
                      "manufacturing": (62, 32), "media": (65, 28), "real_estate": (68, 28), "hospitality": (68, 25)}),
    "stlouis": (4, {"software_tech": (65, 28), "finance": (72, 25), "healthcare": (85, 25), "engineering": (68, 28),
                    "education": (72, 28), "legal": (68, 25), "marketing": (65, 28), "sales": (68, 25),
                    "consulting": (68, 25), "biotech": (62, 30), "government": (58, 28), "remote_hybrid": (70, 18),
                    "manufacturing": (68, 28), "media": (60, 28), "real_estate": (65, 25), "hospitality": (65, 25)}),
    "orlando": (4, {"software_tech": (65, 35), "finance": (62, 32), "healthcare": (78, 30), "engineering": (58, 35),
                    "education": (65, 32), "legal": (62, 30), "marketing": (72, 32), "sales": (72, 30),
                    "consulting": (65, 32), "biotech": (50, 38), "government": (55, 32), "remote_hybrid": (70, 18),
                    "manufacturing": (55, 35), "media": (72, 32), "real_estate": (70, 28), "hospitality": (88, 25)}),
    "charlotte": (4, {"software_tech": (75, 32), "finance": (82, 25), "healthcare": (82, 28), "engineering": (68, 32),
                      "education": (68, 30), "legal": (68, 28), "marketing": (72, 30), "sales": (75, 28),
                      "consulting": (75, 28), "biotech": (55, 35), "government": (58, 30), "remote_hybrid": (75, 18),
                      "manufacturing": (65, 32), "media": (62, 30), "real_estate": (72, 28), "hospitality": (72, 28)}),
    "san_antonio": (4, {"software_tech": (62, 32), "finance": (62, 28), "healthcare": (82, 28), "engineering": (65, 32),
                        "education": (68, 30), "legal": (62, 28), "marketing": (62, 30), "sales": (65, 28),
                        "consulting": (62, 28), "biotech": (52, 35), "government": (72, 25), "remote_hybrid": (68, 18),
                        "manufacturing": (62, 30), "media": (55, 30), "real_estate": (65, 28), "hospitality": (72, 25)}),
    "portland": (3, {"software_tech": (78, 28), "finance": (68, 28), "healthcare": (82, 28), "engineering": (72, 30),
                     "education": (72, 28), "legal": (68, 28), "marketing": (72, 28), "sales": (68, 28),
                     "consulting": (72, 28), "biotech": (65, 32), "government": (58, 28), "remote_hybrid": (82, 15),
                     "manufacturing": (62, 30), "media": (68, 28), "real_estate": (68, 28), "hospitality": (70, 25)}),
    "sacramento": (3, {"software_tech": (68, 32), "finance": (65, 28), "healthcare": (82, 28), "engineering": (65, 32),
                       "education": (72, 28), "legal": (68, 28), "marketing": (65, 30), "sales": (65, 28),
                       "consulting": (65, 28), "biotech": (58, 32), "government": (78, 22), "remote_hybrid": (72, 18),
                       "manufacturing": (58, 32), "media": (60, 30), "real_estate": (68, 28), "hospitality": (68, 25)}),
    "pittsburgh": (4, {"software_tech": (72, 28), "finance": (68, 25), "healthcare": (92, 22), "engineering": (72, 28),
                       "education": (82, 25), "legal": (68, 25), "marketing": (62, 28), "sales": (62, 25),
                       "consulting": (68, 25), "biotech": (68, 28), "government": (55, 28), "remote_hybrid": (72, 18),
                       "manufacturing": (65, 28), "media": (58, 28), "real_estate": (62, 25), "hospitality": (65, 25)}),
    "austin": (3, {"software_tech": (88, 32), "finance": (72, 28), "healthcare": (82, 28), "engineering": (75, 30),
                   "education": (72, 28), "legal": (68, 28), "marketing": (75, 28), "sales": (72, 28),
                   "consulting": (78, 28), "biotech": (62, 32), "government": (62, 28), "remote_hybrid": (85, 18),
                   "manufacturing": (62, 30), "media": (68, 28), "real_estate": (75, 28), "hospitality": (72, 25)}),
    "las_vegas": (4, {"software_tech": (62, 35), "finance": (62, 32), "healthcare": (78, 30), "engineering": (58, 35),
                      "education": (62, 32), "legal": (62, 30), "marketing": (72, 32), "sales": (75, 30),
                      "consulting": (62, 32), "biotech": (48, 38), "government": (55, 32), "remote_hybrid": (68, 18),
                      "manufacturing": (52, 35), "media": (68, 32), "real_estate": (72, 28), "hospitality": (92, 22)}),
    "cincinnati": (4, {"software_tech": (65, 28), "finance": (72, 25), "healthcare": (85, 25), "engineering": (68, 28),
                       "education": (72, 28), "legal": (65, 25), "marketing": (65, 28), "sales": (68, 25),
                       "consulting": (68, 25), "biotech": (62, 30), "government": (58, 28), "remote_hybrid": (68, 18),
                       "manufacturing": (68, 28), "media": (58, 28), "real_estate": (65, 25), "hospitality": (65, 25)}),
    "kansas_city": (4, {"software_tech": (65, 28), "finance": (68, 25), "healthcare": (82, 25), "engineering": (65, 28),
                        "education": (68, 28), "legal": (65, 25), "marketing": (65, 28), "sales": (68, 25),
                        "consulting": (68, 25), "biotech": (55, 32), "government": (58, 28), "remote_hybrid": (68, 18),
                        "manufacturing": (65, 28), "media": (58, 28), "real_estate": (65, 25), "hospitality": (65, 25)}),
    "columbus": (4, {"software_tech": (72, 28), "finance": (68, 25), "healthcare": (85, 25), "engineering": (68, 28),
                     "education": (78, 25), "legal": (65, 25), "marketing": (68, 28), "sales": (68, 25),
                     "consulting": (68, 25), "biotech": (58, 32), "government": (62, 28), "remote_hybrid": (72, 18),
                     "manufacturing": (65, 28), "media": (58, 28), "real_estate": (65, 25), "hospitality": (65, 25)}),
    "indianapolis": (4, {"software_tech": (68, 28), "finance": (72, 25), "healthcare": (85, 25), "engineering": (68, 28),
                         "education": (72, 28), "legal": (65, 25), "marketing": (65, 28), "sales": (68, 25),
                         "consulting": (68, 25), "biotech": (58, 32), "government": (58, 28), "remote_hybrid": (70, 18),
                         "manufacturing": (72, 28), "media": (58, 28), "real_estate": (65, 25), "hospitality": (65, 25)}),
    "cleveland": (4, {"software_tech": (62, 28), "finance": (65, 25), "healthcare": (88, 22), "engineering": (68, 28),
                      "education": (72, 28), "legal": (65, 25), "marketing": (62, 28), "sales": (62, 25),
                      "consulting": (65, 25), "biotech": (62, 30), "government": (58, 28), "remote_hybrid": (65, 18),
                      "manufacturing": (68, 28), "media": (58, 28), "real_estate": (62, 25), "hospitality": (62, 25)}),
    "san_jose": (1, {"software_tech": (99, 30), "finance": (85, 28), "healthcare": (82, 28), "engineering": (92, 28),
                     "education": (75, 28), "legal": (82, 28), "marketing": (82, 28), "sales": (78, 28),
                     "consulting": (88, 28), "biotech": (88, 28), "government": (60, 30), "remote_hybrid": (95, 15),
                     "manufacturing": (75, 30), "media": (72, 28), "real_estate": (75, 28), "hospitality": (72, 25)}),
    "nashville": (4, {"software_tech": (72, 32), "finance": (72, 28), "healthcare": (88, 28), "engineering": (62, 32),
                      "education": (68, 30), "legal": (68, 28), "marketing": (72, 30), "sales": (72, 28),
                      "consulting": (72, 28), "biotech": (55, 35), "government": (58, 30), "remote_hybrid": (72, 18),
                      "manufacturing": (58, 32), "media": (78, 28), "real_estate": (72, 28), "hospitality": (82, 25)}),
    "virginia_beach": (4, {"software_tech": (58, 32), "finance": (58, 28), "healthcare": (78, 28), "engineering": (72, 30),
                           "education": (65, 30), "legal": (58, 28), "marketing": (58, 30), "sales": (58, 28),
                           "consulting": (58, 28), "biotech": (48, 35), "government": (78, 25), "remote_hybrid": (62, 18),
                           "manufacturing": (62, 30), "media": (52, 30), "real_estate": (62, 28), "hospitality": (68, 28)}),
    "providence": (3, {"software_tech": (68, 28), "finance": (72, 25), "healthcare": (85, 25), "engineering": (68, 28),
                       "education": (78, 25), "legal": (68, 25), "marketing": (65, 28), "sales": (62, 25),
                       "consulting": (68, 25), "biotech": (62, 30), "government": (58, 28), "remote_hybrid": (72, 18),
                       "manufacturing": (62, 28), "media": (62, 28), "real_estate": (65, 25), "hospitality": (68, 25)}),
    "milwaukee": (4, {"software_tech": (65, 28), "finance": (68, 25), "healthcare": (82, 25), "engineering": (72, 28),
                      "education": (72, 28), "legal": (65, 25), "marketing": (62, 28), "sales": (62, 25),
                      "consulting": (65, 25), "biotech": (58, 32), "government": (58, 28), "remote_hybrid": (68, 18),
                      "manufacturing": (72, 28), "media": (58, 28), "real_estate": (62, 25), "hospitality": (65, 25)}),
    "jacksonville": (4, {"software_tech": (62, 32), "finance": (62, 28), "healthcare": (78, 28), "engineering": (58, 32),
                         "education": (65, 30), "legal": (62, 28), "marketing": (65, 30), "sales": (68, 28),
                         "consulting": (62, 28), "biotech": (48, 35), "government": (65, 28), "remote_hybrid": (68, 18),
                         "manufacturing": (55, 32), "media": (58, 30), "real_estate": (68, 28), "hospitality": (72, 28)}),
    "oklahoma_city": (5, {"software_tech": (55, 28), "finance": (58, 25), "healthcare": (78, 25), "engineering": (58, 28),
                          "education": (65, 28), "legal": (58, 25), "marketing": (55, 28), "sales": (58, 25),
                          "consulting": (58, 25), "biotech": (45, 32), "government": (62, 25), "remote_hybrid": (62, 18),
                          "manufacturing": (58, 28), "media": (52, 28), "real_estate": (62, 25), "hospitality": (65, 25)}),
    "raleigh": (4, {"software_tech": (82, 30), "finance": (72, 28), "healthcare": (85, 28), "engineering": (72, 30),
                    "education": (82, 28), "legal": (68, 28), "marketing": (72, 28), "sales": (72, 28),
                    "consulting": (75, 28), "biotech": (78, 30), "government": (62, 28), "remote_hybrid": (80, 18),
                    "manufacturing": (58, 32), "media": (62, 28), "real_estate": (72, 28), "hospitality": (68, 25)}),
    "memphis": (5, {"software_tech": (52, 28), "finance": (58, 25), "healthcare": (78, 25), "engineering": (55, 28),
                    "education": (62, 28), "legal": (55, 25), "marketing": (55, 28), "sales": (58, 25),
                    "consulting": (55, 25), "biotech": (48, 32), "government": (55, 28), "remote_hybrid": (58, 18),
                    "manufacturing": (62, 28), "media": (55, 28), "real_estate": (58, 25), "hospitality": (65, 25)}),
    "richmond": (4, {"software_tech": (65, 30), "finance": (68, 28), "healthcare": (82, 28), "engineering": (65, 30),
                     "education": (72, 28), "legal": (68, 28), "marketing": (65, 28), "sales": (65, 28),
                     "consulting": (68, 28), "biotech": (58, 32), "government": (68, 25), "remote_hybrid": (70, 18),
                     "manufacturing": (58, 30), "media": (58, 28), "real_estate": (65, 28), "hospitality": (65, 25)}),
    "louisville": (5, {"software_tech": (58, 28), "finance": (62, 25), "healthcare": (82, 25), "engineering": (62, 28),
                       "education": (68, 28), "legal": (62, 25), "marketing": (58, 28), "sales": (62, 25),
                       "consulting": (62, 25), "biotech": (52, 32), "government": (58, 28), "remote_hybrid": (62, 18),
                       "manufacturing": (65, 28), "media": (55, 28), "real_estate": (62, 25), "hospitality": (65, 25)}),
    "new_orleans": (4, {"software_tech": (55, 30), "finance": (58, 28), "healthcare": (82, 28), "engineering": (58, 30),
                        "education": (68, 28), "legal": (62, 28), "marketing": (62, 28), "sales": (62, 28),
                        "consulting": (58, 28), "biotech": (52, 32), "government": (62, 28), "remote_hybrid": (62, 18),
                        "manufacturing": (58, 30), "media": (68, 28), "real_estate": (62, 28), "hospitality": (88, 22)}),
    "salt_lake_city": (4, {"software_tech": (72, 28), "finance": (68, 25), "healthcare": (82, 25), "engineering": (68, 28),
                           "education": (72, 28), "legal": (65, 25), "marketing": (68, 28), "sales": (68, 25),
                           "consulting": (68, 25), "biotech": (58, 30), "government": (58, 28), "remote_hybrid": (75, 18),
                           "manufacturing": (62, 28), "media": (58, 28), "real_estate": (68, 25), "hospitality": (68, 25)}),
    "hartford": (3, {"software_tech": (68, 28), "finance": (82, 25), "healthcare": (85, 25), "engineering": (72, 28),
                     "education": (72, 28), "legal": (72, 25), "marketing": (65, 28), "sales": (65, 25),
                     "consulting": (72, 25), "biotech": (68, 28), "government": (58, 28), "remote_hybrid": (72, 18),
                     "manufacturing": (65, 28), "media": (62, 28), "real_estate": (65, 25), "hospitality": (65, 25)}),
    "buffalo": (5, {"software_tech": (58, 25), "finance": (62, 22), "healthcare": (85, 22), "engineering": (62, 25),
                    "education": (72, 25), "legal": (62, 22), "marketing": (55, 25), "sales": (55, 22),
                    "consulting": (58, 22), "biotech": (55, 28), "government": (58, 25), "remote_hybrid": (62, 18),
                    "manufacturing": (62, 25), "media": (52, 25), "real_estate": (58, 22), "hospitality": (62, 22)}),
    "birmingham": (5, {"software_tech": (52, 28), "finance": (58, 25), "healthcare": (82, 25), "engineering": (58, 28),
                       "education": (65, 28), "legal": (58, 25), "marketing": (55, 28), "sales": (58, 25),
                       "consulting": (55, 25), "biotech": (48, 32), "government": (55, 28), "remote_hybrid": (58, 18),
                       "manufacturing": (62, 28), "media": (52, 28), "real_estate": (58, 25), "hospitality": (62, 25)}),
}


def _blend_field(field_data: dict, sources: list[tuple[str, float]]) -> tuple[int, int]:
    score = round(sum(field_data[key][0] * weight for key, weight in sources))
    commute = round(sum(field_data[key][1] * weight for key, weight in sources))
    return score, commute


def extend_field_data(field_data: dict) -> dict:
    extended = dict(field_data)
    extended["hardware_engineering"] = _blend_field(
        field_data,
        [("engineering", 0.55), ("software_tech", 0.45)],
    )
    extended["business_intelligence"] = _blend_field(
        field_data,
        [("consulting", 0.4), ("software_tech", 0.35), ("finance", 0.25)],
    )
    extended["data_analytics"] = _blend_field(
        field_data,
        [("software_tech", 0.5), ("consulting", 0.3), ("finance", 0.2)],
    )
    extended["data_engineering"] = _blend_field(
        field_data,
        [("software_tech", 0.7), ("engineering", 0.3)],
    )
    return extended


def build_metro_costs() -> list[dict]:
    metros = json.loads((DATA_DIR / "metros.json").read_text())
    costs = []
    for metro in metros:
        metro_id = metro["id"]
        tier, field_data = METRO_CONFIG[metro_id]
        field_data = extend_field_data(field_data)
        profile = COST_PROFILES[tier]
        career_scores = {k: v[0] for k, v in field_data.items()}
        commute_minutes = {k: v[1] for k, v in field_data.items()}
        costs.append({
            "id": metro_id,
            "base_rent_2br": profile["rent_2br"],
            "base_price_1800sqft": profile["price_1800"],
            "col": {
                "groceries": profile["groceries"],
                "gas": profile["gas"],
                "parking": profile["parking"],
                "electricity": profile["electricity"],
                "water": profile["water"],
            },
            "childcare": {
                "daycare": profile["daycare"],
                "nutrition": profile["nutrition"],
                "hobbies": profile["hobbies"],
            },
            "career_scores": career_scores,
            "commute_minutes": commute_minutes,
        })
    return costs


def main() -> None:
    costs = build_metro_costs()
    output_path = DATA_DIR / "metro_costs.json"
    output_path.write_text(json.dumps(costs, indent=2))
    print(f"Wrote {len(costs)} metro cost records to {output_path}")


if __name__ == "__main__":
    main()
