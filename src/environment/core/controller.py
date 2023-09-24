from typing import List
from dataclasses import dataclass, field

import numpy as np
from src.agents.data_collecting_agent import DataCollectingAgent

from src.agents.data_forwarding_agent import DataForwardingAgent
from src.agents.data_forwarding_agents_controller import DataForwardingAgentsController
from src.data.logger import configure_logger
from src.data.file_manager import FileManager
from src.presentation.plot_view import PlotEnvironment


@dataclass
class EnvironmentController:
    agents: List = field(default_factory=list)

    @staticmethod
    def run(solution_id: int, run_type: str, log_on_file=True) -> None:
        configure_logger(write_on_file=log_on_file)
        file = FileManager(solution_id)
        forwarding_agents = []
        collecting_agents = []
        environment = file.load_environment()
        for uav in environment.uavs:
            forwarding_agent = DataForwardingAgent(uav=uav, action_size=len(environment.uavs), epsilon=1, batch_size=2,
                                                   epsilon_min=0.01, epsilon_max=1, epsilon_decay=0.995, gamma=0.95,
                                                   state_dim=len(environment.uavs) + len(environment.base_stations) + 4,
                                                   target_update_freq=2, checkpoint_freq=1000, checkpoint_path='path')
            collecting_agent = DataCollectingAgent(uav=uav)
            forwarding_agents.append(forwarding_agent)
            collecting_agents.append(collecting_agent)
            # for i, point in enumerate(uav.way_points):
            #     if point.collection_rate != 0:
            #         uav.assign_collect_data_task(i)
        agents_controller = DataForwardingAgentsController(environment=environment, forwarding_agents=forwarding_agents,
                                                           num_of_episodes=40, collecting_agents=collecting_agents,
                                                           max_steps=100, max_delay=50, max_energy=100, k=1, beta=1)
        if run_type == 'plot':
            plot_environment = PlotEnvironment(env=environment, close_on_done=False)
            plot_environment.run()
        elif run_type == 'dqn-forward':
            agents_controller.run_multi_agents()
        else:
            raise ValueError('unknown run type!!')

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
