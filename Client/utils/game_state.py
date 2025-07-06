##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## game_state - État du jeu nettoyé sans doublons
##

import time
from typing import Tuple, Dict, Optional, Any
from config import CommandType, CommandStatus, Orientation
from protocol.commands import Command
from protocol.parser import Parser
from utils.logger import logger
from utils.vision import Vision
from constant import (
    FoodThresholds, IncantationRequirements, AgentRoles, 
    ReproductionRules, GameplayConstants
)


class GameState:
    """Gère l'état du jeu pour un agent avec constantes centralisées et sans doublons"""

    def __init__(self, team_id: str, dimension_map: Tuple[int, int], agent_id: int = 0):
        """
        Initialise l'état du jeu
        
        Args:
            team_id: Identifiant de l'équipe
            dimension_map: Dimensions de la carte (largeur, hauteur)
            agent_id: Identifiant unique de l'agent
        """
        # ===== INVENTAIRE ET RESSOURCES =====
        self.inventory = {
            "food": 10,
            "linemate": 0,
            "deraumere": 0,
            "sibur": 0,
            "mendiane": 0,
            "phiras": 0,
            "thystame": 0
        }

        # ===== IDENTITÉ ET POSITION =====
        self.level = 1
        self.team_id = team_id
        self.agent_id = agent_id
        self.dimension_map = dimension_map
        self.position = (0, 0)
        self.direction = Orientation.SOUTH

        # ===== VISION ET PERCEPTION =====
        self.vision = Vision()
        self.parser = Parser()
        self.needs_look = False

        # ===== ÉTAT DES COMMANDES =====
        self.command_already_send = False

        # ===== REPRODUCTION (niveau 2 uniquement) =====
        self.reproduction_triggered = False
        self.reproduction_completed = False

        # ===== RÔLE DANS LA COORDINATION =====
        self.role = AgentRoles.SURVIVOR

        # ===== RÉFÉRENCES EXTERNES =====
        self.agent_thread = None

        # ===== HISTORIQUE ET STATISTIQUES =====
        self.last_food_update = time.time()
        self.command_history = []
        self.join_incantation = False
        self.direction_incant = None

        logger.info(f"[GameState] Agent {agent_id} initialisé - Team: {team_id}, Food: {self.get_food_count()}")

    def update(self, command: Command):
        """
        Met à jour l'état du jeu après l'exécution d'une commande
        
        Args:
            command: Commande exécutée
        """
        self.command_already_send = False

        self._update_command_history(command)

        if command.type == CommandType.INCANTATION and command.status == CommandStatus.FAILED:
            self._handle_incantation_failure(command)
            return

        if command.type == CommandType.TAKE and command.status == CommandStatus.FAILED:
            self.needs_look = True
            logger.warning(f"[GameState] Take échoué")

        if command.status != CommandStatus.SUCCESS:
            return

        # Traitement des commandes réussies
        if command.type == CommandType.INVENTORY:
            self._update_inventory_from_response(command.response)

        elif command.type == CommandType.LOOK:
            self._update_vision_from_response(command.response)

        elif command.type == CommandType.INCANTATION:
            self._handle_successful_incantation()

        elif command.type == CommandType.FORWARD:
            self._update_position_after_forward()

        elif command.type in (CommandType.LEFT, CommandType.RIGHT):
            self._update_orientation_after_turn(command.type)

        elif command.type == CommandType.TAKE and command.args:
            self._handle_successful_take(command.args[0])

        elif command.type == CommandType.SET and command.args:
            self._handle_successful_set(command.args[0])

        elif command.type == CommandType.FORK:
            self._handle_successful_reproduction()

    def _update_command_history(self, command: Command):
        """Met à jour l'historique des commandes"""
        self.command_history.append({
            'command': command.type,
            'status': command.status,
            'timestamp': time.time(),
            'response': command.response
        })

        if len(self.command_history) > 50:
            self.command_history.pop(0)

    def _update_inventory_from_response(self, response: str):
        """Met à jour l'inventaire à partir de la réponse du serveur"""
        old_food = self.inventory.get('food', 0)
        self.inventory = self.parser.parse_inventory_response(response)
        new_food = self.inventory.get('food', 0)
        
        if new_food != old_food:
            self._update_food_history(old_food, new_food)

    def _update_vision_from_response(self, response: str):
        """Met à jour la vision à partir de la réponse du serveur"""
        self.vision.process_vision(
            response,
            agent_pos=self.position,
            agent_orientation=self.direction
        )
        self.needs_look = False

    def _handle_successful_incantation(self):
        """Gère une incantation réussie"""
        self.needs_look = True
        self._handle_level_up()

    def _update_position_after_forward(self):
        """Met à jour la position après un mouvement forward"""
        x, y = self.position
        if self.direction == Orientation.NORTH:
            y -= 1
        elif self.direction == Orientation.EAST:
            x += 1
        elif self.direction == Orientation.SOUTH:
            y += 1
        elif self.direction == Orientation.WEST:
            x -= 1

        max_x, max_y = self.dimension_map
        x = x % max_x
        y = y % max_y

        self.position = (x, y)
        self.vision.clear()
        self.needs_look = True

    def _update_orientation_after_turn(self, turn_cmd: CommandType):
        """Met à jour l'orientation après une rotation"""
        if turn_cmd == CommandType.LEFT:
            self.direction = (self.direction - 1) % 4
        elif turn_cmd == CommandType.RIGHT:
            self.direction = (self.direction + 1) % 4
            
        self.vision.clear()
        self.needs_look = True

    def _handle_successful_take(self, resource: str):
        """Gère un take réussi"""
        if resource in self.inventory:
            self.inventory[resource] += 1
        self.vision.remove_resource_at((0, 0), resource)

    def _handle_successful_set(self, resource: str):
        """Gère un set réussi"""
        if resource in self.inventory and self.inventory[resource] > 0:
            self.inventory[resource] -= 1
        self.vision.add_resource_at((0, 0), resource)

    def _handle_successful_reproduction(self):
        """Gère une reproduction réussie"""
        self.reproduction_completed = True
        logger.info("[GameState] Reproduction terminée avec succès")

    def _handle_level_up(self):
        """Gère les actions après un level up"""
        if self.level == ReproductionRules.TRIGGER_LEVEL and not self.reproduction_triggered:
            self.reproduction_triggered = True
            logger.info(f"[GameState] 👶 Reproduction activée (niveau {ReproductionRules.TRIGGER_LEVEL} atteint)")

    def _handle_incantation_failure(self, command: Command):
        """Gère l'échec d'incantation avec log détaillé"""
        next_level = self.level + 1
        requirements = self.get_incantation_requirements()
        needed_players = self.get_required_player_count()
        players_here = self._players_on_current_tile()

        logger.error(f"[GameState] 💥 INCANTATION ÉCHEC {self.level} → {next_level}: "
                    f"Joueurs: {players_here}/{needed_players}")
        self.needs_look = True

    def _update_food_history(self, old_food: int, new_food: int):
        """Met à jour l'historique de consommation de nourriture"""
        self.last_food_update = time.time()
        change = new_food - old_food

        if change < 0:
            logger.debug(f"[GameState] Consommation: {change} (reste: {new_food})")

    def _players_on_current_tile(self) -> int:
        """Retourne le nombre de joueurs sur la tuile actuelle"""
        for data in self.vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return data.players
        return 1

    def force_unlock(self):
        """Force le déblocage en cas d'agent bloqué"""
        logger.warning("[GameState] 🔓 FORCE UNLOCK")
        self.command_already_send = False
        self.needs_look = True

    # ===== GETTERS POUR L'INVENTAIRE ET L'ÉTAT =====
    
    def get_food_count(self) -> int:
        """Retourne la quantité de nourriture dans l'inventaire"""
        return self.inventory.get("food", 0)

    def get_inventory(self) -> Dict[str, int]:
        """Retourne l'inventaire complet"""
        return self.inventory.copy()

    def get_player_level(self) -> int:
        """Retourne le niveau du joueur"""
        return self.level

    def get_position(self) -> Tuple[int, int]:
        """Retourne la position courante"""
        return self.position

    def get_orientation(self) -> int:
        """Retourne l'orientation courante"""
        return self.direction

    def get_vision(self) -> Vision:
        """Retourne l'objet Vision"""
        return self.vision

    # ===== VÉRIFICATIONS D'ÉTAT =====

    def has_missing_resources(self) -> bool:
        """Vérifie si des ressources manquent pour l'incantation"""
        requirements = self.get_incantation_requirements()
        return any(self.inventory.get(res, 0) < qty for res, qty in requirements.items())

    def can_incant(self) -> bool:
        """Vérifie si l'agent peut lancer une incantation"""
        requirements = self.get_incantation_requirements()
        if any(self.inventory.get(res, 0) < qty for res, qty in requirements.items()):
            return False

        return self._players_on_current_tile() >= self.get_required_player_count()

    def should_reproduce(self) -> bool:
        """Vérifie si l'agent devrait se reproduire selon les règles strictes"""
        return (
            self.reproduction_triggered and 
            not self.reproduction_completed and
            self.level == ReproductionRules.TRIGGER_LEVEL and
            self.get_food_count() >= ReproductionRules.MIN_FOOD_REQUIRED
        )

    # ===== VÉRIFICATIONS DE NOURRITURE =====

    def is_food_critical(self) -> bool:
        """Vérifie si la nourriture est en état critique"""
        return self.get_food_count() <= FoodThresholds.CRITICAL

    def is_food_sufficient(self) -> bool:
        """Vérifie si la nourriture est suffisante"""
        return self.get_food_count() >= FoodThresholds.SUFFICIENT

    def is_food_abundant(self) -> bool:
        """Vérifie si la nourriture est abondante"""
        return self.get_food_count() >= FoodThresholds.ABUNDANT

    def can_coordinate(self) -> bool:
        """Vérifie si l'agent peut participer à la coordination"""
        return (
            self.level > 1 and 
            self.get_food_count() >= FoodThresholds.COORDINATION_MIN and
            not self.has_missing_resources()
        )

    # ===== INFORMATIONS D'INCANTATION =====

    def get_incantation_requirements(self) -> Dict[str, int]:
        """Retourne les ressources nécessaires pour l'incantation actuelle"""
        return IncantationRequirements.REQUIRED_RESOURCES.get(self.level, {})

    def get_required_player_count(self) -> int:
        """Retourne le nombre de joueurs requis pour l'incantation"""
        return IncantationRequirements.REQUIRED_PLAYERS.get(self.level, 1)

    # ===== GESTION DU RÔLE =====

    def set_role(self, role: str):
        """Définit le rôle de l'agent"""
        if role in [AgentRoles.INCANTER, AgentRoles.HELPER, AgentRoles.SURVIVOR]:
            old_role = getattr(self, 'role', AgentRoles.SURVIVOR)
            self.role = role
            if old_role != role:
                logger.info(f"[GameState] Changement de rôle: {old_role} → {role}")

    def get_role(self) -> str:
        """Retourne le rôle actuel de l'agent"""
        return getattr(self, 'role', AgentRoles.SURVIVOR)

    # ===== RÉSUMÉ D'ÉTAT POUR DEBUG =====

    def get_state_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'état pour debug"""
        return {
            'agent_id': self.agent_id,
            'level': self.level,
            'food': self.get_food_count(),
            'food_status': {
                'critical': self.is_food_critical(),
                'sufficient': self.is_food_sufficient(),
                'abundant': self.is_food_abundant()
            },
            'position': self.position,
            'orientation': self.direction,
            'role': self.get_role(),
            'inventory': self.inventory,
            'missing_resources': self.has_missing_resources(),
            'can_incant': self.can_incant(),
            'can_coordinate': self.can_coordinate(),
            'should_reproduce': self.should_reproduce(),
            'reproduction_status': {
                'triggered': self.reproduction_triggered,
                'completed': self.reproduction_completed
            },
            'needs_look': self.needs_look,
            'command_pending': self.command_already_send,
            'required_players': self.get_required_player_count()
        }