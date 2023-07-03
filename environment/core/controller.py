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
        plot = PlotEnvironment(env=environment)
        while not environment.has_ended():
            # environment.run()
            plot.run()

    @staticmethod
    def run_all_solution() -> None:
        for i in range(len(os.listdir('data/input'))):
            file = FileManager(i)
            environment = file.load_environment()
            plot = PlotEnvironment(env=environment)
            plot.render(i)

    def init_agents(self):
        pass
