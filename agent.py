""" File containing functionality for Deep Q-Learning agent to learn and play Tetris """
import os

import tensorflow as tf
import numpy as np


class TetrisAgent:
    def __init__(self):
        self.__alpha = 2.5e-3           # Define Learning Rate
        self.__epsilon = float(1/25)    # Define Exploration Rate
        self.__gamma = 0.80             # Define Discount Factor

        self.__passive_reward = -1 # -1
        self.__line_reward = 100
        self.__tetris_reward = 800
        self.__game_over_reward = -100000

        input_layer = tf.keras.layers.Input(shape=(200,))
        hidden_layer1 = tf.keras.layers.Dense(128, activation='relu')(input_layer)
        hidden_layer2 = tf.keras.layers.Dense(64, activation='relu')(hidden_layer1)
        hidden_layer3 = tf.keras.layers.Dense(32, activation='relu')(hidden_layer2)
        output = tf.keras.layers.Dense(4, activation='softmax')(hidden_layer3)
        self.__agent = tf.keras.Model(inputs=input_layer, outputs=output)

        self.__agent.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.__alpha),
                             loss=tf.keras.losses.MeanSquaredError(),
                             metrics=['accuracy'])
        
        self.__experience = 0
        self.__memory = 10000
        self.__state_space_replay_buffer = np.array([]).reshape(0, 200)
        self.__action_space_replay_buffer = np.array([]).reshape(0, 1)
        self.__reward_replay_buffer = np.array([]).reshape(0, 1)
        self.__prime_state_space_replay_buffer = np.array([]).reshape(0, 200)
        self.__terminal_state_replay_buffer = np.array([]).reshape(0, 1)

    def summary(self):
        self.__agent.summary()
    
    def reward_function(self, rows_cleared: int = 0, terminal: bool = False) -> int:
        return ((self.__passive_reward * 1 if rows_cleared == 0 else 0) + ((rows_cleared * self.__line_reward) if rows_cleared < 4 else self.__tetris_reward)) if not terminal else self.__game_over_reward

    def epsilon_greedy_selection(self, state_space: np.ndarray) -> int:
        if np.random.uniform(0, 1) < self.__epsilon:
            action = np.random.choice([0, 1, 2, 3])
        else:
            action = np.argmax(self.state_action_q_values(state_space=state_space))
        return action

    def process_state_space(self, piece_position: list[tuple], grid: list[list[tuple]]) -> np.ndarray:       
        state_space = np.zeros(shape=(len(grid), len(grid[0])))
    
        for position in piece_position:
            state_space[position[1]][position[0]] = 1

        for x in range(len(grid)):
            for y in range(len(grid[0])):
                if grid[x][y] != (0, 0, 0):
                    state_space[x][y] = 1
        return state_space.flatten()
    
    def state_action_q_values(self, state_space: np.ndarray) -> np.ndarray:
        return self.__agent.predict(x=state_space)
    
    def update_replay_buffer(self, state_space: np.ndarray, action: int, reward: int, state_space_prime: np.ndarray, terminal_state: bool):
        if self.__experience <= self.__memory:
            self.__state_space_replay_buffer = np.vstack((self.__state_space_replay_buffer, state_space))
            self.__action_space_replay_buffer = np.vstack((self.__action_space_replay_buffer, action))
            self.__reward_replay_buffer = np.vstack((self.__reward_replay_buffer, reward))
            self.__prime_state_space_replay_buffer = np.vstack((self.__prime_state_space_replay_buffer, state_space_prime))
            self.__terminal_state_replay_buffer = np.vstack((self.__terminal_state_replay_buffer, terminal_state))
        else: 
            self.__state_space_replay_buffer[self.__experience % self.__memory] = state_space
            self.__action_space_replay_buffer[self.__experience % self.__memory] = action
            self.__reward_replay_buffer[self.__experience % self.__memory] = reward
            self.__prime_state_space_replay_buffer[self.__experience % self.__memory] = state_space_prime
            self.__terminal_state_replay_buffer[self.__experience % self.__memory] = terminal_state
        self.__experience += 1

    def train(self, mini_batch_size: int = 1000, epochs: int = 1):        
        target_Q_vals_batch = np.array([]).reshape(0, 4)

        batch = np.random.randint(low=0, high=min(mini_batch_size, self.__experience), size=min(mini_batch_size, self.__experience))
        state_space_batch = self.__state_space_replay_buffer[batch]
        action_space_batch = self.__action_space_replay_buffer[batch]
        reward_batch = self.__reward_replay_buffer[batch]
        state_prime_batch = self.__prime_state_space_replay_buffer[batch]
        terminal_state_batch = self.__terminal_state_replay_buffer[batch] 

        for state, action, reward, state_prime, terminal in zip(state_space_batch, action_space_batch, reward_batch, state_prime_batch, terminal_state_batch):
            state_Q_vals = self.state_action_q_values(state_space=state.reshape(1, -1))
            state_prime_Q_vals = self.state_action_q_values(state_space=state_prime.reshape(1, -1))
            
            target_Q_vals = state_Q_vals
            if terminal:
                target_Q_vals[0][int(action)] = reward
            else:
                target_Q_vals[0][int(action)] = reward + (self.__gamma * np.max(state_prime_Q_vals))
            target_Q_vals_batch = np.vstack((target_Q_vals_batch, target_Q_vals))
        
        self.__agent.fit(x=state_space_batch, y=target_Q_vals_batch, epochs=epochs, verbose=1)

    def save_model(self, outdir: str = './dql_tetris.h5'):
        assert(outdir is not None)
        self.__agent.save(filepath=outdir)

    def load_model(self, model_weights: str = './dql_tetris.h5'):
        assert(os.path.exists(model_weights))
        assert(os.path.isfile(model_weights))
        self.__agent.load_weights(filepath=model_weights)
        