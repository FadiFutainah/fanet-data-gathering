from typing import List
from dataclasses import dataclass

from src.data.logger import configure_logger
from src.data.file_manager import FileManager
from src.presentation.plot_environment import PlotEnvironment
from src.algorithms.dqn_agent import RLAlgorithm


@dataclass
class EnvironmentController:
    agents: List

    def init_agents(self):
        for agent in self.agents:
            pass

    @staticmethod
    def run(solution_id: int, run_type: str, log_on_file=True) -> None:
        configure_logger(write_on_file=log_on_file)
        file = FileManager(solution_id)
        environment = file.load_environment()
        data_collection_agent, data_forwarding_agent, dqn_agent = file.load_agents()
        if run_type == 'plot':
            plot_environment = PlotEnvironment(env=environment)
            plot_environment.run()
        elif run_type == 'dqn':
            EnvironmentController.run_dqn_agents(dqn_agent)
        else:
            raise Exception('unknown run type!!')

    @staticmethod
    def run_dqn_agents(algorithm: RLAlgorithm) -> None:
        algorithm.run()
