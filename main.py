from environment.core.controller import EnvironmentController
from environment.utils.logger import configure_logger


def main():
    configure_logger(write_on_file=False)
    EnvironmentController.run_solution(id=0)


if __name__ == '__main__':
    main()
