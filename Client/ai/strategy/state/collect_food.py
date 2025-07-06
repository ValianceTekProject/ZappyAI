##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## collect_food
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder
from config import Constants, CommandType
from constant import FoodThresholds, StateTransitionThresholds, GameplayConstants
from utils.logger import logger


class CollectFoodState(State):
    """État de collecte de nourriture avec seuils centralisés et hystérésis."""

    def __init__(self, planner):
        """
        Initialise l'état de collecte de nourriture.
        
        Args:
            planner: Planificateur FSM
        """
        super().__init__(planner)
        self.pathfinder = Pathfinder()
        self.food_target = None
        self.movement_commands = []
        self.collection_attempts = 0
        self.last_inventory_check = time.time()
        self.food_collected = 0
        self.collection_session_start = time.time()
        self.max_collection_time = 25.0
        
        logger.info("[CollectFoodState] 🍖 Collecte de nourriture activée")

    def execute(self) -> Optional[Any]:
        """
        Logique de collecte de nourriture avec hystérésis pour éviter les boucles.
        
        Returns:
            Commande à exécuter ou None
        """
        current_time = time.time()
        current_food = self.state.get_food_count()

        if current_time - self.collection_session_start > self.max_collection_time:
            logger.warning("[CollectFoodState] Timeout collecte nourriture")
            return self._force_transition()

        if current_food >= StateTransitionThresholds.FOOD_TO_EXPLORATION_THRESHOLD:
            logger.info(f"[CollectFoodState] ✅ Nourriture suffisante ({current_food} >= {StateTransitionThresholds.FOOD_TO_EXPLORATION_THRESHOLD})")
            return self._transition_to_exploration()

        if self._should_check_inventory(current_time):
            self.last_inventory_check = current_time
            return self.cmd_mgr.inventory()

        if self._needs_vision_update():
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()

        if self._food_on_current_tile():
            logger.info("[CollectFoodState] 🍖 Nourriture trouvée ici")
            return self.cmd_mgr.take(Constants.FOOD.value)

        if self.movement_commands:
            next_cmd = self.movement_commands.pop(0)
            return self._execute_movement_command(next_cmd)

        food_target = self._find_best_food_target()
        if food_target:
            if food_target != self.food_target:
                self.food_target = food_target
                self.movement_commands = self._plan_food_collection_path(food_target)
                distance = abs(food_target.rel_position[0]) + abs(food_target.rel_position[1])
                logger.info(f"[CollectFoodState] 🎯 Nouvelle cible nourriture à distance {distance}")

            if self.movement_commands:
                next_cmd = self.movement_commands.pop(0)
                return self._execute_movement_command(next_cmd)

        return self._explore_for_food()

    def _should_check_inventory(self, current_time: float) -> bool:
        """
        Détermine si un check d'inventaire est nécessaire.
        
        Args:
            current_time: Temps actuel
            
        Returns:
            True si vérification nécessaire
        """
        if self.context.get('needs_inventory_check', False):
            self.context['needs_inventory_check'] = False
            return True
        
        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= GameplayConstants.INVENTORY_CHECK_INTERVAL

    def _needs_vision_update(self) -> bool:
        """
        Détermine si une mise à jour de vision est nécessaire.
        
        Returns:
            True si mise à jour nécessaire
        """
        return (
            self.context.get('needs_vision_update', False) or
            not self.state.get_vision().last_vision_data or
            getattr(self.state, 'needs_look', False)
        )

    def _food_on_current_tile(self) -> bool:
        """
        Vérifie si de la nourriture est présente sur la tuile actuelle.
        
        Returns:
            True si nourriture présente
        """
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return Constants.FOOD.value in data.resources and data.resources[Constants.FOOD.value] > 0
        return False

    def _find_best_food_target(self):
        """
        Trouve la meilleure cible de nourriture dans la vision.
        
        Returns:
            Cible de nourriture ou None
        """
        vision = self.state.get_vision()
        food_resources = vision.get_visible_resources().get(Constants.FOOD.value, [])
        
        if not food_resources:
            return None
        
        valid_targets = [pos for pos in food_resources if pos != (0, 0)]
        if not valid_targets:
            return None
            
        closest_pos = min(valid_targets, key=lambda pos: abs(pos[0]) + abs(pos[1]))
        
        class FoodTarget:
            def __init__(self, pos):
                self.rel_position = pos
                self.resource_type = Constants.FOOD.value
                
        return FoodTarget(closest_pos)

    def _plan_food_collection_path(self, target):
        """
        Planifie le chemin optimal vers la nourriture.
        
        Args:
            target: Cible de nourriture
            
        Returns:
            Liste des commandes de mouvement
        """
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return []
            
        commands = self.pathfinder.get_commands_to_target(
            target,
            self.state.get_orientation(),
            vision_data
        )
        
        max_commands = 6
        return commands[:max_commands] if commands else []

    def _execute_movement_command(self, command_type: CommandType):
        """
        Exécute une commande de mouvement.
        
        Args:
            command_type: Type de commande
            
        Returns:
            Commande exécutée
        """
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
        """
        Exploration ciblée pour trouver de la nourriture.
        
        Returns:
            Commande d'exploration
        """
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return self.cmd_mgr.look()
            
        exploration_cmd = self.pathfinder.get_exploration_direction(
            self.state.get_orientation(),
            vision_data
        )
        
        return self._execute_movement_command(exploration_cmd)

    def _transition_to_exploration(self) -> Optional[Any]:
        """
        Transition vers l'exploration.
        
        Returns:
            Exécution du nouvel état
        """
        from ai.strategy.state.explore import ExploreState
        new_state = ExploreState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _force_transition(self) -> Optional[Any]:
        """
        Force une transition pour éviter le blocage.
        
        Returns:
            Transition forcée
        """
        current_food = self.state.get_food_count()
        
        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            from ai.strategy.state.emergency import EmergencyState
            new_state = EmergencyState(self.planner)
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()

        return self._transition_to_exploration()

    def on_command_success(self, command_type, response=None):
        """
        Gestion du succès des commandes.
        
        Args:
            command_type: Type de commande
            response: Réponse du serveur
        """
        if command_type == CommandType.TAKE:
            self.food_collected += 1
            logger.info(f"[CollectFoodState] ✅ Nourriture collectée! Total: {self.food_collected}")
            
            vision = self.state.get_vision()
            vision.remove_resource_at((0, 0), Constants.FOOD.value)
            self.food_target = None
            self.movement_commands.clear()
            self.collection_attempts = 0
            
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True
            
        elif command_type == CommandType.INVENTORY:
            self.last_inventory_check = time.time()

    def on_command_failed(self, command_type, response=None):
        """
        Gestion des échecs de commandes.
        
        Args:
            command_type: Type de commande
            response: Réponse du serveur
        """
        if command_type == CommandType.TAKE:
            self.collection_attempts += 1
            logger.warning(f"[CollectFoodState] ❌ Échec collecte, tentative {self.collection_attempts}")
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
        """
        Gestion des événements.
        
        Args:
            event: Événement reçu
            
        Returns:
            Nouvel état ou None
        """
        if event == Event.FOOD_EMERGENCY:
            logger.warning("[CollectFoodState] Transition vers mode urgence!")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)
            
        elif event == Event.FOOD_SUFFICIENT:
            current_food = self.state.get_food_count()
            if current_food >= StateTransitionThresholds.FOOD_TO_EXPLORATION_THRESHOLD:
                logger.info(f"[CollectFoodState] ✅ Transition exploration (food: {current_food})")
                from ai.strategy.state.explore import ExploreState
                return ExploreState(self.planner)
                
        return None

    def on_enter(self):
        """Actions à l'entrée de l'état."""
        super().on_enter()
        current_food = self.state.get_food_count()
        
        logger.info(f"[CollectFoodState] 🍖 ENTRÉE collecte nourriture - Food: {current_food}")
        
        self.food_target = None
        self.movement_commands.clear()
        self.collection_attempts = 0
        self.food_collected = 0
        self.collection_session_start = time.time()
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état."""
        super().on_exit()
        duration = time.time() - self.collection_session_start
        
        logger.info(f"[CollectFoodState] ✅ SORTIE collecte nourriture - "
                   f"Durée: {duration:.1f}s, Collecté: {self.food_collected}")
        
        self.food_target = None
        self.movement_commands.clear()