##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## dqn_state
##

import numpy as np
from utils.game_state import GameState


class DQNState:
    def __init__(self, game_state: GameState, actualize_food: bool = False):
        self.food_inventory = game_state.inventory.get('food', 0) / 100.0
        self.level = game_state.level / 8.0
        self.linemate_inventory = game_state.inventory.get('linemate', 0) / 20.0
        self.deraumere_inventory = game_state.inventory.get('deraumere', 0) / 20.0
        self.sibur_inventory = game_state.inventory.get('sibur', 0) / 20.0
        self.mediane_inventory = game_state.inventory.get('mendiane', 0) / 20.0
        self.phiras_inventory = game_state.inventory.get('phiras', 0) / 20.0
        self.thystame_inventory = game_state.inventory.get('thystame', 0) / 20.0

        self.food_visible = None
        self.distance_closest_food = None
        self.distance_closest_linemate = None
        if actualize_food:
            distance_closest_food, angle = self.get_closest_food(game_state)

            if distance_closest_food and angle:
                self.food_visible = 1
                self.distance_closest_food = distance_closest_food / 20
                self.angle_closest_food = angle / 360
            else:
                self.food_visible = 0
                self.distance_closest_food = None
                self.angle_closest_food = None
        else:
            self.food_visible = 0

    def get_closest_food(self, game_state: GameState):
        pos = game_state.vision.find_closest_resource("food")
        if pos:
            return self.position_to_vector(pos[0], pos[1])
        return None

    def position_to_vector(self, x, y):
        distance = abs(x) + abs(y)

        if distance == 0:
            angle = 0
        else:
            if y < 0:
                if x > 0:
                    angle = 45
                elif x < 0:
                    angle = 315
                else:
                    angle = 0
        return distance, angle