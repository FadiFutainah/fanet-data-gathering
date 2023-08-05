import os
from dataclasses import dataclass

from src.data.file_manager import FileManager
from src.presentation.plot_environment import PlotEnvironment


@dataclass
class EnvironmentController:
    @staticmethod
    def run_solution(id: int) -> None:
        file = FileManager(id)
        environment = file.load_environment()
        plot_environment = PlotEnvironment(env=environment)
        plot_environment.run()

    @staticmethod
    def run_all_solution() -> None:
        for i in range(len(os.listdir('./data/input'))):
            file = FileManager(i)
            environment = file.load_environment()
            plot = PlotEnvironment(env=environment)
            plot.render(i)

    def init_agents(self):
        pass
