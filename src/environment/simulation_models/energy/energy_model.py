from dataclasses import dataclass

from src.environment.simulation_models.network.data_transition import DataTransition


@dataclass
class EnergyModel:
    e_elec: int = 50
    c: float = 1
    delta: float = 1
    distance_threshold: float = 1
    power_amplifier_for_fs: float = 1
    power_amplifier_for_amp: float = 1
    scale: float = 1

    def get_data_transition_energy(self, data_transition: DataTransition, network_coverage_radius: float) -> float:
        k = data_transition.size
        threshold = self.distance_threshold * network_coverage_radius
        distance = data_transition.source.position.distance_from(data_transition.destination.position)
        if distance < threshold:
            e_t = k * (self.e_elec + self.power_amplifier_for_fs * (distance ** 2))
        else:
            e_t = k * (self.e_elec + self.power_amplifier_for_amp * (distance ** 4))
        e_r = k * self.e_elec
        energy = e_t + e_r
        energy *= self.scale
        return energy
