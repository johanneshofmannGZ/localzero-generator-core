# pyright: strict

from dataclasses import InitVar, dataclass

from ..utils import div


@dataclass(kw_only=True)
class Energy:
    energy: float


@dataclass(kw_only=True)
class EnergyWithPercentage(Energy):
    pct_energy: float = 0
    total_energy: InitVar[float]

    def __post_init__(self, total_energy: float):
        self.pct_energy = div(self.energy, total_energy)
