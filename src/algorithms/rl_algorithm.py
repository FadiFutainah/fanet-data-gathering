from dataclasses import dataclass


@dataclass
class RLAlgorithm:
    num_of_episodes: int
    alpha: float
    max_steps: int
    epsilon_min: float
    gamma: float
    epsilon_decay: float
    epsilon: float

    def run(self):
        pass
