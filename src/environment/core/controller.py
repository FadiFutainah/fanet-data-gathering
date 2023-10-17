import numpy as np

from typing import List
from dataclasses import dataclass, field

from src.data.logger import configure_logger
from src.data.file_manager import FileManager
from src.presentation.plot_view import PlotEnvironment

from src.rl.data_collecting.data_collecting_agent import DataCollectingAgent
from src.rl.data_forwarding.data_forwarding_agent import DataForwardingAgent
from src.rl.rl_agents_controller import RLAgentController


@dataclass
class EnvironmentController:
    agents: List = field(default_factory=list)

    @staticmethod
    def run(solution_id: int, num_of_episodes: int, run_type: str, log_on_file=True) -> None:
        configure_logger(write_on_file=log_on_file)
        file = FileManager(solution_id)
        forwarding_agents = []
        collecting_agents = []
        env = file.load_environment()
        for uav in env.uavs:
            forwarding_agent = DataForwardingAgent(uav=uav, epsilon_decay=0.995, gamma=0.95, target_update_freq=2,
                                                   checkpoint_path='data/model/checkpoints', checkpoint_freq=1000,
                                                   action_size=1 + len(env.uavs) + len(env.base_stations), k=1, beta=10,
                                                   epsilon=1, state_dim=len(env.uavs) * 2 + len(env.base_stations) + 2,
                                                   max_energy=10000, batch_size=2, epsilon_min=0.01, max_delay=10000)
            collecting_agent = DataCollectingAgent(uav=uav)
            forwarding_agents.append(forwarding_agent)
            collecting_agents.append(collecting_agent)
        agents_controller = RLAgentController(environment=env, forwarding_agents=forwarding_agents, max_steps=400,
                                              num_of_episodes=num_of_episodes, collecting_agents=collecting_agents)
        if run_type == 'plot':
            plot_environment = PlotEnvironment(env=env, scale=1, close_on_done=True)
            plot_environment.run()
        elif run_type == 'forward-agent':
            agents_controller.run_forwarding_agents()
        elif run_type == 'console':
            while not env.has_ended():
                env.step()
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
