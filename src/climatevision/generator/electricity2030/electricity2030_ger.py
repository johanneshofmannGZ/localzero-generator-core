# pyright: strict

from ..inputs import Inputs
from ..utils import div, MILLION
from ..electricity2018.e18 import E18
from ..residences2018.r18 import R18
from ..business2018.b18 import B18
from ..agri2030.a30 import A30
from ..business2030.b30 import B30
from ..fuels2030.f30 import F30
from ..heat2030.h30 import H30
from ..industry2030.i30 import I30
from ..residences2030.r30 import R30
from ..transport2030.t30 import T30

from .e30 import E30
from .electricity2030_core import (
    EColVars2030,
    EnergyDemand,
    EnergyDemandWithCostFuel,
    FossilFuelsProduction,
    RenewableGeothermalProduction,
    Energy,
)


# Berechnungsfunktion im Sektor E für 203X
def calc(
    inputs: Inputs,
    *,
    e18: E18,
    r18: R18,
    b18: B18,
    a30: A30,
    b30: B30,
    f30: F30,
    h30: H30,
    i30: I30,
    r30: R30,
    t30: T30,
    p_local_biomass_cogen: EColVars2030,
    p_local_biomass: EColVars2030,
) -> E30:
    fact = inputs.fact
    ass = inputs.ass
    entries = inputs.entries

    Kalkulationszeitraum = entries.m_duration_target
    KlimaneutraleJahre = entries.m_duration_neutral

    e = EColVars2030()
    g = EColVars2030()
    g_grid_offshore = EColVars2030()
    g_grid_onshore = EColVars2030()
    g_grid_pv = EColVars2030()
    d = EnergyDemand()
    d_r = EnergyDemandWithCostFuel()
    d_b = EnergyDemandWithCostFuel()
    d_h = EnergyDemand()
    d_i = EnergyDemandWithCostFuel()
    d_t = EnergyDemandWithCostFuel()
    d_a = EnergyDemandWithCostFuel()
    d_f_hydrogen_reconv = EnergyDemand()
    d_f_wo_hydrogen = EnergyDemand()
    p = EColVars2030()
    p_fossil_and_renew = EColVars2030()
    p_fossil = FossilFuelsProduction()
    p_fossil_nuclear = FossilFuelsProduction()
    p_fossil_coal_brown = FossilFuelsProduction()
    p_fossil_coal_black = FossilFuelsProduction()
    p_fossil_gas = FossilFuelsProduction()
    p_fossil_ofossil = FossilFuelsProduction()
    p_renew = EColVars2030()
    p_renew_pv = EColVars2030()
    p_renew_pv_roof = EColVars2030()
    p_renew_pv_facade = EColVars2030()
    p_renew_pv_park = EColVars2030()
    p_renew_pv_agri = EColVars2030()
    p_renew_wind = EColVars2030()
    p_renew_wind_onshore = EColVars2030()
    p_renew_wind_offshore = EColVars2030()
    p_renew_biomass = EColVars2030()
    p_renew_geoth = RenewableGeothermalProduction()
    p_renew_hydro = EColVars2030()
    p_renew_reverse = EColVars2030()
    p_local = EColVars2030()
    p_local_pv = EColVars2030()
    p_local_pv_roof = EColVars2030()
    p_local_pv_facade = EColVars2030()
    p_local_pv_park = EColVars2030()
    p_local_pv_agri = EColVars2030()
    p_local_wind_onshore = EColVars2030()
    p_local_hydro = EColVars2030()
    p_local_surplus = Energy()

    """S T A R T"""
    g_grid_offshore.invest_outside = 0
    g_grid_offshore.invest_per_x = ass("Ass_E_G_grid_offshore_ratio_invest_to_power")
    g_grid_offshore.pct_of_wage = fact("Fact_B_P_constr_main_revenue_pct_of_wage_2017")
    g_grid_offshore.ratio_wage_to_emplo = fact(
        "Fact_B_P_constr_main_ratio_wage_to_emplo_2017"
    )
    g_grid_onshore.invest_per_x = ass("Ass_E_G_grid_onshore_ratio_invest_to_power")
    g_grid_onshore.pct_of_wage = fact("Fact_B_P_constr_main_revenue_pct_of_wage_2017")
    g_grid_onshore.ratio_wage_to_emplo = fact(
        "Fact_B_P_constr_main_ratio_wage_to_emplo_2017"
    )
    g_grid_pv.invest_per_x = ass("Ass_E_G_grid_pv_ratio_invest_to_power")
    g_grid_pv.pct_of_wage = fact("Fact_B_P_constr_main_revenue_pct_of_wage_2017")
    g_grid_pv.ratio_wage_to_emplo = fact(
        "Fact_B_P_constr_main_ratio_wage_to_emplo_2017"
    )
    d_h.energy = h30.p.demand_electricity
    d_r.energy = r30.p.demand_electricity
    d_b.energy = b30.p.demand_electricity
    d_i.energy = i30.p.demand_electricity
    d_t.energy = t30.t.transport.demand_electricity
    d_a.energy = a30.p_operation.demand_electricity
    d_f_wo_hydrogen.energy = (
        f30.p_petrol.demand_electricity
        + f30.p_jetfuel.demand_electricity
        + f30.p_diesel.demand_electricity
        + f30.p_emethan.demand_electricity
        + f30.p_hydrogen.demand_electricity
    )
    d_f_hydrogen_reconv.energy = f30.p_hydrogen_reconv.demand_electricity
    d_r.cost_fuel_per_MWh = fact("Fact_E_D_R_cost_fuel_per_MWh_2018")
    d_b.cost_fuel_per_MWh = fact("Fact_E_D_B_cost_fuel_per_MWh_2018")
    d_i.cost_fuel_per_MWh = fact("Fact_E_D_I_cost_fuel_per_MWh_2018")
    d_t.cost_fuel_per_MWh = fact("Fact_E_D_R_cost_fuel_per_MWh_2018")
    d_a.cost_fuel_per_MWh = fact("Fact_E_D_R_cost_fuel_per_MWh_2018")
    p_renew.invest_pa_com = 0
    p_renew.invest_com = 0
    p_fossil_nuclear.energy = 0
    p_fossil_coal_brown.energy = 0
    p_fossil_coal_black.energy = 0
    p_fossil_gas.energy = 0
    p_fossil_ofossil.energy = 0
    p_fossil_coal_brown.CO2e_total_2021_estimated = (
        e18.p_fossil_coal_brown.CO2e_combustion_based
        * fact("Fact_M_CO2e_wo_lulucf_2021_vs_2018")
    )
    p_fossil_coal_black.CO2e_total_2021_estimated = (
        e18.p_fossil_coal_black.CO2e_combustion_based
        * fact("Fact_M_CO2e_wo_lulucf_2021_vs_2018")
    )
    p_fossil_gas.CO2e_total_2021_estimated = (
        e18.p_fossil_gas.CO2e_combustion_based
        * fact("Fact_M_CO2e_wo_lulucf_2021_vs_2018")
    )
    p_fossil_ofossil.CO2e_total_2021_estimated = (
        e18.p_fossil_ofossil.CO2e_combustion_based
        * fact("Fact_M_CO2e_wo_lulucf_2021_vs_2018")
    )
    p_fossil_nuclear.cost_fuel_per_MWh = e18.p_fossil_nuclear.cost_fuel_per_MWh
    p_fossil_nuclear.cost_mro_per_MWh = e18.p_fossil_nuclear.cost_mro_per_MWh
    p_fossil_nuclear.CO2e_combustion_based_per_MWh = (
        e18.p_fossil_nuclear.CO2e_combustion_based_per_MWh
    )
    p_fossil_nuclear.CO2e_total_2021_estimated = (
        e18.p_fossil_nuclear.CO2e_combustion_based
        * fact("Fact_M_CO2e_wo_lulucf_2021_vs_2018")
    )
    p_fossil_coal_brown.cost_fuel_per_MWh = e18.p_fossil_coal_brown.cost_fuel_per_MWh
    p_fossil_coal_brown.cost_mro_per_MWh = e18.p_fossil_coal_brown.cost_mro_per_MWh
    p_fossil_coal_brown.CO2e_combustion_based_per_MWh = (
        e18.p_fossil_coal_brown.CO2e_combustion_based_per_MWh
    )
    p_fossil_coal_black.cost_fuel_per_MWh = e18.p_fossil_coal_black.cost_fuel_per_MWh
    p_fossil_coal_black.cost_mro_per_MWh = e18.p_fossil_coal_black.cost_mro_per_MWh
    p_fossil_coal_black.CO2e_combustion_based_per_MWh = (
        e18.p_fossil_coal_black.CO2e_combustion_based_per_MWh
    )
    p_fossil_gas.cost_fuel_per_MWh = e18.p_fossil_gas.cost_fuel_per_MWh
    p_fossil_gas.cost_mro_per_MWh = e18.p_fossil_gas.cost_mro_per_MWh
    p_fossil_gas.CO2e_combustion_based_per_MWh = (
        e18.p_fossil_gas.CO2e_combustion_based_per_MWh
    )
    p_fossil_ofossil.cost_fuel_per_MWh = e18.p_fossil_ofossil.cost_fuel_per_MWh
    p_fossil_ofossil.cost_mro_per_MWh = e18.p_fossil_ofossil.cost_mro_per_MWh
    p_fossil_ofossil.CO2e_combustion_based_per_MWh = (
        e18.p_fossil_ofossil.CO2e_combustion_based_per_MWh
    )
    p_renew_pv.pct_energy = 0
    p_renew_biomass.pct_energy = 0
    p_renew_hydro.pct_energy = 0  # energy
    p_renew_pv.CO2e_total = 0
    p_renew_wind.CO2e_total = 0
    p_renew_geoth.CO2e_total = 0
    p_renew_hydro.CO2e_total = 0
    p_renew_reverse.CO2e_total = 0
    p_renew_biomass.CO2e_total_2021_estimated = (
        e18.p_renew_biomass.CO2e_combustion_based
        * fact("Fact_M_CO2e_wo_lulucf_2021_vs_2018")
    )
    p_renew_geoth.invest_pa_outside = 0
    p_renew_reverse.invest_pa_outside = 0
    p_renew_geoth.invest_outside = 0
    p_renew_reverse.invest_outside = 0
    p_renew_pv.energy = 0
    p_renew_pv.CO2e_combustion_based_per_MWh = fact(
        "Fact_E_P_climate_neutral_ratio_CO2e_cb_to_fec"
    )
    p_renew_pv_roof.pct_energy = 0
    p_local_pv_roof.full_load_hour = entries.e_pv_full_load_hours_sta
    p_renew_pv_facade.pct_energy = 0
    p_local_pv_facade.full_load_hour = ass("Ass_E_P_local_pv_facade_full_load_hours")
    p_renew_pv_park.pct_energy = 0
    p_renew_pv_agri.pct_energy = 0
    p_renew_wind.CO2e_combustion_based_per_MWh = fact(
        "Fact_E_P_climate_neutral_ratio_CO2e_cb_to_fec"
    )
    p_renew_wind_offshore.invest_pa_outside = 0
    p_renew_wind_offshore.invest_outside = 0
    p_renew_wind_offshore.emplo_existing = fact("Fact_E_P_wind_offshore_emplo_2018")
    p_renew_wind_onshore.pct_energy = 0
    p_renew_wind_onshore.cost_mro_per_MWh = (
        ass("Ass_E_P_local_wind_onshore_ratio_invest_to_power_2020")
        * ass("Ass_E_P_local_wind_onshore_mro_per_year")
        / fact("Fact_E_P_wind_onshore_full_load_hours")
        * 1000
    )
    p_renew_wind_offshore.power_installed = fact(
        "Fact_E_P_wind_offshore_power_installed_2018"
    )
    p_renew_wind_offshore.full_load_hour = fact(
        "Fact_E_P_wind_offshore_full_load_hours"
    )
    p_renew_wind_offshore.cost_mro_per_MWh = (
        ass("Ass_E_P_renew_wind_offshore_ratio_invest_to_power_2030")
        * ass("Ass_E_P_renew_wind_offshore_mro_per_year")
        / fact("Fact_E_P_wind_offshore_full_load_hours")
        * 1000
    )
    p_renew_wind_offshore.invest_per_x = (
        ass("Ass_E_P_renew_wind_offshore_ratio_invest_to_power_2030") * 1000
    )
    p_renew_wind_offshore.pct_of_wage = ass(
        "Ass_E_P_constr_plant_invest_pct_of_wage_2017"
    )
    p_renew_wind_offshore.ratio_wage_to_emplo = ass(
        "Ass_E_P_constr_elec_ratio_wage_to_emplo_2017"
    )
    p_renew_wind_offshore.power_installable = ass(
        "Ass_E_P_renew_wind_offshore_power_installable"
    )
    p_renew_wind_offshore.power_to_be_installed_pct = ass(
        "Ass_E_P_renew_wind_offshore_power_to_be_installed_2035"
    )
    p_renew_biomass.cost_fuel_per_MWh = ass(
        "Ass_E_P_local_biomass_material_costs"
    ) / ass("Ass_E_P_local_biomass_efficiency")
    p_renew_biomass.cost_mro_per_MWh = ass("Ass_E_P_local_biomass_mro_per_MWh")
    p_renew_biomass.CO2e_combustion_based_per_MWh = (
        e18.p_renew_biomass.CO2e_combustion_based_per_MWh
    )
    p_renew_biomass.change_energy_MWh = 0
    p_renew_geoth.power_installed = fact("Fact_E_P_geoth_power_installed_2018")
    p_renew_geoth.full_load_hour = fact("Fact_E_P_geoth_full_load_hours")
    p_renew_geoth.cost_mro_per_MWh = ass("Ass_E_P_renew_geoth_mro_per_MWh")
    p_renew_geoth.CO2e_combustion_based_per_MWh = fact(
        "Fact_E_P_climate_neutral_ratio_CO2e_cb_to_fec"
    )
    p_renew_geoth.invest_per_x = ass("Ass_E_P_renew_geoth_invest") * 1000
    p_renew_geoth.pct_of_wage = ass("Ass_E_P_constr_plant_invest_pct_of_wage_2017")
    p_renew_geoth.ratio_wage_to_emplo = ass(
        "Ass_E_P_constr_elec_ratio_wage_to_emplo_2017"
    )
    p_renew_geoth.power_installable = ass("Ass_E_P_renew_geoth_power_installable")
    p_renew_geoth.power_to_be_installed_pct = ass(
        "Ass_E_P_renew_geoth_power_to_be_installed_2035"
    )
    p_renew_hydro.cost_mro_per_MWh = ass("Ass_E_P_local_hydro_mro_per_MWh")
    p_renew_hydro.CO2e_combustion_based_per_MWh = fact(
        "Fact_E_P_climate_neutral_ratio_CO2e_cb_to_fec"
    )
    p_renew_reverse.cost_mro_per_MWh = ass(
        "Ass_E_P_renew_reverse_gud_cost_mro_per_MW"
    ) / ass("Ass_E_P_renew_reverse_full_load_hours")
    p_renew_reverse.CO2e_combustion_based_per_MWh = fact(
        "Fact_E_P_climate_neutral_ratio_CO2e_cb_to_fec"
    )
    p_renew_reverse.invest_per_x = (
        ass("Ass_E_P_renew_reverse_gud_ratio_invest_to_power") * 1000
    )
    p_renew_reverse.pct_of_wage = ass("Ass_E_P_constr_plant_invest_pct_of_wage_2017")
    p_renew_reverse.ratio_wage_to_emplo = ass(
        "Ass_E_P_constr_elec_ratio_wage_to_emplo_2017"
    )
    p_renew_reverse.power_installed = fact("Fact_E_P_gas_power_installed_2018")
    p_renew_reverse.full_load_hour = ass("Ass_E_P_renew_reverse_full_load_hours")
    p_local_biomass.CO2e_total_2021_estimated = (
        e18.p_local_biomass.CO2e_combustion_based
        * fact("Fact_M_CO2e_wo_lulucf_2021_vs_2018")
    )
    p_local_pv.CO2e_combustion_based_per_MWh = fact(
        "Fact_E_P_climate_neutral_ratio_CO2e_cb_to_fec"
    )
    p_local_pv.emplo_existing = (
        fact("Fact_B_P_install_elec_emplo_2017")
        * entries.m_population_com_2018
        / entries.m_population_nat
    )
    p_local_pv_roof.power_installed = entries.e_PV_power_inst_roof
    p_local_pv_facade.power_installed = entries.e_PV_power_inst_facade
    p_local_pv_park.power_installed = entries.e_PV_power_inst_park
    p_local_pv_agri.power_installed = entries.e_PV_power_inst_agripv
    p_local_pv_roof.invest_per_x = (
        ass("Ass_E_P_local_pv_roof_ratio_invest_to_power_2030") * 1000
    )
    p_local_pv_roof.pct_of_wage = ass("Ass_E_P_pv_invest_pct_of_wage")
    p_local_pv_roof.ratio_wage_to_emplo = ass(
        "Ass_E_P_constr_elec_ratio_wage_to_emplo_2017"
    )
    p_local_pv_roof.power_to_be_installed_pct = entries.e_PV_power_to_be_inst_roof
    p_local_pv_roof.area_ha_available = (
        (4 / 3)
        * (
            (
                entries.r_area_m2_1flat
                / 100
                * ass("Ass_E_P_local_pv_roof_area_building1")
                + entries.r_area_m2_2flat
                / 100
                * ass("Ass_E_P_local_pv_roof_area_building2")
                + entries.r_area_m2_3flat
                / 100
                * ass("Ass_E_P_local_pv_roof_area_buildingD")
                + entries.r_area_m2_dorm
                / 100
                * ass("Ass_E_P_local_pv_roof_area_buildingD")
            )
        )
        / 10000
    )
    p_local_pv_roof.area_ha_available_pct_of_action = ass(
        "Ass_E_P_local_pv_roof_potential"
    )
    p_local_pv_roof.ratio_power_to_area_ha = ass(
        "Ass_E_P_local_pv_roof_ratio_power_to_area_ha"
    )
    p_local_pv_facade.cost_mro_per_MWh = (
        ass("Ass_E_S_local_pv_facade_ratio_invest_to_power")
        * ass("Ass_E_P_local_pv_roof_mro_per_year")
        / ass("Ass_E_P_local_pv_facade_full_load_hours")
        * 1000
    )
    p_local_pv_facade.invest_per_x = (
        ass("Ass_E_S_local_pv_facade_ratio_invest_to_power") * 1000
    )
    p_local_pv_facade.pct_of_wage = ass("Ass_E_P_pv_invest_pct_of_wage")
    p_local_pv_facade.ratio_wage_to_emplo = ass(
        "Ass_E_P_constr_elec_ratio_wage_to_emplo_2017"
    )
    p_local_pv_facade.power_to_be_installed_pct = entries.e_PV_power_to_be_inst_facade
    p_local_pv_facade.ratio_power_to_area_ha = ass(
        "Ass_E_P_local_pv_facade_ratio_power_to_area_ha"
    )
    p_local_pv_facade.area_ha_available = (
        ass("Ass_E_P_lcoal_pv_facade_potential")
        * entries.r_buildings_com
        / entries.r_buildings_nat
    )
    p_local_pv_facade.area_ha_available_pct_of_action = ass(
        "Ass_E_P_local_pv_facade_potential_usable"
    )
    p_local_pv_park.invest_per_x = (
        ass("Ass_E_S_local_pv_park_ratio_invest_to_power_2030") * 1000
    )
    p_local_pv_park.pct_of_wage = ass("Ass_E_P_pv_invest_pct_of_wage")
    p_local_pv_park.ratio_wage_to_emplo = ass(
        "Ass_E_P_constr_elec_ratio_wage_to_emplo_2017"
    )
    p_local_pv_park.power_to_be_installed_pct = entries.e_PV_power_to_be_inst_park
    p_local_pv_park.ratio_power_to_area_ha = ass("Ass_E_P_local_pv_park_power_per_ha")
    p_local_pv_park.area_ha_available_pct_of_action = ass(
        "Ass_E_P_local_pv_park_area_pct_of_available"
    )
    p_local_pv_park.area_ha_available = entries.m_area_total_com
    p_local_pv_agri.invest_per_x = (
        ass("Ass_E_P_local_pv_agri_ratio_invest_to_power") * 1000
    )
    p_local_pv_agri.pct_of_wage = ass("Ass_E_P_pv_invest_pct_of_wage")
    p_local_pv_agri.ratio_wage_to_emplo = ass(
        "Ass_E_P_constr_elec_ratio_wage_to_emplo_2017"
    )
    p_local_pv_agri.ratio_power_to_area_ha = ass("Ass_E_P_local_pv_agri_power_per_ha")
    p_local_pv_agri.area_ha_available_pct_of_action = ass(
        "Ass_E_P_local_pv_agri_power_installable"
    ) / (ass("Ass_E_P_local_pv_agri_power_per_ha") * entries.m_area_agri_nat)
    p_local_pv_agri.area_ha_available = entries.m_area_agri_com
    p_local_wind_onshore.power_installed = entries.e_PV_power_inst_wind_on
    p_local_wind_onshore.full_load_hour = fact("Fact_E_P_wind_onshore_full_load_hours")
    p_local_wind_onshore.cost_mro_per_MWh = (
        ass("Ass_E_P_local_wind_onshore_ratio_invest_to_power_2030")
        * ass("Ass_E_P_local_wind_onshore_mro_per_year")
        / fact("Fact_E_P_wind_onshore_full_load_hours")
        * 1000
    )
    p_local_wind_onshore.CO2e_combustion_based_per_MWh = fact(
        "Fact_E_P_climate_neutral_ratio_CO2e_cb_to_fec"
    )
    p_local_wind_onshore.invest_per_x = (
        ass("Ass_E_P_local_wind_onshore_ratio_invest_to_power_2030") * 1000
    )
    p_local_wind_onshore.pct_of_wage = ass(
        "Ass_E_P_constr_plant_invest_pct_of_wage_2017"
    )
    p_local_wind_onshore.ratio_wage_to_emplo = ass(
        "Ass_E_P_constr_elec_ratio_wage_to_emplo_2017"
    )
    p_local_wind_onshore.emplo_existing = (
        fact("Fact_E_P_wind_onshore_emplo_2018")
        * entries.m_population_com_2018
        / entries.m_population_nat
    )
    p_local_wind_onshore.power_to_be_installed_pct = (
        entries.e_PV_power_to_be_inst_local_wind_onshore
    )
    p_local_wind_onshore.ratio_power_to_area_ha = (
        entries.e_local_wind_onshore_ratio_power_to_area_sta
    )
    p_local_wind_onshore.area_ha_available = (
        entries.m_area_agri_com + entries.m_area_wood_com
    )
    p_local_wind_onshore.area_ha_available_pct_of_action = ass(
        "Ass_E_P_local_wind_onshore_pct_action"
    )
    p_local_biomass.cost_fuel_per_MWh = ass(
        "Ass_E_P_local_biomass_material_costs"
    ) / ass("Ass_E_P_local_biomass_efficiency")
    p_local_biomass.cost_mro_per_MWh = ass("Ass_E_P_local_biomass_mro_per_MWh")
    p_local_biomass.CO2e_combustion_based_per_MWh = fact(
        "Fact_E_P_biomass_ratio_CO2e_cb_nonCO2_to_gep_2018"
    ) / (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    p_local_biomass.invest_per_x = ass(
        "Ass_E_P_local_biomass_ratio_invest_to_power"
    )  # invest
    p_local_biomass.pct_of_wage = ass(
        "Ass_E_P_constr_plant_invest_pct_of_wage_2017"
    )  # cost_wage
    p_local_biomass.ratio_wage_to_emplo = ass(
        "Ass_E_P_constr_elec_ratio_wage_to_emplo_2017"
    )  # demand_emplo
    p_local_biomass.emplo_existing = (
        fact("Fact_E_P_biomass_emplo_2018")
        * entries.m_population_com_2018
        / entries.m_population_nat
    )
    p_local_hydro.power_installed = entries.e_PV_power_inst_water
    p_local_hydro.full_load_hour = fact("Fact_E_P_hydro_full_load_hours")  # energy
    p_local_hydro.cost_mro_per_MWh = ass("Ass_E_P_local_hydro_mro_per_MWh")  # cost_mro
    p_local_hydro.CO2e_combustion_based_per_MWh = fact(
        "Fact_E_P_climate_neutral_ratio_CO2e_cb_to_fec"
    )
    g.invest_outside = g_grid_offshore.invest_outside
    g_grid_offshore.invest_pa_outside = (
        g_grid_offshore.invest_outside / entries.m_duration_target
    )
    d_h.change_energy_MWh = d_h.energy - e18.d_h.energy  #
    d_r.change_energy_MWh = d_r.energy - e18.d_r.energy
    d_b.change_energy_MWh = d_b.energy - e18.d_b.energy
    d_i.change_energy_MWh = d_i.energy - e18.d_i.energy
    d_t.change_energy_MWh = d_t.energy - e18.d_t.energy
    d_a.change_energy_MWh = d_a.energy - e18.d_a.energy
    d_f_wo_hydrogen.change_energy_MWh = d_f_wo_hydrogen.energy - 0
    p_renew_reverse.energy = (
        (
            d_h.energy
            + d_r.energy
            + d_b.energy
            + d_i.energy
            + d_t.energy
            + d_a.energy
            + d_f_wo_hydrogen.energy
        )
        * ass("Ass_E_P_renew_reverse_addon_to_demand_2035")
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    d.energy = (
        d_h.energy
        + d_r.energy
        + d_b.energy
        + d_i.energy
        + d_t.energy
        + d_a.energy
        + d_f_wo_hydrogen.energy
        + d_f_hydrogen_reconv.energy
    )  #
    d_f_hydrogen_reconv.change_energy_MWh = (
        d_f_hydrogen_reconv.energy - e18.d_f_hydrogen_reconv.energy
    )
    p_fossil_and_renew.invest_pa_com = p_renew.invest_pa_com
    p_fossil_and_renew.invest_com = p_renew.invest_com
    p_fossil_nuclear.change_energy_MWh = (
        p_fossil_nuclear.energy - e18.p_fossil_nuclear.energy
    )
    p_fossil_coal_brown.change_energy_MWh = (
        p_fossil_coal_brown.energy - e18.p_fossil_coal_brown.energy
    )
    p_fossil_coal_black.change_energy_MWh = (
        p_fossil_coal_black.energy - e18.p_fossil_coal_black.energy
    )
    p_fossil_gas.change_energy_MWh = p_fossil_gas.energy - e18.p_fossil_gas.energy
    p_fossil.energy = (
        p_fossil_nuclear.energy
        + p_fossil_coal_brown.energy
        + p_fossil_coal_black.energy
        + p_fossil_gas.energy
        + p_fossil_ofossil.energy
    )

    p_fossil_ofossil.change_energy_MWh = (
        p_fossil_ofossil.energy - e18.p_fossil_ofossil.energy
    )
    p_fossil.CO2e_total_2021_estimated = (
        p_fossil_coal_brown.CO2e_total_2021_estimated
        + p_fossil_coal_black.CO2e_total_2021_estimated
        + p_fossil_gas.CO2e_total_2021_estimated
        + p_fossil_ofossil.CO2e_total_2021_estimated
    )
    p_fossil_nuclear.cost_fuel = (
        p_fossil_nuclear.cost_fuel_per_MWh * p_fossil_nuclear.energy / 1000000
    )
    p_fossil_nuclear.cost_mro = (
        p_fossil_nuclear.cost_mro_per_MWh * p_fossil_nuclear.energy / 1000000
    )
    p_fossil_nuclear.CO2e_combustion_based = (
        p_fossil_nuclear.energy * p_fossil_nuclear.CO2e_combustion_based_per_MWh
    )
    p_fossil_coal_brown.cost_fuel = (
        p_fossil_coal_brown.cost_fuel_per_MWh * p_fossil_coal_brown.energy / 1000000
    )
    p_fossil_coal_brown.cost_mro = (
        p_fossil_coal_brown.cost_mro_per_MWh * p_fossil_coal_brown.energy / 1000000
    )
    p_fossil_coal_brown.CO2e_combustion_based = (
        p_fossil_coal_brown.energy * p_fossil_coal_brown.CO2e_combustion_based_per_MWh
    )
    p_fossil_coal_black.cost_fuel = (
        p_fossil_coal_black.cost_fuel_per_MWh * p_fossil_coal_black.energy / 1000000
    )
    p_fossil_coal_black.cost_mro = (
        p_fossil_coal_black.cost_mro_per_MWh * p_fossil_coal_black.energy / 1000000
    )
    p_fossil_coal_black.CO2e_combustion_based = (
        p_fossil_coal_black.energy * p_fossil_coal_black.CO2e_combustion_based_per_MWh
    )
    p_fossil_gas.cost_fuel = (
        p_fossil_gas.cost_fuel_per_MWh * p_fossil_gas.energy / 1000000
    )
    p_fossil_gas.cost_mro = (
        p_fossil_gas.cost_mro_per_MWh * p_fossil_gas.energy / 1000000
    )
    p_fossil_gas.CO2e_combustion_based = (
        p_fossil_gas.energy * p_fossil_gas.CO2e_combustion_based_per_MWh
    )
    p_fossil_ofossil.cost_fuel = (
        p_fossil_ofossil.cost_fuel_per_MWh * p_fossil_ofossil.energy / 1000000
    )
    p_fossil_ofossil.cost_mro = (
        p_fossil_ofossil.cost_mro_per_MWh * p_fossil_ofossil.energy / 1000000
    )
    p_fossil_ofossil.CO2e_combustion_based = (
        p_fossil_ofossil.energy * p_fossil_ofossil.CO2e_combustion_based_per_MWh
    )
    p_renew.CO2e_total_2021_estimated = p_renew_biomass.CO2e_total_2021_estimated
    p_renew_pv.CO2e_combustion_based = (
        p_renew_pv.energy * p_renew_pv.CO2e_combustion_based_per_MWh
    )
    p_renew_pv_roof.energy = p_renew_pv.energy * p_renew_pv_roof.pct_energy
    p_renew_pv_roof.cost_mro_per_MWh = (
        ass("Ass_E_P_local_pv_roof_ratio_invest_to_power_2020")
        * ass("Ass_E_P_local_pv_roof_mro_per_year")
        / p_local_pv_roof.full_load_hour
        * 1000
    )
    p_local_pv_roof.cost_mro_per_MWh = (
        ass("Ass_E_P_local_pv_roof_ratio_invest_to_power_2030")
        * ass("Ass_E_P_local_pv_roof_mro_per_year")
        / p_local_pv_roof.full_load_hour
        * 1000
    )
    p_local_pv_park.full_load_hour = p_local_pv_roof.full_load_hour
    p_local_pv_agri.full_load_hour = p_local_pv_roof.full_load_hour
    p_renew_pv_facade.energy = p_renew_pv.energy * p_renew_pv_facade.pct_energy
    p_renew_pv_facade.cost_mro_per_MWh = (
        ass("Ass_E_S_local_pv_facade_ratio_invest_to_power")
        * ass("Ass_E_P_local_pv_roof_mro_per_year")
        / p_local_pv_facade.full_load_hour
        * 1000
    )
    p_renew_pv_park.energy = p_renew_pv.energy * p_renew_pv_park.pct_energy
    p_renew_pv_agri.energy = p_renew_pv.energy * p_renew_pv_agri.pct_energy
    p_renew_wind.invest_pa_outside = p_renew_wind_offshore.invest_pa_outside
    p_renew_wind.invest_outside = p_renew_wind_offshore.invest_outside
    p_renew_wind.emplo_existing = p_renew_wind_offshore.emplo_existing
    p_renew_wind_offshore.energy_installable = (
        p_renew_wind_offshore.full_load_hour
        * p_renew_wind_offshore.power_installable
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_renew_wind_offshore.power_to_be_installed = max(
        0,
        p_renew_wind_offshore.power_installable
        * p_renew_wind_offshore.power_to_be_installed_pct
        - p_renew_wind_offshore.power_installed,
    )
    p_renew_biomass.change_energy_pct = div(
        p_renew_biomass.change_energy_MWh, e18.p_renew_biomass.energy
    )
    p_renew_geoth.energy_installable = (
        p_renew_geoth.full_load_hour
        * p_renew_geoth.power_installable
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_renew_geoth.power_to_be_installed = max(
        0,
        p_renew_geoth.power_installable * p_renew_geoth.power_to_be_installed_pct
        - p_renew_geoth.power_installed,
    )
    p_renew_reverse.power_to_be_installed = max(
        0,
        ass("Ass_E_P_renew_reverse_addon_to_demand_2035")
        * ass("Ass_E_P_renew_nep_total_2035")
        / ass("Ass_E_P_renew_reverse_full_load_hours")
        - p_renew_reverse.power_installed,
    )
    p_local.CO2e_total_2021_estimated = p_local_biomass.CO2e_total_2021_estimated
    p_local_pv.power_installed = (
        p_local_pv_roof.power_installed
        + p_local_pv_facade.power_installed
        + p_local_pv_park.power_installed
        + p_local_pv_agri.power_installed
    )  #
    p_local_pv_roof.power_installable = (
        p_local_pv_roof.area_ha_available
        * p_local_pv_roof.area_ha_available_pct_of_action
        * p_local_pv_roof.ratio_power_to_area_ha
    )
    p_local_pv_facade.power_installable = (
        p_local_pv_facade.ratio_power_to_area_ha
        * p_local_pv_facade.area_ha_available
        * p_local_pv_facade.area_ha_available_pct_of_action
    )
    p_local_pv_park.power_installable = (
        p_local_pv_park.ratio_power_to_area_ha
        * p_local_pv_park.area_ha_available_pct_of_action
        * p_local_pv_park.area_ha_available
    )
    p_local_pv_agri.power_installable = (
        p_local_pv_agri.ratio_power_to_area_ha
        * p_local_pv_agri.area_ha_available_pct_of_action
        * p_local_pv_agri.area_ha_available
    )
    p_local_wind_onshore.power_installable = (
        p_local_wind_onshore.ratio_power_to_area_ha
        * p_local_wind_onshore.area_ha_available
        * p_local_wind_onshore.area_ha_available_pct_of_action
    )
    p_local_biomass.energy_installable = (
        p_local_biomass.power_installable
        * p_local_biomass.full_load_hour
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )

    p_local_hydro.energy = (
        p_local_hydro.power_installed
        * p_local_hydro.full_load_hour
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    g.invest_pa_outside = g_grid_offshore.invest_pa_outside
    d_h.change_energy_pct = div(d_h.change_energy_MWh, e18.d_h.energy)  # todo div0
    d_r.change_energy_pct = div(d_r.change_energy_MWh, e18.d_r.energy)  # todo
    d_b.change_energy_pct = div(d_b.change_energy_MWh, e18.d_b.energy)  # todo
    d_i.change_energy_pct = div(d_i.change_energy_MWh, e18.d_i.energy)
    d_t.change_energy_pct = div(d_t.change_energy_MWh, e18.d_t.energy)
    d_a.change_energy_pct = div(d_a.change_energy_MWh, e18.d_a.energy)  # Todo
    p_renew_reverse.cost_mro = (
        p_renew_reverse.energy * p_renew_reverse.cost_mro_per_MWh / MILLION
    )
    p_renew_reverse.CO2e_combustion_based = (
        p_renew_reverse.energy * p_renew_reverse.CO2e_combustion_based_per_MWh
    )
    p_renew_reverse.change_energy_MWh = p_renew_reverse.energy
    d.change_energy_MWh = d.energy - e18.d.energy
    d_h.pct_energy = div(d_h.energy, d.energy)
    d_r.pct_energy = div(d_r.energy, d.energy)
    d_b.pct_energy = div(d_b.energy, d.energy)
    d_i.pct_energy = div(d_i.energy, d.energy)
    d_t.pct_energy = div(d_t.energy, d.energy)
    d_a.pct_energy = div(d_a.energy, d.energy)
    d_f_wo_hydrogen.pct_energy = div(d_f_wo_hydrogen.energy, d.energy)
    d_f_hydrogen_reconv.pct_energy = div(d_f_hydrogen_reconv.energy, d.energy)
    p_fossil_nuclear.change_energy_pct = div(
        p_fossil_nuclear.change_energy_MWh, e18.p_fossil_nuclear.energy
    )
    p_fossil_nuclear.change_CO2e_t = (
        e18.p_fossil_nuclear.CO2e_combustion_based_per_MWh
        * p_fossil_nuclear.change_energy_MWh
        * fact("Fact_E_P_ratio_gross_electricity_prod_to_fec_electricity_2018")
    )
    p_fossil_coal_brown.change_energy_pct = div(
        p_fossil_coal_brown.change_energy_MWh, e18.p_fossil_coal_brown.energy
    )
    p_fossil_coal_black.change_energy_pct = div(
        p_fossil_coal_black.change_energy_MWh, e18.p_fossil_coal_black.energy
    )
    p_fossil_gas.change_energy_pct = div(
        p_fossil_gas.change_energy_MWh, e18.p_fossil_gas.energy
    )
    p_fossil.change_energy_MWh = p_fossil.energy - e18.p_fossil.energy
    p_fossil_ofossil.change_energy_pct = div(
        p_fossil_ofossil.change_energy_MWh, e18.p_fossil_ofossil.energy
    )
    p_fossil_nuclear.change_cost_energy = (
        p_fossil_nuclear.cost_fuel - e18.p_fossil_nuclear.cost_fuel
    )
    p_fossil_nuclear.change_cost_mro = (
        p_fossil_nuclear.cost_mro - e18.p_fossil_nuclear.cost_mro
    )
    p_fossil_nuclear.cost_climate_saved = (
        (
            p_fossil_nuclear.CO2e_total_2021_estimated
            - p_fossil_nuclear.CO2e_combustion_based
        )
        * KlimaneutraleJahre
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_fossil_coal_brown.change_cost_energy = (
        p_fossil_coal_brown.cost_fuel - e18.p_fossil_coal_brown.cost_fuel
    )
    p_fossil_coal_brown.change_cost_mro = (
        p_fossil_coal_brown.cost_mro - e18.p_fossil_coal_brown.cost_mro
    )
    p_fossil_coal_brown.CO2e_total = p_fossil_coal_brown.CO2e_combustion_based
    p_fossil_coal_brown.cost_climate_saved = (
        (
            p_fossil_coal_brown.CO2e_total_2021_estimated
            - p_fossil_coal_brown.CO2e_combustion_based
        )
        * KlimaneutraleJahre
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_fossil_coal_black.change_cost_energy = (
        p_fossil_coal_black.cost_fuel - e18.p_fossil_coal_black.cost_fuel
    )
    p_fossil_coal_black.change_cost_mro = (
        p_fossil_coal_black.cost_mro - e18.p_fossil_coal_black.cost_mro
    )
    p_fossil_coal_black.CO2e_total = p_fossil_coal_black.CO2e_combustion_based
    p_fossil_coal_black.cost_climate_saved = (
        (
            p_fossil_coal_black.CO2e_total_2021_estimated
            - p_fossil_coal_black.CO2e_combustion_based
        )
        * KlimaneutraleJahre
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_fossil_gas.change_cost_energy = (
        p_fossil_gas.cost_fuel - e18.p_fossil_gas.cost_fuel
    )
    p_fossil_gas.change_cost_mro = p_fossil_gas.cost_mro - e18.p_fossil_gas.cost_mro
    p_fossil_gas.CO2e_total = p_fossil_gas.CO2e_combustion_based
    p_fossil_gas.cost_climate_saved = (
        (p_fossil_gas.CO2e_total_2021_estimated - p_fossil_gas.CO2e_combustion_based)
        * KlimaneutraleJahre
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_fossil.cost_fuel = (
        p_fossil_nuclear.cost_fuel
        + p_fossil_coal_brown.cost_fuel
        + p_fossil_coal_black.cost_fuel
        + p_fossil_gas.cost_fuel
        + p_fossil_ofossil.cost_fuel
    )
    p_fossil_ofossil.change_cost_energy = (
        p_fossil_ofossil.cost_fuel - e18.p_fossil_ofossil.cost_fuel
    )
    p_fossil.cost_mro = (
        p_fossil_nuclear.cost_mro
        + p_fossil_coal_brown.cost_mro
        + p_fossil_gas.cost_mro
        + p_fossil_ofossil.cost_mro
    )
    p_fossil_ofossil.change_cost_mro = (
        p_fossil_ofossil.cost_mro - e18.p_fossil_ofossil.cost_mro
    )
    p_fossil.CO2e_combustion_based = (
        p_fossil_nuclear.CO2e_combustion_based
        + p_fossil_coal_brown.CO2e_combustion_based
        + p_fossil_coal_black.CO2e_combustion_based
        + p_fossil_gas.CO2e_combustion_based
        + p_fossil_ofossil.CO2e_combustion_based
    )
    p_fossil_ofossil.CO2e_total = p_fossil_ofossil.CO2e_combustion_based
    p_fossil_ofossil.cost_climate_saved = (
        (
            p_fossil_ofossil.CO2e_total_2021_estimated
            - p_fossil_ofossil.CO2e_combustion_based
        )
        * KlimaneutraleJahre
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_fossil_and_renew.CO2e_total_2021_estimated = (
        p_fossil.CO2e_total_2021_estimated + p_renew.CO2e_total_2021_estimated
    )
    p_renew_pv_roof.change_energy_MWh = (
        p_renew_pv_roof.energy - e18.p_renew_pv_roof.energy
    )
    p_renew_pv_roof.cost_mro = (
        p_renew_pv_roof.energy * p_renew_pv_roof.cost_mro_per_MWh / MILLION
    )
    p_renew_pv_park.cost_mro_per_MWh = (
        ass("Ass_E_S_local_pv_park_ratio_invest_to_power_2020")
        * ass("Ass_E_P_local_pv_park_mro_per_year")
        / p_local_pv_park.full_load_hour
        * 1000
    )
    p_local_pv_park.cost_mro_per_MWh = (
        ass("Ass_E_S_local_pv_park_ratio_invest_to_power_2030")
        * ass("Ass_E_P_local_pv_park_mro_per_year")
        / p_local_pv_park.full_load_hour
        * 1000
    )
    p_local_pv_agri.cost_mro_per_MWh = (
        ass("Ass_E_P_local_pv_agri_ratio_invest_to_power")
        * ass("Ass_E_P_local_pv_agri_mro_per_year")
        / p_local_pv_park.full_load_hour
        * 1000
    )
    p_renew_pv_agri.cost_mro_per_MWh = (
        ass("Ass_E_P_local_pv_agri_ratio_invest_to_power")
        * ass("Ass_E_P_local_pv_roof_mro_per_year")
        / p_local_pv_agri.full_load_hour
        * 1000
    )
    p_renew_pv_facade.change_energy_MWh = (
        p_renew_pv_facade.energy - e18.p_renew_pv_facade.energy
    )
    p_renew_pv_facade.cost_mro = (
        p_renew_pv_facade.energy * p_renew_pv_facade.cost_mro_per_MWh / MILLION
    )
    p_renew_pv_park.change_energy_MWh = (
        p_renew_pv_park.energy - e18.p_renew_pv_park.energy
    )
    p_renew_pv_agri.change_energy_MWh = (
        p_renew_pv_agri.energy - e18.p_renew_pv_agri.energy
    )
    p_renew.invest_pa_outside = (
        p_renew_wind.invest_pa_outside
        + p_renew_geoth.invest_pa_outside
        + p_renew_reverse.invest_pa_outside
    )
    p_renew.invest_outside = (
        p_renew_wind.invest_outside
        + p_renew_geoth.invest_outside
        + p_renew_reverse.invest_outside
    )
    g_grid_offshore.power_to_be_installed = p_renew_wind_offshore.power_to_be_installed
    p_renew_wind_offshore.energy = (
        (
            p_renew_wind_offshore.power_to_be_installed
            + p_renew_wind_offshore.power_installed
        )
        * p_renew_wind_offshore.full_load_hour
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_renew_wind_offshore.invest = (
        p_renew_wind_offshore.power_to_be_installed * p_renew_wind_offshore.invest_per_x
    )
    p_renew_geoth.energy = (
        (p_renew_geoth.power_to_be_installed + p_renew_geoth.power_installed)
        * p_renew_geoth.full_load_hour
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_renew_geoth.invest = (
        p_renew_geoth.power_to_be_installed * p_renew_geoth.invest_per_x
    )
    p_renew_reverse.invest = (
        p_renew_reverse.power_to_be_installed * p_renew_reverse.invest_per_x
    )
    p_local_pv_roof.power_to_be_installed = max(
        0,
        p_local_pv_roof.power_installable * p_local_pv_roof.power_to_be_installed_pct
        - p_local_pv_roof.power_installed,
    )
    p_local_pv_roof.energy_installable = (
        p_local_pv_roof.power_installable
        * p_local_pv_roof.full_load_hour
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_local_pv_facade.power_to_be_installed = max(
        0,
        p_local_pv_facade.power_installable
        * p_local_pv_facade.power_to_be_installed_pct
        - p_local_pv_facade.power_installed,
    )
    p_local_pv_facade.energy_installable = (
        p_local_pv_facade.full_load_hour
        * p_local_pv_facade.power_installable
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_local_pv_park.power_to_be_installed = max(
        0,
        p_local_pv_park.power_installable * p_local_pv_park.power_to_be_installed_pct
        - p_local_pv_park.power_installed,
    )
    p_local_pv_park.energy_installable = (
        p_local_pv_park.full_load_hour
        * p_local_pv_park.power_installable
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_local_pv.power_installable = (
        p_local_pv_roof.power_installable
        + p_local_pv_facade.power_installable
        + p_local_pv_park.power_installable
        + p_local_pv_agri.power_installable
    )
    p_local_pv_agri.energy_installable = (
        p_local_pv_agri.full_load_hour
        * p_local_pv_agri.power_installable
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_local_wind_onshore.power_to_be_installed = max(
        0,
        p_local_wind_onshore.power_installable
        * p_local_wind_onshore.power_to_be_installed_pct
        - p_local_wind_onshore.power_installed,
    )
    p_local_wind_onshore.energy_installable = (
        p_local_wind_onshore.full_load_hour
        * p_local_wind_onshore.power_installable
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_local_biomass.invest = (
        p_local_biomass.power_to_be_installed * p_local_biomass.invest_per_x
    )
    p_local_hydro.cost_mro = (
        p_local_hydro.energy * p_local_hydro.cost_mro_per_MWh / MILLION
    )
    p_local_hydro.CO2e_combustion_based = (
        p_local_hydro.energy * p_local_hydro.CO2e_combustion_based_per_MWh
    )
    p_local_hydro.CO2e_total = p_local_hydro.CO2e_combustion_based
    p_local_hydro.change_energy_MWh = p_local_hydro.energy - e18.p_local_hydro.energy
    p_renew_reverse.change_cost_mro = p_renew_reverse.cost_mro - 0
    d.change_energy_pct = div(d.change_energy_MWh, e18.d.energy)
    d.pct_energy = (
        d_h.pct_energy
        + d_r.pct_energy
        + d_b.pct_energy
        + d_i.pct_energy
        + d_t.pct_energy
        + d_a.pct_energy
        + d_f_wo_hydrogen.pct_energy
        + d_f_hydrogen_reconv.pct_energy
    )
    p_fossil.change_energy_pct = div(p_fossil.change_energy_MWh, e18.p_fossil.energy)
    p_fossil_coal_brown.change_CO2e_t = (
        p_fossil_coal_brown.CO2e_total - e18.p_fossil_coal_brown.CO2e_total
    )
    p_fossil_coal_black.change_CO2e_t = (
        p_fossil_coal_black.CO2e_total - e18.p_fossil_coal_black.CO2e_total
    )
    p_fossil_gas.change_CO2e_t = p_fossil_gas.CO2e_total - e18.p_fossil_gas.CO2e_total
    p_fossil.change_cost_energy = (
        p_fossil_nuclear.change_cost_energy
        + p_fossil_coal_brown.change_cost_energy
        + p_fossil_coal_black.change_cost_energy
        + p_fossil_gas.change_cost_energy
        + p_fossil_ofossil.change_cost_energy
    )
    p_fossil.change_cost_mro = (
        p_fossil_nuclear.change_cost_energy
        + p_fossil_coal_brown.change_cost_mro
        + p_fossil_coal_black.change_cost_mro
        + p_fossil_gas.change_cost_mro
        + p_fossil_ofossil.change_cost_mro
    )
    p_fossil_ofossil.change_CO2e_t = (
        p_fossil_ofossil.CO2e_total - e18.p_fossil_ofossil.CO2e_total
    )
    p_fossil.cost_climate_saved = (
        p_fossil_coal_brown.cost_climate_saved
        + p_fossil_coal_black.cost_climate_saved
        + p_fossil_gas.cost_climate_saved
        + p_fossil_ofossil.cost_climate_saved
    )
    p.CO2e_total_2021_estimated = (
        p_fossil_and_renew.CO2e_total_2021_estimated + p_local.CO2e_total_2021_estimated
    )
    p_renew_pv_roof.change_energy_pct = div(
        p_renew_pv_roof.change_energy_MWh, e18.p_renew_pv_roof.energy
    )
    p_renew_pv_roof.change_cost_mro = (
        p_renew_pv_roof.cost_mro - e18.p_renew_pv_roof.cost_mro
    )
    p_renew_pv_park.cost_mro = (
        p_renew_pv_park.energy * p_renew_pv_park.cost_mro_per_MWh / MILLION
    )
    p_renew_pv_agri.cost_mro = (
        p_renew_pv_agri.energy * p_renew_pv_agri.cost_mro_per_MWh / MILLION
    )
    p_renew_pv_facade.change_energy_pct = div(
        p_renew_pv_facade.change_energy_MWh, e18.p_renew_pv_facade.energy
    )
    p_renew_pv_facade.change_cost_mro = (
        p_renew_pv_facade.cost_mro - e18.p_renew_pv_facade.cost_mro
    )
    p_renew_pv_park.change_energy_pct = div(
        p_renew_pv_park.change_energy_MWh, e18.p_renew_pv_park.energy
    )
    p_renew_pv.change_energy_MWh = (
        p_renew_pv_roof.change_energy_MWh
        + p_renew_pv_facade.change_energy_MWh
        + p_renew_pv_park.change_energy_MWh
        + p_renew_pv_agri.change_energy_MWh
    )
    p_renew_pv_agri.change_energy_pct = div(
        p_renew_pv_agri.change_energy_MWh, e18.p_renew_pv_agri.energy
    )
    p_fossil_and_renew.invest_pa_outside = p_renew.invest_pa_outside
    p_fossil_and_renew.invest_outside = p_renew.invest_outside
    g_grid_offshore.invest = (
        g_grid_offshore.power_to_be_installed * g_grid_offshore.invest_per_x
    )
    p_renew_wind_offshore.cost_mro = (
        p_renew_wind_offshore.energy * p_renew_wind_offshore.cost_mro_per_MWh / MILLION
    )
    p_renew_wind_offshore.change_energy_MWh = (
        p_renew_wind_offshore.energy - e18.p_renew_wind_offshore.energy
    )
    p_renew_wind.invest = p_renew_wind_offshore.invest
    p_renew_wind_offshore.invest_pa = (
        p_renew_wind_offshore.invest / Kalkulationszeitraum
    )
    p_renew.energy = (
        p_renew_wind_offshore.energy + p_renew_geoth.energy + p_renew_reverse.energy
    )
    p_renew_geoth.cost_mro = (
        p_renew_geoth.energy * p_renew_geoth.cost_mro_per_MWh / MILLION
    )
    p_renew_geoth.CO2e_combustion_based = (
        p_renew_geoth.energy * p_renew_geoth.CO2e_combustion_based_per_MWh
    )
    p_renew_geoth.change_energy_MWh = p_renew_geoth.energy - e18.p_renew_geoth.energy
    p_renew_geoth.invest_pa = p_renew_geoth.invest / Kalkulationszeitraum
    p_renew_reverse.invest_pa = p_renew_reverse.invest / Kalkulationszeitraum
    p_local_pv_roof.energy = (
        (p_local_pv_roof.power_to_be_installed + p_local_pv_roof.power_installed)
        * p_local_pv_roof.full_load_hour
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_local_pv_roof.invest = (
        p_local_pv_roof.power_to_be_installed * p_local_pv_roof.invest_per_x
    )
    p_local_pv_facade.energy = (
        (p_local_pv_facade.power_to_be_installed + p_local_pv_facade.power_installed)
        * p_local_pv_facade.full_load_hour
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_local_pv_facade.invest = (
        p_local_pv_facade.power_to_be_installed * p_local_pv_facade.invest_per_x
    )
    p_local_pv_park.energy = (
        (p_local_pv_park.power_to_be_installed + p_local_pv_park.power_installed)
        * p_local_pv_park.full_load_hour
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_local_pv_park.invest = (
        p_local_pv_park.power_to_be_installed * p_local_pv_park.invest_per_x
    )
    p_local_pv.energy_installable = (
        p_local_pv_roof.energy_installable
        + p_local_pv_facade.energy_installable
        + p_local_pv_park.energy_installable
        + p_local_pv_agri.energy_installable
    )
    g_grid_onshore.power_to_be_installed = p_local_wind_onshore.power_to_be_installed
    p_local_wind_onshore.energy = (
        (
            p_local_wind_onshore.power_to_be_installed
            + p_local_wind_onshore.power_installed
        )
        * p_local_wind_onshore.full_load_hour
        * (1 - ass("Ass_E_P_renew_loss_brutto_to_netto"))
    )
    p_local_wind_onshore.invest = (
        p_local_wind_onshore.power_to_be_installed * p_local_wind_onshore.invest_per_x
    )
    p_local_biomass.cost_fuel = (
        p_local_biomass.cost_fuel_per_MWh * p_local_biomass.energy / MILLION
    )
    p_local_biomass.cost_mro = (
        p_local_biomass.energy * p_local_biomass.cost_mro_per_MWh / MILLION
    )
    p_local_biomass.CO2e_combustion_based = (
        p_local_biomass.energy * p_local_biomass.CO2e_combustion_based_per_MWh
    )
    p_local_biomass.change_energy_MWh = (
        p_local_biomass.energy - e18.p_local_biomass.energy
    )
    p_local_biomass.invest_pa = p_local_biomass.invest / Kalkulationszeitraum
    p_fossil.change_CO2e_t = (
        p_fossil_nuclear.change_CO2e_t
        + p_fossil_coal_brown.change_CO2e_t
        + p_fossil_coal_black.change_CO2e_t
        + p_fossil_gas.change_CO2e_t
        + p_fossil_ofossil.change_CO2e_t
    )
    e.CO2e_total_2021_estimated = p.CO2e_total_2021_estimated
    p_renew_pv_park.change_cost_mro = (
        p_renew_pv_park.cost_mro - e18.p_renew_pv_park.cost_mro
    )
    p_renew_pv.cost_mro = (
        p_renew_pv_roof.cost_mro
        + p_renew_pv_facade.cost_mro
        + p_renew_pv_park.cost_mro
        + p_renew_pv_agri.cost_mro
    )  #
    p_renew_pv_agri.change_cost_mro = (
        p_renew_pv_agri.cost_mro - e18.p_renew_pv_agri.cost_mro
    )
    p_renew_pv.change_energy_pct = div(
        p_renew_pv.change_energy_MWh, e18.p_renew_pv.energy
    )
    p.invest_pa_outside = p_fossil_and_renew.invest_pa_outside
    p.invest_outside = p_fossil_and_renew.invest_outside
    g_grid_offshore.cost_mro = (
        g_grid_offshore.invest * ass("Ass_E_G_grid_offshore_mro") / MILLION
    )
    g_grid_offshore.invest_pa = g_grid_offshore.invest / entries.m_duration_target
    p_renew_wind_offshore.change_cost_mro = (
        p_renew_wind_offshore.cost_mro - e18.p_renew_wind_offshore.cost_mro
    )
    p_renew_wind_offshore.change_energy_pct = div(
        p_renew_wind_offshore.change_energy_MWh, e18.p_renew_wind_offshore.energy
    )
    p_renew.invest = p_renew_wind.invest + p_renew_geoth.invest + p_renew_reverse.invest
    p_renew_wind.invest_pa = p_renew_wind_offshore.invest_pa
    p_renew_wind_offshore.cost_wage = (
        p_renew_wind_offshore.invest_pa
        * p_renew_wind_offshore.pct_of_wage
        / Kalkulationszeitraum
    )
    p_fossil_and_renew.energy = p_renew.energy
    p_renew.change_energy_MWh = p_renew.energy - e18.p_renew.energy
    p_renew_wind_onshore.energy = p_renew.energy * p_renew_wind_onshore.pct_energy
    p_renew_biomass.energy = p_renew.energy * p_renew_biomass.pct_energy
    p_renew_geoth.pct_energy = div(p_renew_geoth.energy, p_renew.energy)
    p_renew_hydro.energy = p_renew.energy * p_renew_hydro.pct_energy
    p_renew_reverse.pct_energy = div(p_renew_reverse.energy, p_renew.energy)
    p_renew_geoth.change_cost_mro = p_renew_geoth.cost_mro - e18.p_renew_geoth.cost_mro
    p_renew_geoth.change_energy_pct = div(
        p_renew_geoth.change_energy_MWh, e18.p_renew_geoth.energy
    )
    p_renew_geoth.cost_wage = p_renew_geoth.invest_pa * p_renew_geoth.pct_of_wage
    p_renew_reverse.cost_wage = p_renew_reverse.invest_pa * p_renew_reverse.pct_of_wage

    p_local_pv_roof.cost_mro = (
        p_local_pv_roof.energy * p_local_pv_roof.cost_mro_per_MWh / MILLION
    )
    p_local_pv_roof.change_energy_MWh = (
        p_local_pv_roof.energy - e18.p_local_pv_roof.energy
    )
    p_local_pv_roof.invest_pa = p_local_pv_roof.invest / Kalkulationszeitraum
    p_local_pv_roof.invest_com = (
        p_local_pv_roof.invest
        * (r18.p_buildings_area_m2_com.area_m2 + b18.p_nonresi_com.area_m2)
        / (b18.p_nonresi.area_m2 + r18.p_buildings_total.area_m2)
    )
    p_local_pv_facade.cost_mro = (
        p_local_pv_facade.energy * p_local_pv_facade.cost_mro_per_MWh / MILLION
    )
    p_local_pv_facade.change_energy_MWh = (
        p_local_pv_facade.energy - e18.p_local_pv_facade.energy
    )
    p_local_pv_facade.invest_pa = p_local_pv_facade.invest / Kalkulationszeitraum
    p_local_pv_facade.invest_com = (
        p_local_pv_facade.invest
        * (r18.p_buildings_area_m2_com.area_m2 + b18.p_nonresi_com.area_m2)
        / (b18.p_nonresi.area_m2 + r18.p_buildings_total.area_m2)
    )
    p_local_pv_park.cost_mro = (
        p_local_pv_park.energy * p_local_pv_park.cost_mro_per_MWh / MILLION
    )
    p_local_pv_park.change_energy_MWh = (
        p_local_pv_park.energy - e18.p_local_pv_park.energy
    )
    p_local_pv_park.invest_pa = p_local_pv_park.invest / Kalkulationszeitraum
    g_grid_onshore.invest = (
        g_grid_onshore.power_to_be_installed * g_grid_onshore.invest_per_x
    )
    p_local_pv_agri.energy = max(
        0,
        d.energy
        - (
            p_local_pv_roof.energy
            + p_local_pv_facade.energy
            + p_local_pv_park.energy
            + p_local_wind_onshore.energy
            + p_local_biomass.energy
            + p_local_hydro.energy
            + p_renew.energy
        ),
    )
    p_local_wind_onshore.cost_mro = (
        p_local_wind_onshore.energy * p_local_wind_onshore.cost_mro_per_MWh / MILLION
    )
    p_local_wind_onshore.CO2e_combustion_based = (
        p_local_wind_onshore.energy * p_local_wind_onshore.CO2e_combustion_based_per_MWh
    )
    p_local_wind_onshore.change_energy_MWh = (
        p_local_wind_onshore.energy - e18.p_local_wind_onshore.energy
    )
    p_local_wind_onshore.invest_pa = p_local_wind_onshore.invest / Kalkulationszeitraum
    p_local.cost_fuel = p_local_biomass.cost_fuel
    p_local_biomass.change_cost_energy = (
        p_local_biomass.cost_fuel - e18.p_local_biomass.cost_fuel
    )
    p_local_biomass.change_cost_mro = (
        p_local_biomass.cost_mro - e18.p_local_biomass.cost_mro
    )
    p_local_biomass.CO2e_total = p_local_biomass.CO2e_combustion_based
    p_local_biomass.cost_climate_saved = (
        (
            p_local_biomass.CO2e_total_2021_estimated
            - p_local_biomass.CO2e_combustion_based
        )
        * KlimaneutraleJahre
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_local_biomass.cost_wage = (
        p_local_biomass.invest_pa * p_local_biomass.pct_of_wage / Kalkulationszeitraum
    )  # ratio_wage_to_emplo
    p_renew_pv.change_cost_mro = (
        p_renew_pv_roof.change_cost_mro
        + p_renew_pv_facade.change_cost_mro
        + p_renew_pv_park.change_cost_mro
        + p_renew_pv_agri.change_cost_mro
    )
    e.invest_pa_outside = g.invest_pa_outside + p.invest_pa_outside
    e.invest_outside = g.invest_outside + p.invest_outside
    g_grid_offshore.cost_wage = g_grid_offshore.invest_pa * g_grid_offshore.pct_of_wage
    p_fossil_and_renew.invest = p_renew.invest
    p_renew.invest_pa = (
        p_renew_wind.invest_pa + p_renew_geoth.invest_pa + p_renew_reverse.invest_pa
    )
    p_renew_wind.cost_wage = p_renew_wind_offshore.cost_wage
    p_renew_wind_offshore.demand_emplo = div(
        p_renew_wind_offshore.cost_wage,
        p_renew_wind_offshore.ratio_wage_to_emplo,
    )
    p_fossil_and_renew.change_energy_MWh = (
        p_fossil_and_renew.energy - e18.p_fossil_and_renew.energy
    )  # change_energy_pct
    p_renew.change_energy_pct = div(p_renew.change_energy_MWh, e18.p_renew.energy)
    p_renew_wind.energy = p_renew_wind_onshore.energy + p_renew_wind_offshore.energy
    p_renew_wind_onshore.cost_mro = (
        p_renew_wind_onshore.energy * p_renew_wind_onshore.cost_mro_per_MWh / MILLION
    )
    p_renew_wind_onshore.change_energy_MWh = (
        p_renew_wind_onshore.energy - e18.p_renew_wind_onshore.energy
    )
    p_renew_biomass.cost_fuel = (
        p_renew_biomass.energy * p_renew_biomass.cost_fuel_per_MWh / MILLION
    )
    p_renew_biomass.cost_mro = (
        p_renew_biomass.energy * p_renew_biomass.cost_mro_per_MWh / MILLION
    )
    p_renew_biomass.CO2e_combustion_based = (
        p_renew_biomass.energy * p_renew_biomass.CO2e_combustion_based_per_MWh
    )
    p_renew_hydro.cost_mro = (
        p_renew_hydro.energy * p_renew_hydro.cost_mro_per_MWh / MILLION
    )
    p_renew_hydro.CO2e_combustion_based = (
        p_renew_hydro.energy * p_renew_hydro.CO2e_combustion_based_per_MWh
    )
    p_renew_hydro.change_energy_MWh = p_renew_hydro.energy - e18.p_renew_hydro.energy
    p_renew_geoth.demand_emplo = div(
        p_renew_geoth.cost_wage, p_renew_geoth.ratio_wage_to_emplo
    )
    p_renew_reverse.demand_emplo = div(
        p_renew_reverse.cost_wage, p_renew_reverse.ratio_wage_to_emplo
    )
    p_local_pv_roof.change_cost_mro = (
        p_local_pv_roof.cost_mro - e18.p_local_pv_roof.cost_mro
    )
    p_local_pv_roof.change_energy_pct = div(
        p_local_pv_roof.change_energy_MWh, e18.p_local_pv_roof.energy
    )
    p_local_pv_roof.cost_wage = p_local_pv_roof.invest_pa * p_local_pv_roof.pct_of_wage
    p_local_pv_roof.invest_pa_com = p_local_pv_roof.invest_com / Kalkulationszeitraum
    p_local_pv_facade.change_cost_mro = (
        p_local_pv_facade.cost_mro - e18.p_local_pv_facade.cost_mro
    )
    p_local_pv_facade.change_energy_pct = div(
        p_local_pv_facade.change_energy_MWh, e18.p_local_pv_facade.energy
    )
    p_local_pv_facade.cost_wage = (
        p_local_pv_facade.invest_pa * p_local_pv_facade.pct_of_wage
    )
    p_local_pv.invest_com = p_local_pv_roof.invest_com + p_local_pv_facade.invest_com
    p_local_pv_facade.invest_pa_com = (
        p_local_pv_facade.invest_com / Kalkulationszeitraum
    )
    p_local_pv_park.change_cost_mro = (
        p_local_pv_park.cost_mro - e18.p_local_pv_park.cost_mro
    )
    p_local_pv_park.change_energy_pct = div(
        p_local_pv_park.change_energy_MWh, e18.p_local_pv_park.energy
    )
    p_local_pv_park.cost_wage = p_local_pv_park.invest_pa * p_local_pv_park.pct_of_wage
    g_grid_onshore.cost_mro = (
        g_grid_onshore.invest * ass("Ass_E_G_grid_onshore_mro") / MILLION
    )
    g_grid_onshore.invest_pa = g_grid_onshore.invest / entries.m_duration_target
    p_local_pv.energy = (
        p_local_pv_roof.energy
        + p_local_pv_facade.energy
        + p_local_pv_park.energy
        + p_local_pv_agri.energy
    )  #
    p_local_pv_agri.cost_mro = (
        p_local_pv_agri.energy * p_local_pv_agri.cost_mro_per_MWh / MILLION
    )
    p_local_pv_agri.change_energy_MWh = (
        p_local_pv_agri.energy - e18.p_local_pv_agri.energy
    )
    p_local_pv_agri.power_to_be_installed_pct = div(
        p_local_pv_agri.energy, p_local_pv_agri.energy_installable
    )
    p_local_wind_onshore.change_cost_mro = (
        p_local_wind_onshore.cost_mro - e18.p_local_wind_onshore.cost_mro
    )
    p_local_wind_onshore.change_energy_pct = div(
        p_local_wind_onshore.change_energy_MWh, e18.p_local_wind_onshore.energy
    )
    p_local_wind_onshore.cost_wage = (
        p_local_wind_onshore.invest_pa * p_local_wind_onshore.pct_of_wage
    )
    p_local.change_cost_energy = p_local_biomass.change_cost_energy
    p_local.change_cost_mro = p_local_biomass.change_cost_mro
    p_local_biomass.change_CO2e_t = p_local_biomass.CO2e_total - 0
    p_local.cost_climate_saved = p_local_biomass.cost_climate_saved
    p_local_biomass.demand_emplo = div(
        p_local_biomass.cost_wage, p_local_biomass.ratio_wage_to_emplo
    )
    g_grid_offshore.demand_emplo = div(
        g_grid_offshore.cost_wage, g_grid_offshore.ratio_wage_to_emplo
    )
    p_fossil_and_renew.invest_pa = p_renew.invest_pa
    p_renew.cost_wage = (
        p_renew_wind.cost_wage + p_renew_geoth.cost_wage + p_renew_reverse.cost_wage
    )
    p_renew_wind.demand_emplo = p_renew_wind_offshore.demand_emplo
    p_renew_wind_offshore.demand_emplo_new = max(
        0, p_renew_wind_offshore.demand_emplo - p_renew_wind_offshore.emplo_existing
    )
    p_fossil_and_renew.change_energy_pct = div(
        p_fossil_and_renew.change_energy_MWh, e18.p_fossil_and_renew.energy
    )
    p_renew_wind.pct_energy = div(p_renew_wind.energy, p_renew.energy)
    p_renew_wind.CO2e_combustion_based = (
        p_renew_wind.energy * p_renew_wind.CO2e_combustion_based_per_MWh
    )
    p_renew_wind_offshore.pct_energy = div(
        p_renew_wind_offshore.energy, p_renew_wind.energy
    )
    p_renew_wind.cost_mro = (
        p_renew_wind_onshore.cost_mro + p_renew_wind_offshore.cost_mro
    )
    p_renew_wind_onshore.change_cost_mro = (
        p_renew_wind_onshore.cost_mro - e18.p_renew_wind_onshore.cost_mro
    )
    p_renew_wind.change_energy_MWh = (
        p_renew_wind_onshore.change_energy_MWh + p_renew_wind_offshore.change_energy_MWh
    )
    p_renew_wind_onshore.change_energy_pct = div(
        p_renew_wind_onshore.change_energy_MWh, e18.p_renew_wind_onshore.energy
    )
    p_renew.cost_fuel = p_renew_biomass.cost_fuel
    p_renew_biomass.change_cost_energy = (
        p_renew_biomass.cost_fuel - e18.p_renew_biomass.cost_fuel
    )
    p_renew_biomass.change_cost_mro = (
        p_renew_biomass.cost_mro - e18.p_renew_biomass.cost_mro
    )
    p_renew_biomass.CO2e_total = p_renew_biomass.CO2e_combustion_based
    p_renew_biomass.cost_climate_saved = (
        (
            p_renew_biomass.CO2e_total_2021_estimated
            - p_renew_biomass.CO2e_combustion_based
        )
        * KlimaneutraleJahre
        * fact("Fact_M_cost_per_CO2e_2020")
    )
    p_renew_hydro.change_cost_mro = p_renew_hydro.cost_mro - e18.p_renew_hydro.cost_mro
    p_renew_hydro.change_energy_pct = div(
        p_renew_hydro.change_energy_MWh, e18.p_renew_hydro.energy
    )
    p_renew_geoth.emplo_existing = (
        fact("Fact_E_P_plant_construct_emplo_2018")
        * p_renew_geoth.demand_emplo
        / (p_renew_geoth.demand_emplo + p_renew_reverse.demand_emplo)
    )
    p_renew_reverse.emplo_existing = (
        fact("Fact_E_P_plant_construct_emplo_2018")
        * p_renew_reverse.demand_emplo
        / (p_renew_geoth.demand_emplo + p_renew_reverse.demand_emplo)
    )
    p_renew_reverse.demand_emplo_new = p_renew_reverse.demand_emplo
    p_local_pv_roof.demand_emplo = div(
        p_local_pv_roof.cost_wage, p_local_pv_roof.ratio_wage_to_emplo
    )
    p_local_pv_facade.demand_emplo = div(
        p_local_pv_facade.cost_wage, p_local_pv_facade.ratio_wage_to_emplo
    )
    p_local.invest_com = p_local_pv.invest_com
    p_local_pv_park.invest_pa_com = 0
    p_local_pv_agri.invest_pa_com = 0
    p_local.invest_pa_com = (
        p_local_pv_roof.invest_pa_com
        + p_local_pv_facade.invest_pa_com
        + p_local_pv_park.invest_pa_com
        + p_local_pv_agri.invest_pa_com
    )  #
    p_local_pv.invest_pa_com = (
        p_local_pv_roof.invest_pa_com
        + p_local_pv_facade.invest_pa_com
        + p_local_pv_park.invest_pa_com
        + p_local_pv_agri.invest_pa_com
    )  #
    p_local_pv_park.demand_emplo = div(
        p_local_pv_park.cost_wage, p_local_pv_park.ratio_wage_to_emplo
    )
    g_grid_onshore.cost_wage = g_grid_onshore.invest_pa * g_grid_onshore.pct_of_wage
    p_local.energy = (
        p_local_pv.energy
        + p_local_wind_onshore.energy
        + p_local_biomass.energy
        + p_local_hydro.energy
    )
    p_local_pv.CO2e_combustion_based = (
        p_local_pv.energy * p_local_pv.CO2e_combustion_based_per_MWh
    )
    p_local_pv.CO2e_total = p_local_pv.CO2e_combustion_based
    p_local_pv.change_CO2e_t = p_local_pv.CO2e_total - e18.p_local_pv.CO2e_total
    p_local_pv.change_energy_MWh = p_local_pv.energy - e18.p_local_pv.energy
    p_local_pv_roof.pct_energy = div(p_local_pv_roof.energy, p_local_pv.energy)
    p_local_pv_roof.pet_sites = div(p_local_pv_roof.energy, p_local_pv.energy)
    p_local_pv_facade.pct_energy = div(p_local_pv_facade.energy, p_local_pv.energy)
    p_local_pv_facade.pet_sites = div(p_local_pv_facade.energy, p_local_pv.energy)
    p_local_pv_park.pct_energy = div(p_local_pv_park.energy, p_local_pv.energy)
    p_local_pv_park.pet_sites = div(p_local_pv_park.energy, p_local_pv.energy)
    p_local_pv_agri.pct_energy = div(p_local_pv_agri.energy, p_local_pv.energy)
    p_local_pv_agri.pet_sites = div(p_local_pv_agri.energy, p_local_pv.energy)
    p_local_pv.cost_mro = (
        p_local_pv_roof.cost_mro
        + p_local_pv_facade.cost_mro
        + p_local_pv_park.cost_mro
        + p_local_pv_agri.cost_mro
    )  #
    p_local_pv_agri.change_cost_mro = (
        p_local_pv_agri.cost_mro - e18.p_local_pv_agri.cost_mro
    )
    p_local_pv_agri.change_energy_pct = div(
        p_local_pv_agri.change_energy_MWh, e18.p_local_pv_agri.energy
    )
    p_local_pv_agri.power_to_be_installed = max(
        0,
        p_local_pv_agri.power_installable * p_local_pv_agri.power_to_be_installed_pct
        - p_local_pv_agri.power_installed,
    )
    p_local_wind_onshore.demand_emplo = div(
        p_local_wind_onshore.cost_wage, p_local_wind_onshore.ratio_wage_to_emplo
    )
    p_local.change_CO2e_t = p_local_biomass.change_CO2e_t
    p_local_biomass.demand_emplo_new = max(
        0, p_local_biomass.demand_emplo - p_local_biomass.emplo_existing
    )
    g_grid_offshore.demand_emplo_new = g_grid_offshore.demand_emplo
    p_fossil_and_renew.cost_wage = p_renew.cost_wage
    p_renew.demand_emplo = (
        p_renew_wind.demand_emplo
        + p_renew_geoth.demand_emplo
        + p_renew_reverse.demand_emplo
    )
    p_renew_wind.demand_emplo_new = max(
        0, p_renew_wind.demand_emplo - p_renew_wind.emplo_existing
    )
    p_renew.pct_energy = (
        p_renew_pv.pct_energy
        + p_renew_wind.pct_energy
        + p_renew_biomass.pct_energy
        + p_renew_geoth.pct_energy
        + p_renew_hydro.pct_energy
        + p_renew_reverse.pct_energy
    )
    p_renew.CO2e_combustion_based = (
        p_renew_pv.CO2e_combustion_based
        + p_renew_wind.CO2e_combustion_based
        + p_renew_biomass.CO2e_combustion_based
        + p_renew_geoth.CO2e_combustion_based
        + p_renew_hydro.CO2e_combustion_based
        + p_renew_reverse.CO2e_combustion_based
    )
    p_renew.cost_mro = (
        p_renew_pv.cost_mro
        + p_renew_wind.cost_mro
        + p_renew_biomass.cost_mro
        + p_renew_geoth.cost_mro
        + p_renew_hydro.cost_mro
        + p_renew_reverse.cost_mro
    )
    p_renew_wind.change_cost_mro = p_renew_wind.cost_mro - e18.p_renew_wind.cost_mro
    p_renew_wind.change_energy_pct = div(
        p_renew_wind.change_energy_MWh, e18.p_renew_wind.energy
    )
    p_fossil_and_renew.cost_fuel = p_fossil.cost_fuel + p_renew.cost_fuel
    p_renew.change_cost_energy = p_renew_biomass.change_cost_energy
    p_renew.change_cost_mro = p_renew_biomass.change_cost_mro
    p_renew.CO2e_total = (
        p_renew_pv.CO2e_total
        + p_renew_wind.CO2e_total
        + p_renew_biomass.CO2e_total
        + p_renew_geoth.CO2e_total
        + p_renew_hydro.CO2e_total
        + p_renew_reverse.CO2e_total
    )
    p_renew_biomass.change_CO2e_t = (
        p_renew_biomass.CO2e_total - e18.p_renew_biomass.CO2e_total
    )
    p_renew.cost_climate_saved = p_renew_biomass.cost_climate_saved
    p_renew_geoth.demand_emplo_new = max(
        0, p_renew_geoth.demand_emplo - p_renew_geoth.emplo_existing
    )
    p.invest_com = p_fossil_and_renew.invest_com + p_local.invest_com
    p.invest_pa_com = p_fossil_and_renew.invest_pa_com + p_local.invest_pa_com
    g_grid_onshore.demand_emplo = div(
        g_grid_onshore.cost_wage, g_grid_onshore.ratio_wage_to_emplo
    )
    p.energy = p_fossil_and_renew.energy + p_local.energy
    p_local.change_energy_MWh = p_local.energy - e18.p_local.energy
    p_local_pv.pct_energy = div(p_local_pv.energy, p_local.energy)
    p_local_wind_onshore.pct_energy = div(p_local_wind_onshore.energy, p_local.energy)
    p_local_biomass.pct_energy = div(p_local_biomass.energy, p_local.energy)
    p_local_hydro.pct_energy = div(p_local_hydro.energy, p_local.energy)
    p_local_surplus.energy = p_local.energy - d.energy
    p_local.CO2e_combustion_based = (
        p_local_pv.CO2e_combustion_based
        + p_local_wind_onshore.CO2e_combustion_based
        + p_local_biomass.CO2e_combustion_based
        + p_local_hydro.CO2e_combustion_based
    )
    p_local_pv.change_energy_pct = div(
        p_local_pv.change_energy_MWh, e18.p_local_pv.energy
    )
    p_local.cost_mro = (
        p_local_pv.cost_mro
        + p_local_wind_onshore.cost_mro
        + p_local_biomass.cost_mro
        + p_local_hydro.cost_mro
    )
    p_local_pv.change_cost_mro = p_local_pv.cost_mro - e18.p_local_pv.cost_mro
    p_local_pv.power_to_be_installed = (
        p_local_pv_roof.power_to_be_installed
        + p_local_pv_facade.power_to_be_installed
        + p_local_pv_park.power_to_be_installed
        + p_local_pv_agri.power_to_be_installed
    )
    p_local_pv_agri.invest = (
        p_local_pv_agri.power_to_be_installed * p_local_pv_agri.invest_per_x
    )
    p_local_wind_onshore.demand_emplo_new = max(
        0, p_local_wind_onshore.demand_emplo - p_local_wind_onshore.emplo_existing
    )
    p_fossil_and_renew.demand_emplo = p_renew.demand_emplo
    p_fossil_and_renew.CO2e_combustion_based = (
        p_fossil.CO2e_combustion_based + p_renew.CO2e_combustion_based
    )
    p_renew.CO2e_combustion_based_per_MWh = div(
        p_renew.CO2e_combustion_based, p_renew.energy
    )
    p_fossil_and_renew.cost_mro = p_fossil.cost_mro + p_renew.cost_mro
    p.cost_fuel = p_fossil_and_renew.cost_fuel + p_local.cost_fuel
    p_fossil_and_renew.change_cost_energy = (
        p_fossil.change_cost_energy + p_renew.change_cost_energy
    )
    p_fossil_and_renew.change_cost_mro = (
        p_fossil.change_cost_mro + p_renew.change_cost_mro
    )
    p_renew.change_CO2e_t = p_renew_biomass.change_CO2e_t
    p_renew_biomass.change_CO2e_pct = div(
        p_renew_biomass.change_CO2e_t, e18.p_renew_biomass.CO2e_total
    )
    p_fossil_and_renew.cost_climate_saved = (
        p_fossil.cost_climate_saved + p_renew.cost_climate_saved
    )
    p_renew.demand_emplo_new = (
        p_renew_wind.demand_emplo_new
        + p_renew_geoth.demand_emplo_new
        + p_renew_reverse.demand_emplo_new
    )
    e.invest_com = 0 + p.invest_com
    e.invest_pa_com = 0 + p.invest_pa_com
    g_grid_onshore.demand_emplo_new = g_grid_onshore.demand_emplo
    d_r.cost_fuel = (
        d_r.energy
        * d_r.cost_fuel_per_MWh
        * p_fossil_and_renew.energy
        / p.energy
        / MILLION
    )
    d_b.cost_fuel = (
        d_b.energy
        * d_b.cost_fuel_per_MWh
        * p_fossil_and_renew.energy
        / p.energy
        / MILLION
    )
    d_i.cost_fuel = (
        d_i.energy
        * d_i.cost_fuel_per_MWh
        * p_fossil_and_renew.energy
        / p.energy
        / MILLION
    )
    d_t.cost_fuel = (
        d_t.energy
        * d_t.cost_fuel_per_MWh
        * p_fossil_and_renew.energy
        / p.energy
        / MILLION
    )
    d_a.cost_fuel = (
        d_a.energy
        * d_a.cost_fuel_per_MWh
        * p_fossil_and_renew.energy
        / p.energy
        / MILLION
    )
    p.change_energy_MWh = p.energy - e18.p.energy
    p_renew_wind_offshore.pct_x = div(p_renew_wind_offshore.energy, p.energy)
    p_renew_geoth.pct_x = div(p_renew_geoth.energy, p.energy)
    p_renew_reverse.pct_x = div(p_renew_reverse.energy, p.energy)
    p_local_pv.pct_x = div(p_local_pv.energy, p.energy)
    p_local_wind_onshore.pct_x = div(p_local_wind_onshore.energy, p.energy)
    p_local_biomass.pct_x = div(p_local_biomass.energy, p.energy)
    p_local_hydro.pct_x = div(p_local_hydro.energy, p.energy)  #
    p_local.change_energy_pct = div(p_local.change_energy_MWh, e18.p_local.energy)

    p_local_pv_roof.pct_x = div(p_local_pv_roof.energy, p.energy)

    p_local.pct_energy = (
        p_local_pv.pct_energy
        + p_local_wind_onshore.pct_energy
        + p_local_biomass.pct_energy
        + p_local_hydro.pct_energy
    )
    p_local.CO2e_combustion_based_per_MWh = div(
        p_local.CO2e_combustion_based, p_local.energy
    )
    p_local.CO2e_total = p_local.CO2e_combustion_based  # change_energy_MWh
    g_grid_pv.power_to_be_installed = p_local_pv.power_to_be_installed
    p_local.invest = (
        p_local_pv_roof.invest
        + p_local_pv_facade.invest
        + p_local_pv_park.invest
        + p_local_pv_agri.invest
        + p_local_wind_onshore.invest
        + p_local_biomass.invest
    )
    p_local_pv.invest = (
        p_local_pv_roof.invest
        + p_local_pv_facade.invest
        + p_local_pv_park.invest
        + p_local_pv_agri.invest
    )  #
    p_local_pv_agri.invest_pa = p_local_pv_agri.invest / Kalkulationszeitraum
    p.CO2e_combustion_based = (
        p_fossil_and_renew.CO2e_combustion_based + p_local.CO2e_combustion_based
    )
    p_fossil_and_renew.CO2e_combustion_based_per_MWh = div(
        p_fossil_and_renew.CO2e_combustion_based, p_fossil_and_renew.energy
    )
    p_fossil_and_renew.CO2e_total = p_fossil_and_renew.CO2e_combustion_based
    p.cost_mro = p_fossil_and_renew.cost_mro + p_local.cost_mro
    p.change_cost_energy = (
        p_fossil_and_renew.change_cost_energy + p_local.change_cost_energy
    )
    p.change_cost_mro = p_fossil_and_renew.change_cost_mro + p_local.change_cost_mro
    p.change_CO2e_t = (
        p_fossil.change_CO2e_t + p_renew.change_CO2e_t + p_local.change_CO2e_t
    )
    p_fossil_and_renew.change_CO2e_t = p_fossil.change_CO2e_t + p_renew.change_CO2e_t
    p_renew.change_CO2e_pct = div(p_renew.change_CO2e_t, e18.p_renew.CO2e_total)
    p.cost_climate_saved = (
        p_fossil_and_renew.cost_climate_saved + p_local.cost_climate_saved
    )
    p_fossil_and_renew.demand_emplo_new = p_renew.demand_emplo_new
    e.change_energy_MWh = p.change_energy_MWh
    p.change_energy_pct = div(p.change_energy_MWh, e18.p.energy)
    g_grid_pv.invest = g_grid_pv.power_to_be_installed * g_grid_pv.invest_per_x
    p.invest = p_fossil_and_renew.invest + p_local.invest
    p_local.invest_pa = (
        p_local_pv_roof.invest_pa
        + p_local_pv_facade.invest_pa
        + p_local_pv_park.invest_pa
        + p_local_pv_agri.invest_pa
        + p_local_wind_onshore.invest_pa
        + p_local_biomass.invest_pa
    )  #
    p_local_pv.invest_pa = (
        p_local_pv_roof.invest_pa
        + p_local_pv_facade.invest_pa
        + p_local_pv_park.invest_pa
        + p_local_pv_agri.invest_pa
    )  # (
    p_local_pv_agri.cost_wage = p_local_pv_agri.invest_pa * p_local_pv_agri.pct_of_wage
    e.CO2e_combustion_based = p.CO2e_combustion_based
    p.CO2e_combustion_based_per_MWh = div(p.CO2e_combustion_based, p.energy)
    p.CO2e_total = p.CO2e_combustion_based
    e.change_CO2e_t = p.change_CO2e_t
    p.change_CO2e_pct = div(p.change_CO2e_t, e18.p.CO2e_combustion_based)
    p_fossil_and_renew.change_CO2e_pct = div(
        p_fossil_and_renew.change_CO2e_t, e18.p_fossil_and_renew.CO2e_total
    )
    e.cost_climate_saved = p.cost_climate_saved
    e.change_energy_pct = p.change_energy_pct
    g.invest = g_grid_offshore.invest + g_grid_onshore.invest + g_grid_pv.invest
    g_grid_pv.cost_mro = g_grid_pv.invest * ass("Ass_E_G_grid_pv_mro") / MILLION
    g_grid_pv.invest_pa = g_grid_pv.invest / entries.m_duration_target
    p.invest_pa = p_fossil_and_renew.invest_pa + p_local.invest_pa
    p_local_pv.cost_wage = (
        p_local_pv_roof.cost_wage
        + p_local_pv_facade.cost_wage
        + p_local_pv_park.cost_wage
        + p_local_pv_agri.cost_wage
    )
    p_local_pv_agri.demand_emplo = div(
        p_local_pv_agri.cost_wage, p_local_pv_agri.ratio_wage_to_emplo
    )
    e.CO2e_total = p.CO2e_total
    e.change_CO2e_pct = p.change_CO2e_pct
    e.invest = g.invest + p.invest
    g.invest_pa = (
        g_grid_offshore.invest_pa + g_grid_onshore.invest_pa + g_grid_pv.invest_pa
    )
    g_grid_pv.cost_wage = g_grid_pv.invest_pa * g_grid_pv.pct_of_wage
    p_local.cost_wage = (
        p_local_pv.cost_wage
        + p_local_wind_onshore.cost_wage
        + p_local_biomass.cost_wage
    )
    p_local_pv.demand_emplo = (
        p_local_pv_roof.demand_emplo
        + p_local_pv_facade.demand_emplo
        + p_local_pv_park.demand_emplo
        + p_local_pv_agri.demand_emplo
    )
    e.invest_pa = g.invest_pa + p.invest_pa
    g.cost_wage = (
        g_grid_offshore.cost_wage + g_grid_onshore.cost_wage + g_grid_pv.cost_wage
    )
    g_grid_pv.demand_emplo = div(g_grid_pv.cost_wage, g_grid_pv.ratio_wage_to_emplo)
    p.cost_wage = p_fossil_and_renew.cost_wage + p_local.cost_wage
    p_local.demand_emplo = (
        p_local_pv.demand_emplo
        + p_local_wind_onshore.demand_emplo
        + p_local_biomass.demand_emplo
    )  # emplo_existing
    p_local_pv.demand_emplo_new = max(
        0, p_local_pv.demand_emplo - p_local_pv.emplo_existing
    )
    g.demand_emplo = (
        g_grid_offshore.demand_emplo
        + g_grid_onshore.demand_emplo
        + g_grid_pv.demand_emplo
    )
    g_grid_pv.demand_emplo_new = g_grid_pv.demand_emplo
    e.cost_wage = g.cost_wage + p.cost_wage
    p.demand_emplo = p_fossil_and_renew.demand_emplo + p_local.demand_emplo
    p_local.demand_emplo_new = (
        p_local_pv.demand_emplo_new
        + p_local_wind_onshore.demand_emplo_new
        + p_local_biomass.demand_emplo_new
    )  # lifecycle
    g.demand_emplo_new = (
        g_grid_offshore.demand_emplo_new
        + g_grid_onshore.demand_emplo_new
        + g_grid_pv.demand_emplo_new
    )
    e.demand_emplo = g.demand_emplo + p.demand_emplo
    p.demand_emplo_new = p_fossil_and_renew.demand_emplo_new + p_local.demand_emplo_new
    e.demand_emplo_new = g.demand_emplo_new + p.demand_emplo_new

    p_local.power_installed = (
        p_local_pv.power_installed
        + p_local_wind_onshore.power_installed
        + p_local_biomass.power_installed
        + p_local_hydro.power_installed
    )

    p_local.power_installable = (
        p_local_pv.power_installable
        + p_local_wind_onshore.power_installable
        + p_local_biomass.power_installable
        # p_local_hydro.power_installable
    )

    p_local.power_to_be_installed = (
        p_local_pv.power_to_be_installed
        + p_local_wind_onshore.power_to_be_installed
        + p_local_biomass.power_to_be_installed
        # p_local_hydro.power_to_be_installed
    )

    # TODO: correct excel calculations and reimport these somehow missing variabels to python
    p_local_pv.cost_climate_saved = 0
    p_local_pv_park.change_CO2e_t = 0
    p_local_pv_park.cost_climate_saved = 0
    p_local_pv_facade.change_CO2e_t = 0
    p_local_pv_facade.cost_climate_saved = 0
    p_local_pv_agri.change_CO2e_t = 0
    p_local_pv_agri.cost_climate_saved = 0
    p_local_pv_roof.change_CO2e_t = 0
    p_local_pv_roof.cost_climate_saved = 0

    p_local_wind_onshore.CO2e_total = 0
    p_local_wind_onshore.cost_climate_saved = 0

    p_local_hydro.cost_climate_saved = 0
    p_local_hydro.change_CO2e_t = 0

    p_fossil.CO2e_total = 0

    p_renew_wind.change_CO2e_t = 0
    p_renew_wind.cost_climate_saved = 0

    p_renew_wind_onshore.CO2e_total = 0
    p_renew_wind_onshore.cost_climate_saved = 0
    p_renew_wind_onshore.change_CO2e_t = 0
    p_renew_wind_offshore.change_CO2e_t = 0
    p_renew_wind_offshore.CO2e_total = 0
    p_renew_wind_offshore.cost_climate_saved = 0

    p_renew_hydro.cost_climate_saved = 0
    p_renew_hydro.change_CO2e_t = 0

    p_renew_reverse.change_CO2e_t = 0
    p_renew_reverse.cost_climate_saved = 0

    p_renew_pv.cost_climate_saved = 0
    p_renew_pv.change_CO2e_t = 0

    p_renew_pv_roof.change_CO2e_t = 0
    p_renew_pv_agri.change_CO2e_t = 0
    p_renew_pv_facade.change_CO2e_t = 0
    p_renew_pv_park.change_CO2e_t = 0

    p_renew_geoth.change_CO2e_t = 0
    p_renew_geoth.cost_climate_saved = 0

    p_local_pv_agri.CO2e_total = 0
    p_local_pv_roof.CO2e_total = 0
    p_local_pv_facade.CO2e_total = 0
    p_local_pv_park.CO2e_total = 0

    # ---copy
    p_renew_pv.change_CO2e_pct = 0
    p_renew_pv_roof.change_CO2e_pct = 0
    p_renew_pv_agri.change_CO2e_pct = 0
    p_renew_pv_facade.change_CO2e_pct = 0
    p_renew_pv_park.change_CO2e_pct = 0

    p_renew_wind.change_CO2e_pct = 0
    p_renew_wind_onshore.change_CO2e_pct = 0
    p_renew_wind_offshore.change_CO2e_pct = 0

    p_renew_geoth.change_CO2e_pct = 0
    p_renew_hydro.change_CO2e_pct = 0

    p_local.change_CO2e_pct = 0
    p_local_pv.change_CO2e_pct = 0
    p_local_pv_roof.change_CO2e_pct = 0
    p_local_pv_agri.change_CO2e_pct = 0
    p_local_pv_facade.change_CO2e_pct = 0
    p_local_pv_park.change_CO2e_pct = 0
    p_local_wind_onshore.change_CO2e_pct = 0
    p_local_biomass.change_CO2e_pct = div(
        p_local_biomass.change_CO2e_t, e18.p_local_biomass.CO2e_total
    )
    p_local_hydro.change_CO2e_pct = 0

    p_renew_pv.cost_climate_saved = 0
    p_renew_pv_roof.cost_climate_saved = 0
    p_renew_pv_agri.cost_climate_saved = 0
    p_renew_pv_facade.cost_climate_saved = 0
    p_renew_pv_park.cost_climate_saved = 0

    p_renew_wind.cost_climate_saved = 0
    p_renew_wind_onshore.cost_climate_saved = 0
    p_renew_wind_offshore.cost_climate_saved = 0

    p_renew_geoth.cost_climate_saved = 0
    p_renew_hydro.cost_climate_saved = 0

    p_local.cost_climate_saved = 0
    p_local_pv.cost_climate_saved = 0
    p_local_pv_roof.cost_climate_saved = 0
    p_local_pv_agri.cost_climate_saved = 0
    p_local_pv_facade.cost_climate_saved = 0
    p_local_pv_park.cost_climate_saved = 0
    p_local_wind_onshore.cost_climate_saved = 0

    p_local_hydro.cost_climate_saved = 0

    return E30(
        e=e,
        g=g,
        g_grid_offshore=g_grid_offshore,
        g_grid_onshore=g_grid_onshore,
        g_grid_pv=g_grid_pv,
        d=d,
        d_r=d_r,
        d_b=d_b,
        d_h=d_h,
        d_i=d_i,
        d_t=d_t,
        d_a=d_a,
        d_f_hydrogen_reconv=d_f_hydrogen_reconv,
        d_f_wo_hydrogen=d_f_wo_hydrogen,
        p=p,
        p_fossil_and_renew=p_fossil_and_renew,
        p_fossil=p_fossil,
        p_fossil_nuclear=p_fossil_nuclear,
        p_fossil_coal_brown=p_fossil_coal_brown,
        p_fossil_coal_black=p_fossil_coal_black,
        p_fossil_gas=p_fossil_gas,
        p_fossil_ofossil=p_fossil_ofossil,
        p_renew=p_renew,
        p_renew_pv=p_renew_pv,
        p_renew_pv_roof=p_renew_pv_roof,
        p_renew_pv_facade=p_renew_pv_facade,
        p_renew_pv_park=p_renew_pv_park,
        p_renew_pv_agri=p_renew_pv_agri,
        p_renew_wind=p_renew_wind,
        p_renew_wind_onshore=p_renew_wind_onshore,
        p_renew_wind_offshore=p_renew_wind_offshore,
        p_renew_biomass=p_renew_biomass,
        p_renew_geoth=p_renew_geoth,
        p_renew_hydro=p_renew_hydro,
        p_renew_reverse=p_renew_reverse,
        p_local=p_local,
        p_local_pv=p_local_pv,
        p_local_pv_roof=p_local_pv_roof,
        p_local_pv_facade=p_local_pv_facade,
        p_local_pv_park=p_local_pv_park,
        p_local_pv_agri=p_local_pv_agri,
        p_local_wind_onshore=p_local_wind_onshore,
        p_local_biomass=p_local_biomass,
        p_local_biomass_cogen=p_local_biomass_cogen,
        p_local_hydro=p_local_hydro,
        p_local_surplus=p_local_surplus,
    )
