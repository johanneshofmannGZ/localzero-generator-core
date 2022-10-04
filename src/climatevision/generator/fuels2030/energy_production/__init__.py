# pyright: strict

from dataclasses import dataclass

from ...inputs import Inputs
from ...fuels2018.f18 import F18
from ...agri2030.a30 import A30
from ...business2030.b30 import B30
from ...heat2030.h30 import H30
from ...industry2030.i30 import I30
from ...residences2030.r30 import R30
from ...transport2030.t30 import T30

from ..energy_demand import EnergyDemand

from .eFuelProduction import EFuelProduction
from .fuelWithoutDirectReplacement import FuelWithoutDirectReplacement
from .newEFuelProduction import NewEFuelProduction
from .eFuels import EFuels
from .totalEFuelProduction import TotalEFuelProduction


@dataclass(kw_only=True)
class Production:
    petrol: EFuelProduction
    jetfuel: EFuelProduction
    diesel: EFuelProduction
    bioethanol: FuelWithoutDirectReplacement
    biodiesel: FuelWithoutDirectReplacement
    biogas: FuelWithoutDirectReplacement
    emethan: NewEFuelProduction
    hydrogen: NewEFuelProduction
    hydrogen_reconv: NewEFuelProduction
    hydrogen_total: EnergyDemand  # Actually this is total hydrogen production
    efuels: EFuels

    total: TotalEFuelProduction


def calc_production(
    inputs: Inputs,
    f18: F18,
    a30: A30,
    b30: B30,
    h30: H30,
    i30: I30,
    r30: R30,
    t30: T30,
) -> Production:

    fact = inputs.fact
    ass = inputs.ass

    petrol = EFuelProduction.calc(
        energy=t30.t.transport.demand_epetrol + a30.p_operation.demand_epetrol,
        CO2e_emission_factor=fact("Fact_T_S_petrol_EmFa_tank_wheel_2018"),
        inputs=inputs,
        production_2018=f18.p_petrol,
    )
    jetfuel = EFuelProduction.calc(
        energy=t30.t.transport.demand_ejetfuel,
        CO2e_emission_factor=fact("Fact_T_S_petroljet_EmFa_tank_wheel_2018"),
        inputs=inputs,
        production_2018=f18.p_jetfuel,
    )
    diesel = EFuelProduction.calc(
        energy=(
            b30.p.demand_ediesel
            + t30.t.transport.demand_ediesel
            + a30.p_operation.demand_ediesel
        ),
        CO2e_emission_factor=fact("Fact_T_S_diesel_EmFa_tank_wheel_2018"),
        inputs=inputs,
        production_2018=f18.p_diesel,
    )
    biogas = FuelWithoutDirectReplacement.calc(energy2018=f18.p_biogas.energy)
    biodiesel = FuelWithoutDirectReplacement.calc(energy2018=f18.p_biodiesel.energy)
    bioethanol = FuelWithoutDirectReplacement.calc(energy2018=f18.p_bioethanol.energy)

    emethan = NewEFuelProduction.calc(
        inputs,
        energy=r30.p.demand_emethan
        + b30.p.demand_emethan
        + i30.p.demand_emethan
        + a30.p_operation.demand_emethan,
        CO2e_emission_factor=fact("Fact_T_S_methan_EmFa_tank_wheel_2018"),
        invest_per_power=ass("Ass_S_methan_invest_per_power"),
        full_load_hour=ass("Ass_S_power_to_x_full_load_hours2"),
        fuel_efficiency=ass("Ass_S_methan_efficiency"),
    )
    hydrogen = NewEFuelProduction.calc(
        inputs,
        energy=i30.p.demand_hydrogen + t30.t.transport.demand_hydrogen,
        CO2e_emission_factor=0,
        invest_per_power=ass("Ass_S_electrolyses_invest_per_power"),
        full_load_hour=ass("Ass_F_P_electrolysis_full_load_hours"),
        fuel_efficiency=ass("Ass_F_P_electrolysis_efficiency"),
    )
    hydrogen_reconv = NewEFuelProduction.calc(
        inputs,
        energy=(
            (
                h30.p.demand_electricity
                + r30.p.demand_electricity
                + b30.p.demand_electricity
                + i30.p.demand_electricity
                + t30.t.transport.demand_electricity
                + a30.p_operation.demand_electricity
                + petrol.demand_electricity
                + jetfuel.demand_electricity
                + diesel.demand_electricity
                + emethan.demand_electricity
                + hydrogen.demand_electricity
            )
            * ass("Ass_E_P_renew_reverse_addon_to_demand_2035")
            / ass("Ass_E_P_renew_reverse_gud_efficiency")
        ),
        CO2e_emission_factor=0,
        invest_per_power=ass("Ass_S_electrolyses_invest_per_power"),
        full_load_hour=ass("Ass_F_P_electrolysis_full_load_hours"),
        fuel_efficiency=ass("Ass_F_P_electrolysis_efficiency"),
    )
    efuels = EFuels.calc(petrol, diesel, jetfuel)

    total = TotalEFuelProduction.calc(
        f18,
        new_efuels=[emethan, hydrogen, hydrogen_reconv],
        efuels=[petrol, jetfuel, diesel],
        fuels_without_repl=[biogas, biodiesel, bioethanol],
    )

    return Production(
        petrol=petrol,
        jetfuel=jetfuel,
        diesel=diesel,
        biogas=biogas,
        biodiesel=biodiesel,
        bioethanol=bioethanol,
        emethan=emethan,
        hydrogen=hydrogen,
        hydrogen_reconv=hydrogen_reconv,
        efuels=efuels,
        hydrogen_total=EnergyDemand(energy=hydrogen.energy + hydrogen_reconv.energy),
        total=total,
    )
