import os

from data.file_reader import FileReader
from environment.devices.mobile_sink import MobileSink
from environment.utils.position import Position


def main():
    ms = MobileSink(id=1, position=Position(0, 0))
    run_all_solution()


def run_all_solution():
    file = FileReader(path='resources/matlab_output/')
    for i in range(len(os.listdir('resources/matlab_output/solutions'))):
        environment = file.load_environment(solution_id=i + 1)
        environment.run('plots/plot-' + str(i))


if __name__ == '__main__':
    main()
