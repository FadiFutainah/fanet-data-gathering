from dataclasses import dataclass


@dataclass
class EnergyModel:
    e_elec: int = 50
    c: float = 1
    delta: float = 1
    distance_threshold: float = 1
    power_amplifier_for_fs: float = 1
    power_amplifier_for_amp: float = 1
