from dataclasses import dataclass

from ..utils import div
from .. import (
    agri2018,
    electricity2018,
    business2018,
    fuels2018,
    heat2018,
    industry2018,
    lulucf2018,
    residences2018,
    transport2018,
    agri2030,
    business2030,
    electricity2030,
    fuels2030,
    heat2030,
    industry2030,
    lulucf2030,
    residences2030,
    transport2030,
)

@dataclass
class EnergySourceCalcIntermediate:
    

    eb_energy_from_same_sector: float

    eb_CO2e_cb_from_same_sector: float

    eb_energy_from_agri: float|None = None     

    eb_CO2e_cb_from_heat: float|None = None
    eb_CO2e_cb_from_elec: float|None = None
    eb_CO2e_cb_from_fuels: float|None = None

    energy: float = 0
    CO2e_cb: float = 0

    # production based Emissions
    CO2e_pb: float|None = None

    def __post_init__(self):

        def sum_over_none_and_float(*args:float|None)->float:
            return_float: float = 0
            for elem in args:
                if  elem is None:
                    continue
                return_float += elem

            return return_float
        #automatically sum over all cb_based emissions    
        self.CO2e_cb = sum_over_none_and_float(self.eb_CO2e_cb_from_same_sector,self.eb_CO2e_cb_from_heat,self.eb_CO2e_cb_from_elec,self.eb_CO2e_cb_from_fuels)
        self.energy = sum_over_none_and_float(self.eb_energy_from_same_sector,self.eb_energy_from_traffic,self.eb_energy_from_agri)


@dataclass
class Sum_Class:
    # energy consumption
    energy: float

    energy_from_same_eb_sector: float
    energy_from_eb_agri_sector: float

    # combustion based Emissions
    CO2e_cb: float

    # production based Emissions
    CO2e_pb: float|None = None



    @classmethod
    def calc(cls,*args: EnergySourceCalcIntermediate):
        energy = sum([elem.energy if elem.energy != None else 0 for elem in args])
        CO2e_cb = sum([elem.CO2e_cb if elem.CO2e_cb != None else 0 for elem in args])
        CO2e_pb = sum([elem.CO2e_pb if elem.CO2e_pb != None else 0 for elem in args])

        return cls(
            energy=energy,
            CO2e_cb=CO2e_cb,
            CO2e_pb = CO2e_pb,
        )
        



