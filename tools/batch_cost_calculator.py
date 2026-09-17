"""
batch_cost_calculator.py
=========================
Craft Brewery Batch Cost Calculator

Inspired by price-calculation logic from tfrayner/beerfestdb
(CBF_beer_price_calculator.py), which computes sale prices as the
greater of an ABV-based price or a cask-cost-based price. This script
adapts that principle for a craft brewery setting: it computes the
total cost of a brewing batch, the cost per barrel, and then applies a
configurable margin to recommend a selling price per barrel.

Author: Platform Team
License: MIT
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class IngredientCosts:
    """Input costs for a single batch."""
    grain_per_lb: float = 1.50       # $ per pound of malt
    hops_per_oz: float = 0.75        # $ per ounce of hops
    yeast_per_unit: float = 5.00     # $ per yeast unit (packet/liquid)
    packaging_per_unit: float = 0.25 # $ per unit (bottle/can)
    grain_lbs: float = 100.0         # pounds of grain in the batch
    hops_oz: float = 20.0            # ounces of hops in the batch
    yeast_units: int = 2             # number of yeast units
    packaging_units: int = 400       # number of bottles/cans per batch


def calculate_batch_cost(
    batch_size_bbl: float,
    costs: IngredientCosts,
    margin_pct: float = 30.0,
    market_floor_per_bbl: Optional[float] = None,
) -> dict:
    """
    Calculate the full cost breakdown and recommended selling price.

    Parameters
    ----------
    batch_size_bbl : float
        Batch size in barrels (1 bbl = 31 US gallons).
    costs : IngredientCosts
        Ingredient and packaging cost inputs.
    margin_pct : float
        Desired margin as a percentage (e.g. 30 = 30%).
    market_floor_per_bbl : float, optional
        Minimum price per barrel imposed by the market; if set, the
        recommended selling price will be at least this value.

    Returns
    -------
    dict with all cost metrics.
    """
    grain_cost = costs.grain_per_lb * costs.grain_lbs
    hops_cost = costs.hops_per_oz * costs.hops_oz
    yeast_cost = costs.yeast_per_unit * costs.yeast_units
    packaging_cost = costs.packaging_per_unit * costs.packaging_units

    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_bbl = total_cost / batch_size_bbl

    calculated_price = cost_per_bbl * (1.0 + margin_pct / 100.0)

    if market_floor_per_bbl is not None:
        recommended_price = max(calculated_price, market_floor_per_bbl)
    else:
        recommended_price = calculated_price

    recommended_price = round(recommended_price * 2) / 2

    estimated_revenue = recommended_price * batch_size_bbl
    estimated_profit = estimated_revenue - total_cost

    return {
        "batch_size_bbl": batch_size_bbl,
        "grain_cost": round(grain_cost, 2),
        "hops_cost": round(hops_cost, 2),
        "yeast_cost": round(yeast_cost, 2),
        "packaging_cost": round(packaging_cost, 2),
        "total_cost": round(total_cost, 2),
        "cost_per_bbl": round(cost_per_bbl, 2),
        "margin_pct": margin_pct,
        "calculated_price_per_bbl": round(calculated_price, 2),
        "market_floor_per_bbl": market_floor_per_bbl,
        "recommended_price_per_bbl": round(recommended_price, 2),
        "estimated_revenue": round(estimated_revenue, 2),
        "estimated_profit": round(estimated_profit, 2),
    }


def print_report(result: dict) -> None:
    """Pretty-print the batch cost report."""
    print("=" * 60)
    print("   CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 60)
    print(f"\nBatch Size:            {result['batch_size_bbl']} barrels")
    print("-" * 60)
    print("INGREDIENT COSTS:")
    print(f"  Grain:                ${result['grain_cost']:>8.2f}")
    print(f"  Hops:                 ${result['hops_cost']:>8.2f}")
    print(f"  Yeast:                ${result['yeast_cost']:>8.2f}")
    print(f"  Packaging:            ${result['packaging_cost']:>8.2f}")
    print("-" * 60)
    print(f"  TOTAL BATCH COST:     ${result['total_cost']:>8.2f}")
    print(f"  COST PER BARREL:      ${result['cost_per_bbl']:>8.2f}")
    print("-" * 60)
    print("PRICING:")
    print(f"  Margin:               {result['margin_pct']:.1f}%")
    print(f"  Calculated Price:     ${result['calculated_price_per_bbl']:>8.2f} / bbl")
    if result['market_floor_per_bbl'] is not None:
        print(f"  Market Floor:         ${result['market_floor_per_bbl']:>8.2f} / bbl")
    print(f"  >> RECOMMENDED PRICE: ${result['recommended_price_per_bbl']:>8.2f} / bbl")
    print("-" * 60)
    print("PROJECTIONS:")
    print(f"  Est. Revenue:         ${result['estimated_revenue']:>8.2f}")
    print(f"  Est. Profit:          ${result['estimated_profit']:>8.2f}")
    print("=" * 60)


if __name__ == "__main__":
    sample_costs = IngredientCosts(
        grain_per_lb=1.75,
        hops_per_oz=1.20,
        yeast_per_unit=6.50,
        packaging_per_unit=0.30,
        grain_lbs=120,
        hops_oz=25,
        yeast_units=2,
        packaging_units=450,
    )

    result = calculate_batch_cost(
        batch_size_bbl=5.0,
        costs=sample_costs,
        margin_pct=35.0,
        market_floor_per_bbl=45.0,
    )
    print_report(result)

    print("\n\n--- No Market Floor Scenario ---\n")
    result_no_floor = calculate_batch_cost(
        batch_size_bbl=5.0,
        costs=sample_costs,
        margin_pct=35.0,
        market_floor_per_bbl=None,
    )
    print_report(result_no_floor)
