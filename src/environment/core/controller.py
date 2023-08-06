from src.data.logger import configure_logger
from src.data.file_manager import FileManager
from src.presentation.plot_environment import PlotEnvironment
from src.algorithms.dqn_agent import RLAlgorithm


def run(solution_id: int, run_type: str, log_on_file=True) -> None:
    configure_logger(write_on_file=log_on_file)
    file = FileManager(solution_id)
    environment = file.load_environment()
    data_collection_agent, data_forwarding_agent, dqn_algorithm = file.load_agents()
    if run_type == 'plot':
        plot_environment = PlotEnvironment(env=environment)
        plot_environment.run()
    elif run_type == 'dqn':
        run_dqn_agents(dqn_algorithm)
    else:
        raise Exception('unknown run type!!')


def run_dqn_agents(algorithm: RLAlgorithm) -> None:
    algorithm.run()
