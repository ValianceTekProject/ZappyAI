##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## game_state amélioré pour support FSM complet
##

import math
import time
from typing import Tuple, Dict, Optional
from config import CommandType, CommandStatus, Orientation, Constants
from protocol.commands import Command
from protocol.parser import Parser
from utils.logger import logger
from utils.vision import Vision

class GameState:
    def __init__(self, team_id: str, dimension_map: Tuple[int, int], agent_id: int = 0):
        """
        Initialise l'état du jeu pour un agent avec support FSM complet.
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
        self.agent_id = agent_id
        self.dimension_map = dimension_map
        self.position = (0, 0)
        self.direction = Orientation.SOUTH

        self.vision = Vision()
        self.parser = Parser()

        # Flags de gestion des commandes
        self.command_already_send = False
        self.needs_look = False
        self.needs_repro = False

        # Seuils de nourriture adaptatifs
        self.food_thresholds = self._calculate_food_thresholds()
        
        # Rôle de l'agent (pour future coordination)
        self.role = "survivor"  # survivor, incanter, helper
        
        # Historique et statistiques
        self.last_food_update = time.time()
        self.food_consumption_history = []
        self.command_history = []
        
        logger.info(f"[GameState] Agent {agent_id} initialisé - Team: {team_id}, Role: {self.role}")

    def _calculate_food_thresholds(self) -> Dict[str, int]:
        """Calcule les seuils de nourriture selon le niveau."""
        base_critical = 8
        base_safe = 20
        base_abundant = 35
        
        if self.level >= 7:
            multiplier = 2.5
        elif self.level >= 4:
            multiplier = 1.8
        else:
            multiplier = 1.0
            
        return {
            'critical': int(base_critical * multiplier),
            'safe': int(base_safe * multiplier),
            'abundant': int(base_abundant * multiplier)
        }

    def update(self, command: Command):
        """
        Met à jour l'état du jeu après l'exécution d'une commande.
        Version améliorée avec support FSM complet.
        """
        self.command_already_send = False
        
        # Ajouter à l'historique
        self.command_history.append({
            'command': command.type,
            'status': command.status,
            'timestamp': time.time(),
            'response': command.response
        })
        
        # Limiter l'historique
        if len(self.command_history) > 50:
            self.command_history.pop(0)

        # Gestion spéciale des échecs d'incantation
        if command.type == CommandType.INCANTATION and command.status == CommandStatus.FAILED:
            self._handle_incantation_failure(command)
            return

        # Gestion des échecs de TAKE
        if command.type == CommandType.TAKE and command.status == CommandStatus.FAILED:
            self.needs_look = True
            logger.warning(f"[GameState] Take {command.args[0] if command.args else 'unknown'} échoué")

        # Ignorer les commandes non-SUCCESS
        if command.status != CommandStatus.SUCCESS:
            logger.debug(f"[GameState] Commande {command.type} ignorée: {command.status}")
            return

        # Traitement des commandes réussies
        if command.type == CommandType.INVENTORY:
            old_food = self.inventory.get('food', 0)
            self.inventory = self.parser.parse_inventory_response(command.response)
            new_food = self.inventory.get('food', 0)
            
            # Détecter changement de nourriture
            if new_food != old_food:
                self._update_food_history(old_food, new_food)
            
            logger.debug(f"[GameState] Inventaire mis à jour: food={new_food}")

        elif command.type == CommandType.LOOK:
            self.vision.process_vision(
                command.response,
                agent_pos=self.position,
                agent_orientation=self.direction
            )
            self.needs_look = False
            logger.debug("[GameState] Vision mise à jour")

        elif command.type == CommandType.INCANTATION:
            logger.info(f"[GameState] ✅ Élévation réussie! Nouveau niveau: {self.level}")
            self.needs_look = True
            self.needs_repro = True
            self._recalculate_thresholds()

        elif command.type == CommandType.FORWARD:
            self.update_position_after_forward()
            self.vision.clear()
            self.needs_look = True
            logger.debug(f"[GameState] Position mise à jour: {self.position}")

        elif command.type in (CommandType.LEFT, CommandType.RIGHT):
            self.update_orientation_after_turn(command.type)
            self.vision.clear()
            self.needs_look = True
            logger.debug(f"[GameState] Orientation mise à jour: {self.direction}")

        elif command.type == CommandType.TAKE and command.args:
            resource = command.args[0]
            logger.info(f"[GameState] ✅ {resource} ramassé")
            
            # Mise à jour automatique vision et inventaire
            self.vision.remove_resource_at((0, 0), resource)
            self._update_inventory_after_take(resource)
            self.needs_look = False  # Éviter LOOK inutile

        elif command.type == CommandType.SET and command.args:
            resource = command.args[0]
            logger.info(f"[GameState] ✅ {resource} déposé")
            
            # Mise à jour automatique vision et inventaire
            self.vision.add_resource_at((0, 0), resource)
            self._update_inventory_after_set(resource)
            self.needs_look = False  # Éviter LOOK inutile

    def _handle_incantation_failure(self, command: Command):
        """Gère l'échec d'incantation avec log détaillé."""
        next_level = self.level + 1
        requirements = self.get_incantation_requirements()
        needed_players = self.get_required_player_count()
        players_here = self._players_on_current_tile()
        ground = self._get_resources_at_current_position()
        
        missing_resources = {}
        for res, qty in requirements.items():
            on_ground = ground.get(res, 0)
            if on_ground < qty:
                missing_resources[res] = (qty, on_ground)
        
        players_missing = max(0, needed_players - players_here)
        
        logger.error(
            f"[GameState] 💥 INCANTATION ÉCHEC {self.level} → {next_level}: "
            f"Joueurs: {players_here}/{needed_players} (manque: {players_missing}), "
            f"Sol: {ground}, Manque: {missing_resources}, "
            f"Inventaire: {self.inventory}"
        )
        
        self.needs_look = True
        self.needs_repro = False

    def _update_food_history(self, old_food: int, new_food: int):
        """Met à jour l'historique de consommation de nourriture."""
        now = time.time()
        change = new_food - old_food
        
        self.food_consumption_history.append({
            'timestamp': now,
            'old_food': old_food,
            'new_food': new_food,
            'change': change
        })
        
        # Limiter l'historique
        if len(self.food_consumption_history) > 20:
            self.food_consumption_history.pop(0)
        
        self.last_food_update = now
        
        if change < 0:
            logger.debug(f"[GameState] Consommation nourriture: {change} (reste: {new_food})")

    def _update_inventory_after_take(self, resource: str):
        """Met à jour l'inventaire après un TAKE réussi."""
        if resource in self.inventory:
            self.inventory[resource] += 1
        else:
            self.inventory[resource] = 1

    def _update_inventory_after_set(self, resource: str):
        """Met à jour l'inventaire après un SET réussi."""
        if resource in self.inventory and self.inventory[resource] > 0:
            self.inventory[resource] -= 1

    def _recalculate_thresholds(self):
        """Recalcule les seuils après changement de niveau."""
        old_thresholds = self.food_thresholds.copy()
        self.food_thresholds = self._calculate_food_thresholds()
        
        logger.info(f"[GameState] Seuils niveau {self.level}: {old_thresholds} → {self.food_thresholds}")

    def force_unlock(self):
        """Force le déblocage en cas d'agent bloqué."""
        logger.warning("[GameState] 🔓 FORCE UNLOCK - Reset flags bloquants")
        self.command_already_send = False
        self.needs_look = True

    # === MÉTHODES POUR LA FSM ===

    def get_food_count(self) -> int:
        """Retourne la quantité de nourriture dans l'inventaire."""
        return self.inventory.get(Constants.FOOD.value, 0)

    def get_inventory(self) -> Dict[str, int]:
        """Retourne l'inventaire complet."""
        return self.inventory.copy()

    def get_player_level(self) -> int:
        """Retourne le niveau du joueur."""
        return self.level

    def get_position(self) -> Tuple[int, int]:
        """Retourne la position courante."""
        return self.position

    def get_orientation(self) -> int:
        """Retourne l'orientation courante."""
        return self.direction

    def get_vision(self) -> Vision:
        """Retourne l'objet Vision."""
        return self.vision

    def has_missing_resources(self) -> bool:
        """Vérifie si des ressources manquent pour l'incantation."""
        requirements = self.get_incantation_requirements()
        return any(self.inventory.get(res, 0) < qty for res, qty in requirements.items())

    def can_incant(self) -> bool:
        """Vérifie si l'agent peut lancer une incantation."""
        # Vérifier ressources
        requirements = self.get_incantation_requirements()
        if any(self.inventory.get(res, 0) < qty for res, qty in requirements.items()):
            return False
        
        # Vérifier nombre de joueurs
        return self._players_on_current_tile() >= self.get_required_player_count()

    def get_incantation_requirements(self) -> Dict[str, int]:
        """Retourne les ressources nécessaires pour l'incantation actuelle."""
        level_requirements = {
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
        return level_requirements.get(self.level, {})

    def get_required_player_count(self) -> int:
        """Retourne le nombre de joueurs requis pour l'incantation."""
        player_requirements = {1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 6, 7: 6}
        return player_requirements.get(self.level, 1)

    def update_position_after_forward(self):
        """Met à jour la position après un mouvement forward."""
        x, y = self.position
        if self.direction == Orientation.NORTH:
            y -= 1
        elif self.direction == Orientation.EAST:
            x += 1
        elif self.direction == Orientation.SOUTH:
            y += 1
        elif self.direction == Orientation.WEST:
            x -= 1
        
        # Gérer le wrap-around du monde toroïdal
        max_x, max_y = self.dimension_map
        x = x % max_x
        y = y % max_y
        
        self.position = (x, y)

    def update_orientation_after_turn(self, turn_cmd: CommandType):
        """Met à jour l'orientation après une rotation."""
        if turn_cmd == CommandType.LEFT:
            self.direction = (self.direction - 1) % 4
        elif turn_cmd == CommandType.RIGHT:
            self.direction = (self.direction + 1) % 4

    def _get_resources_at_current_position(self) -> Dict[str, int]:
        """Retourne les ressources sur la tuile actuelle selon la vision."""
        if not self.vision.last_vision_data:
            return {}
        
        for data in self.vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return dict(data.resources)
        return {}

    def _players_on_current_tile(self) -> int:
        """Retourne le nombre de joueurs sur la tuile actuelle."""
        for data in self.vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return data.players
        return 1  # Au minimum nous-même

    # === MÉTHODES DE DEBUG ET STATISTIQUES ===

    def get_food_consumption_rate(self) -> float:
        """Estime le taux de consommation de nourriture."""
        if len(self.food_consumption_history) < 2:
            return 126.0  # Valeur par défaut du jeu
        
        # Calculer les intervalles entre consommations
        intervals = []
        for i in range(1, len(self.food_consumption_history)):
            prev = self.food_consumption_history[i-1]
            curr = self.food_consumption_history[i]
            
            if curr['change'] < 0 and prev['change'] < 0:
                interval = curr['timestamp'] - prev['timestamp']
                if 100 < interval < 200:  # Filtrer valeurs aberrantes
                    intervals.append(interval)
        
        return sum(intervals) / len(intervals) if intervals else 126.0

    def get_state_summary(self) -> Dict[str, any]:
        """Retourne un résumé de l'état pour debug."""
        return {
            'agent_id': self.agent_id,
            'level': self.level,
            'food': self.get_food_count(),
            'food_thresholds': self.food_thresholds,
            'position': self.position,
            'orientation': self.direction,
            'role': self.role,
            'inventory': self.inventory,
            'missing_resources': self.has_missing_resources(),
            'can_incant': self.can_incant(),
            'needs_look': self.needs_look,
            'command_pending': self.command_already_send,
            'last_commands': [cmd['command'].value for cmd in self.command_history[-3:]]
        }