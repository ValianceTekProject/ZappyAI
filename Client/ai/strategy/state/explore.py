##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## explore - État d'exploration optimisé avec transitions intelligentes
##

import time
import random
from typing import Optional, Any, Dict
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder
from config import CommandType
from constant import (
    StateTransitionThresholds, GameplayConstants, 
    IncantationRequirements, FoodThresholds
)
from utils.logger import logger


class ExploreState(State):
    """État d'exploration intelligente avec transitions optimisées"""
    
    def __init__(self, planner):
        super().__init__(planner)
        self.pathfinder = Pathfinder()
        self.exploration_pattern = "spiral"
        self.exploration_commands = []
        self.visited_areas = set()
        self.exploration_start_time = time.time()
        self.steps_since_last_find = 0
        self.last_inventory_check = time.time()
        self.total_moves = 0
        self.resources_discovered = 0
        self.food_discovered = 0
        self.max_exploration_time = 25.0
        self.food_discoveries_ignored = 0
        
        self.spiral_state = {
            'direction': random.randint(0, 3),
            'steps_in_direction': 0,
            'steps_limit': 1,
            'direction_changes': 0
        }
        
        logger.info(f"[ExploreState] 🗺️ Exploration activée - Pattern: {self.exploration_pattern}")

    def execute(self) -> Optional[Any]:
        """Logique d'exploration intelligente avec transitions optimisées"""
        current_time = time.time()
        current_food = self.state.get_food_count()
        
        if current_time - self.exploration_start_time > self.max_exploration_time:
            logger.warning("[ExploreState] Timeout exploration, transition forcée")
            return self._force_transition()
        
        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            logger.warning(f"[ExploreState] Urgence alimentaire ({current_food})")
            return self._transition_to_emergency()
        
        if self._should_check_inventory(current_time):
            self.last_inventory_check = current_time
            return self.cmd_mgr.inventory()

        if self._needs_vision_update():
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()

        discovery = self._analyze_current_vision()
        if discovery:
            transition_result = self._handle_discovery(discovery)
            if transition_result:
                return transition_result

        if self.exploration_commands:
            next_cmd = self.exploration_commands.pop(0)
            return self._execute_exploration_command(next_cmd)

        return self._generate_exploration_pattern()

    def _should_check_inventory(self, current_time: float) -> bool:
        """Détermine si un check d'inventaire est nécessaire"""
        if self.context.get('needs_inventory_check', False):
            self.context['needs_inventory_check'] = False
            return True
        
        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= GameplayConstants.INVENTORY_CHECK_INTERVAL

    def _needs_vision_update(self) -> bool:
        """Détermine si une mise à jour de vision est nécessaire"""
        return (
            self.context.get('needs_vision_update', False) or
            not self.state.get_vision().last_vision_data or
            getattr(self.state, 'needs_look', False)
        )

    def _analyze_current_vision(self) -> Optional[Dict[str, Any]]:
        """Analyse optimisée de la vision actuelle avec priorités claires"""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return None
        
        total_resources = 0
        food_count = 0
        resource_types = set()
        needed_resources = set(self._get_missing_resources().keys())
        needed_resources_found = set()
        
        for data in vision.last_vision_data:
            if data.rel_pos != (0, 0):
                for resource, count in data.resources.items():
                    total_resources += count
                    resource_types.add(resource)
                    if resource == 'food':
                        food_count += count
                    if resource in needed_resources:
                        needed_resources_found.add(resource)

        current_food = self.state.get_food_count()

        if needed_resources_found:
            self.resources_discovered += len(needed_resources_found)
            self.steps_since_last_find = 0
            logger.info(f"[ExploreState] 🎯 Ressources nécessaires trouvées: {needed_resources_found}")
            return {
                'type': 'needed_resources',
                'resources': needed_resources_found,
                'priority': 'high'
            }

        if food_count > 0 and current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
            self.food_discovered += food_count
            self.steps_since_last_find = 0
            logger.info(f"[ExploreState] 🍖 Nourriture trouvée (nécessaire): {food_count} unités")
            return {'type': 'food', 'count': food_count, 'priority': 'high'}
            
        if food_count > 0 and current_food > StateTransitionThresholds.FOOD_LOW_THRESHOLD:
            self.food_discoveries_ignored += 1
            if self.food_discoveries_ignored % 10 == 1:
                logger.debug(f"[ExploreState] Nourriture ignorée ({current_food} > {StateTransitionThresholds.FOOD_LOW_THRESHOLD})")
            return None
            
        if total_resources >= 3:
            self.resources_discovered += total_resources
            self.steps_since_last_find = 0
            logger.info(f"[ExploreState] 🔍 Ressources diverses trouvées: {total_resources}")
            return {
                'type': 'other_resources', 
                'count': total_resources, 
                'types': resource_types,
                'priority': 'medium'
            }
            
        return None

    def _handle_discovery(self, discovery: Dict[str, Any]) -> Optional[Any]:
        """Gère une découverte selon sa priorité avec transitions claires"""
        discovery_type = discovery['type']
        priority = discovery.get('priority', 'low')
        
        if priority == 'high':
            if discovery_type == 'needed_resources':
                logger.info("[ExploreState] → Transition collecte ressources (nécessaires)")
                return self._transition_to_resource_collection()
            elif discovery_type == 'food':
                logger.info("[ExploreState] → Transition collecte nourriture (nécessaire)")
                return self._transition_to_food_collection()
        
        if priority == 'medium' and self.steps_since_last_find < 5:
            return None
        
        return None

    def _generate_exploration_pattern(self) -> Optional[Any]:
        """Génère le prochain pattern d'exploration"""
        self.steps_since_last_find += 1
        
        if self.steps_since_last_find >= 15:
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
        """Change de pattern d'exploration de manière optimisée"""
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
        """Pattern d'exploration en spirale optimisé"""
        state = self.spiral_state
        direction_commands = {
            0: [CommandType.FORWARD],
            1: [CommandType.RIGHT, CommandType.FORWARD],
            2: [CommandType.RIGHT, CommandType.RIGHT, CommandType.FORWARD],
            3: [CommandType.LEFT, CommandType.FORWARD]
        }
        
        if state['steps_in_direction'] < state['steps_limit']:
            commands = direction_commands[state['direction']]
            self.exploration_commands.extend(commands)
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
        """Pattern d'exploration aléatoire pondéré"""
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
        """Pattern d'exploration des bords"""
        choices = [CommandType.FORWARD] * 4 + [CommandType.LEFT, CommandType.RIGHT]
        exploration_cmd = random.choice(choices)
        return self._execute_exploration_command(exploration_cmd)

    def _execute_exploration_command(self, command_type: CommandType) -> Optional[Any]:
        """Exécute une commande d'exploration"""
        self.total_moves += 1
        
        command_map = {
            CommandType.FORWARD: self.cmd_mgr.forward,
            CommandType.LEFT: self.cmd_mgr.left,
            CommandType.RIGHT: self.cmd_mgr.right,
        }
        
        command_func = command_map.get(command_type)
        if command_func:
            return command_func()
        
        return self.cmd_mgr.forward()

    def _get_missing_resources(self) -> Dict[str, int]:
        """Retourne les ressources manquantes pour l'incantation"""
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        inventory = self.state.get_inventory()
        missing = {}
        
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current
                
        return missing

    def _transition_to_emergency(self) -> Optional[Any]:
        """Transition vers l'état d'urgence"""
        from ai.strategy.state.emergency import EmergencyState
        new_state = EmergencyState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _transition_to_food_collection(self) -> Optional[Any]:
        """Transition vers la collecte de nourriture"""
        from ai.strategy.state.collect_food import CollectFoodState
        new_state = CollectFoodState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _transition_to_resource_collection(self) -> Optional[Any]:
        """Transition vers la collecte de ressources"""
        from ai.strategy.state.collect_resources import CollectResourcesState
        new_state = CollectResourcesState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _force_transition(self) -> Optional[Any]:
        """Force une transition pour éviter de rester en exploration"""
        current_food = self.state.get_food_count()
        
        if self.state.should_reproduce():
            logger.info("[ExploreState] → Transition reproduction forcée")
            from ai.strategy.state.reproduction import ReproductionState
            new_state = ReproductionState(self.planner)
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()
        
        if self._can_attempt_incantation():
            logger.info("[ExploreState] → Transition incantation forcée")
            if self.state.level == 1:
                from ai.strategy.state.incantation import IncantationState
                new_state = IncantationState(self.planner)
            else:
                from ai.strategy.state.coordination_incantation import CoordinateIncantationState
                new_state = CoordinateIncantationState(self.planner)
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()
        
        missing_resources = self._get_missing_resources()
        if missing_resources and current_food >= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
            logger.info("[ExploreState] → Transition collecte ressources forcée")
            return self._transition_to_resource_collection()
        
        if current_food <= FoodThresholds.SUFFICIENT:
            logger.info("[ExploreState] → Transition collecte nourriture forcée")
            return self._transition_to_food_collection()
        
        self._change_exploration_pattern()
        return None

    def _can_attempt_incantation(self) -> bool:
        """Vérifie si une incantation est possible"""
        if self.state.level >= GameplayConstants.MAX_LEVEL:
            return False
            
        if self.state.has_missing_resources():
            return False
            
        current_food = self.state.get_food_count()
        if self.state.level == 1:
            min_food = StateTransitionThresholds.MIN_FOOD_FOR_LEVEL_1_INCANTATION
        else:
            min_food = StateTransitionThresholds.MIN_FOOD_FOR_COORDINATION
            
        return current_food >= min_food

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes d'exploration"""
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True
        elif command_type == CommandType.INVENTORY:
            self.last_inventory_check = time.time()

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs en exploration"""
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            stuck_counter = self.context.get('stuck_counter', 0) + 1
            self.context['stuck_counter'] = stuck_counter
            
            if stuck_counter >= GameplayConstants.MAX_STUCK_ATTEMPTS:
                self._change_exploration_pattern()
                self.context['stuck_counter'] = 0

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements en exploration"""
        if event == Event.FOOD_EMERGENCY:
            logger.warning("[ExploreState] Urgence alimentaire!")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)
            
        elif event == Event.FOOD_LOW:
            current_food = self.state.get_food_count()
            if current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
                logger.info(f"[ExploreState] Transition collecte nourriture ({current_food})")
                from ai.strategy.state.collect_food import CollectFoodState
                return CollectFoodState(self.planner)
                
        elif event == Event.RESOURCES_FOUND:
            missing_resources = self._get_missing_resources()
            if missing_resources:
                logger.info(f"[ExploreState] Ressources trouvées: {missing_resources}")
                from ai.strategy.state.collect_resources import CollectResourcesState
                return CollectResourcesState(self.planner)
                
        return None

    def on_enter(self):
        """Actions à l'entrée de l'état d'exploration"""
        super().on_enter()
        current_food = self.state.get_food_count()
        
        logger.info(f"[ExploreState] 🗺️ ENTRÉE exploration - Food: {current_food}, Pattern: {self.exploration_pattern}")
        
        self.exploration_start_time = time.time()
        self.total_moves = 0
        self.resources_discovered = 0
        self.food_discovered = 0
        self.food_discoveries_ignored = 0
        self.steps_since_last_find = 0
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état d'exploration"""
        super().on_exit()
        exploration_time = time.time() - self.exploration_start_time
        
        logger.info(f"[ExploreState] ✅ SORTIE exploration - "
                   f"Durée: {exploration_time:.1f}s, Mouvements: {self.total_moves}, "
                   f"Ressources: {self.resources_discovered}, Nourriture: {self.food_discovered}, "
                   f"Nourriture ignorée: {self.food_discoveries_ignored}")
        
        self.exploration_commands.clear()