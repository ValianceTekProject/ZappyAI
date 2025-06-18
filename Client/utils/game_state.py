##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## game_state
##

import math
from typing import Tuple, Dict
from config import CommandType, CommandStatus, Orientation, Constants
from protocol.commands import Command
from protocol.parser import Parser
from utils.logger import logger
from utils.vision import Vision

class GameState:
    def __init__(self, team_id: str, dimension_map: Tuple[int, int]):
        """
        Initialise l'état du jeu pour un agent :
        - inventaire initial
        - niveau et identifiant d'équipe
        - dimensions de la carte
        - position et orientation
        - vision et parser
        - flags pour gestion des commandes et actions (look, reproduction)
        - seuils de nourriture
        """
        self.inventory = {
            "food": 10,
            "linemate": 0,
            "deraumere": 0,
            "sibur": 0,
            "mendiane": 0,
            "phiras": 0,
            "thystame": 0
        }
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
        """
        Met à jour l'état du jeu après l'exécution d'une commande :
        - réinitialise flag command_already_send
        - gère l'échec d'incantation en log détaillé et force un look
        - si TAKE échoue, force un look
        - ignore toute commande non-SUCCESS avec warning
        - pour SUCCESS :
          - INVENTORY : met à jour l'inventaire
          - LOOK : traite la vision et réinitialise le flag needs_look
          - INCANTATION : incrémente de niveau (via réception côté supérieur), déclenche look et reproduction
          - FORWARD : met à jour position, vide la vision, déclenche look
          - LEFT/RIGHT : met à jour orientation, vide la vision, déclenche look
          - TAKE réussite : retire la ressource du sol dans la vision, désactive needs_look
          - SET réussite : ajoute la ressource au sol dans la vision, désactive needs_look
        """
        self.command_already_send = False

        if command.type == CommandType.INCANTATION and command.status == CommandStatus.FAILED:
            next_level = self.level + 1
            requirements = self.get_incantation_requirements()
            needed_players = self.get_required_player_count()
            players_here = self._players_on_current_tile()
            ground = self._get_resources_at_current_position()
            inv = self.inventory.copy()

            missing_resources = {}
            for res, qty in requirements.items():
                on_ground = ground.get(res, 0)
                if on_ground < qty:
                    missing_resources[res] = (qty, on_ground)
            players_missing = needed_players - players_here if players_here < needed_players else 0

            logger.warning(
                "[GameState] Incantation FAILED for level %d -> %d: "
                "Players present: %d (needed: %d)%s; "
                "Ground resources: %s; "
                "Missing on ground: %s; "
                "Inventory before incant: %s; "
                "Vision data (rel positions + players + resources): %s",
                self.level, next_level,
                players_here, needed_players,
                f", missing players: {players_missing}" if players_missing > 0 else "",
                ground,
                missing_resources if missing_resources else "{}",
                inv,
                self.vision.last_vision_data
            )
            self.needs_look = True
            self.needs_repro = False
            return

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
                agent_orientation=None
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
            logger.debug(f"[GameState] Set {command.args[0]}")
            self.vision.add_resource_at((0, 0), command.args[0])
            self.needs_look = False

    def get_inventory(self) -> Dict[str, int]:
        """Retourne l'inventaire courant."""
        return self.inventory

    def get_food_count(self) -> int:
        """Retourne la quantité de nourriture dans l'inventaire."""
        return self.inventory.get(Constants.FOOD.value, 0)

    def _get_critical_food_threshold(self) -> int:
        """
        Calcule le seuil critique de nourriture selon le niveau :
        - niveau <4 : seuil de base
        - 4 à 6 : double
        - >6 : triple
        """
        if self.level < 4:
            return self.critical_food_threshold
        elif self.level <= 6:
            return self.critical_food_threshold * 2
        else:
            return self.critical_food_threshold * 3

    def _get_safe_food_threshold(self) -> float:
        """
        Calcule le seuil sûr de nourriture selon le niveau :
        - niveau <4 : seuil de base
        - 4 à 6 : 1.5x
        - >6 : 2x
        """
        if self.level < 4:
            return self.safe_food_threshold
        elif self.level <= 6:
            return self.safe_food_threshold * 1.5
        else:
            return self.safe_food_threshold * 2

    def estimate_food_needed_for_incant(self) -> int:
        """
        Estime la nourriture nécessaire pour rejoindre l'initiateur au pire cas puis effectuer l'incantation.
        """
        W, H = self.dimension_map
        if W is None or H is None:
            return float('inf')
        max_dist = (W // 2) + (H // 2)
        time_travel = (max_dist + 2) * 7
        time_incant = 300
        total = time_travel + time_incant
        needed = math.ceil(total / 126)
        return needed + 1

    def get_player_level(self) -> int:
        """Retourne le niveau du joueur."""
        return self.level

    def get_position(self) -> Tuple[int, int]:
        """Retourne la position courante du joueur."""
        return self.position

    def get_orientation(self) -> int:
        """Retourne l'orientation courante du joueur."""
        return self.direction

    def update_position(self, new_position: Tuple[int, int]):
        """Met à jour la position du joueur."""
        self.position = new_position

    def update_orientation(self, new_orientation: int):
        """Met à jour l'orientation du joueur."""
        self.direction = new_orientation

    def get_visible_tiles(self) -> Vision:
        """Retourne l'objet Vision actuel."""
        return self.vision

    def get_vision(self) -> Vision:
        """Retourne l'objet Vision actuel."""
        return self.vision

    def update_vision(self, look_response: str, pos: Tuple[int, int], orientation: int):
        """Traite la réponse LOOK pour mettre à jour la vision."""
        self.vision.process_vision(look_response, pos, orientation)

    def update_position_after_forward(self):
        """Met à jour la position en avançant d'une case selon l'orientation."""
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
        """Met à jour l'orientation après un TURN LEFT ou RIGHT."""
        if turn_cmd == CommandType.LEFT:
            self.direction = (self.direction - 1) % 4
        elif turn_cmd == CommandType.RIGHT:
            self.direction = (self.direction + 1) % 4

    def has_missing_resources(self) -> bool:
        """
        Indique si l'inventaire manque de ressources nécessaires pour incanter.
        """
        requirements = self.get_incantation_requirements()
        return any(self.inventory.get(res, 0) < qty for res, qty in requirements.items())

    def can_incant(self) -> bool:
        """
        Détermine si l'agent dispose des ressources et du nombre de joueurs requis sur la tuile pour incanter.
        """
        requirements = self.get_incantation_requirements()
        if any(self.inventory.get(res, 0) < qty for res, qty in requirements.items()):
            return False
        return self._players_on_current_tile() >= self.get_required_player_count()

    def get_incantation_requirements(self) -> Dict[str, int]:
        """Retourne le dict des ressources nécessaires pour incanter au niveau courant."""
        level_reqs = {
            1: {Constants.LINEMATE.value: 1},
            2: {
                Constants.LINEMATE.value: 1,
                Constants.DERAUMERE.value: 1,
                Constants.SIBUR.value: 1
            },
            3: {
                Constants.LINEMATE.value: 2,
                Constants.SIBUR.value: 1,
                Constants.PHIRAS.value: 2
            },
            4: {
                Constants.LINEMATE.value: 1,
                Constants.DERAUMERE.value: 1,
                Constants.SIBUR.value: 2,
                Constants.PHIRAS.value: 1
            },
            5: {
                Constants.LINEMATE.value: 1,
                Constants.DERAUMERE.value: 2,
                Constants.SIBUR.value: 1,
                Constants.MENDIANE.value: 3
            },
            6: {
                Constants.LINEMATE.value: 1,
                Constants.DERAUMERE.value: 2,
                Constants.SIBUR.value: 3,
                Constants.PHIRAS.value: 1
            },
            7: {
                Constants.LINEMATE.value: 2,
                Constants.DERAUMERE.value: 2,
                Constants.SIBUR.value: 2,
                Constants.MENDIANE.value: 2,
                Constants.PHIRAS.value: 2,
                Constants.THYSTAME.value: 1
            }
        }
        return level_reqs.get(self.level, {})

    def get_required_player_count(self) -> int:
        """Retourne le nombre de joueurs requis pour incanter au niveau courant."""
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

    def _get_resources_at_current_position(self) -> Dict[str, int]:
        """Retourne les ressources présentes à la case actuelle (0,0) selon la dernière vision."""
        if not self.vision.last_vision_data:
            return {}
        for td in self.vision.last_vision_data:
            if td.rel_pos == (0, 0):
                return dict(td.resources)
        return {}

    def _players_on_current_tile(self) -> int:
        """Retourne le nombre de joueurs visibles sur la case actuelle (0,0)."""
        for data in self.vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return data.players
        return 0
