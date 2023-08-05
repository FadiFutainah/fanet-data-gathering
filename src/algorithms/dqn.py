import random

import numpy as np
import tensorflow as tf

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from src.algorithms.rl_algorithm import RLAlgorithm
from src.agents.agent import Agent


@dataclass
class DQNAlgorithm(RLAlgorithm):
    agent: Agent
    checkpoint_path: str = ''
    state_dim = 2
    buffer_size: int = 2000
    batch_size: int = 32
    tau: float = 0.125
    memory: Any = field(init=False)
    target_update_freq = 20
    checkpoint_freq = 25
    model: tf.keras.models = field(init=False)
    target_model: tf.keras.models = field(init=False)
    wins: int = field(init=False, default=0)

    def __post_init__(self):
        self.memory = deque(maxlen=self.buffer_size)
        self.model = self.create_model()
        self.target_model = tf.keras.models.clone_model(self.model)

    def create_model(self):
        num_units = 24
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Dense(num_units, input_dim=self.state_dim, activation="relu"))
        model.add(tf.keras.layers.Dense(num_units, activation="relu"))
        model.add(tf.keras.layers.Dense(self.agent.action_size))
        model.compile(loss="mse", optimizer=tf.keras.optimizers.Adam())
        return model

    def run(self):
        for episode in range(self.num_of_episodes):
            tf.summary.scalar("epsilon", self.epsilon, step=episode)
            episode_return = 0
            state = self.agent.reset_environment()
            done = False
            steps = 0
            self.wins = 0
            while not done and steps <= self.max_steps:
                steps += 1
                print("\r> DQN: Episode {}/{}, Step {}, epsilon {}, state{}, Return {}".format(
                    episode + 1, self.num_of_episodes, steps, self.epsilon, state, episode_return), end="")

                if np.random.rand() < self.epsilon:
                    actions = self.agent.get_available_actions()
                    action = random.choice(actions)
                else:
                    action = np.argmax(self.model.predict(np.array([state]), verbose=0)[0])

                state_new, reward, done = self.agent.step(action)
                episode_return += reward
                if done:
                    self.wins += 1
                self.memory.append((state, action, reward, state_new, done))

                if len(self.memory) > self.batch_size:
                    experience_sample = random.sample(self.memory, self.batch_size)
                    x = np.array([e[0] for e in experience_sample])

                    y = self.model.predict(x, verbose=0)
                    x2 = np.array([e[3] for e in experience_sample])
                    q2 = self.gamma * np.max(self.target_model.predict(x2, verbose=0), axis=1)
                    for i, (s, a, r, s2, d) in enumerate(experience_sample):
                        y[i][a] = r
                        if not d:
                            y[i][a] += q2[i]

                    self.model.fit(x, y, batch_size=self.batch_size, epochs=1, verbose=0)

                    for layer in self.model.layers:
                        for weight in layer.weights:
                            weight_name = weight.name.replace(':', '_')
                            tf.summary.histogram(weight_name, weight, step=steps)

                if steps % self.target_update_freq == 0:
                    self.target_model.set_weights(self.model.get_weights())

                if steps % self.checkpoint_freq == 0:
                    self.model.save_weights("{}/weights-{:08d}-{:08d}".format(
                        self.checkpoint_path, episode, steps))

                state = state_new

            epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

            tf.summary.scalar("return", episode_return, step=episode)
            tf.summary.flush()
            self.agent.episodes_rewards.append(episode_return)
            if (steps - 1) % self.checkpoint_freq != 0:
                self.model.save_weights("{}/weights-{:08d}-{:08d}".format(
                    self.checkpoint_path, episode, steps - 1))
        print()
