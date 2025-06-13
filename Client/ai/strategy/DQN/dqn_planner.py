##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## dqn_planner
##

import numpy as np
from typing import List

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

        self.actualize_food = False
        self.distance_closest_food = None
        self.angle_closest_food = None

        self.state_size = 11

    def dqn_decision(self):
        if self.state.command_already_send:
            return None
        current_state = self.dqn.build_state(self.state, self.actualize_food)
        if self.actualize_food:
            self.actualize_food = False
            self.distance_closest_food = current_state.distance_closest_food
            self.angle_closest_food = current_state.angle_closest_food
        else:
            current_state.distance_closest_food = self.distance_closest_food
            current_state.angle_closest_food = self.angle_closest_food
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
        if state.food_visible == 1:
            vector.append(state.food_visible)
            vector.append(state.distance_closest_food)
            vector.append(state.angle_closest_food)
        else:
            vector.append(state.food_visible)
            vector.append(-1)
            vector.append(-1)

        return np.array(vector)

    def handle_forward_action(self, action, current_state):
        if self.dqn.distance_closest_food:
            if self.dqn.angle_closest_food == 0:
                self.dqn.distance_closest_food -= 1
        if self.dqn.angle_closest_food == 180:
            self.dqn.distance_closest_food += 1
        return self.cmd_manager.forward()

    def execute_dqn_action(self, action, current_state):
        if action == CommandType.FORWARD:
            return self.handle_forward_action(action, current_state)
        elif action == CommandType.LEFT:
            if self.dqn.angle_closest_food:
                self.dqn.angle_closest_food = (self.dqn.angle_closest_food + 90) % 360
            return self.cmd_manager.left()
        elif action == CommandType.RIGHT:
            if self.dqn.angle_closest_food:
                self.dqn.angle_closest_food = (self.dqn.angle_closest_food - 90) % 360
            return self.cmd_manager.right()
        elif action == CommandType.TAKE:
            return self.cmd_manager.take(Constants.FOOD.value)
        elif action == CommandType.LOOK:
            self.actualize_food = True
            return self.cmd_manager.look()
        return None
