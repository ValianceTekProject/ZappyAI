##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## emergency - État d'urgence avec constantes centralisées
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder, RelativeTarget
from config import CommandType
from constant import (
    FoodThresholds, StateTransitionThresholds, GameplayConstants,
    ResourceNames, TimingConstants
)
from utils.logger import logger


class EmergencyState(State):
    """État d'urgence critique - Survie immédiate avec priorité absolue"""
    
    def __init__(self, planner):
        super().__init__(planner)
        self.pathfinder = Pathfinder()
        self.emergency_target = None
        self.emergency_commands = []
        self.desperate_mode = False
        self.last_emergency_action = time.time()
        self.failed_attempts = 0
        self.emergency_start_time = time.time()
        self.food_search_attempts = 0
        self.max_emergency_time = TimingConstants.FALLBACK_TIMEOUT
        
        logger.error(f"[EmergencyState] 🚨 MODE URGENCE ACTIVÉ - Food: {self.state.get_food_count()}/{FoodThresholds.CRITICAL}")

    def execute(self) -> Optional[Any]:
        """Logique d'urgence optimisée pour la survie immédiate"""
        current_time = time.time()
        current_food = self.state.get_food_count()

        if current_time - self.last_emergency_action > 2.0:
            logger.error(f"[EmergencyState] 💀 CRITIQUE! Food: {current_food}/{FoodThresholds.CRITICAL}")
            self.last_emergency_action = current_time

        if current_food > StateTransitionThresholds.EMERGENCY_EXIT_THRESHOLD:
            logger.info(f"[EmergencyState] ✅ Sortie d'urgence (food: {current_food})")
            return self._exit_emergency()

        if current_time - self.emergency_start_time > self.max_emergency_time:
            logger.warning("[EmergencyState] ⏰ Timeout urgence")
            return self._exit_emergency()

        if self._needs_vision_update():
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()

        if self._food_on_current_tile():
            logger.info("[EmergencyState] 🍖 NOURRITURE TROUVÉE ICI!")
            return self.cmd_mgr.take(ResourceNames.FOOD)

        if self.emergency_commands:
            next_cmd = self.emergency_commands.pop(0)
            return self._execute_emergency_command(next_cmd)

        food_target = self._find_closest_food()
        if food_target:
            if not self.emergency_target or food_target.rel_position != self.emergency_target.rel_position:
                self.emergency_target = food_target
                self.emergency_commands = self._plan_emergency_path(food_target)
                distance = abs(food_target.rel_position[0]) + abs(food_target.rel_position[1])
                logger.error(f"[EmergencyState] 🎯 CIBLE URGENCE à distance {distance}: {food_target.rel_position}")

            if self.emergency_commands:
                next_cmd = self.emergency_commands.pop(0)
                return self._execute_emergency_command(next_cmd)

        if not self.desperate_mode:
            self.desperate_mode = True
            logger.error("[EmergencyState] 😰 MODE DÉSESPÉRÉ ACTIVÉ")

        return self._desperate_exploration()

    def _needs_vision_update(self) -> bool:
        """Détermine si une mise à jour de vision est nécessaire"""
        return (
            not self.state.get_vision().last_vision_data or
            self.context.get('needs_vision_update', False) or
            getattr(self.state, 'needs_look', False)
        )

    def _food_on_current_tile(self) -> bool:
        """Vérifie si de la nourriture est présente sur la tuile actuelle"""
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return ResourceNames.FOOD in data.resources and data.resources[ResourceNames.FOOD] > 0
        return False

    def _find_closest_food(self) -> Optional[RelativeTarget]:
        """Trouve la nourriture la plus proche dans la vision"""
        vision = self.state.get_vision()
        closest_food_pos = vision.find_closest_resource(ResourceNames.FOOD)
        
        if closest_food_pos:
            return RelativeTarget(closest_food_pos, ResourceNames.FOOD)
        
        return None

    def _plan_emergency_path(self, target: RelativeTarget) -> list:
        """Planifie le chemin d'urgence le plus court vers la cible"""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return []
        
        commands = self.pathfinder.get_commands_to_target(
            target, 
            self.state.get_orientation(), 
            vision_data
        )
        
        max_emergency_commands = 4
        return commands[:max_emergency_commands] if commands else []

    def _execute_emergency_command(self, command_type: CommandType) -> Optional[Any]:
        """Exécute une commande d'urgence spécifique"""
        command_map = {
            CommandType.FORWARD: self.cmd_mgr.forward,
            CommandType.LEFT: self.cmd_mgr.left,
            CommandType.RIGHT: self.cmd_mgr.right,
        }
        
        command_func = command_map.get(command_type)
        if command_func:
            return command_func()
        
        logger.error(f"[EmergencyState] Commande inconnue: {command_type}")
        return None

    def _desperate_exploration(self) -> Optional[Any]:
        """Exploration désespérée quand aucune nourriture n'est visible"""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return self.cmd_mgr.look()
        
        exploration_cmd = self.pathfinder.get_exploration_direction(
            self.state.get_orientation(), 
            vision_data
        )
        
        self.food_search_attempts += 1
        if self.food_search_attempts % 5 == 0:
            logger.error(f"[EmergencyState] 🔍 Recherche désespérée #{self.food_search_attempts}")
        
        return self._execute_emergency_command(exploration_cmd)

    def _exit_emergency(self) -> Optional[Any]:
        """Sortie de l'état d'urgence vers un état approprié"""
        current_food = self.state.get_food_count()
        emergency_duration = time.time() - self.emergency_start_time
        
        logger.info(f"[EmergencyState] SURVIE RÉUSSIE! Food: {current_food}, Durée: {emergency_duration:.1f}s")
        
        # Import des états nécessaires
        from ai.strategy.state.reproduction import ReproductionState
        from ai.strategy.state.incantation import IncantationState
        from ai.strategy.state.coordination_incantation import CoordinateIncantationState
        from ai.strategy.state.collect_food import CollectFoodState
        from ai.strategy.state.explore import ExploreState
        
        if current_food >= FoodThresholds.SUFFICIENT:
            if self.state.should_reproduce():
                new_state = ReproductionState(self.planner)
            elif not self.state.has_missing_resources() and current_food >= FoodThresholds.ABUNDANT:
                if self.state.level == 1:
                    new_state = IncantationState(self.planner)
                else:
                    new_state = CoordinateIncantationState(self.planner)
            else:
                new_state = ExploreState(self.planner)
        else:
            new_state = CollectFoodState(self.planner)
        
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes en mode urgence"""
        self.failed_attempts = 0
        
        if command_type == CommandType.TAKE:
            logger.info("[EmergencyState] ✅🎉 NOURRITURE SAUVÉE!")
            vision = self.state.get_vision()
            vision.remove_resource_at((0, 0), ResourceNames.FOOD)
            self.emergency_target = None
            self.emergency_commands.clear()
            self.desperate_mode = False
            
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs en mode urgence"""
        self.failed_attempts += 1
        logger.error(f"[EmergencyState] ❌ Échec commande {command_type}, tentative {self.failed_attempts}")
        
        if command_type == CommandType.TAKE:
            self.emergency_target = None
            self.emergency_commands.clear()
            self.context['needs_vision_update'] = True
            
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            if self.failed_attempts >= GameplayConstants.MAX_STUCK_ATTEMPTS:
                self.emergency_target = None
                self.emergency_commands.clear()
                self.desperate_mode = True

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements en mode urgence"""
        if event == Event.FOOD_SUFFICIENT:
            current_food = self.state.get_food_count()
            if current_food > StateTransitionThresholds.EMERGENCY_EXIT_THRESHOLD:
                return self._exit_emergency()
                
        return None

    def on_enter(self):
        """Actions à l'entrée du mode urgence"""
        super().on_enter()
        current_food = self.state.get_food_count()
        
        logger.error(f"[EmergencyState] 🚨 ENTRÉE MODE URGENCE - Food: {current_food}/{FoodThresholds.CRITICAL}")
        
        self.emergency_target = None
        self.emergency_commands.clear()
        self.desperate_mode = False
        self.failed_attempts = 0
        self.emergency_start_time = time.time()
        self.food_search_attempts = 0
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie du mode urgence"""
        super().on_exit()
        emergency_duration = time.time() - self.emergency_start_time
        
        logger.info(f"[EmergencyState] ✅ SORTIE MODE URGENCE - "
                   f"Durée: {emergency_duration:.1f}s, Tentatives: {self.food_search_attempts}")
        
        self.emergency_target = None
        self.emergency_commands.clear()
        self.desperate_mode = False