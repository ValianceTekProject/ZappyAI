##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## dqn
##

import random
from collections import deque
import numpy as np
from config import CommandType, GameStates
import torch
import torch.nn as nn
import torch.optim as optim
from ai.strategy.DQN.dqn_state import DQNState
from utils.game_state import GameState

class DeepQNetwork(nn.Module):
    def __init__(self, hidden_layer_size = 32, learning_rate = 0.001, gamma = 0.99, epsilon = 1.0, epsilon_decay = 0.99,
                 epsilon_min = 0.01, batch_size = 64):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size
        self.learning_rate = learning_rate
        self.available_state = list(GameStates)
        self.main_actions = [
            CommandType.FORWARD,
            CommandType.RIGHT,
            CommandType.LEFT,
            CommandType.TAKE,
            CommandType.LOOK
        ]
        self.output_size = len(self.main_actions)

        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size

        self.memory = deque(maxlen=10000)

        self.input_size = self.state_size

        self.fc1 = nn.Linear(self.input_size, self.hidden_layer_size)
        self.fc2 = nn.Linear(self.hidden_layer_size, self.output_size)

        self.optimizer = optim.Adam(self.parameters(), lr=self.learning_rate)

    def get_action_form_index(self, index: int) -> CommandType:
        if index < 0:
            return CommandType.FORWARD
        return self.main_actions[index]

    def forward(self, x):
        logits = self.fc1(x)
        logits = torch.relu(logits)
        logits = self.fc2(logits)
        return logits

    def choose_action(self, state):
        state = torch.from_numpy(state).float()
        if random.random() < self.epsilon:
            return random.randint(0, 4)
        else:
            state_batch = torch.unsqueeze(state, 0)
            q_values = self.forward(state_batch)
            maxq = torch.argmax(q_values)
            return maxq.item()

    def calculate_reward(self, action, result, old_state, new_state):
        reward = 0
        if result == "ko":
            return -0.1
        old_food = old_state[0] * 100
        new_food = new_state[0] * 100
        if new_food > old_food:
            reward += 10
        if new_food < 20:
            reward -= 1
        if new_state[1] > old_state[1]:
            reward += 30
        if result == "dead":
            reward -= 100
        reward += 0.1
        return reward

    def build_state(self, game_state: GameState, actualize_food: bool = False):
        return DQNState(game_state, actualize_food)

    def save_experience(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def load_experiences(self, filename):
        pass

    def save_model(self, filename):
        pass

    def load_model(self, filename):
        pass
