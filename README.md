# Next Nest

Find your best city together.

Flask app that helps dual-income couples compare ~50 US metro areas across career fit, housing, cost of living, commute feasibility, and childcare.

## Setup

```bash
cd relocation-advisor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/seed_data.py   # regenerates app/data/metro_costs.json
python3 scripts/seed_employers.py  # regenerates app/data/metro_employers.json
python3 run.py
```

Open https://couples-metro-match.onrender.com/ 

## Run tests

```bash
pytest -q
```

## Data

Static JSON under `app/data/` powers the scoring engine. `scripts/seed_data.py` builds curated metro cost profiles using public research benchmarks (HUD FMR-style rents, regional COL, childcare estimates).

## Flow

1. Partner 1: career field + max commute
2. Partner 2: career field + max commute
3. Household: kids flag + priority sliders for both partners
4. Results: ranked metros with monthly cost breakdowns and category scores
