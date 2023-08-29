import random

import numpy as np
import tensorflow as tf

from collections import deque
from dataclasses import dataclass, field
from typing import Any, List

from src.algorithms.rl_algorithm import RLAlgorithm
from src.agents.agent import Agent


@dataclass
class DQNAgent(RLAlgorithm):
    agent: Agent
    checkpoint_paths: List[str] = ''
    state_dim = 2
    buffer_size: int = 2000
    batch_size: int = 32
    tau: float = 0.125
    memories: List[Any] = field(init=False)
    target_update_freq = 20
    checkpoint_freq = 25
    models: List[Any] = field(init=False)
    target_models: List[Any] = field(init=False)
    wins: list[int] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.memories = [deque(maxlen=self.buffer_size) for _ in range(len(self.agent.uav_indices))]
        self.models = [self.create_model() for _ in range(len(self.agent.uav_indices))]
        self.target_models = [tf.keras.models.clone_model(model) for model in range(len(self.agent.uav_indices))]

    def create_model(self):
        num_units = 24
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Dense(num_units, input_dim=self.state_dim, activation='relu'))
        model.add(tf.keras.layers.Dense(num_units, activation='relu'))
        model.add(tf.keras.layers.Dense(self.agent.action_size))
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam())
        return model

    def run(self):
        for episode in range(self.num_of_episodes):
            tf.summary.scalar('epsilon', self.epsilon, step=episode)
            episode_return = 0
            states = self.agent.reset_environment()
            done = False
            steps = 0
            rewards = []
            self.wins = np.zeros(len(self.models))
            while not done and steps <= self.max_steps:
                steps += 1
                print(
                    f'\r> DQN: Episode {episode + 1}/{self.num_of_episodes}, Step {steps}, epsilon {self.epsilon},'
                    f' Return {episode_return}',
                    end='')
                accumulated_done = True
                actions = []
                next_states = []
                for i in self.agent.uav_indices:
                    if np.random.rand() < self.epsilon:
                        actions = self.agent.get_available_actions(index=i)
                        action = random.choice(actions)
                    else:
                        action = np.argmax(self.models[i].predict(np.array([states[i]]), verbose=0)[0])
                    state_new, reward, done = self.agent.step(action, index=i)
                    next_states.append(state_new)
                    rewards.append(reward)
                    actions.append(action)
                    accumulated_done = accumulated_done and done
                    if done:
                        self.wins[i] += 1
                episode_return += sum(rewards)
                for i in range(len(self.memories)):
                    self.memories[i].append((states[i], actions[i], rewards[i], next_states[i], accumulated_done))
                    if len(self.memories[i]) > self.batch_size:
                        experience_sample = random.sample(self.memories[i], self.batch_size)
                        x = np.array([e[0] for e in experience_sample])

                        y = self.models[i].predict(x, verbose=0)
                        x2 = np.array([e[3] for e in experience_sample])
                        q2 = self.gamma * np.max(self.target_models[i].predict(x2, verbose=0), axis=1)
                        for j, (s, a, r, s2, d) in enumerate(experience_sample):
                            y[j][a] = r
                            if not d:
                                y[j][a] += q2[j]

                        self.models[i].fit(x, y, batch_size=self.batch_size, epochs=1, verbose=0)

                        for layer in self.models[i].layers:
                            for weight in layer.weights:
                                weight_name = weight.name.replace(':', '_')
                                tf.summary.histogram(weight_name, weight, step=steps)

                    if steps % self.target_update_freq == 0:
                        self.target_models[i].set_weights(self.models[i].get_weights())

                    if steps % self.checkpoint_freq == 0:
                        self.models[i].save_weights('{}/weights-{:08d}-{:08d}'.format(
                            self.checkpoint_paths[i], episode, steps))

                states = next_states

            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

            tf.summary.scalar('return', episode_return, step=episode)
            tf.summary.flush()
            self.agent.episodes_rewards.append(episode_return)
            for i in range(len(self.agent.uav_indices)):
                if (steps - 1) % self.checkpoint_freq != 0:
                    self.models[i].save_weights('{}/weights-{:08d}-{:08d}'.format(
                        self.checkpoint_paths[i], episode, steps - 1))
        print()
