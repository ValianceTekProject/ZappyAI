##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## emergency - État d'urgence corrigé
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder, RelativeTarget
from config import Constants, CommandType
from constant import FoodThresholds, TimingConstants
from utils.logger import logger


class EmergencyState(State):
    """
    État d'urgence critique - Survie immédiate.
    """
    
    def __init__(self, planner):
        super().__init__(planner)
        self.pathfinder = Pathfinder()
        self.emergency_target = None
        self.emergency_commands = []
        self.desperate_mode = False
        self.last_emergency_action = time.time()
        self.failed_attempts = 0
        self.max_failed_attempts = TimingConstants.MAX_INCANTATION_ATTEMPTS
        logger.warning("[EmergencyState] 🚨 MODE URGENCE ACTIVÉ - SURVIE CRITIQUE")

    def execute(self) -> Optional[Any]:
        """
        Logique d'urgence optimisée pour la survie immédiate.
        """
        current_food = self.state.get_food_count()
        critical_threshold = self._get_critical_threshold()

        if time.time() - self.last_emergency_action > 2.0:
            logger.error(f"[EmergencyState] 💀 CRITIQUE! Food: {current_food}/{critical_threshold}")
            self.last_emergency_action = time.time()

        if not self.state.get_vision().last_vision_data or self.context.get('needs_vision_update', False):
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()

        if self._food_on_current_tile():
            return self.cmd_mgr.take(Constants.FOOD.value)

        if self.emergency_commands:
            next_cmd = self.emergency_commands.pop(0)
            return self._execute_emergency_command(next_cmd)

        food_target = self._find_closest_food()
        if food_target:
            if not self.emergency_target or food_target.rel_position != self.emergency_target.rel_position:
                self.emergency_target = food_target
                self.emergency_commands = self._plan_emergency_path(food_target)
            
            if self.emergency_commands:
                next_cmd = self.emergency_commands.pop(0)
                return self._execute_emergency_command(next_cmd)

        if not self.desperate_mode:
            self.desperate_mode = True

        return self._desperate_exploration()

    def _get_critical_threshold(self) -> int:
        """Calcule le seuil critique selon le niveau."""
        base = FoodThresholds.BASE_CRITICAL
        if self.state.level >= 7:
            return int(base * FoodThresholds.MULTIPLIER_HIGH_LEVEL)
        elif self.state.level >= 4:
            return int(base * FoodThresholds.MULTIPLIER_MID_LEVEL)
        return base

    def _food_on_current_tile(self) -> bool:
        """Vérifie si de la nourriture est présente sur la tuile actuelle."""
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return Constants.FOOD.value in data.resources and data.resources[Constants.FOOD.value] > 0
        return False

    def _find_closest_food(self) -> Optional[RelativeTarget]:
        """Trouve la nourriture la plus proche dans la vision."""
        vision = self.state.get_vision()
        closest_food_pos = vision.find_closest_resource(Constants.FOOD.value)
        
        if closest_food_pos:
            return RelativeTarget(closest_food_pos, Constants.FOOD.value)
        
        return None

    def _plan_emergency_path(self, target: RelativeTarget) -> list:
        """Planifie le chemin d'urgence le plus court vers la cible."""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return []
        
        commands = self.pathfinder.get_commands_to_target(
            target, 
            self.state.get_orientation(), 
            vision_data
        )
        return commands[:5] if commands else []

    def _execute_emergency_command(self, command_type: CommandType) -> Optional[Any]:
        """Exécute une commande d'urgence spécifique."""
        if command_type == CommandType.FORWARD:
            return self.cmd_mgr.forward()
        elif command_type == CommandType.LEFT:
            return self.cmd_mgr.left()
        elif command_type == CommandType.RIGHT:
            return self.cmd_mgr.right()
        else:
            logger.error(f"[EmergencyState] Commande inconnue: {command_type}")
            return None

    def _desperate_exploration(self) -> Optional[Any]:
        """Exploration désespérée quand aucune nourriture n'est visible."""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return self.cmd_mgr.look()
        
        exploration_cmd = self.pathfinder.get_exploration_direction(
            self.state.get_orientation(), 
            vision_data
        )
        return self._execute_emergency_command(exploration_cmd)

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes en mode urgence."""
        self.failed_attempts = 0
        
        if command_type == CommandType.TAKE:
            vision = self.state.get_vision()
            vision.remove_resource_at((0, 0), Constants.FOOD.value)
            self.emergency_target = None
            self.emergency_commands.clear()
            
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs en mode urgence."""
        self.failed_attempts += 1
        logger.error(f"[EmergencyState] ❌ Échec commande {command_type}, tentative {self.failed_attempts}")
        
        if command_type == CommandType.TAKE:
            self.emergency_target = None
            self.emergency_commands.clear()
            self.context['needs_vision_update'] = True
            
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            if self.failed_attempts >= 2:
                self.emergency_target = None
                self.emergency_commands.clear()
                self.desperate_mode = True

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements en mode urgence."""
        if event == Event.FOOD_SUFFICIENT:
            from ai.strategy.state.collect_food import CollectFoodState
            return CollectFoodState(self.planner)
        return None

    def on_enter(self):
        """Actions à l'entrée du mode urgence."""
        super().on_enter()
        current_food = self.state.get_food_count()
        critical = self._get_critical_threshold()
        logger.error(f"[EmergencyState] 🚨 ENTRÉE MODE URGENCE - Food: {current_food}/{critical}")
        
        self.emergency_target = None
        self.emergency_commands.clear()
        self.desperate_mode = False
        self.failed_attempts = 0
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie du mode urgence."""
        super().on_exit()
        logger.info("[EmergencyState] ✅ SORTIE MODE URGENCE - Situation stabilisée")
        self.emergency_target = None
        self.emergency_commands.clear()
        self.desperate_mode = False