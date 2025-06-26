##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## explore
##

import time
import random
from typing import Optional, Any, List, Tuple
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder
from config import Constants, CommandType
from utils.logger import logger

class ExploreState(State):
    """
    État d'exploration intelligente.
    """
    
    def __init__(self, planner):
        super().__init__(planner)
        self.pathfinder = Pathfinder()
        self.exploration_pattern = "spiral"
        self.exploration_commands = []
        self.current_direction_preference = None
        self.visited_areas = set()
        self.exploration_start_time = time.time()
        self.steps_since_last_find = 0
        self.max_steps_before_pattern_change = 15
        self.last_inventory_check = time.time()
        self.last_vision_update = time.time()
        self.inventory_check_interval = 15.0
        self.total_moves = 0
        self.resources_discovered = 0
        self.food_discovered = 0
        self.spiral_state = {
            'direction': 0,
            'steps_in_direction': 0,
            'steps_limit': 1,
            'direction_changes': 0
        }
        logger.info(f"[ExploreState] 🗺️ Exploration activée - Pattern: {self.exploration_pattern}")

    def execute(self) -> Optional[Any]:
        """
        Logique d'exploration intelligente avec patterns adaptatifs.
        """
        current_time = time.time()
        current_food = self.state.get_food_count()
        if current_food <= self._get_food_check_threshold():
            logger.info(f"[ExploreState] Nourriture surveillée: {current_food}")
        if self._should_check_inventory(current_time):
            logger.debug("[ExploreState] Vérification inventaire d'exploration")
            self.last_inventory_check = current_time
            return self.cmd_mgr.inventory()
        if self._needs_vision_update():
            logger.debug("[ExploreState] Mise à jour vision d'exploration")
            self.context['needs_vision_update'] = False
            self.last_vision_update = current_time
            return self.cmd_mgr.look()
        discovery = self._analyze_current_vision()
        if discovery:
            logger.info(f"[ExploreState] 🎯 Découverte: {discovery['type']} x{discovery['count']}")
            if discovery['type'] == 'resources':
                missing_resources = self._get_missing_resources()
                if missing_resources:
                    logger.info(f"[ExploreState] Transition vers collecte ressources: {missing_resources}")
                    from ai.strategy.state.collect_resources import CollectResourcesState
                    new_state = CollectResourcesState(self.planner)
                    self.planner.fsm.transition_to(new_state)
                    return new_state.execute()
            elif discovery['type'] == 'food':
                current_food = self.state.get_food_count()
                food_threshold = self._get_food_check_threshold()
                if current_food <= food_threshold:
                    logger.info(f"[ExploreState] Transition vers collecte nourriture ({current_food} <= {food_threshold})")
                    from ai.strategy.state.collect_food import CollectFoodState
                    new_state = CollectFoodState(self.planner)
                    self.planner.fsm.transition_to(new_state)
                    return new_state.execute()
        if self.exploration_commands:
            next_cmd = self.exploration_commands.pop(0)
            return self._execute_exploration_command(next_cmd)
        return self._generate_exploration_pattern()

    def _get_food_check_threshold(self) -> int:
        """Seuil de surveillance alimentaire en exploration."""
        base = 30
        if self.state.level >= 7:
            return int(base * 1.5)
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

    def _analyze_current_vision(self) -> Optional[dict]:
        """Analyse la vision actuelle pour détecter des ressources intéressantes."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return None
        total_resources = 0
        food_count = 0
        resource_types = set()
        for data in vision.last_vision_data:
            if data.rel_pos != (0, 0):
                for resource, count in data.resources.items():
                    total_resources += count
                    resource_types.add(resource)
                    if resource == Constants.FOOD.value:
                        food_count += count
        if food_count > 0:
            self.food_discovered += food_count
            self.steps_since_last_find = 0
            return {'type': 'food', 'count': food_count}
        if total_resources >= 2:
            self.resources_discovered += total_resources
            self.steps_since_last_find = 0
            return {'type': 'resources', 'count': total_resources, 'types': resource_types}
        return None

    def _generate_exploration_pattern(self) -> Optional[Any]:
        """Génère le prochain pattern d'exploration selon la stratégie actuelle."""
        self.steps_since_last_find += 1
        if self.steps_since_last_find >= self.max_steps_before_pattern_change:
            self._change_exploration_pattern()
        if self.exploration_pattern == "spiral":
            return self._spiral_exploration()
        elif self.exploration_pattern == "random":
            return self._random_exploration()
        elif self.exploration_pattern == "edge":
            return self._edge_exploration()
        else:
            return self._random_exploration()

    def _change_exploration_pattern(self):
        """Change de pattern d'exploration."""
        patterns = ["spiral", "random", "edge"]
        current_index = patterns.index(self.exploration_pattern)
        new_pattern = patterns[(current_index + 1) % len(patterns)]
        logger.info(f"[ExploreState] 🔄 Changement pattern: {self.exploration_pattern} → {new_pattern}")
        self.exploration_pattern = new_pattern
        self.steps_since_last_find = 0
        if new_pattern == "spiral":
            self.spiral_state = {
                'direction': random.randint(0, 3),
                'steps_in_direction': 0,
                'steps_limit': 1,
                'direction_changes': 0
            }

    def _spiral_exploration(self) -> Optional[Any]:
        """Pattern d'exploration en spirale."""
        state = self.spiral_state
        direction_commands = {
            0: [CommandType.FORWARD],
            1: [CommandType.RIGHT, CommandType.FORWARD],
            2: [CommandType.RIGHT, CommandType.RIGHT, CommandType.FORWARD],
            3: [CommandType.LEFT, CommandType.FORWARD]
        }
        if state['steps_in_direction'] < state['steps_limit']:
            self.exploration_commands.extend(direction_commands[state['direction']])
            state['steps_in_direction'] += 1
        else:
            state['direction'] = (state['direction'] + 1) % 4
            state['steps_in_direction'] = 0
            state['direction_changes'] += 1
            if state['direction_changes'] % 2 == 0:
                state['steps_limit'] += 1
        if self.exploration_commands:
            next_cmd = self.exploration_commands.pop(0)
            return self._execute_exploration_command(next_cmd)
        return self.cmd_mgr.forward()

    def _random_exploration(self) -> Optional[Any]:
        """Pattern d'exploration aléatoire pondéré."""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return self.cmd_mgr.look()
        exploration_cmd = self.pathfinder.get_exploration_direction(
            self.state.get_orientation(),
            vision_data
        )
        if random.random() < 0.3:
            random_commands = [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]
            exploration_cmd = random.choice(random_commands)
        return self._execute_exploration_command(exploration_cmd)

    def _edge_exploration(self) -> Optional[Any]:
        """Pattern d'exploration des bords de carte."""
        choices = [CommandType.FORWARD, CommandType.FORWARD, CommandType.FORWARD,
                   CommandType.LEFT, CommandType.RIGHT]
        exploration_cmd = random.choice(choices)
        return self._execute_exploration_command(exploration_cmd)

    def _execute_exploration_command(self, command_type: CommandType) -> Optional[Any]:
        """Exécute une commande d'exploration."""
        self.total_moves += 1
        if command_type == CommandType.FORWARD:
            return self.cmd_mgr.forward()
        elif command_type == CommandType.LEFT:
            return self.cmd_mgr.left()
        elif command_type == CommandType.RIGHT:
            return self.cmd_mgr.right()
        else:
            logger.warning(f"[ExploreState] Commande inconnue: {command_type}")
            return self.cmd_mgr.forward()

    def _add_to_visited(self, position: Tuple[int, int]):
        """Ajoute une position à l'historique des zones visitées."""
        approx_x = position[0] // 3
        approx_y = position[1] // 3
        self.visited_areas.add((approx_x, approx_y))

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes d'exploration."""
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True
            current_pos = self.state.get_position()
            self._add_to_visited(current_pos)
        elif command_type == CommandType.LOOK:
            self.last_vision_update = time.time()
        elif command_type == CommandType.INVENTORY:
            self.last_inventory_check = time.time()

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs en exploration."""
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            logger.debug("[ExploreState] Mouvement bloqué, adaptation pattern")
            stuck_counter = self.context.get('stuck_counter', 0) + 1
            self.context['stuck_counter'] = stuck_counter
            if stuck_counter >= 3:
                self._change_exploration_pattern()
                self.context['stuck_counter'] = 0

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements en exploration."""
        if event == Event.FOOD_EMERGENCY:
            logger.warning("[ExploreState] Urgence alimentaire détectée!")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)
        elif event == Event.FOOD_LOW:
            current_food = self.state.get_food_count()
            threshold = self._get_food_check_threshold()
            if current_food <= threshold:
                logger.info(f"[ExploreState] Transition collecte nourriture ({current_food} <= {threshold})")
                from ai.strategy.state.collect_food import CollectFoodState
                return CollectFoodState(self.planner)
        elif event == Event.RESOURCES_FOUND:
            missing_resources = self._get_missing_resources()
            if missing_resources:
                logger.info(f"[ExploreState] Ressources trouvées, transition collecte: {missing_resources}")
                from ai.strategy.state.collect_resources import CollectResourcesState
                return CollectResourcesState(self.planner)
        return None

    def _get_missing_resources(self) -> dict:
        """Retourne les ressources manquantes pour l'incantation."""
        requirements = self.state.get_incantation_requirements()
        inventory = self.state.get_inventory()
        missing = {}
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current
        return missing

    def on_enter(self):
        """Actions à l'entrée de l'état d'exploration."""
        super().on_enter()
        current_food = self.state.get_food_count()
        logger.info(f"[ExploreState] 🗺️ ENTRÉE exploration - Food: {current_food}, Pattern: {self.exploration_pattern}")
        self.exploration_start_time = time.time()
        self.total_moves = 0
        self.resources_discovered = 0
        self.food_discovered = 0
        self.steps_since_last_find = 0
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état d'exploration."""
        super().on_exit()
        exploration_time = time.time() - self.exploration_start_time
        logger.info(f"[ExploreState] ✅ SORTIE exploration - Durée: {exploration_time:.1f}s, "
                    f"Mouvements: {self.total_moves}, Ressources: {self.resources_discovered}, "
                    f"Nourriture: {self.food_discovered}")
        self.exploration_commands.clear()
