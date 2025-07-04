##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## collect_resources - État de collecte de ressources optimisé
##

import time
from typing import Optional, Any, Dict, List
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder
from config import Constants, CommandType
from constant import (
    StateTransitionThresholds, GameplayConstants, TimingConstants,
    IncantationRequirements
)
from utils.logger import logger

class CollectResourcesState(State):
    """État de collecte de ressources optimisé avec gestion des boucles infinies."""
    
    def __init__(self, planner):
        super().__init__(planner)
        self.pathfinder = Pathfinder()
        self.resource_target = None
        self.movement_commands = []
        self.current_priority_resource = None
        self.collection_attempts = 0
        self.max_collection_attempts = TimingConstants.MAX_COLLECTION_ATTEMPTS
        self.failed_resources = set()
        self.last_inventory_check = time.time()
        self.inventory_check_interval = GameplayConstants.INVENTORY_CHECK_INTERVAL
        self.resources_collected = {}
        self.collection_session_start = time.time()
        self.stuck_prevention_counter = 0
        self.max_stuck_attempts = GameplayConstants.MAX_STUCK_ATTEMPTS
        self.max_collection_time = 30.0  # Temps maximum en collecte
        logger.info(f"[CollectResourcesState] ⚒️ Collecte ressources niveau {self.state.level} activée")

    def execute(self) -> Optional[Any]:
        """
        Logique de collecte avec protection renforcée contre les boucles infinies.
        """
        current_time = time.time()
        current_food = self.state.get_food_count()
        
        # Timeout global pour éviter de rester bloqué en collecte
        if current_time - self.collection_session_start > self.max_collection_time:
            logger.warning("[CollectResourcesState] Timeout collecte, transition forcée")
            return self._force_transition()
        
        # Seuil de sécurité alimentaire
        safety_threshold = StateTransitionThresholds.FOOD_LOW_THRESHOLD
        
        if current_food <= safety_threshold:
            logger.warning(f"[CollectResourcesState] Nourriture critique ({current_food} <= {safety_threshold})")
            return self._transition_to_food_collection()

        # Vérification critique : Si toutes les ressources sont collectées
        if self._all_resources_collected():
            logger.info("[CollectResourcesState] ✅ TOUTES RESSOURCES COLLECTÉES!")
            return self._transition_to_incantation()

        # Vérifications périodiques
        if self._should_check_inventory(current_time):
            logger.debug("[CollectResourcesState] Vérification inventaire")
            self.last_inventory_check = current_time
            return self.cmd_mgr.inventory()
            
        if self._needs_vision_update():
            logger.debug("[CollectResourcesState] Mise à jour vision")
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()
            
        # Priorité absolue : collecter ressource sur la tuile actuelle
        needed_resource = self._get_needed_resource_on_tile()
        if needed_resource:
            logger.info(f"[CollectResourcesState] ⚒️ {needed_resource} trouvé ici")
            return self.cmd_mgr.take(needed_resource)
            
        # Recherche de cible avec mouvement effectif
        if not self.movement_commands:
            priority_target = self._find_priority_resource_target()
            if priority_target:
                self.resource_target = priority_target
                self.current_priority_resource = priority_target.resource_type
                self.movement_commands = self._plan_resource_collection_path(priority_target)
                distance = abs(priority_target.rel_position[0]) + abs(priority_target.rel_position[1])
                logger.info(f"[CollectResourcesState] 🎯 Cible {priority_target.resource_type} à distance {distance}")
                
        if self.movement_commands:
            next_cmd = self.movement_commands.pop(0)
            logger.debug(f"[CollectResourcesState] Déplacement: {next_cmd}")
            return self._execute_movement_command(next_cmd)
                
        # Protection contre le blocage - transition forcée si trop d'échecs
        self.stuck_prevention_counter += 1
        if self.stuck_prevention_counter >= self.max_stuck_attempts:
            logger.warning("[CollectResourcesState] Trop d'échecs, transition forcée")
            return self._force_transition()
            
        return self._explore_for_resources()

    def _should_check_inventory(self, current_time: float) -> bool:
        """Détermine si un check d'inventaire est nécessaire."""
        if self.context.get('needs_inventory_check', False):
            self.context['needs_inventory_check'] = False
            return True
        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= self.inventory_check_interval

    def _needs_vision_update(self) -> bool:
        """Détermine si une mise à jour de vision est nécessaire."""
        return (
            self.context.get('needs_vision_update', False) or
            not self.state.get_vision().last_vision_data or
            getattr(self.state, 'needs_look', False)
        )

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
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        inventory = self.state.get_inventory()
        missing = {}
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current
        return missing

    def _find_priority_resource_target(self):
        """Trouve la ressource prioritaire la plus proche avec validation."""
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
        """Ordre de priorité pour la collecte de ressources (rareté décroissante)."""
        rarity_order = [
            Constants.THYSTAME.value,
            Constants.PHIRAS.value,
            Constants.MENDIANE.value,
            Constants.SIBUR.value,
            Constants.DERAUMERE.value,
            Constants.LINEMATE.value
        ]
        
        priority_list = [res for res in rarity_order if res in missing_resources]
        logger.debug(f"[CollectResourcesState] Priorité: {priority_list}")
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
        
        max_commands = 6  # Réduit pour éviter les longs déplacements
        return commands[:max_commands] if commands else []

    def _all_resources_collected(self) -> bool:
        """Vérifie si toutes les ressources nécessaires sont collectées."""
        missing = self._get_missing_resources()
        is_complete = len(missing) == 0
        
        if is_complete:
            session_time = time.time() - self.collection_session_start
            logger.info(f"[CollectResourcesState] ✅ COMPLET! Durée: {session_time:.1f}s")
            
        return is_complete

    def _transition_to_incantation(self) -> Optional[Any]:
        """Transition vers l'incantation selon les règles du protocole."""
        if self.state.level == 1:
            logger.info("[CollectResourcesState] → Incantation solo niveau 1")
            from ai.strategy.state.incantation import IncantationState
            new_state = IncantationState(self.planner)
        else:
            required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
            logger.info(f"[CollectResourcesState] → Coordination niveau {self.state.level} ({required_players} joueurs)")
            from ai.strategy.state.coordination_incantation import CoordinateIncantationState
            new_state = CoordinateIncantationState(self.planner)
            
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _transition_to_food_collection(self) -> Optional[Any]:
        """Transition vers la collecte de nourriture."""
        logger.info("[CollectResourcesState] → Collecte nourriture")
        from ai.strategy.state.collect_food import CollectFoodState
        new_state = CollectFoodState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _force_transition(self) -> Optional[Any]:
        """Force une transition pour éviter de rester bloqué."""
        current_food = self.state.get_food_count()
        
        # Priorité 1: Nourriture si faible
        if current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
            return self._transition_to_food_collection()
        
        # Priorité 2: Incantation si ressources suffisantes
        if self._all_resources_collected():
            return self._transition_to_incantation()
        
        # Priorité 3: Exploration
        logger.info("[CollectResourcesState] → Exploration forcée")
        from ai.strategy.state.explore import ExploreState
        new_state = ExploreState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _execute_movement_command(self, command_type: CommandType) -> Optional[Any]:
        """Exécute une commande de mouvement."""
        command_map = {
            CommandType.FORWARD: self.cmd_mgr.forward,
            CommandType.LEFT: self.cmd_mgr.left,
            CommandType.RIGHT: self.cmd_mgr.right,
        }
        
        command_func = command_map.get(command_type)
        if command_func:
            return command_func()
        
        logger.warning(f"[CollectResourcesState] Commande inconnue: {command_type}")
        return None

    def _explore_for_resources(self) -> Optional[Any]:
        """Exploration pour trouver des ressources."""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return self.cmd_mgr.look()
            
        exploration_cmd = self.pathfinder.get_exploration_direction(
            self.state.get_orientation(),
            vision_data
        )
        
        logger.debug(f"[CollectResourcesState] 🔍 Exploration: {exploration_cmd}")
        return self._execute_movement_command(exploration_cmd)

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes."""
        if command_type == CommandType.TAKE:
            resource = self.current_priority_resource
            if resource:
                self.resources_collected[resource] = self.resources_collected.get(resource, 0) + 1
                logger.info(f"[CollectResourcesState] ✅ {resource} collecté! Total: {self.resources_collected}")
                
                # Mise à jour de la vision et reset des variables
                vision = self.state.get_vision()
                vision.remove_resource_at((0, 0), resource)
                self.resource_target = None
                self.movement_commands.clear()
                self.collection_attempts = 0
                self.current_priority_resource = None
                self.failed_resources.discard(resource)
                self.stuck_prevention_counter = 0
                
                # Vérification immédiate si on peut passer à l'incantation
                if self._all_resources_collected():
                    logger.info("[CollectResourcesState] 🎯 COMPLET après collecte!")
                    self._transition_to_incantation()
                    
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True
            self.stuck_prevention_counter = 0
            
        elif command_type == CommandType.INVENTORY:
            self.last_inventory_check = time.time()
            if self._all_resources_collected():
                logger.info("[CollectResourcesState] 🎯 COMPLET après inventaire!")
                self._transition_to_incantation()

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes."""
        if command_type == CommandType.TAKE:
            self.collection_attempts += 1
            resource = self.current_priority_resource
            logger.warning(f"[CollectResourcesState] ❌ Échec collecte {resource}")
            
            if resource and self.collection_attempts >= self.max_collection_attempts:
                self.failed_resources.add(resource)
                logger.warning(f"[CollectResourcesState] {resource} marquée inaccessible")
                
            self.resource_target = None
            self.movement_commands.clear()
            self.context['needs_vision_update'] = True
            
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.stuck_prevention_counter += 1
            if self.stuck_prevention_counter >= self.max_stuck_attempts:
                logger.warning("[CollectResourcesState] Mouvements bloqués")
                self.resource_target = None
                self.movement_commands.clear()

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements."""
        if event == Event.FOOD_EMERGENCY:
            logger.warning("[CollectResourcesState] Urgence alimentaire!")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)
            
        elif event == Event.FOOD_LOW:
            current_food = self.state.get_food_count()
            if current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
                logger.info(f"[CollectResourcesState] Nourriture faible ({current_food})")
                from ai.strategy.state.collect_food import CollectFoodState
                return CollectFoodState(self.planner)
                
        return None

    def on_enter(self):
        """Actions à l'entrée de l'état."""
        super().on_enter()
        missing = self._get_missing_resources()
        logger.info(f"[CollectResourcesState] ⚒️ ENTRÉE collecte - Manquants: {missing}")
        
        # Reset de tous les compteurs
        self.resource_target = None
        self.movement_commands.clear()
        self.collection_attempts = 0
        self.failed_resources.clear()
        self.resources_collected.clear()
        self.collection_session_start = time.time()
        self.stuck_prevention_counter = 0
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état."""
        super().on_exit()
        session_time = time.time() - self.collection_session_start
        total_collected = sum(self.resources_collected.values())
        logger.info(f"[CollectResourcesState] ✅ SORTIE collecte - Durée: {session_time:.1f}s, "
                   f"Collecté: {total_collected} ressources")
        
        # Nettoyage
        self.resource_target = None
        self.movement_commands.clear()
        self.failed_resources.clear()