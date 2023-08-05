import os

from src.data.logger import configure_logger
from src.data.file_manager import FileManager
from src.presentation.plot_environment import PlotEnvironment


def run_solution(id: int) -> None:
    file = FileManager(id)
    environment = file.load_environment()
    plot_environment = PlotEnvironment(env=environment)
    plot_environment.run()


def run_all_solution() -> None:
    for i in range(len(os.listdir('./data/input'))):
        file = FileManager(i)
        environment = file.load_environment()
        plot = PlotEnvironment(env=environment)
        plot.render(i)


def init_agents(self):
    pass


def main():
    configure_logger(write_on_file=True)
    run_solution(id=0)


if __name__ == '__main__':
    main()
