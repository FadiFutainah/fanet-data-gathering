import os

from data.file_manager import FileManager
from environment.plot.plot_environment import PlotEnvironment
from environment.utils.logger import configure_logger


def run_solution(id: int) -> None:
    file = FileManager(id)
    environment = file.load_environment()
    plot = PlotEnvironment(env=environment)
    plot.render()
    # environment.render()


def run_all_solution() -> None:
    for i in range(len(os.listdir('data/input'))):
        file = FileManager(i)
        environment = file.load_environment()
        print(environment)
        # environment.render()


def main():
    configure_logger(write_on_file=True)
    run_solution(id=0)


if __name__ == '__main__':
    main()
