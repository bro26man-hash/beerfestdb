# batch_cost_calculator.py
"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by tfrayner/beerfestdb -> tool_dashboard/CBF_beer_price_calculator.py
(https://github.com/tfrayner/beerfestdb)

Unlike the reference (which prices festival cask products from a SQL DB using an
ABV coefficient vs. cask cost, taking whichever is greater), this standalone
script computes the COST of brewing a single batch from raw ingredient inputs,
then derives a cost-per-barrel figure and a recommended selling price that
applies a configurable margin.

Key concepts borrowed from the reference:
  - "cost_price" vs "abv_price" -> here "cost_per_barrel" vs "sale_price"
  - taking the greater of two figures (reference used max(cost, abv)); we
    instead apply a margin on top of cost to guarantee coverage.
  - configurable coefficients (reference used pence/litre coefficients) -> here
    $/lb, $/oz, $/unit ingredient and packaging coefficients plus a margin %.
"""

# ---------------------------------------------------------------------------
# Default coefficients (mirrors the "default_*" constants in the reference)
# ---------------------------------------------------------------------------
DEFAULT_GRAIN_COST = 1.50      # $ per pound of malt
DEFAULT_HOPS_COST = 2.00      # $ per ounce of hops
DEFAULT_YEAST_COST = 5.00     # $ per yeast unit (a typical lab pitchable unit)
DEFAULT_PACKAGING_COST = 0.75 # $ per unit (bottle/can + cap/lid)
DEFAULT_BARREL_SIZE_GALLONS = 31.0  # US beer barrel = 31 US gallons
DEFAULT_MARGIN_PCT = 30.0     # 30% margin on cost


class BatchCostCalculator:
    """Compute batch cost, cost-per-barrel, and recommended sale price."""

    def __init__(
        self,
        grain_cost_per_lb,
        hops_cost_per_oz,
        yeast_cost_per_unit,
        packaging_cost_per_unit,
        margin_pct,
        gallons_per_barrel=DEFAULT_BARREL_SIZE_GALLONS,
    ):
        self.grain_cost_per_lb = grain_cost_per_lb
        self.hops_cost_per_oz = hops_cost_per_oz
        self.yeast_cost_per_unit = yeast_cost_per_unit
        self.packaging_cost_per_unit = packaging_cost_per_unit
        self.margin_pct = margin_pct
        self.gallons_per_barrel = gallons_per_barrel

    def calculate(
        self,
        batch_size_barrels,
        grain_lbs,
        hops_oz,
        yeast_units,
        packaging_units,
    ):
        """Return a dict of all computed figures for the batch."""
        # --- ingredient line items (cost = rate * quantity) ---
        grain_cost = self.grain_cost_per_lb * grain_lbs
        hops_cost = self.hops_cost_per_oz * hops_oz
        yeast_cost = self.yeast_cost_per_unit * yeast_units
        packaging_cost = self.packaging_cost_per_unit * packaging_units

        # --- totals ---
        total_ingredient_cost = (
            grain_cost + hops_cost + yeast_cost + packaging_cost
        )
        total_cost = total_ingredient_cost  # extend with overhead if desired

        # --- per-barrel figures ---
        cost_per_barrel = total_cost / batch_size_barrels

        # --- recommended selling price with margin (like the reference's
        #     "price_to_round" but driven by a percentage margin) ---
        margin_multiplier = 1.0 + (self.margin_pct / 100.0)
        recommended_price_per_barrel = cost_per_barrel * margin_multiplier

        return {
            "batch_size_barrels": batch_size_barrels,
            "grain_cost": grain_cost,
            "hops_cost": hops_cost,
            "yeast_cost": yeast_cost,
            "packaging_cost": packaging_cost,
            "total_cost": total_cost,
            "cost_per_barrel": cost_per_barrel,
            "margin_pct": self.margin_pct,
            "recommended_price_per_barrel": recommended_price_per_barrel,
        }


def format_report(result):
    """Render a human-readable report (similar to the reference's st.write output)."""
    lines = []
    lines.append("=" * 60)
    lines.append("CRAFT BREWERY BATCH COST REPORT")
    lines.append("=" * 60)
    lines.append(f"Batch size           : {result['batch_size_barrels']} bbl ({result['batch_size_barrels'] * DEFAULT_BARREL_SIZE_GALLONS:.0f} gal)")
    lines.append("-" * 60)
    lines.append("Ingredient line items:")
    lines.append(f"  Grain              : ${result['grain_cost']:.2f}")
    lines.append(f"  Hops               : ${result['hops_cost']:.2f}")
    lines.append(f"  Yeast              : ${result['yeast_cost']:.2f}")
    lines.append(f"  Packaging          : ${result['packaging_cost']:.2f}")
    lines.append("-" * 60)
    lines.append(f"TOTAL COST           : ${result['total_cost']:.2f}")
    lines.append(f"COST / BARREL        : ${result['cost_per_barrel']:.2f}")
    lines.append(f"MARGIN               : {result['margin_pct']:.1f}%")
    lines.append(f"RECOMMENDED SELL/BBL : ${result['recommended_price_per_barrel']:.2f}")
    lines.append("=" * 60)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Demo / sample batch (executed on direct run)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Sample 10-barrel pale ale batch
    calc = BatchCostCalculator(
        grain_cost_per_lb=DEFAULT_GRAIN_COST,
        hops_cost_per_oz=DEFAULT_HOPS_COST,
        yeast_cost_per_unit=DEFAULT_YEAST_COST,
        packaging_cost_per_unit=DEFAULT_PACKAGING_COST,
        margin_pct=DEFAULT_MARGIN_PCT,
    )

    sample = calc.calculate(
        batch_size_barrels=10,
        grain_lbs=200,   # ~20 lb / bbl
        hops_oz=60,      # ~6 oz / bbl
        yeast_units=4,
        packaging_units=1200,  # bottles/cans
    )

    print(format_report(sample))
