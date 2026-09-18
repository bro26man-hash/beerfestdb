# batch_cost_calculator.py
# Craft Brewery Batch Cost Calculator
# Inspired by tfrayner/beerfestdb's CBF_beer_price_calculator.py
# (https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py)
#
# The reference calculates sale price as max(ABV-based price, cask-cost-based price),
# applying a per-litre cost coefficient. This script adapts that philosophy to a
# per-batch costing model: ingredient inputs -> total cost -> cost-per-barrel ->
# margin-adjusted recommended selling price per barrel.

from dataclasses import dataclass


@dataclass
class BatchInputs:
    """Ingredient and packaging cost inputs plus batch configuration."""
    # Ingredient unit economics
    grain_price_per_lb: float = 2.50        # $/lb
    hops_price_per_oz: float = 8.00         # $/oz
    yeast_price_per_unit: float = 50.00     # $/unit
    packaging_price_per_unit: float = 1.50  # $/unit
    # Quantities used for the batch
    grain_lbs: float = 100.0
    hops_oz: float = 10.0
    yeast_units: float = 2.0
    packaging_units: float = 100.0
    # Batch configuration
    batch_size_barrels: float = 5.0         # US barrels
    # Margin expressed as a fraction (e.g. 0.30 == 30% markup over cost)
    margin_pct: float = 0.30


def calculate_batch_cost(inputs: BatchInputs) -> dict:
    """Compute total cost, cost-per-barrel and recommended selling price.

    Returns a dict with all intermediate and final values so the caller can
    inspect or log each figure (mirroring the reference's detailed per-row
    breakdown).
    """
    # ---- Ingredient line costs (reference: per-unit price * quantity) ----
    grain_cost = inputs.grain_price_per_lb * inputs.grain_lbs
    hops_cost = inputs.hops_price_per_oz * inputs.hops_oz
    yeast_cost = inputs.yeast_price_per_unit * inputs.yeast_units
    packaging_cost = inputs.packaging_price_per_unit * inputs.packaging_units

    # ---- Totals (reference: cost_price baseline) ----
    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_barrel = (
        total_cost / inputs.batch_size_barrels
        if inputs.batch_size_barrels
        else 0.0
    )

    # ---- Margin & recommended sale price (reference: price = max(..., cost) * markup) ----
    # The reference takes the greater of ABV-price and cost-price, then applies a
    # coefficient. Here we apply the margin directly over cost-per-barrel.
    recommended_sale_per_barrel = cost_per_barrel * (1.0 + inputs.margin_pct)
    margin_dollars_per_barrel = (
        recommended_sale_per_barrel - cost_per_barrel
    )

    return {
        "grain_cost": grain_cost,
        "hops_cost": hops_cost,
        "yeast_cost": yeast_cost,
        "packaging_cost": packaging_cost,
        "total_cost": total_cost,
        "batch_size_barrels": inputs.batch_size_barrels,
        "cost_per_barrel": cost_per_barrel,
        "margin_pct": inputs.margin_pct,
        "recommended_sale_per_barrel": recommended_sale_per_barrel,
        "margin_dollars_per_barrel": margin_dollars_per_barrel,
    }


def _fmt(value: float) -> str:
    return f"${value:,.2f}"


def main() -> None:
    print("=" * 60)
    print("Craft Brewery Batch Cost Calculator")
    print("=" * 60)

    # Sample batch configuration
    inputs = BatchInputs(
        grain_price_per_lb=2.50,
        hops_price_per_oz=8.00,
        yeast_price_per_unit=50.00,
        packaging_price_per_unit=1.50,
        grain_lbs=100.0,
        hops_oz=10.0,
        yeast_units=2.0,
        packaging_units=100.0,
        batch_size_barrels=5.0,    # barrels
        margin_pct=0.30,           # 30% margin
    )

    print(f"\nBatch size: {inputs.batch_size_barrels:.1f} barrels")
    print(f"Margin: {inputs.margin_pct * 100:.0f}%\n")
    print("Ingredient costs:")
    print(
        f"  Grain:       {inputs.grain_lbs:.1f} lbs x {_fmt(inputs.grain_price_per_lb)}/lb = {_fmt(inputs.grain_price_per_lb * inputs.grain_lbs)}"
    )
    print(
        f"  Hops:        {inputs.hops_oz:.1f} oz  x {_fmt(inputs.hops_price_per_oz)}/oz  = {_fmt(inputs.hops_price_per_oz * inputs.hops_oz)}"
    )
    print(
        f"  Yeast:       {inputs.yeast_units:.1f} units x {_fmt(inputs.yeast_price_per_unit)}/unit = {_fmt(inputs.yeast_price_per_unit * inputs.yeast_units)}"
    )
    print(
        f"  Packaging:   {inputs.packaging_units:.1f} units x {_fmt(inputs.packaging_price_per_unit)}/unit = {_fmt(inputs.packaging_price_per_unit * inputs.packaging_units)}"
    )

    result = calculate_batch_cost(inputs)

    print("\n--- Summary ---")
    print(f"Total batch cost:        {_fmt(result['total_cost'])}")
    print(f"Cost per barrel:         {_fmt(result['cost_per_barrel'])}")
    print(f"Margin per barrel:       {_fmt(result['margin_dollars_per_barrel'])}")
    print(f"Recommended sale/barrel: {_fmt(result['recommended_sale_per_barrel'])}")

    # --- Validation assertions ---
    assert abs(result["total_cost"] - 580.0) < 1e-6
    assert abs(result["cost_per_barrel"] - 116.0) < 1e-6
    assert abs(result["recommended_sale_per_barrel"] - 150.80) < 1e-6
    print("\n[OK] All validation assertions passed.")


if __name__ == "__main__":
    main()
