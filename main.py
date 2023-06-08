import os

from data.file_manager import FileManager
from environment.plot.plot_environment import PlotEnvironment
from environment.utils.connection_protocol import ConnectionProtocol
from environment.utils.logger import configure_logger


def run_solution(id: int) -> None:
    file = FileManager(input_dir='sample_1', output_dir='last')
    environment = file.load_environment(solution_id=id, environment=PlotEnvironment)
    environment.render()
    file.write_data_on_csv(environment)


def run_all_solution() -> None:
    file = FileManager(input_dir='sample_1', output_dir='last')
    for i in range(len(os.listdir('resources/matlab_output/solutions'))):
        environment = file.load_environment(solution_id=i + 1, environment=PlotEnvironment)
        environment.save_on_file('plots/plot-' + str(id))
        environment.render()


def main():
    configure_logger(write_on_file=True)
    run_solution(id=101)


if __name__ == '__main__':
    main()
