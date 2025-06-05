##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## game_state
##

from typing import Tuple
from config import CommandType, CommandStatus, Orientation
from protocol.commands import Command
from protocol.parser import Parser
from utils.logger import logger
from utils.vision import Vision

class GameState:
    def __init__(self):
        self.inventory = {"food": 10, "linemate": 0, "deraumere": 0, "sibur": 0, "mendiane": 0, "phiras": 0, "thystame": 0}
        self.level = 1
        self.position = (0, 0)
        self.direction = Orientation.SOUTH

        self.vision = Vision()
        self.parser = Parser()

        self.command_already_send = False
        self.needs_look = False

    def update(self, command: Command):
        """Met à jour l'état du jeu après l'exécution d'une commande."""
        self.command_already_send = False

        if command.status != CommandStatus.SUCCESS:
            logger.warning(f"[GameState] Ignored failed command: {command.type}")
            return

        if command.type == CommandType.INVENTORY:
            self.inventory = self.parser.parse_inventory_response(command.response)

        elif command.type == CommandType.LOOK:
            self.vision.process_vision(
                command.response,
                agent_pos=self.position,
                agent_orientation=self.direction
            )
            self.needs_look = False

        elif command.type == CommandType.INCANTATION:
            self.level += 1
            logger.info(f"[GameState] Leveled up to {self.level}")
            self.needs_look = True

        elif command.type == CommandType.FORWARD:
            self.update_position_after_forward()
            self.vision.clear()
            self.needs_look = True

        elif command.type in (CommandType.LEFT, CommandType.RIGHT):
            self.update_orientation_after_turn(command.type)
            self.vision.clear()
            self.needs_look = True

        elif command.type == CommandType.TAKE and command.args:
            self.vision.remove_resource_at((0, 0), command.args[0])
            self.needs_look = False

        elif command.type == CommandType.SET and command.args:
            self.vision.add_resource_at((0, 0), command.args[0])
            self.needs_look = False

    def get_inventory(self):
        return self.inventory

    def get_food_count(self) -> int:
        """Retourne la quantité de nourriture dans l'inventaire."""
        return self.inventory.get("food", 0)

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
            1: {"linemate": 1},
            2: {"linemate": 1, "deraumere": 1, "sibur": 1},
            3: {"linemate": 2, "sibur": 1, "phiras": 2},
            4: {"linemate": 1, "deraumere": 1, "sibur": 2, "phiras": 1},
            5: {"linemate": 1, "deraumere": 2, "sibur": 1, "mendiane": 3},
            6: {"linemate": 1, "deraumere": 2, "sibur": 3, "phiras": 1},
            7: {"linemate": 2, "deraumere": 2, "sibur": 2, "mendiane": 2, "phiras": 2, "thystame": 1}
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
