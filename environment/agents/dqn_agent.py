from typing import Any, List

from environment.agents.data_forwarding_agent import DataForwardingAgent
from dataclasses import dataclass, field
import numpy as np
import random
from matplotlib import pyplot as plt
import tensorflow as tf


@dataclass
class DQNAgent(DataForwardingAgent):
    agent_rewards = []
    memory_max_size: int
    batch_size: int
    tau: int
    target_model: Any = field(init=False)
    model: Any = field(init=False)
    memory: List = field(init=False, default=list)

    def __post_init__(self):
        self.target_model = self.create_model()
        self.model = self.create_model()

    def create_model(self):
        model = tf.keras.layers.Sequintial([
            tf.keras.Input(shape=(self.state_size,)),
            tf.kears.Dense(24, activation='relu'),
            tf.kears.Dense(24, activation='relu'),
            tf.kears.Dense(self.action_size, activation='linear'),
        ])
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(learning_rate=self.alpha))
        return model

    def reset_environment(self):
        self.env.reset_with_random_data_collection_rates()

    def run(self):
        for episode in range(self.num_of_episodes):
            self.reset_environment()
            state = self.get_current_state()
            episode_reward = 0
            for step in range(self.max_steps):
                actions = self.get_available_actions()
                random_num = random.uniform(0, 1)
                if random_num < self.epsilon:
                    action = random.choice(actions)
                else:
                    q_values = self.model.predict(state)[0]
                    action = np.argmax(q_values)
                next_state, reward, done = self.get_next_state(action)
                experience = (state, action, reward, next_state, done)
                self.memory.append(experience)
                if len(self.memory) > self.memory_max_size:
                    np.delete(self.memory, 0)
                episode_reward += reward
                if done:
                    break
                state = next_state
                self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            if len(self.memory) >= self.batch_size:
                mini_batch = random.sample(list(self.memory), self.batch_size)
                for experience in mini_batch:
                    state, action, reward, next_state, done = experience
                    target = self.target_model.predict(state)
                    target[0][action] = reward
                    if not done:
                        target[0][action] += self.gamma * max(self.target_model.predict(next_state)[0])
                    self.model.fit(state, target, epochs=1, verbose=0)
            weights = self.model.get_weights()
            target_weights = self.target_model.get_weights()
            for i in range(len(target_weights)):
                target_weights[i] = self.tau * weights[i] + (1 - self.tau) * target_weights[i]
            self.target_model.set_weights(target_weights)
            self.agent_rewards.append(episode_reward)

    def show_results(self):
        plt.plot(range(self.num_of_episodes), self.agent_rewards)
        plt.show()
