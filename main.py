import argparse

from src.environment.core.controller import run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('solution', type=int)
    parser.add_argument('run_type', type=str)
    args = parser.parse_args()
    run(solution_id=args.solution, run_type=args.run_type)


if __name__ == '__main__':
    main()
