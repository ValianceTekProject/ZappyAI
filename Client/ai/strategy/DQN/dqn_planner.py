##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## dqn_planner
##

import numpy as np

from ai.strategy.DQN.dqn_state import DQNState
from protocol.commands import CommandManager
from utils.game_state import GameState
from config import CommandType, Constants
from ai.strategy.DQN.dqn import DeepQNetwork

class DQNPlanner:
    def __init__(self, game_state: GameState, command_manager: CommandManager):
        self.dqn = DeepQNetwork()
        self.cmd_manager = command_manager
        self.state = game_state

        self.last_state = None
        self.last_action_index = None

        self.actualize_inventory = False

    def dqn_decision(self):
        if self.state.command_already_send:
            return None
        current_state = self.dqn.build_state(self.state, self.actualize_inventory)
        if self.actualize_inventory:
            actual_inventory = False
        else:
            current_state.vision = self.state.vision
        current_state = self.transform_state_into_vector(current_state)
        action_index = self.dqn.choose_action(current_state)
        action = self.dqn.get_action_form_index(action_index)
        self.last_state = current_state
        self.last_action_index = action_index
        return self.execute_dqn_action(action, current_state)

    def transform_state_into_vector(self, state: DQNState):
        vector = []

        vector.append(state.food_inventory)
        vector.append(state.level)
        vector.append(state.linemate_inventory)
        vector.append(state.deraumere_inventory)
        vector.append(state.sibur_inventory)
        vector.append(state.mediane_inventory)
        vector.append(state.phiras_inventory)
        vector.append(state.thystame_inventory)
        vector.append(state.vision)
        return np.array(vector)

    def handle_forward_action(self, action, current_state):
        return self.cmd_manager.forward()

    def execute_dqn_action(self, action, current_state):
        if action == CommandType.FORWARD:
            return self.handle_forward_action(action, current_state)
        elif action == CommandType.LEFT:
            return self.cmd_manager.left()
        elif action == CommandType.RIGHT:
            return self.cmd_manager.right()
        elif action == CommandType.TAKE:
            return self.cmd_manager.take(Constants.FOOD.value)
        elif action == CommandType.LOOK:
            self.actualize_inventory = True
            return self.cmd_manager.look()
        return None
