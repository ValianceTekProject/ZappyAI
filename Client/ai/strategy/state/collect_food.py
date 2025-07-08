##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## collect_food - État de collecte nourriture avec pathfinding corrigé
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder
from config import CommandType
from constant import (
    FoodThresholds, StateTransitionThresholds, GameplayConstants,
    ResourceNames
)
from utils.logger import logger


class CollectFoodState(State):
    """État de collecte de nourriture avec pathfinding corrigé vers ressources visibles"""

    def __init__(self, planner):
        super().__init__(planner)
        self.pathfinder = Pathfinder()
        self.food_target = None
        self.movement_commands = []
        self.collection_attempts = 0
        self.last_inventory_check = time.time()
        self.food_collected = 0
        self.collection_session_start = time.time()
        self.max_collection_time = 30.0
        self.emergency_mode = self._is_emergency_mode()
        
        current_food = self.state.get_food_count()
        logger.info(f"[CollectFoodState] Collecte nourriture activée - Food: {current_food}, Mode urgence: {self.emergency_mode}")

    def execute(self) -> Optional[Any]:
        """Logique de collecte optimisée avec pathfinding corrigé"""
        current_time = time.time()
        current_food = self.state.get_food_count()

        if self._update_emergency_mode(current_food):
            if current_time - self.collection_session_start > self.max_collection_time:
                logger.warning("[CollectFoodState] Timeout collecte urgente")
                return self._force_transition()

        if self._should_exit_collection(current_food):
            logger.info(f"[CollectFoodState] Nourriture suffisante ({current_food})")
            return self._transition_to_next_priority()

        if self._should_check_inventory(current_time):
            self.last_inventory_check = current_time
            return self.cmd_mgr.inventory()

        if self._needs_vision_update():
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()

        if self._food_on_current_tile():
            logger.info("[CollectFoodState] Nourriture trouvée ici!")
            return self.cmd_mgr.take(ResourceNames.FOOD)

        if self.movement_commands:
            next_cmd = self.movement_commands.pop(0)
            return self._execute_movement_command(next_cmd)

        food_target = self._find_best_food_target_with_pathfinder()
        if food_target:
            if food_target != self.food_target:
                self.food_target = food_target
                self.movement_commands = self._plan_food_collection_path(food_target)
                distance = abs(food_target.rel_position[0]) + abs(food_target.rel_position[1])
                priority = "URGENTE" if self.emergency_mode else "normale"
                logger.info(f"[CollectFoodState] Cible {priority} à distance {distance}: {food_target.rel_position}")

            if self.movement_commands:
                next_cmd = self.movement_commands.pop(0)
                return self._execute_movement_command(next_cmd)

        return self._explore_for_food()

    def _find_best_food_target_with_pathfinder(self):
        """Trouve la meilleure cible de nourriture en utilisant le pathfinder"""
        vision = self.state.get_vision()
        vision_data = vision.last_vision_data
        
        if not vision_data:
            logger.debug("[CollectFoodState] Pas de données de vision disponibles")
            return None
        
        food_target = self.pathfinder.find_target_in_vision(vision_data, ResourceNames.FOOD)
        
        if food_target:
            logger.debug(f"[CollectFoodState] Nourriture détectée à {food_target.rel_position} (distance: {food_target.distance})")
            return food_target
        else:
            logger.debug("[CollectFoodState] Aucune nourriture visible dans la vision")
            return None

    def _is_emergency_mode(self) -> bool:
        """Détermine si on est en mode urgence"""
        return self.state.get_food_count() <= FoodThresholds.CRITICAL

    def _update_emergency_mode(self, current_food: int) -> bool:
        """Met à jour le mode urgence selon la nourriture actuelle"""
        new_emergency = current_food <= FoodThresholds.CRITICAL
        if new_emergency != self.emergency_mode:
            self.emergency_mode = new_emergency
            mode_text = "URGENCE" if new_emergency else "normal"
            logger.warning(f"[CollectFoodState] Mode changé: {mode_text}")
        return self.emergency_mode

    def _should_exit_collection(self, current_food: int) -> bool:
        """Détermine si on doit sortir de la collecte de nourriture"""
        if self.emergency_mode:
            return current_food >= StateTransitionThresholds.EMERGENCY_EXIT_THRESHOLD
        else:
            return current_food >= StateTransitionThresholds.FOOD_TO_EXPLORATION_THRESHOLD

    def _should_check_inventory(self, current_time: float) -> bool:
        """Détermine si un check d'inventaire est nécessaire"""
        if self.context.get('needs_inventory_check', False):
            self.context['needs_inventory_check'] = False
            return True
        
        interval = 4.0 if self.emergency_mode else GameplayConstants.INVENTORY_CHECK_INTERVAL
        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= interval

    def _needs_vision_update(self) -> bool:
        """Détermine si une mise à jour de vision est nécessaire"""
        return (
            self.context.get('needs_vision_update', False) or
            not self.state.get_vision().last_vision_data or
            getattr(self.state, 'needs_look', False)
        )

    def _food_on_current_tile(self) -> bool:
        """Vérifie si de la nourriture est présente sur la tuile actuelle"""
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return ResourceNames.FOOD in data.resources and data.resources[ResourceNames.FOOD] > 0
        return False

    def _plan_food_collection_path(self, target):
        """Planifie le chemin vers la nourriture avec priorité urgence"""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return []
            
        commands = self.pathfinder.get_commands_to_target(
            target,
            self.state.get_orientation(),
            vision_data
        )
        
        max_commands = 4 if self.emergency_mode else 6
        return commands[:max_commands] if commands else []

    def _execute_movement_command(self, command_type: CommandType):
        """Exécute une commande de mouvement"""
        command_map = {
            CommandType.FORWARD: self.cmd_mgr.forward,
            CommandType.LEFT: self.cmd_mgr.left,
            CommandType.RIGHT: self.cmd_mgr.right,
        }
        
        command_func = command_map.get(command_type)
        if command_func:
            return command_func()
        
        return None

    def _explore_for_food(self):
        """Exploration ciblée pour trouver de la nourriture avec urgence"""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return self.cmd_mgr.look()
            
        exploration_cmd = self.pathfinder.get_exploration_direction(
            self.state.get_orientation(),
            vision_data
        )
        
        return self._execute_movement_command(exploration_cmd)

    def _transition_to_next_priority(self) -> Optional[Any]:
        """Transition vers la prochaine priorité selon la situation"""
        current_food = self.state.get_food_count()
        
        if self.state.should_reproduce():
            logger.info("[CollectFoodState] → Reproduction prioritaire")
            from ai.strategy.state.reproduction import ReproductionState
            new_state = ReproductionState(self.planner)
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()
        
        if (not self.state.has_missing_resources() and 
            current_food >= StateTransitionThresholds.MIN_FOOD_FOR_COORDINATION):
            
            if self.state.level == 1:
                logger.info("[CollectFoodState] → Incantation solo niveau 1")
                from ai.strategy.state.incantation import IncantationState
                new_state = IncantationState(self.planner)
            else:
                logger.info("[CollectFoodState] → Coordination incantation")
                from ai.strategy.state.coordination_incantation import CoordinateIncantationState
                new_state = CoordinateIncantationState(self.planner)
            
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()
        
        if (self.state.has_missing_resources() and 
            current_food >= StateTransitionThresholds.RESOURCES_TO_FOOD_THRESHOLD):
            logger.info("[CollectFoodState] → Collecte ressources")
            from ai.strategy.state.collect_resources import CollectResourcesState
            new_state = CollectResourcesState(self.planner)
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()
        
        logger.info("[CollectFoodState] → Exploration")
        from ai.strategy.state.explore import ExploreState
        new_state = ExploreState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _force_transition(self) -> Optional[Any]:
        """Force une transition pour éviter le blocage"""
        current_food = self.state.get_food_count()
        
        if current_food <= FoodThresholds.CRITICAL:
            logger.error("[CollectFoodState] → Mode urgence critique")
            from ai.strategy.state.emergency import EmergencyState
            new_state = EmergencyState(self.planner)
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()

        return self._transition_to_next_priority()

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes avec priorité nourriture"""
        if command_type == CommandType.TAKE:
            self.food_collected += 1
            current_food = self.state.get_food_count()
            priority = "CRITIQUE" if self.emergency_mode else "normale"
            logger.info(f"[CollectFoodState] Nourriture {priority} collectée! Total session: {self.food_collected}, Inventaire: {current_food}")
            
            vision = self.state.get_vision()
            vision.remove_resource_at((0, 0), ResourceNames.FOOD)
            self.food_target = None
            self.movement_commands.clear()
            self.collection_attempts = 0
            
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True
            
        elif command_type == CommandType.INVENTORY:
            self.last_inventory_check = time.time()

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes"""
        if command_type == CommandType.TAKE:
            self.collection_attempts += 1
            logger.warning(f"[CollectFoodState] Échec collecte nourriture, tentative {self.collection_attempts}")
            self.food_target = None
            self.movement_commands.clear()
            self.context['needs_vision_update'] = True
            
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            stuck_counter = self.context.get('stuck_counter', 0) + 1
            self.context['stuck_counter'] = stuck_counter
            if stuck_counter >= GameplayConstants.MAX_STUCK_ATTEMPTS:
                self.food_target = None
                self.movement_commands.clear()

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements avec priorité nourriture"""
        if event == Event.FOOD_EMERGENCY:
            self.emergency_mode = True
            logger.error("[CollectFoodState] Mode urgence activé!")
            
        elif event == Event.FOOD_SUFFICIENT:
            current_food = self.state.get_food_count()
            if self._should_exit_collection(current_food):
                logger.info(f"[CollectFoodState] Sortie (food: {current_food})")
                return self._transition_to_next_priority()
                
        return None

    def on_enter(self):
        """Actions à l'entrée de l'état"""
        super().on_enter()
        current_food = self.state.get_food_count()
        
        logger.info(f"[CollectFoodState] ENTRÉE collecte nourriture")
        logger.info(f"[CollectFoodState] Food: {current_food}, Seuils: critique={FoodThresholds.CRITICAL}, suffisant={FoodThresholds.SUFFICIENT}")
        
        self.food_target = None
        self.movement_commands.clear()
        self.collection_attempts = 0
        self.food_collected = 0
        self.collection_session_start = time.time()
        self.emergency_mode = self._is_emergency_mode()
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état"""
        super().on_exit()
        duration = time.time() - self.collection_session_start
        current_food = self.state.get_food_count()
        
        logger.info(f"[CollectFoodState] SORTIE collecte nourriture")
        logger.info(f"[CollectFoodState] Durée: {duration:.1f}s, Collecté: {self.food_collected}, Food final: {current_food}")
        
        self.food_target = None
        self.movement_commands.clear()