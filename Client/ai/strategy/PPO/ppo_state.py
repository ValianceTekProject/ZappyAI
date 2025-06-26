##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## ppo_state
##

from utils.game_state import GameState

class ppo_state():
    def __init__(self, game_state: GameState, actualize_vision: bool = False):
        self.game_state = game_state
        self.food_inventory = game_state.inventory.get('food', 0) / 20.0
        self.level = game_state.level / 8.0
        self.linemate_inventory = game_state.inventory.get('linemate', 0) / 20.0
        self.deraumere_inventory = game_state.inventory.get('deraumere', 0) / 20.0
        self.sibur_inventory = game_state.inventory.get('sibur', 0) / 20.0
        self.mediane_inventory = game_state.inventory.get('mendiane', 0) / 20.0
        self.phiras_inventory = game_state.inventory.get('phiras', 0) / 20.0
        self.thystame_inventory = game_state.inventory.get('thystame', 0) / 20.0

        self.distance_closest_food = -1
        self.angle_closest_food = -1
        if actualize_vision:
            result = self.get_closest_food(game_state)
            if result is not None:
                self.distance_closest_food, self.angle_closest_food = result
            else:
                self.distance_closest_food, self.angle_closest_food = -1, -1

    def get_closest_food(self, game_state: GameState):
        pos = game_state.vision.find_closest_resource("food")
        if pos:
            return self.position_to_vector(pos[0], pos[1])
        return None

    def position_to_vector(self, x, y):
        """Convertit position relative en distance + angle"""
        distance = abs(x) + abs(y)

        if distance == 0:
            return 0, 0

        if y < 0:
            if x == 0:
                angle = 0
            elif x > 0:
                angle = 45
            else:
                angle = 315
        elif y > 0:
            if x == 0:
                angle = 180
            elif x > 0:
                angle = 135
            else:
                angle = 225
        else:
            if x > 0:
                angle = 90
            else:
                angle = 270

        angle_normalized = angle / 360.0

        distance_normalized = min(distance / 20.0, 1.0)

        return distance_normalized, angle_normalized