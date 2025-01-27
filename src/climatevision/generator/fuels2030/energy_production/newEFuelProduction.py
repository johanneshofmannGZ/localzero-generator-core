# pyright: strict

from dataclasses import dataclass

from ...inputs import Inputs
from ...utils import div


@dataclass(kw_only=True)
class NewEFuelProduction:
    """Production of new style of efuels that are not yet used (at an industrial scale)."""

    CO2e_production_based: float
    CO2e_production_based_per_MWh: float
    CO2e_total: float
    CO2e_total_2021_estimated: float
    change_CO2e_pct: float
    change_CO2e_t: float
    change_energy_MWh: float
    cost_climate_saved: float
    cost_wage: float
    demand_electricity: float
    demand_emplo: float
    demand_emplo_new: float
    energy: float
    full_load_hour: float
    invest: float
    invest_outside: float
    invest_pa: float
    invest_pa_outside: float
    invest_per_x: float
    pct_of_wage: float
    power_to_be_installed: float
    ratio_wage_to_emplo: float

    @classmethod
    def calc(
        cls,
        inputs: Inputs,
        energy: float,
        CO2e_emission_factor: float,
        invest_per_power: float,
        full_load_hour: float,
        fuel_efficiency: float,
    ) -> "NewEFuelProduction":
        fact = inputs.fact
        ass = inputs.ass
        entries = inputs.entries

        CO2e_total_2021_estimated = 0
        # We assume that we take as much CO2e out of the air when the E-Fuel
        # is produced, as we later emit when it is burned.
        CO2e_production_based_per_MWh = -1 * CO2e_emission_factor
        CO2e_production_based = CO2e_production_based_per_MWh * energy
        CO2e_total = CO2e_production_based
        change_CO2e_t = CO2e_total
        change_CO2e_pct = 0

        pct_of_wage = ass("Ass_S_constr_renew_gas_pct_of_wage_2017")
        ratio_wage_to_emplo = ass("Ass_S_constr_renew_gas_wage_per_year_2017")
        demand_electricity = energy / fuel_efficiency
        change_energy_MWh = energy
        power_to_be_installed = demand_electricity / full_load_hour
        invest = power_to_be_installed * invest_per_power
        cost_climate_saved = (
            -CO2e_total * entries.m_duration_neutral * fact("Fact_M_cost_per_CO2e_2020")
        )
        invest_pa = invest / entries.m_duration_target
        invest_outside = invest
        invest_pa_outside = invest_pa
        cost_wage = invest_pa * pct_of_wage
        demand_emplo = div(cost_wage, ratio_wage_to_emplo)
        demand_emplo_new = demand_emplo
        return cls(
            CO2e_production_based=CO2e_production_based,
            CO2e_production_based_per_MWh=CO2e_production_based_per_MWh,
            CO2e_total=CO2e_total,
            CO2e_total_2021_estimated=CO2e_total_2021_estimated,
            change_CO2e_pct=change_CO2e_pct,
            change_CO2e_t=change_CO2e_t,
            change_energy_MWh=change_energy_MWh,
            cost_climate_saved=cost_climate_saved,
            cost_wage=cost_wage,
            demand_electricity=demand_electricity,
            demand_emplo=demand_emplo,
            demand_emplo_new=demand_emplo_new,
            energy=energy,
            full_load_hour=full_load_hour,
            invest=invest,
            invest_outside=invest_outside,
            invest_pa=invest_pa,
            invest_pa_outside=invest_pa_outside,
            invest_per_x=invest_per_power,
            pct_of_wage=pct_of_wage,
            power_to_be_installed=power_to_be_installed,
            ratio_wage_to_emplo=ratio_wage_to_emplo,
        )
