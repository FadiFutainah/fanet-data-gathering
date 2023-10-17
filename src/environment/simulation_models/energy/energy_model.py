from dataclasses import dataclass

from src.environment.simulation_models.network.data_transition import DataTransition


@dataclass
class EnergyModel:
    e_elec: int
    distance_threshold: float
    power_amplifier_for_fs: float
    power_amplifier_for_amp: float

    def get_data_transition_energy(self, data_transition: DataTransition) -> float:
        k = data_transition.size
        distance = data_transition.source.position.distance_from(data_transition.destination.position)
        if distance < self.distance_threshold:
            e_t = k * (self.e_elec + self.power_amplifier_for_fs * (distance ** 2))
        else:
            e_t = k * (self.e_elec + self.power_amplifier_for_amp * (distance ** 4))
        e_r = k * self.e_elec
        energy = e_t + e_r
        energy /= 1e4
        energy = int(energy)
        return energy
