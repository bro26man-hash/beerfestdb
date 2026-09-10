"""
batch_cost_calculator.py
Craft brewery batch cost calculator.

Inspired by CBF_beer_price_calculator.py (tfrayner/beerfestdb).
Computes total batch cost, cost per barrel, and recommended selling price
per barrel based on a configurable margin.
"""

from dataclasses import dataclass


@dataclass
class IngredientCost:
    grain_per_lb: float
    hops_per_oz: float
    yeast_per_unit: float
    packaging_per_unit: float


class BatchCostCalculator:
    def __init__(
        self,
        grain_cost: IngredientCost,
        batch_size_bbl: float,
        grain_lbs: float,
        hops_oz: float,
        yeast_units: float,
        packaging_units: float,
        margin_pct: float = 25.0,
    ):
        self.grain = grain_cost
        self.batch_size_bbl = batch_size_bbl
        self.grain_lbs = grain_lbs
        self.hops_oz = hops_oz
        self.yeast_units = yeast_units
        self.packaging_units = packaging_units
        self.margin_pct = margin_pct
        self._validate()

    def _validate(self):
        if self.batch_size_bbl <= 0:
            raise ValueError("Batch size must be greater than 0.")
        if self.margin_pct < 0:
            raise ValueError("Margin percentage must be non-negative.")
        for name, val in [
            ("grain_lbs", self.grain_lbs),
            ("hops_oz", self.hops_oz),
            ("yeast_units", self.yeast_units),
            ("packaging_units", self.packaging_units),
        ]:
            if val < 0:
                raise ValueError(f"{name} must be non-negative.")

    def grain_cost_total(self) -> float:
        return self.grain_lbs * self.grain.grain_per_lb

    def hops_cost_total(self) -> float:
        return self.hops_oz * self.grain.hops_per_oz

    def yeast_cost_total(self) -> float:
        return self.yeast_units * self.grain.yeast_per_unit

    def packaging_cost_total(self) -> float:
        return self.packaging_units * self.grain.packaging_per_unit

    def total_cost(self) -> float:
        return (
            self.grain_cost_total()
            + self.hops_cost_total()
            + self.yeast_cost_total()
            + self.packaging_cost_total()
        )

    def cost_per_barrel(self) -> float:
        return self.total_cost() / self.batch_size_bbl

    def recommended_price_per_barrel(self) -> float:
        return self.cost_per_barrel() * (1 + self.margin_pct / 100.0)

    def report(self) -> str:
        lines = [
            "===== CRAFT BREWERY BATCH COST CALCULATOR =====",
            f"Batch size:           {self.batch_size_bbl} bbl",
            f"Margin:               {self.margin_pct}%",
            "--- Ingredient quantities & unit prices ---",
            f"  Grain:   {self.grain_lbs} lbs  @ ${self.grain.grain_per_lb:.2f}/lb  = ${self.grain_cost_total():.2f}",
            f"  Hops:    {self.hops_oz} oz   @ ${self.grain.hops_per_oz:.2f}/oz   = ${self.hops_cost_total():.2f}",
            f"  Yeast:   {self.yeast_units} units @ ${self.grain.yeast_per_unit:.2f}/unit = ${self.yeast_cost_total():.2f}",
            f"  Packaging: {self.packaging_units} units @ ${self.grain.packaging_per_unit:.2f}/unit = ${self.packaging_cost_total():.2f}",
            "--- Totals ---",
            f"  Total batch cost:   ${self.total_cost():.2f}",
            f"  Cost per barrel:    ${self.cost_per_barrel():.2f}",
            f"  Recommended price/bbl: ${self.recommended_price_per_barrel():.2f}",
            "==============================================",
        ]
        return "\n".join(lines)


def main():
    grain = IngredientCost(
        grain_per_lb=0.75,
        hops_per_oz=3.50,
        yeast_per_unit=8.00,
        packaging_per_unit=1.20,
    )

    calc = BatchCostCalculator(
        grain_cost=grain,
        batch_size_bbl=10.0,
        grain_lbs=800.0,
        hops_oz=5.0,
        yeast_units=2.0,
        packaging_units=300.0,
        margin_pct=30.0,
    )

    print(calc.report())


if __name__ == "__main__":
    main()
