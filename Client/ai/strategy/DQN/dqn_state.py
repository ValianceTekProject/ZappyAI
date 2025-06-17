##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## dqn_state
##

import numpy as np
from utils.game_state import GameState
from typing import Dict
from enum import Enum

class Item(Enum):
    FOOD = 1
    LINEMATE = 2
    DERAUMERE = 3
    SIBUR = 4
    MEDIANE = 5
    PHIRAS = 6
    THYSTAME = 7
    PLAYER = 8

class DQNState:
    def __init__(self, game_state: GameState, actualize_inventory: bool = False):
        self.game_state = game_state
        self.food_inventory = game_state.inventory.get('food', 0) / 100.0
        self.level = game_state.level / 8.0
        self.linemate_inventory = game_state.inventory.get('linemate', 0) / 20.0
        self.deraumere_inventory = game_state.inventory.get('deraumere', 0) / 20.0
        self.sibur_inventory = game_state.inventory.get('sibur', 0) / 20.0
        self.mediane_inventory = game_state.inventory.get('mendiane', 0) / 20.0
        self.phiras_inventory = game_state.inventory.get('phiras', 0) / 20.0
        self.thystame_inventory = game_state.inventory.get('thystame', 0) / 20.0

        self.vision = []
        for line in range(9):
            tiles_in_line = 1 + (line * 2)
            self.vision.append([self.create_empty_tile() for _ in range(tiles_in_line)])

        if actualize_inventory:
            self.fill_vision()

    def create_empty_tile(self):
        return {
            Item.FOOD: 0,
            Item.LINEMATE: 0,
            Item.DERAUMERE: 0,
            Item.SIBUR: 0,
            Item.MEDIANE: 0,
            Item.PHIRAS: 0,
            Item.THYSTAME: 0,
            Item.PLAYER: 0
        }

    def map_to_vision_index(self, rel_pos):
        x, y = rel_pos
        line = y
        index = x + line
        return index, line

    def fill_vision(self):
        vision = self.game_state.get_vision()
        resources = vision.get_visible_resources()
        for resource_name, positions_list in resources.items():
            for position in positions_list:
                x, y = position
                index, line = self.map_to_vision_index((x, y))
                item = self.convert_ressources(resource_name)
                if item:
                    self.vision[line][index][item] += 1

    def convert_ressources(self, ressource):
        if ressource == "food":
            return Item.FOOD
        if ressource == "linemate":
            return Item.LINEMATE
        if ressource == "deraumere":
            return Item.DERAUMERE
        if ressource == "sibur":
            return Item.SIBUR
        if ressource == "mediane":
            return Item.MEDIANE
        if ressource == "phiras":
            return Item.PHIRAS
        if ressource == "thystame":
            return Item.THYSTAME
        if ressource == "player":
            return Item.PLAYER
        return None

    def get_closest_food(self, game_state: GameState):
        pos = game_state.vision.find_closest_resource("food")
        if pos:
            return self.position_to_vector(pos[0], pos[1])
        return None