@dataclass
class Bisko_Sector:

    total: Sum_Class
    petrol: EnergySourceCalcIntermediate|None = None
    fueloil: EnergySourceCalcIntermediate|None = None
    coal: EnergySourceCalcIntermediate|None = None
    lpg: EnergySourceCalcIntermediate|None = None
    gas: EnergySourceCalcIntermediate|None = None
    heatnet: EnergySourceCalcIntermediate|None = None
    biomass: EnergySourceCalcIntermediate|None = None
    solarth: EnergySourceCalcIntermediate|None = None
    heatpump: EnergySourceCalcIntermediate|None = None
    elec: EnergySourceCalcIntermediate|None = None
    heatpump: EnergySourceCalcIntermediate|None = None
    diesel: EnergySourceCalcIntermediate|None = None
    jetfuel: EnergySourceCalcIntermediate|None = None
    biomass: EnergySourceCalcIntermediate|None = None
    bioethanol: EnergySourceCalcIntermediate|None = None
    biodiesel: EnergySourceCalcIntermediate|None = None
    biogas: EnergySourceCalcIntermediate|None = None
    other: EnergySourceCalcIntermediate|None = None

    @classmethod
    def calc_ph_bisko(cls, r18:residences2018.R18,h18:heat2018.H18,f18:fuels2018.F18,e18:electricity2018.E18) -> "Bisko_Sector":

        petrol = EnergySourceCalcIntermediate(eb_energy_from_same_sector=r18.s_petrol.energy,eb_CO2e_cb_from_same_sector=r18.s_petrol.CO2e_total,eb_CO2e_cb_from_fuels=f18.p_petrol.CO2e_production_based*div(f18.d_r.energy,f18.d.energy)) 
        fueloil = EnergySourceCalcIntermediate(eb_energy_from_same_sector=r18.s_fueloil.energy,eb_CO2e_cb_from_same_sector=r18.s_fueloil.CO2e_total,eb_CO2e_cb_from_heat=h18.p_fueloil.CO2e_combustion_based*div(h18.d_r.energy,h18.d.energy))
        coal = EnergySourceCalcIntermediate(eb_energy_from_same_sector=r18.s_coal.energy,eb_CO2e_cb_from_same_sector=r18.s_coal.CO2e_total,eb_CO2e_cb_from_heat=h18.p_coal.CO2e_combustion_based*div(h18.d_r.energy,h18.d.energy),CO2e_pb=h18.p_coal.CO2e_production_based*div(h18.d_r.energy,h18.d.energy))
        lpg = EnergySourceCalcIntermediate(eb_energy_from_same_sector=r18.s_lpg.energy,eb_CO2e_cb_from_same_sector=r18.s_lpg.CO2e_total,eb_CO2e_cb_from_heat=h18.p_lpg.CO2e_combustion_based*div(h18.d_r.energy,h18.d.energy))
        gas = EnergySourceCalcIntermediate(eb_energy_from_same_sector=r18.s_gas.energy,eb_CO2e_cb_from_same_sector=r18.s_gas.CO2e_total,eb_CO2e_cb_from_heat=h18.p_gas.CO2e_combustion_based*div(h18.d_r.energy,h18.d.energy),CO2e_pb=h18.p_gas.CO2e_production_based*div(h18.d_r.energy,h18.d.energy))
        heatnet = EnergySourceCalcIntermediate(eb_energy_from_same_sector=r18.s_heatnet.energy,eb_CO2e_cb_from_same_sector=r18.s_heatnet.CO2e_total,eb_CO2e_cb_from_heat=h18.p_heatnet.CO2e_combustion_based*div(h18.d_r.energy,h18.d.energy))
        biomass = EnergySourceCalcIntermediate(eb_energy_from_same_sector=r18.s_biomass.energy,eb_CO2e_cb_from_same_sector=r18.s_biomass.CO2e_total,CO2e_pb=h18.p_biomass.CO2e_production_based*div(h18.d_r.energy,h18.d.energy))
        solarth = EnergySourceCalcIntermediate(eb_energy_from_same_sector=r18.s_solarth.energy,eb_CO2e_cb_from_same_sector=r18.s_solarth.CO2e_total,CO2e_pb=h18.p_solarth.CO2e_production_based*div(h18.d_r.energy,h18.d.energy))
        heatpump = EnergySourceCalcIntermediate(eb_energy_from_same_sector=r18.s_heatpump.energy,eb_CO2e_cb_from_same_sector=r18.s_heatpump.CO2e_total,CO2e_pb=h18.p_heatpump.CO2e_production_based*div(h18.d_r.energy,h18.d.energy))
        elec = EnergySourceCalcIntermediate(eb_energy_from_same_sector=r18.s_elec.energy,eb_CO2e_cb_from_same_sector=r18.s_elec.CO2e_total,eb_CO2e_cb_from_elec=e18.p.CO2e_total*div(e18.d_r.energy,e18.d.energy))

        total = Sum_Class.calc(petrol,fueloil,coal,lpg,gas,heatnet,biomass,solarth,heatpump,elec)

        return cls(
            petrol=petrol,
            fueloil=fueloil,
            coal=coal,
            lpg=lpg,
            gas=gas,
            heatnet=heatnet,
            biomass=biomass,
            solarth=solarth,
            heatpump=heatpump,
            elec=elec,
            total=total,
        )
   


@dataclass
class Bisko:
    ph: Bisko_Sector
    #ghd: Bisko_Sector
    #traffic: Bisko_Sector
    #industry: Bisko_Sector

    
    @classmethod
    def calc(cls,
        *,
        a18: agri2018.A18,
        b18: business2018.B18,
        e18: electricity2018.E18,
        f18: fuels2018.F18,
        h18: heat2018.H18,
        i18: industry2018.I18,
        l18: lulucf2018.L18,
        r18: residences2018.R18,
        t18: transport2018.T18,
        a30: agri2030.A30,
        b30: business2030.B30,
        e30: electricity2030.E30,
        f30: fuels2030.F30,
        h30: heat2030.H30,
        i30: industry2030.I30,
        l30: lulucf2030.L30,
        r30: residences2030.R30,
        t30: transport2030.T30,
    ) -> "Bisko":

        ph_bisko = Bisko_Sector.calc_ph_bisko(r18=r18,h18=h18,f18=f18,e18=e18)
        #ghd_bisko = calc_ghd_bisko()
        #traffic_bisko = calc_traffic_bisko()
        #industry_bisko = calc_industry_bisko()

        return cls(
            ph=ph_bisko,
            #ghd=ghd_bisko,
            #traffic=traffic_bisko,
            #industry=industry_bisko,
        )


    