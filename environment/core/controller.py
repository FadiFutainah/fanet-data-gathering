import os
from dataclasses import dataclass

from data.file_manager import FileManager
from environment.plot.plot_environment import PlotEnvironment


@dataclass
class EnvironmentController:
    @staticmethod
    def run_solution(id: int) -> None:
        file = FileManager(id)
        environment = file.load_environment()
        environment.uavs[0].areas_collection_rates[0] = 10000
        plot_environment = PlotEnvironment(env=environment)
        plot_environment.run()

    @staticmethod
    def run_all_solution() -> None:
        for i in range(len(os.listdir('data/input'))):
            file = FileManager(i)
            environment = file.load_environment()
            plot = PlotEnvironment(env=environment)
            plot.render(i)

    def init_agents(self):
        pass
