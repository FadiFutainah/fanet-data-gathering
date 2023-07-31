import logging
import math

from environment.agents.agent import Agent
from environment.networking.transfer_type import TransferType

from dataclasses import dataclass
from typing import List

from environment.devices.uav import UAV


@dataclass
class DataForwardingState:
    uav: UAV
    neighbouring_uavs: List[UAV]

    def calculate_state_hash(self):
        pass


@dataclass
class DataForwardingAction:
    index: int
    type: int
    """ 
    type possible values are:
    0: base_station.
    1: uav.
    """


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

    def get_current_state(self):
        state = DataForwardingState(self.uav, self.env.get_uavs_in_range(self.uav_index))
        return state.calculate_state_hash()

    def send_to_base_station(self) -> None:
        for base_station in self.env.base_stations:
            if self.uav.in_range(base_station):
                self.uav.transfer_data(base_station, self.uav.memory.current_size, TransferType.SEND)

    def send_to_uav(self, uav: UAV, data_size: int) -> None:
        uavs = self.env.get_uavs_in_range(self.uav_index)
        if uav in uavs:
            self.uav.transfer_data(uav, data_size, TransferType.SEND)
        else:
            logging.error(f'the {uav} is not in the {self.uav} range')

    def get_available_actions(self):
        actions = []
        uav = self.env.uavs[self.uav_index]
        if not uav.memory.has_data():
            return []
        base_stations = self.env.get_base_stations_in_range(self.uav_index)
        if len(base_stations) > 0:
            for i in range(len(base_stations)):
                actions.append(DataForwardingAction(index=i, type=0))
        else:
            uavs = self.env.get_uavs_in_range(self.uav_index)
            for i in range(len(uavs)):
                actions.append(DataForwardingAction(index=i, type=1))
        return actions

    def get_next_state(self, action: DataForwardingAction):
        uav = self.env.uavs[self.uav_index]
        if action.type == 0:
            target = self.env.base_stations[action.index]
        else:
            target = self.env.uavs[action.index]
        uav.forward_data_target = target
        self.env.run()
        return self.get_current_state(), self.get_reward(), self.env.has_ended()
