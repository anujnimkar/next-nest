from __future__ import annotations

MORTGAGE_RATE = 0.07
MORTGAGE_YEARS = 30
DOWN_PAYMENT_RATIO = 0.20
TAX_INSURANCE_RATIO = 0.012


def monthly_mortgage(principal: float, annual_rate: float = MORTGAGE_RATE, years: int = MORTGAGE_YEARS) -> float:
    if principal <= 0:
        return 0.0
    monthly_rate = annual_rate / 12
    payments = years * 12
    factor = (1 + monthly_rate) ** payments
    return principal * monthly_rate * factor / (factor - 1)


def housing_costs(metro_cost: dict, tier: dict) -> dict:
    rent = round(metro_cost["base_rent_2br"] * tier["housing_multiplier"])
    home_price = metro_cost["base_price_1800sqft"] * tier["housing_multiplier"]
    loan_amount = home_price * (1 - DOWN_PAYMENT_RATIO)
    mortgage = monthly_mortgage(loan_amount)
    taxes_insurance = home_price * TAX_INSURANCE_RATIO / 12
    mortgage_equiv = round(mortgage + taxes_insurance)
    burden = min(rent, mortgage_equiv)
    return {
        "rent": rent,
        "mortgage_equiv": mortgage_equiv,
        "home_price": round(home_price),
        "burden": burden,
        "total_display": rent,
    }
