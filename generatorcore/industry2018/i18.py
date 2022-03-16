from dataclasses import dataclass, field, asdict
from .co2e import CO2e
from .empty import Empty
from .co2e_per_t import CO2e_per_t
from .co2e_with_pct_energy import CO2e_with_pct_energy
from .co2e_per_mwh import CO2e_per_MWh
from .co2e_basic import CO2e_basic
from .energy_pct import Energy_pct
from .energy import Energy


@dataclass
class I18:
    i: CO2e = field(default_factory=CO2e)
    p: CO2e = field(default_factory=CO2e)

    p_miner: CO2e = field(default_factory=CO2e)
    p_miner_cement: CO2e_per_t = field(default_factory=CO2e_per_t)
    p_miner_chalk: CO2e_per_t = field(default_factory=CO2e_per_t)
    p_miner_glas: CO2e_per_t = field(default_factory=CO2e_per_t)
    p_miner_ceram: CO2e_per_t = field(default_factory=CO2e_per_t)

    p_chem: CO2e = field(default_factory=CO2e)
    p_chem_basic: CO2e_per_t = field(default_factory=CO2e_per_t)
    p_chem_ammonia: CO2e_per_t = field(default_factory=CO2e_per_t)
    p_chem_other: CO2e_per_t = field(default_factory=CO2e_per_t)

    p_metal: CO2e = field(default_factory=CO2e)
    p_metal_steel: CO2e_with_pct_energy = field(default_factory=CO2e_with_pct_energy)
    p_metal_steel_primary: CO2e_per_t = field(default_factory=CO2e_per_t)
    p_metal_steel_secondary: CO2e_per_t = field(default_factory=CO2e_per_t)
    p_metal_nonfe: CO2e_per_t = field(default_factory=CO2e_per_t)

    p_other: CO2e = field(default_factory=CO2e)
    p_other_paper: CO2e_per_t = field(default_factory=CO2e_per_t)
    p_other_food: CO2e_per_t = field(default_factory=CO2e_per_t)
    p_other_further: CO2e_per_MWh = field(default_factory=CO2e_per_MWh)
    p_other_2efgh: CO2e_basic = field(default_factory=CO2e_basic)

    s: Energy_pct = field(default_factory=Energy_pct)
    s_fossil: Energy = field(default_factory=Energy)
    s_fossil_gas: Energy_pct = field(default_factory=Energy_pct)
    s_fossil_coal: Energy_pct = field(default_factory=Energy_pct)
    s_fossil_diesel: Energy_pct = field(default_factory=Energy_pct)
    s_fossil_fueloil: Energy_pct = field(default_factory=Energy_pct)
    s_fossil_lpg: Energy_pct = field(default_factory=Energy_pct)
    s_fossil_opetpro: Energy_pct = field(default_factory=Energy_pct)
    s_fossil_ofossil: Energy_pct = field(default_factory=Energy_pct)
    s_renew: Energy = field(default_factory=Energy)
    s_renew_hydrogen: Empty = field(default_factory=Empty)
    s_renew_emethan: Empty = field(default_factory=Empty)
    s_renew_biomass: Energy_pct = field(default_factory=Energy_pct)
    s_renew_heatnet: Energy_pct = field(default_factory=Energy_pct)
    s_renew_heatpump: Energy_pct = field(default_factory=Energy_pct)
    s_renew_solarth: Energy_pct = field(default_factory=Energy_pct)
    s_renew_elec: Energy_pct = field(default_factory=Energy_pct)

    def dict(self):
        return asdict(self)
