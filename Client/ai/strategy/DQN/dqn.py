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
    def __init__(self, hidden_layer_size = 32, learning_rate = 0.0005, gamma = 0.99, epsilon = 1.0, epsilon_decay = 0.995,
                 epsilon_min = 0.3, batch_size = 64, state_size = 657):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size
        self.learning_rate = learning_rate
        self.available_state = list(GameStates)
        self.main_actions = [
            CommandType.FORWARD,
            CommandType.RIGHT,
            CommandType.LEFT,
            CommandType.TAKE,
            CommandType.LOOK,
            CommandType.INVENTORY
        ]
        self.output_size = len(self.main_actions)

        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size

        self.memory = deque(maxlen=100000)

        self.input_size = state_size

        self.fc1 = nn.Linear(self.input_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 32)
        self.fc5 = nn.Linear(32, self.output_size)

        self.optimizer = optim.Adam(self.parameters(), lr=self.learning_rate)

    def get_action_form_index(self, index: int) -> CommandType:
        if index < 0:
            return CommandType.FORWARD
        return self.main_actions[index]

    def forward(self, x):
        logits = self.fc1(x)
        logits = torch.relu(logits)
        logits = self.fc2(logits)
        logits = torch.relu(logits)
        logits = self.fc3(logits)
        logits = torch.relu(logits)
        logits = self.fc4(logits)
        logits = torch.relu(logits)
        logits = self.fc5(logits)
        return logits

    def choose_action(self, state):
        state = torch.from_numpy(state).float()
        if random.random() < self.epsilon:
            return random.randint(0, 5)
        else:
            state_batch = torch.unsqueeze(state, 0)
            q_values = self.forward(state_batch)
            maxq = torch.argmax(q_values)
            return maxq.item()

    def calculate_reward(self, action, result, old_state, new_state):
        if result == "dead":
            return -100
        if result == "ko":
            return -100
        if new_state[9] > 0 and action == 3:
            return 10000
        if new_state[9] > 0:
            return 100
        if new_state[0] > old_state[0]:
            return 100
        if action == 4:
            return 50
        if new_state[1] == 8 and old_state[1] < 8:
            return 1000
        if new_state[0] < 0.3 and old_state[0] >= 0.3:
            return -1000
        return 0

    def build_state(self, game_state: GameState, actualize_inventory: bool = False):
        return DQNState(game_state, actualize_inventory)

    def save_experience(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)

        states = np.array([e[0] for e in batch])
        actions = [e[1] for e in batch]
        rewards = [e[2] for e in batch]
        next_states = np.array([e[3] for e in batch])
        dones = [e[4] for e in batch]

        states = torch.FloatTensor(states)
        next_states = torch.FloatTensor(next_states)
        rewards = torch.FloatTensor(rewards)
        actions = torch.LongTensor(actions)
        dones = torch.FloatTensor(dones)

        current_q_values = self.forward(states).gather(1, actions.unsqueeze(1))

        next_q_values = self.forward(next_states).max(1)[0].detach()

        target_q_values = rewards + (self.gamma * next_q_values * (1 - dones))

        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load_experiences(self, filename):
        try:
            with open(filename, 'rb') as f:
                import pickle
                experiences = pickle.load(f)
                self.memory = deque(experiences, maxlen=10000)
                print(f"Chargé {len(self.memory)} expériences")
        except FileNotFoundError:
            print("Pas d'expériences trouvées")

    def save_model(self, filename):
        torch.save({
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'memory': list(self.memory)
        }, filename)

    def load_model(self, filename):
        try:
            checkpoint = torch.load(filename, weights_only=False)
            self.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint['epsilon']
            self.memory = deque(checkpoint['memory'], maxlen=100000)
            print(f"Modèle chargé avec {len(self.memory)} expériences, epsilon={self.epsilon}")
        except FileNotFoundError:
            print("Pas de modèle trouvé, démarrage avec un nouveau modèle")
