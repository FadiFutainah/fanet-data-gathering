import os

from data.file_reader import FileReader


def main():
    run_solution(id=1)


def run_solution(id: int) -> None:
    file = FileReader(path='resources/matlab_output/')
    environment = file.load_environment(solution_id=id)
    environment.run('plots/plot-' + str(0))


def run_all_solution() -> None:
    file = FileReader(path='resources/matlab_output/')
    for i in range(len(os.listdir('resources/matlab_output/solutions'))):
        environment = file.load_environment(solution_id=i + 1)
        environment.run('plots/plot-' + str(i))


if __name__ == '__main__':
    main()
