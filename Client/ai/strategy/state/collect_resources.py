##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## collect_resources
##

import time
from typing import Optional, Any, Dict, List
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder
from config import Constants, CommandType
from utils.logger import logger

class CollectResourcesState(State):
    """
    État de collecte de ressources (pierres) pour l'incantation.
    
    Objectifs:
    1. Collecter les ressources manquantes pour le niveau actuel
    2. Prioriser selon les besoins d'incantation
    3. Gérer la nourriture en parallèle (seuil de sécurité)
    4. Optimiser les trajets de collecte
    """
    
    def __init__(self, planner):
        super().__init__(planner)
        self.pathfinder = Pathfinder()
        self.resource_target = None
        self.movement_commands = []
        self.current_priority_resource = None
        self.collection_attempts = 0
        self.max_collection_attempts = 3
        self.failed_resources = set()
        self.last_inventory_check = time.time()
        self.inventory_check_interval = 12.0
        self.resources_collected = {}
        self.collection_session_start = time.time()
        logger.info(f"[CollectResourcesState] ⚒️ Collecte ressources niveau {self.state.level} activée")

    def execute(self) -> Optional[Any]:
        """Logique de collecte AMÉLIORÉE avec priorité linemate."""
        current_time = time.time()
        current_food = self.state.get_food_count()
        safety_threshold = self._get_food_safety_threshold()
        if current_food <= safety_threshold:
            logger.warning(f"[CollectResourcesState] Nourriture insuffisante ({current_food} <= {safety_threshold})")
            return None
        linemate_action = self._force_collect_linemate_if_visible()
        if linemate_action:
            return linemate_action
        if self._should_check_inventory(current_time):
            logger.debug("[CollectResourcesState] Vérification inventaire")
            self.last_inventory_check = current_time
            return self.cmd_mgr.inventory()
        if self._needs_vision_update():
            logger.debug("[CollectResourcesState] Mise à jour vision")
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()
        needed_resource = self._get_needed_resource_on_tile()
        if needed_resource:
            logger.info(f"[CollectResourcesState] ⚒️ {needed_resource} trouvé ici, collecte immédiate")
            return self.cmd_mgr.take(needed_resource)
        priority_target = self._find_priority_resource_target()
        if priority_target:
            if priority_target != self.resource_target:
                self.resource_target = priority_target
                self.current_priority_resource = priority_target.resource_type
                self.movement_commands = self._plan_resource_collection_path(priority_target)
                distance = abs(priority_target.rel_position[0]) + abs(priority_target.rel_position[1])
                logger.info(f"[CollectResourcesState] 🎯 Cible {priority_target.resource_type} à distance {distance}")
            if self.movement_commands:
                next_cmd = self.movement_commands.pop(0)
                return self._execute_movement_command(next_cmd)
        if self._all_resources_collected():
            logger.info("[CollectResourcesState] ✅ Toutes les ressources collectées!")
            return None
        return self._explore_for_resources()

    def _get_food_safety_threshold(self) -> int:
        """Seuil de sécurité RÉDUIT pour continuer la collecte."""
        base = 15
        if self.state.level >= 7:
            return int(base * 1.4)
        elif self.state.level >= 4:
            return int(base * 1.2)
        return base

    def _should_check_inventory(self, current_time: float) -> bool:
        """Détermine si un check d'inventaire est nécessaire."""
        if self.context.get('needs_inventory_check', False):
            self.context['needs_inventory_check'] = False
            return True
        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= self.inventory_check_interval

    def _needs_vision_update(self) -> bool:
        """Détermine si une mise à jour de vision est nécessaire."""
        if self.context.get('needs_vision_update', False):
            return True
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return True
        if getattr(self.state, 'needs_look', False):
            return True
        return False

    def _get_needed_resource_on_tile(self) -> Optional[str]:
        """Trouve une ressource nécessaire présente sur la tuile actuelle."""
        vision = self.state.get_vision()
        needed_resources = self._get_missing_resources()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                for resource in needed_resources:
                    if resource in data.resources and data.resources[resource] > 0:
                        return resource
        return None

    def _get_missing_resources(self) -> Dict[str, int]:
        """Retourne les ressources manquantes pour l'incantation actuelle."""
        requirements = self.state.get_incantation_requirements()
        inventory = self.state.get_inventory()
        missing = {}
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current
        return missing

    def _find_priority_resource_target(self):
        """Trouve la ressource prioritaire la plus proche."""
        missing_resources = self._get_missing_resources()
        if not missing_resources:
            return None
        vision = self.state.get_vision()
        visible_resources = vision.get_visible_resources()
        priority_order = self._get_resource_priority_order(missing_resources)
        for resource in priority_order:
            if resource in self.failed_resources:
                continue
            positions = visible_resources.get(resource, [])
            valid_positions = [pos for pos in positions if pos != (0, 0)]
            if valid_positions:
                closest_pos = min(valid_positions, key=lambda pos: abs(pos[0]) + abs(pos[1]))
                class ResourceTarget:
                    def __init__(self, pos, res_type):
                        self.rel_position = pos
                        self.resource_type = res_type
                return ResourceTarget(closest_pos, resource)
        return None

    def _get_resource_priority_order(self, missing_resources: Dict[str, int]) -> List[str]:
        """Ordre de priorité OPTIMISÉ pour incantation rapide."""
        if hasattr(self, 'state') and getattr(self.state, 'level', 1) == 1:
            if Constants.LINEMATE.value in missing_resources:
                priority_list = [Constants.LINEMATE.value]
                logger.info(f"[CollectResourcesState] 🔥 PRIORITÉ NIVEAU 1: {priority_list}")
                return priority_list
        rarity_order = [
            Constants.THYSTAME.value,
            Constants.PHIRAS.value,
            Constants.MENDIANE.value,
            Constants.SIBUR.value,
            Constants.DERAUMERE.value,
            Constants.LINEMATE.value
        ]
        priority_list = [res for res in rarity_order if res in missing_resources]
        logger.debug(f"[CollectResourcesState] Priorité ressources: {priority_list}")
        return priority_list

    def _plan_resource_collection_path(self, target):
        """Planifie le chemin optimal vers la ressource."""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return []
        commands = self.pathfinder.get_commands_to_target(
            target,
            self.state.get_orientation(),
            vision_data
        )
        max_commands = 10
        return commands[:max_commands] if commands else []

    def _force_collect_linemate_if_visible(self) -> Optional[Any]:
        """FORCE la collecte de linemate si visible (priorité absolue niveau 1)."""
        if self.state.level != 1:
            return None
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                if Constants.LINEMATE.value in data.resources and data.resources[Constants.LINEMATE.value] > 0:
                    logger.info("[CollectResourcesState] 🔥 LINEMATE ICI! Collecte forcée")
                    return self.cmd_mgr.take(Constants.LINEMATE.value)
        return None

    def _check_completion_frequently(self) -> bool:
        """Vérification FRÉQUENTE de la complétion pour transition rapide."""
        requirements = self.state.get_incantation_requirements()
        inventory = self.state.get_inventory()
        missing = {}
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current
        is_complete = len(missing) == 0
        if is_complete:
            logger.info("[CollectResourcesState] ✅ RESSOURCES COMPLÈTES! Transition immédiate")
            from ai.strategy.state.incantation import IncantationState
            new_state = IncantationState(self.planner)
            self.planner.fsm.transition_to(new_state)
            return True
        else:
            logger.debug(f"[CollectResourcesState] Encore manquant: {missing}")
            return False

    def _execute_movement_command(self, command_type: CommandType):
        """Exécute une commande de mouvement."""
        if command_type == CommandType.FORWARD:
            return self.cmd_mgr.forward()
        elif command_type == CommandType.LEFT:
            return self.cmd_mgr.left()
        elif command_type == CommandType.RIGHT:
            return self.cmd_mgr.right()
        else:
            logger.warning(f"[CollectResourcesState] Commande inconnue: {command_type}")
            return None

    def _explore_for_resources(self):
        """Exploration pour trouver des ressources."""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return self.cmd_mgr.look()
        exploration_cmd = self.pathfinder.get_exploration_direction(
            self.state.get_orientation(),
            vision_data
        )
        logger.debug(f"[CollectResourcesState] 🔍 Exploration pour ressources: {exploration_cmd}")
        return self._execute_movement_command(exploration_cmd)

    def _all_resources_collected(self) -> bool:
        """Vérifie si toutes les ressources nécessaires sont collectées."""
        missing = self._get_missing_resources()
        is_complete = len(missing) == 0
        if is_complete:
            session_time = time.time() - self.collection_session_start
            logger.info(f"[CollectResourcesState] ✅ Collection complète en {session_time:.1f}s: {self.resources_collected}")
        return is_complete

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes."""
        if command_type == CommandType.TAKE:
            resource = self.current_priority_resource
            if resource:
                self.resources_collected[resource] = self.resources_collected.get(resource, 0) + 1
                logger.info(f"[CollectResourcesState] ✅ {resource} collecté! Total: {self.resources_collected}")
                vision = self.state.get_vision()
                vision.remove_resource_at((0, 0), resource)
                self.resource_target = None
                self.movement_commands.clear()
                self.collection_attempts = 0
                self.current_priority_resource = None
                self.failed_resources.discard(resource)
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True
        elif command_type == CommandType.INVENTORY:
            self.last_inventory_check = time.time()

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes."""
        if command_type == CommandType.TAKE:
            self.collection_attempts += 1
            resource = self.current_priority_resource
            logger.warning(f"[CollectResourcesState] ❌ Échec collecte {resource}, tentative {self.collection_attempts}")
            if resource and self.collection_attempts >= 2:
                self.failed_resources.add(resource)
                logger.warning(f"[CollectResourcesState] {resource} marquée comme inaccessible temporairement")
            self.resource_target = None
            self.movement_commands.clear()
            self.context['needs_vision_update'] = True
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            stuck_counter = self.context.get('stuck_counter', 0) + 1
            self.context['stuck_counter'] = stuck_counter
            if stuck_counter >= 2:
                logger.warning("[CollectResourcesState] Mouvements bloqués, reset cible")
                self.resource_target = None
                self.movement_commands.clear()

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements."""
        if event == Event.FOOD_EMERGENCY:
            logger.warning("[CollectResourcesState] Urgence alimentaire, arrêt collecte ressources")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)
        elif event == Event.FOOD_LOW:
            current_food = self.state.get_food_count()
            threshold = self._get_food_safety_threshold()
            if current_food <= threshold:
                logger.info(f"[CollectResourcesState] Nourriture faible ({current_food} <= {threshold}), collecte nourriture")
                from ai.strategy.state.collect_food import CollectFoodState
                return CollectFoodState(self.planner)
        elif event == Event.RESOURCES_COLLECTED:
            if self._all_resources_collected():
                logger.info("[CollectResourcesState] ✅ Ressources complètes, transition exploration")
                from ai.strategy.state.explore import ExploreState
                return ExploreState(self.planner)
        return None

    def on_enter(self):
        """Actions à l'entrée de l'état."""
        super().on_enter()
        missing = self._get_missing_resources()
        logger.info(f"[CollectResourcesState] ⚒️ ENTRÉE collecte ressources - Manquants: {missing}")
        self.resource_target = None
        self.movement_commands.clear()
        self.collection_attempts = 0
        self.failed_resources.clear()
        self.resources_collected.clear()
        self.collection_session_start = time.time()
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état."""
        super().on_exit()
        session_time = time.time() - self.collection_session_start
        logger.info(f"[CollectResourcesState] ✅ SORTIE collecte ressources - Durée: {session_time:.1f}s, Collecté: {self.resources_collected}")
        self.resource_target = None
        self.movement_commands.clear()
        self.failed_resources.clear()
