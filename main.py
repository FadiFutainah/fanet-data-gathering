import logging
import os

from data.file_reader import FileReader
from environment.utils.logger import configure_logger


def run_solution(id: int) -> None:
    file = FileReader(path='resources/matlab_output/')
    environment = file.load_environment(solution_id=id)
    environment.render()


def run_all_solution() -> None:
    file = FileReader(path='resources/matlab_output/')
    for i in range(len(os.listdir('resources/matlab_output/solutions'))):
        environment = file.load_environment(solution_id=i + 1)
        environment.save_on_file('plots/plot-' + str(id))
        environment.render()


def main():
    configure_logger()
    run_solution(id=101)


if __name__ == '__main__':
    main()
