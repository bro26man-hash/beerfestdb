#!/usr/bin/env python3
"""
batch_cost_calculator.py — Craft Brewery Batch Cost Calculator
================================================================
Inspired by: tfrayner/beerfestdb → tool_dashboard/CBF_beer_price_calculator.py
(which applies a "greater-of cost-vs-ABV-value" pricing philosophy).

This standalone script computes the full cost breakdown and recommended
selling price for a single brew batch. It can be used as a library
(import `calculate_batch_cost`) or run directly for a guided sample.

Features
--------
(a) Ingredient cost inputs — grain, hops, yeast, packaging
(b) Batch size in barrels
(c) Total cost and cost-per-barrel calculations
(d) Configurable margin percentage → recommended selling price per barrel
    Plus a "base price floor" per barrel (inspired by the ABV-based minimum
    price in the reference calculator) — the recommended price is the
    GREATER of (cost + margin) and the floor.

Author   : Platform Engineering Team
Reference: https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py
License  : MIT
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Data model — all configurable inputs collected in one place
# ---------------------------------------------------------------------------
@dataclass
class BatchInputs:
    """All inputs required to cost a single brew batch."""

    # ---- (a) Ingredient cost inputs ---------------------------------------
    grain_price_per_lb: float        # $ / pound of grain
    grain_lbs_used: float            # lbs of grain in the recipe
    hops_price_per_oz: float         # $ / ounce of hops
    hops_oz_used: float              # oz of hops in the recipe
    yeast_price_per_unit: float      # $ / yeast unit (eco-starter / liquid culture)
    yeast_units_used: float          # number of yeast units
    packaging_price_per_unit: float  # $ / packaging unit (bottle / can / keg)
    packaging_units_used: float      # number of packaging units

    # ---- (b) Batch size ---------------------------------------------------
    batch_size_barrels: float        # US beer barrels (1 bbl = 31 US gal)

    # ---- (d) Pricing ------------------------------------------------------
    margin_percentage: float         # e.g. 30 = 30% markup over cost
    base_price_floor_per_barrel: Optional[float] = None  # minimum $/bbl to remain viable


# ---------------------------------------------------------------------------
# Core calculation engine
# ---------------------------------------------------------------------------
def calculate_batch_cost(inputs: BatchInputs) -> dict:
    """
    Compute every cost and pricing figure for a brew batch.

    Returns a dict with all intermediate and final values so the caller can
    inspect, log, or display them — mirroring the DataFrame-powered reporting
    in the original Streamlit reference.

    Raises
    ------
    ValueError
        If batch_size_barrels is zero or negative.
    """

    # ---- (a) Ingredient cost breakdown -----------------------------------
    grain_cost       = round(inputs.grain_price_per_lb  * inputs.grain_lbs_used, 2)
    hops_cost        = round(inputs.hops_price_per_oz   * inputs.hops_oz_used,  2)
    yeast_cost       = round(inputs.yeast_price_per_unit * inputs.yeast_units_used, 2)
    packaging_cost   = round(inputs.packaging_price_per_unit * inputs.packaging_units_used, 2)

    # ---- (c) Total cost & cost-per-barrel -------------------------------
    total_cost = round(grain_cost + hops_cost + yeast_cost + packaging_cost, 2)

    if inputs.batch_size_barrels <= 0:
        raise ValueError("batch_size_barrels must be greater than zero.")

    cost_per_barrel = round(total_cost / inputs.batch_size_barrels, 2)

    # ---- (d) Recommended selling price with configurable margin -----------
    markup_multiplier = 1 + (inputs.margin_percentage / 100.0)
    margin_price = round(cost_per_barrel * markup_multiplier, 2)

    # "Greater-of" rule from the reference:
    # the selling price must be at least the base price floor per barrel.
    # (Original CBF calculator uses max(ABV_price, cost_price).)
    floor = round(inputs.base_price_floor_per_barrel, 2) if inputs.base_price_floor_per_barrel is not None else None

    if floor is not None and floor > margin_price:
        recommended_price = floor
        price_basis = "base_price_floor"
    else:
        recommended_price = margin_price
        price_basis = "margin_markup"

    return {
        # ingredient costs
        "grain_cost":        grain_cost,
        "hops_cost":         hops_cost,
        "yeast_cost":        yeast_cost,
        "packaging_cost":    packaging_cost,
        # totals
        "total_cost":        total_cost,
        "cost_per_barrel":   cost_per_barrel,
        # pricing
        "margin_percentage": inputs.margin_percentage,
        "markup_multiplier": round(markup_multiplier, 4),
        "margin_price":      margin_price,
        "base_price_floor":  floor,
        "recommended_price_per_barrel": recommended_price,
        "price_basis":       price_basis,
    }


# ---------------------------------------------------------------------------
# Pretty-print helper
# ---------------------------------------------------------------------------
def print_report(inputs: BatchInputs, result: dict) -> None:
    """Print a human-readable cost report to stdout."""
    print("=" * 60)
    print("  CRAFT BREWERY BATCH COST REPORT")
    print("=" * 60)
    print(f"\n  Batch size          : {inputs.batch_size_barrels} bbl")

    print(f"\n  --- Ingredient Costs (a) ---")
    print(f"    Grain             : {inputs.grain_lbs_used} lbs × "
          f"${inputs.grain_price_per_lb:.2f}/lb   = ${result['grain_cost']:.2f}")
    print(f"    Hops              : {inputs.hops_oz_used} oz  × "
          f"${inputs.hops_price_per_oz:.2f}/oz    = ${result['hops_cost']:.2f}")
    print(f"    Yeast             : {inputs.yeast_units_used} units × "
          f"${inputs.yeast_price_per_unit:.2f}/unit = ${result['yeast_cost']:.2f}")
    print(f"    Packaging         : {inputs.packaging_units_used} units × "
          f"${inputs.packaging_price_per_unit:.2f}/unit = ${result['packaging_cost']:.2f}")

    print(f"\n  --- Totals (c) ---")
    print(f"    Total Batch Cost  : ${result['total_cost']:.2f}")
    print(f"    Cost / Barrel     : ${result['cost_per_barrel']:.2f}")

    print(f"\n  --- Pricing (d) ---")
    print(f"    Margin %          : {inputs.margin_percentage}%")
    print(f"    Markup multiplier : ×{result['markup_multiplier']}")
    if result["base_price_floor"] is not None:
        print(f"    Base price floor  : ${result['base_price_floor']:.2f}/bbl")
    print(f"    Price basis       : {result['price_basis']}")
    print(f"    >>> Sell / Barrel : ${result['recommended_price_per_barrel']:.2f}")
    print("\n" + "=" * 60)


# ---------------------------------------------------------------------------
# Sample run — executes when the script is run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Sample batch: a 10-barrel Pale Ale
    sample = BatchInputs(
        grain_price_per_lb       = 1.50,   # e.g. 2-row malt
        grain_lbs_used           = 600.0,  # ~6 lbs / bbl
        hops_price_per_oz        = 0.40,   # mild variety
        hops_oz_used             = 100.0,
        yeast_price_per_unit     = 120.0,  # liquid cultured yeast
        yeast_units_used         = 2.0,
        packaging_price_per_unit = 0.75,   # aluminum cans
        packaging_units_used     = 1200.0, # ~120 × 12 oz cans per bbl
        batch_size_barrels       = 10.0,
        margin_percentage        = 30.0,
        base_price_floor_per_barrel = 25.0,  # minimum $/bbl to stay viable
    )

    print("\n>>> Running SAMPLE batch <<<\n")
    results = calculate_batch_cost(sample)
    print_report(sample, results)

    # Also dump as JSON for programmatic consumers
    print("\n--- JSON Output ---")
    print(json.dumps({
        "batch_size_barrels": sample.batch_size_barrels,
        **results,
    }, indent=2))

    # ---- Built-in self-check assertions ----------------------------------
    assert results["grain_cost"]       == 900.00
    assert results["hops_cost"]        == 40.00
    assert results["yeast_cost"]       == 240.00
    assert results["packaging_cost"]   == 900.00
    assert results["total_cost"]       == 2080.00
    assert results["cost_per_barrel"]  == 208.00
    assert results["recommended_price_per_barrel"] == 270.40
    assert results["price_basis"]      == "margin_markup"
    print("\n✅ Self-check assertions passed — calculator is valid.")
