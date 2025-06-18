##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## game_state
##

import math
from typing import Tuple
from config import CommandType, CommandStatus, Orientation, Constants
from protocol.commands import Command
from protocol.parser import Parser
from utils.logger import logger
from utils.vision import Vision

class GameState:
    def __init__(self, team_id: str, dimension_map: Tuple[int, int]):
        self.inventory = {"food": 10, "linemate": 0, "deraumere": 0, "sibur": 0, "mendiane": 0, "phiras": 0, "thystame": 0}
        self.level = 1
        self.team_id = team_id
        self.dimension_map = dimension_map
        self.position = (0, 0)
        self.direction = Orientation.SOUTH

        self.vision = Vision()
        self.parser = Parser()

        self.command_already_send = False
        self.needs_look = False
        self.needs_repro = False

        self.critical_food_threshold = 15
        self.safe_food_threshold = 20

    def update(self, command: Command):
        """Met à jour l'état du jeu après l'exécution d'une commande."""
        self.command_already_send = False

        # logger.info(f"[GameState] Updated with command: {command.type}, response: {command.response}")

        if command.type == CommandType.INCANTATION and command.status == CommandStatus.FAILED:
            logger.debug(f"[GameState] Incantation {self.level + 1} failed, because of .")
            self.needs_look = True
            self.needs_repro = False

        if command.type == CommandType.TAKE and command.status == CommandStatus.FAILED:
            self.needs_look = True

        if command.status != CommandStatus.SUCCESS:
            logger.warning(f"[GameState] Ignored failed command: {command.type}, response: {command.response}")
            return

        if command.type == CommandType.INVENTORY:
            self.inventory = self.parser.parse_inventory_response(command.response)
            logger.debug(f"[GameState] Inventory contains: {self.inventory}")

        elif command.type == CommandType.LOOK:
            self.vision.process_vision(
                command.response,
                agent_pos=self.position,
                agent_orientation=self.direction
            )
            self.needs_look = False

        elif command.type == CommandType.INCANTATION:
            logger.info(f"[GameState] Leveled up to {self.level}")
            self.needs_look = True
            self.needs_repro = True

        elif command.type == CommandType.FORWARD:
            self.update_position_after_forward()
            self.vision.clear()
            self.needs_look = True

        elif command.type in (CommandType.LEFT, CommandType.RIGHT):
            self.update_orientation_after_turn(command.type)
            self.vision.clear()
            self.needs_look = True

        elif command.type == CommandType.TAKE and command.args:
            logger.debug(f"[GameState] Took {command.args[0]}")
            self.vision.remove_resource_at((0, 0), command.args[0])
            self.needs_look = False

        elif command.type == CommandType.SET and command.args:
            self.vision.add_resource_at((0, 0), command.args[0])
            self.needs_look = False

    def get_inventory(self):
        return self.inventory

    def get_food_count(self) -> int:
        """Retourne la quantité de nourriture dans l'inventaire."""
        return self.inventory.get(Constants.FOOD.value, 0)

    def _get_critical_food_threshold(self) -> int:
        if self.level < 4:
            return self.critical_food_threshold
        elif self.level >= 4 and self.level <= 6:
            return self.critical_food_threshold * 2
        elif self.level > 6:
            return self.critical_food_threshold * 3

    def _get_safe_food_threshold(self) -> int:
        if self.level < 4:
            return self.safe_food_threshold
        elif self.level >= 4 and self.level <= 6:
            return self.safe_food_threshold * 1.5
        elif self.level > 6:
            return self.safe_food_threshold * 2

    def estimate_food_needed_for_incant(self):
        W, H = self.dimension_map[0], self.dimension_map[1]
        if W is None or H is None:
            return float('inf')
        max_dist = (W // 2) + (H // 2)
        commands_forward = max_dist
        commands_turn = 2
        time_travel = (commands_forward + commands_turn) * 7
        time_incant = 300
        total = time_travel + time_incant
        needed = math.ceil(total / 126)
        return needed + 1

    def get_player_level(self):
        return self.level

    def get_position(self) -> Tuple[int, int]:
        return self.position

    def get_orientation(self) -> int:
        return self.direction

    def update_position(self, new_position: Tuple[int, int]):
        self.position = new_position

    def update_orientation(self, new_orientation: int):
        self.direction = new_orientation

    def get_visible_tiles(self):
        return self.vision

    def get_vision(self) -> Vision:
        return self.vision

    def update_vision(self, look_response: str, pos: Tuple[int, int], orientation: int):
        self.vision.process_vision(look_response, pos, orientation)

    def update_position_after_forward(self):
        """Déplace le joueur d'une case en fonction de l'orientation actuelle."""
        x, y = self.position
        if self.direction == Orientation.NORTH:
            y -= 1
        elif self.direction == Orientation.EAST:
            x += 1
        elif self.direction == Orientation.SOUTH:
            y += 1
        elif self.direction == Orientation.WEST:
            x -= 1
        self.position = (x, y)

    def update_orientation_after_turn(self, turn_cmd: CommandType):
        """Tourne le joueur à gauche ou à droite."""
        if turn_cmd == CommandType.LEFT:
            self.direction = (self.direction - 1) % 4
        elif turn_cmd == CommandType.RIGHT:
            self.direction = (self.direction + 1) % 4

    def has_missing_resources(self) -> bool:
        """Retourne True si l'inventaire est incomplet pour incanter."""
        requirements = self.get_incantation_requirements()
        return any(self.inventory.get(res, 0) < qty for res, qty in requirements.items())

    def can_incant(self) -> bool:
        """Retourne True si toutes les conditions pour incanter sont remplies."""
        requirements = self.get_incantation_requirements()
        if any(self.inventory.get(res, 0) < qty for res, qty in requirements.items()):
            return False
        return self._players_on_current_tile() >= self.get_required_player_count()

    def get_incantation_requirements(self) -> dict:
        """Retourne les ressources nécessaires pour incanter selon le niveau actuel."""
        level_reqs = {
            1: {Constants.LINEMATE.value: 1},
            2: {Constants.LINEMATE.value: 1, Constants.DERAUMERE.value: 1, Constants.SIBUR.value: 1},
            3: {Constants.LINEMATE.value: 2, Constants.SIBUR.value: 1, Constants.PHIRAS.value: 2},
            4: {Constants.LINEMATE.value: 1, Constants.DERAUMERE.value: 1, Constants.SIBUR.value: 2, Constants.PHIRAS.value: 1},
            5: {Constants.LINEMATE.value: 1, Constants.DERAUMERE.value: 2, Constants.SIBUR.value: 1, Constants.MENDIANE.value: 3},
            6: {Constants.LINEMATE.value: 1, Constants.DERAUMERE.value: 2, Constants.SIBUR.value: 3, Constants.PHIRAS.value: 1},
            7: {Constants.LINEMATE.value: 2, Constants.DERAUMERE.value: 2, Constants.SIBUR.value: 2, Constants.MENDIANE.value: 2, Constants.PHIRAS.value: 2, Constants.THYSTAME.value: 1}
        }
        return level_reqs.get(self.level, {})

    def get_required_player_count(self) -> int:
        """Retourne le nombre de joueurs requis pour incanter à ce niveau."""
        players_reqs = {
            1: 1,
            2: 2,
            3: 2,
            4: 4,
            5: 4,
            6: 6,
            7: 6
        }
        return players_reqs.get(self.level, 1)

    def _players_on_current_tile(self) -> int:
        """Retourne le nombre de joueurs visibles sur la case actuelle (0,0)."""
        for data in self.vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return data.players
        return 0
