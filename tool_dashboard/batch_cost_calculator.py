# batch_cost_calculator.py
# A craft brewery batch cost calculator inspired by CBF_beer_price_calculator.py from tfrayner/beerfestdb

def calculate_batch_cost(
    grain_cost_per_lb: float,
    hops_cost_per_oz: float,
    yeast_cost_per_unit: float,
    packaging_cost_per_unit: float,
    batch_size_barrels: float,
    grain_lbs_per_barrel: float,
    hops_oz_per_barrel: float,
    yeast_units_per_barrel: float,
    packaging_units_per_barrel: float,
    margin_pct: float
) -> dict:
    """
    Calculates the total cost and recommended selling price for a craft brewery batch.
    
    Args:
        grain_cost_per_lb: Price per pound of grain ($)
        hops_cost_per_oz: Price per ounce of hops ($)
        yeast_cost_per_unit: Price per unit of yeast ($)
        packaging_cost_per_unit: Price per unit of packaging ($)
        batch_size_barrels: Total batch size in barrels
        grain_lbs_per_barrel: Pounds of grain used per barrel
        hops_oz_per_barrel: Ounces of hops used per barrel
        yeast_units_per_barrel: Units of yeast used per barrel
        packaging_units_per_barrel: Units of packaging used per barrel
        margin_pct: Desired profit margin as a percentage (e.g., 30 for 30%)
    
    Returns:
        dict with cost breakdown and recommended price
    """
    # --- Ingredient Quantities (for the full batch) ---
    total_grain_lbs = grain_lbs_per_barrel * batch_size_barrels
    total_hops_oz = hops_oz_per_barrel * batch_size_barrels
    total_yeast_units = yeast_units_per_barrel * batch_size_barrels
    total_packaging_units = packaging_units_per_barrel * batch_size_barrels

    # --- Ingredient Costs ---
    grain_cost = total_grain_lbs * grain_cost_per_lb
    hops_cost = total_hops_oz * hops_cost_per_oz
    yeast_cost = total_yeast_units * yeast_cost_per_unit
    packaging_cost = total_packaging_units * packaging_cost_per_unit

    # --- Totals ---
    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_barrel = total_cost / batch_size_barrels if batch_size_barrels > 0 else 0

    # --- Selling Price with Margin ---
    recommended_price_per_barrel = cost_per_barrel * (1 + margin_pct / 100)

    return {
        "batch_size_barrels": batch_size_barrels,
        "total_grain_lbs": round(total_grain_lbs, 2),
        "total_hops_oz": round(total_hops_oz, 2),
        "total_yeast_units": round(total_yeast_units, 2),
        "total_packaging_units": round(total_packaging_units, 2),
        "grain_cost": round(grain_cost, 2),
        "hops_cost": round(hops_cost, 2),
        "yeast_cost": round(yeast_cost, 2),
        "packaging_cost": round(packaging_cost, 2),
        "total_cost": round(total_cost, 2),
        "cost_per_barrel": round(cost_per_barrel, 2),
        "margin_pct": margin_pct,
        "recommended_price_per_barrel": round(recommended_price_per_barrel, 2),
    }


def print_results(r: dict) -> None:
    """Pretty-prints the calculation results."""
    print("=" * 55)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 55)
    print(f"  Batch Size          : {r['batch_size_barrels']} barrels")
    print("-" * 55)
    print(f"  Grain               : {r['total_grain_lbs']} lbs  ->  ${r['grain_cost']:,.2f}")
    print(f"  Hops                : {r['total_hops_oz']} oz   ->  ${r['hops_cost']:,.2f}")
    print(f"  Yeast               : {r['total_yeast_units']} units ->  ${r['yeast_cost']:,.2f}")
    print(f"  Packaging           : {r['total_packaging_units']} units ->  ${r['packaging_cost']:,.2f}")
    print("-" * 55)
    print(f"  TOTAL COST          :  ${r['total_cost']:,.2f}")
    print(f"  COST PER BARREL     :  ${r['cost_per_barrel']:,.2f}")
    print(f"  MARGIN              :  {r['margin_pct']}%")
    print(f"  RECOMMENDED PRICE/B :  ${r['recommended_price_per_barrel']:,.2f}")
    print("=" * 55)


# ── Sample batch run ──────────────────────────────────────────────
if __name__ == "__main__":
    sample = calculate_batch_cost(
        grain_cost_per_lb=1.50,
        hops_cost_per_oz=1.20,
        yeast_cost_per_unit=8.00,
        packaging_cost_per_unit=0.45,
        batch_size_barrels=30,
        grain_lbs_per_barrel=6.0,
        hops_oz_per_barrel=1.2,
        yeast_units_per_barrel=1.0,
        packaging_units_per_barrel=110,
        margin_pct=30,
    )
    print_results(sample)
