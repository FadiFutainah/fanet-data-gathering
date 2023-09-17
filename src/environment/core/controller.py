from typing import List
from dataclasses import dataclass, field

import numpy as np

from src.agents.data_forwarding_agent import DataForwardingAgent
from src.agents.data_forwarding_agents_controller import DataForwardingAgentsController
from src.data.logger import configure_logger
from src.data.file_manager import FileManager
from src.environment.core.environment import Environment
from src.presentation.plot_environment import PlotEnvironment


@dataclass
class EnvironmentController:
    environment: Environment
    agents: List = field(default_factory=list)

    @staticmethod
    def run(solution_id: int, run_type: str, log_on_file=True) -> None:
        configure_logger(write_on_file=log_on_file)
        file = FileManager(solution_id)
        agents = []
        environment = file.load_environment()
        for uav in environment.uavs:
            agent = DataForwardingAgent(uav=uav, state_dim=len(environment.uavs) + 3,
                                        action_size=len(environment.uavs), epsilon=1, epsilon_min=0.01, epsilon_max=1,
                                        epsilon_decay=0.995, target_update_freq=2, checkpoint_freq=1000,
                                        checkpoint_path='path', gamma=0.95, batch_size=2)
            agents.append(agent)
        agents_controller = DataForwardingAgentsController(environment=environment, agents=agents, num_of_episodes=10,
                                                           max_steps=100, max_delay=50, max_energy=100, k=1, beta=1)
        if run_type == 'plot':
            plot_environment = PlotEnvironment(env=environment, close_on_done=True)
            plot_environment.run()
        elif run_type == 'dqn-forward':
            agents_controller.run_multi_agents()
        else:
            raise Exception('unknown run type!!')

    @staticmethod
    def num_of_generated_packets(environment) -> int:
        return int(np.sum(sensor.num_of_collected_packets for sensor in environment.sensors))

    @staticmethod
    def num_of_received_packets(environment) -> int:
        return int(np.sum(base_station.num_of_collected_packets for base_station in environment.base_stations))

    def calculate_pdr(self, environment) -> float:
        if self.num_of_generated_packets(environment) == 0:
            return 0
        return self.num_of_received_packets(environment) / self.num_of_generated_packets(environment)
