import logging
import math
from dataclasses import dataclass

from environment.agents.agent import Agent
from environment.agents.data_forwarding_state import DataForwardingState
from environment.devices.uav import UAV
from environment.networking.transfer_type import TransferType


@dataclass
class DataForwardingAgent(Agent):
    max_delay: float
    max_energy: float
    max_queue_length: float
    beta: float
    gamma_e: float
    """ represents the maximum penalty for exceeding the max_energy """
    sigma_q: float
    """ represents the maximum penalty for exceeding the max_queue_length """
    lambda_d: float
    """ represents the maximum penalty for exceeding the max_delay """
    k: float
    """ describes the steepness of the sigmoid function """

    def get_delay_penalty(self, delay: float) -> float:
        return 1 / (1 + math.exp(-self.k * (delay - self.max_delay)))

    def get_energy_penalty(self, energy: float) -> float:
        return 1 / (1 + math.exp(-self.k * (energy - self.max_energy)))

    def get_queue_penalty(self, queue_length: float) -> float:
        return 1 / (1 + math.exp(-self.k * (queue_length - self.max_queue_length)))

    def get_reward(self):
        delay = self.env.calculate_e2e_delay(self.uav_index)
        energy = self.env.calculate_consumed_energy(self.uav_index)
        queue_length = self.env.uavs[self.uav_index].memory.current_size
        pdr = self.env.calculate_pdr()
        delay_penalty = self.lambda_d * self.get_delay_penalty(delay)
        queue_length_penalty = self.sigma_q * self.get_queue_penalty(queue_length)
        energy_penalty = self.gamma_e * self.get_energy_penalty(energy)
        pdr_penalty = pdr * self.beta
        return pdr_penalty - energy_penalty - queue_length_penalty - delay_penalty

    def get_state(self):
        return DataForwardingState(self.uav, self.env.get_neighbouring_uavs(self.uav_index))

    def send_to_base_station(self) -> None:
        for base_station in self.env.base_stations:
            if self.uav.in_range(base_station):
                self.uav.transfer_data(base_station, self.uav.memory.current_size, TransferType.SEND)

    def send_to_uav(self, uav: UAV, data_size: int) -> None:
        uavs = self.env.get_neighbouring_uavs(self.uav_index)
        if uav in uavs:
            self.uav.transfer_data(uav, data_size, TransferType.SEND)
        else:
            logging.error(f'the {uav} is not in the {self.uav} range')
