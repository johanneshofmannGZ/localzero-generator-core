# pyright: strict

from dataclasses import dataclass

from ...inputs import Inputs
from ...agri2018.a18 import A18

from .co2eChange import CO2eChange


@dataclass(kw_only=True)
class CO2eChangeFermentationOrManure(CO2eChange):
    CO2e_production_based_per_t: float = 0
    amount: float = 0
    demand_change: float = 0

    @classmethod
    def calc_fermen(
        cls, inputs: Inputs, what: str, ass_demand_change: str, a18: A18
    ) -> "CO2eChangeFermentationOrManure":
        CO2e_combustion_based = 0

        demand_change = inputs.ass(ass_demand_change)
        amount = getattr(a18, what).amount * (1 + demand_change)

        CO2e_production_based_per_t = getattr(a18, what).CO2e_production_based_per_t
        CO2e_production_based = amount * CO2e_production_based_per_t

        parent = CO2eChange(
            inputs=inputs,
            what=what,
            a18=a18,
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_production_based=CO2e_production_based,
        )

        return cls(
            inputs=inputs,
            what=what,
            a18=a18,
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_production_based=CO2e_production_based,
            CO2e_production_based_per_t=CO2e_production_based_per_t,
            CO2e_total=parent.CO2e_total,
            CO2e_total_2021_estimated=parent.CO2e_total_2021_estimated,
            amount=amount,
            change_CO2e_pct=parent.change_CO2e_pct,
            change_CO2e_t=parent.change_CO2e_t,
            cost_climate_saved=parent.cost_climate_saved,
            demand_change=demand_change,
        )

    @classmethod
    def calc_manure(
        cls, inputs: Inputs, what: str, a18: A18, amount: float
    ) -> "CO2eChangeFermentationOrManure":
        CO2e_combustion_based = 0

        demand_change = inputs.ass("Ass_A_P_manure_ratio_CO2e_to_amount_change")

        CO2e_production_based_per_t = getattr(a18, what).CO2e_production_based_per_t * (
            1 + demand_change
        )
        CO2e_production_based = amount * CO2e_production_based_per_t

        parent = CO2eChange(
            inputs=inputs,
            what=what,
            a18=a18,
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_production_based=CO2e_production_based,
        )

        return cls(
            inputs=inputs,
            what=what,
            a18=a18,
            CO2e_combustion_based=CO2e_combustion_based,
            CO2e_production_based=CO2e_production_based,
            CO2e_production_based_per_t=CO2e_production_based_per_t,
            CO2e_total=parent.CO2e_total,
            CO2e_total_2021_estimated=parent.CO2e_total_2021_estimated,
            amount=amount,
            change_CO2e_pct=parent.change_CO2e_pct,
            change_CO2e_t=parent.change_CO2e_t,
            cost_climate_saved=parent.cost_climate_saved,
            demand_change=demand_change,
        )
