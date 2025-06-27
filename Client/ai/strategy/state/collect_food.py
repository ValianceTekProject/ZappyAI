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
from utils.logger import logger

class CollectFoodState(State):
    """
    État de collecte de nourriture préventive.

    Objectifs:
    1. Maintenir un niveau de nourriture sécurisé
    2. Collecte intelligente avec pathfinding optimisé
    3. Éviter les situations d'urgence
    4. Transition vers exploration quand nourriture suffisante
    """

    def __init__(self, planner):
        super().__init__(planner)
        self.pathfinder = Pathfinder()
        self.food_target = None
        self.movement_commands = []
        self.collection_attempts = 0
        self.max_collection_attempts = 3
        self.last_inventory_check = time.time()
        self.last_vision_update = time.time()
        self.inventory_check_interval = 8.0
        self.food_collected = 0
        self.successful_collections = 0
        logger.info("[CollectFoodState] 🍖 Mode collecte de nourriture activé")

    def execute(self) -> Optional[Any]:
        """
        Logique de collecte de nourriture optimisée.
        Balance entre efficacité et sécurité.
        """
        current_time = time.time()

        if self._should_check_inventory(current_time):
            logger.debug("[CollectFoodState] Vérification inventaire périodique")
            self.last_inventory_check = current_time
            return self.cmd_mgr.inventory()

        if self._needs_vision_update():
            logger.debug("[CollectFoodState] Mise à jour vision nécessaire")
            self.context['needs_vision_update'] = False
            self.last_vision_update = current_time
            return self.cmd_mgr.look()

        if self._food_on_current_tile():
            logger.info("[CollectFoodState] 🍖 Nourriture disponible ici, ramassage")
            return self.cmd_mgr.take(Constants.FOOD.value)

        if self.movement_commands:
            next_cmd = self.movement_commands.pop(0)
            logger.debug(f"[CollectFoodState] Déplacement vers nourriture: {next_cmd}")
            return self._execute_movement_command(next_cmd)

        food_target = self._find_best_food_target()
        if food_target:
            if food_target != self.food_target:
                self.food_target = food_target
                self.movement_commands = self._plan_food_collection_path(food_target)
                distance = abs(food_target.rel_position[0]) + abs(food_target.rel_position[1])
                logger.info(f"[CollectFoodState] 🎯 Nouvelle cible nourriture à distance {distance}: {food_target.rel_position}")

            if self.movement_commands:
                next_cmd = self.movement_commands.pop(0)
                return self._execute_movement_command(next_cmd)

        return self._explore_for_food()

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

    def _food_on_current_tile(self) -> bool:
        """Vérifie si de la nourriture est présente sur la tuile actuelle."""
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return Constants.FOOD.value in data.resources and data.resources[Constants.FOOD.value] > 0
        return False

    def _find_best_food_target(self):
        """Trouve la meilleure cible de nourriture selon distance et accessibilité."""
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
        """Planifie le chemin optimal vers la nourriture."""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return []
        commands = self.pathfinder.get_commands_to_target(
            target,
            self.state.get_orientation(),
            vision_data
        )
        max_commands = 8
        return commands[:max_commands] if commands else []

    def _execute_movement_command(self, command_type: CommandType):
        """Exécute une commande de mouvement."""
        if command_type == CommandType.FORWARD:
            return self.cmd_mgr.forward()
        elif command_type == CommandType.LEFT:
            return self.cmd_mgr.left()
        elif command_type == CommandType.RIGHT:
            return self.cmd_mgr.right()
        else:
            logger.warning(f"[CollectFoodState] Commande inconnue: {command_type}")
            return None

    def _explore_for_food(self):
        """Exploration ciblée pour trouver de la nourriture."""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return self.cmd_mgr.look()
        exploration_cmd = self.pathfinder.get_exploration_direction(
            self.state.get_orientation(),
            vision_data
        )
        logger.debug(f"[CollectFoodState] 🔍 Exploration pour nourriture: {exploration_cmd}")
        return self._execute_movement_command(exploration_cmd)

    def _get_safe_threshold(self) -> int:
        """Calcule le seuil de sécurité selon le niveau."""
        base = 20
        if self.state.level >= 7:
            return int(base * 2.0)
        elif self.state.level >= 4:
            return int(base * 1.5)
        return base

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes."""
        if command_type == CommandType.TAKE:
            old_food = self.state.get_food_count()
            self.food_collected += 1
            self.successful_collections += 1
            logger.info(f"[CollectFoodState] ✅ Nourriture collectée! Total collecté: {self.food_collected}")
            vision = self.state.get_vision()
            vision.remove_resource_at((0, 0), Constants.FOOD.value)
            self.food_target = None
            self.movement_commands.clear()
            self.collection_attempts = 0
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True
        elif command_type == CommandType.LOOK:
            self.last_vision_update = time.time()
        elif command_type == CommandType.INVENTORY:
            self.last_inventory_check = time.time()

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes."""
        if command_type == CommandType.TAKE:
            self.collection_attempts += 1
            logger.warning(f"[CollectFoodState] ❌ Échec collecte, tentative {self.collection_attempts}")
            self.food_target = None
            self.movement_commands.clear()
            self.context['needs_vision_update'] = True
            if self.collection_attempts >= self.max_collection_attempts:
                logger.warning("[CollectFoodState] Trop d'échecs de collecte, transition exploration")
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            stuck_counter = self.context.get('stuck_counter', 0) + 1
            self.context['stuck_counter'] = stuck_counter
            if stuck_counter >= 2:
                logger.warning("[CollectFoodState] Mouvements bloqués, reset cible")
                self.food_target = None
                self.movement_commands.clear()

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements."""
        if event == Event.FOOD_EMERGENCY:
            logger.warning("[CollectFoodState] Transition vers mode urgence!")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)
        elif event == Event.FOOD_SUFFICIENT:
            current_food = self.state.get_food_count()
            safe_threshold = self._get_safe_threshold()
            if current_food >= safe_threshold:
                logger.info(f"[CollectFoodState] ✅ Nourriture suffisante ({current_food} >= {safe_threshold}), transition exploration")
                from ai.strategy.state.explore import ExploreState
                return ExploreState(self.planner)
        return None

    def on_enter(self):
        """Actions à l'entrée de l'état."""
        super().on_enter()
        current_food = self.state.get_food_count()
        safe_threshold = self._get_safe_threshold()
        logger.info(f"[CollectFoodState] 🍖 ENTRÉE mode collecte - Food: {current_food}/{safe_threshold}")
        self.food_target = None
        self.movement_commands.clear()
        self.collection_attempts = 0
        self.food_collected = 0
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état."""
        super().on_exit()
        logger.info(f"[CollectFoodState] ✅ SORTIE collecte nourriture - Collecté: {self.food_collected}")
        self.food_target = None
        self.movement_commands.clear()
