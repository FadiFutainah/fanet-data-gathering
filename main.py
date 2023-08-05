from src.environment.core.controller import EnvironmentController
from src.data.logger import configure_logger


def main():
    configure_logger(write_on_file=True)
    EnvironmentController.run_solution(id=0)


if __name__ == '__main__':
    main()
