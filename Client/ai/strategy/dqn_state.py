##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## dqn_state
##

from config import GameStates
import numpy as np

class DQNState:
    def __init__(self):
        self.state = []

    """State
    [
      food_inventory,
      level,
      food_on_current_tile,
      Vision []
      linemate_inventory,
      deraumere_inventory,
      sibur_inventory,
      mendiane_inventory,
      phiras_inventory,
      thystame_inventory
    ]"""
    def set_state(self, game_state, state_size):

        self.state = np.zeros(state_size)

        self.state[0] = game_state.inventory.get('food', 0) / 100.0
        self.state[1] = game_state.level / 8.0
        self.state[3] = game_state.vision
        self.state[4] = game_state.inventory.get('linemate', 0) / 20.0
        self.state[5] = game_state.inventory.get('deraumere', 0) / 20.0
        self.state[6] = game_state.inventory.get('sibur', 0) / 20.0
        self.state[7] = game_state.inventory.get('mendiane', 0) / 20.0
        self.state[8] = game_state.inventory.get('phiras', 0) / 20.0
        self.state[9] = game_state.inventory.get('thystame', 0) / 20.0

    def get_state(self):
        return self.state
