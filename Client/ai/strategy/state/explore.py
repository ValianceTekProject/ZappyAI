##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## explore - État d'exploration optimisé pour survie et reproduction
##

import time
import random
from typing import Optional, Any, Dict
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder
from config import CommandType
from constant import (
    StateTransitionThresholds, GameplayConstants, 
    IncantationRequirements, FoodThresholds, ReproductionRules
)
from utils.logger import logger


class ExploreState(State):
    """État d'exploration optimisé avec priorité survie et reproduction"""

    def __init__(self, planner):
        super().__init__(planner)
        self.pathfinder = Pathfinder()
        self.exploration_pattern = "adaptive"  # Pattern adaptatif selon situation
        self.exploration_commands = []
        self.visited_areas = set()
        self.exploration_start_time = time.time()
        self.steps_since_last_find = 0
        self.last_inventory_check = time.time()
        self.total_moves = 0
        self.resources_discovered = 0
        self.food_discovered = 0
        self.max_exploration_time = 30.0  # Réduit pour éviter trop d'exploration
        self.food_discoveries_ignored = 0
        self.survival_mode = False
        
        # État spirale adaptatif
        self.spiral_state = {
            'direction': random.randint(0, 3),
            'steps_in_direction': 0,
            'steps_limit': 1,
            'direction_changes': 0
        }
        
        current_food = self.state.get_food_count()
        self.survival_mode = current_food <= FoodThresholds.SUFFICIENT
        
        logger.info(f"[ExploreState] 🗺️ Exploration optimisée activée - Food: {current_food}, Mode survie: {self.survival_mode}")

    def execute(self) -> Optional[Any]:
        """Logique d'exploration avec priorité survie et reproduction"""
        current_time = time.time()
        current_food = self.state.get_food_count()
        
        # PRIORITÉ 1: Vérifications critiques de survie
        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            logger.error(f"[ExploreState] 🚨 Urgence alimentaire en exploration ({current_food})")
            return self._transition_to_emergency()
        
        # PRIORITÉ 2: Reproduction si conditions remplies
        if self.state.should_reproduce():
            logger.info(f"[ExploreState] 👶 PRIORITÉ reproduction niveau {self.state.level}")
            return self._transition_to_reproduction()
        
        # PRIORITÉ 3: Timeout adaptatif selon nourriture
        max_time = self.max_exploration_time
        if current_food <= FoodThresholds.SUFFICIENT:
            max_time *= 0.7  # Réduire exploration si nourriture faible
        
        if current_time - self.exploration_start_time > max_time:
            logger.warning(f"[ExploreState] Timeout exploration adaptatif ({max_time:.1f}s)")
            return self._force_transition()
        
        # PRIORITÉ 4: Mise à jour mode survie
        self._update_survival_mode(current_food)
        
        # PRIORITÉ 5: Gestion mises à jour d'état
        if self._should_check_inventory(current_time):
            self.last_inventory_check = current_time
            return self.cmd_mgr.inventory()

        if self._needs_vision_update():
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()

        # PRIORITÉ 6: Analyse et action selon découvertes
        discovery = self._analyze_current_vision()
        if discovery:
            transition_result = self._handle_discovery(discovery)
            if transition_result:
                return transition_result

        # PRIORITÉ 7: Exécution exploration
        if self.exploration_commands:
            next_cmd = self.exploration_commands.pop(0)
            return self._execute_exploration_command(next_cmd)

        return self._generate_exploration_pattern()

    def _update_survival_mode(self, current_food: int):
        """
        Met à jour le mode survie selon la nourriture
        
        Args:
            current_food: Nourriture actuelle
        """
        new_survival_mode = current_food <= FoodThresholds.SUFFICIENT
        if new_survival_mode != self.survival_mode:
            self.survival_mode = new_survival_mode
            mode_text = "SURVIE" if new_survival_mode else "NORMAL"
            logger.info(f"[ExploreState] Mode exploration: {mode_text} (food: {current_food})")

    def _should_check_inventory(self, current_time: float) -> bool:
        """Détermine si un check d'inventaire est nécessaire"""
        if self.context.get('needs_inventory_check', False):
            self.context['needs_inventory_check'] = False
            return True
        
        # Fréquence adaptée selon mode survie
        interval = 6.0 if self.survival_mode else GameplayConstants.INVENTORY_CHECK_INTERVAL
        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= interval

    def _needs_vision_update(self) -> bool:
        """Détermine si une mise à jour de vision est nécessaire"""
        return (
            self.context.get('needs_vision_update', False) or
            not self.state.get_vision().last_vision_data or
            getattr(self.state, 'needs_look', False)
        )

    def _analyze_current_vision(self) -> Optional[Dict[str, Any]]:
        """Analyse optimisée de la vision avec priorités survie et reproduction"""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return None
        
        # Debug de la vision pour détecter les problèmes de pathfinding
        resource_counts = self.pathfinder.debug_vision_content(vision.last_vision_data)
        
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

        # PRIORITÉ 1: Ressources nécessaires pour progression
        if needed_resources_found:
            self.resources_discovered += len(needed_resources_found)
            self.steps_since_last_find = 0
            logger.info(f"[ExploreState] Ressources nécessaires trouvées: {needed_resources_found}")
            return {
                'type': 'needed_resources',
                'resources': needed_resources_found,
                'priority': 'high'
            }

        # PRIORITÉ 2: Nourriture si nécessaire (mode survie plus permissif)
        food_threshold = FoodThresholds.SUFFICIENT if self.survival_mode else StateTransitionThresholds.FOOD_LOW_THRESHOLD
        if food_count > 0 and current_food <= food_threshold:
            self.food_discovered += food_count
            self.steps_since_last_find = 0
            priority = "CRITIQUE" if self.survival_mode else "normale"
            logger.info(f"[ExploreState] Nourriture {priority} trouvée: {food_count} unités (vision: {resource_counts.get('food', 0)})")
            return {'type': 'food', 'count': food_count, 'priority': 'high'}
            
        # PRIORITÉ 3: Nourriture ignorée (seulement si abondante)
        if food_count > 0 and current_food > food_threshold:
            self.food_discoveries_ignored += 1
            if self.food_discoveries_ignored % 10 == 1:
                logger.debug(f"[ExploreState] Nourriture ignorée (food: {current_food} > {food_threshold})")
            return None
            
        # PRIORITÉ 4: Autres ressources si abondance
        if total_resources >= 3 and current_food >= FoodThresholds.ABUNDANT:
            self.resources_discovered += total_resources
            self.steps_since_last_find = 0
            logger.info(f"[ExploreState] Ressources diverses trouvées: {total_resources}")
            return {
                'type': 'other_resources', 
                'count': total_resources, 
                'types': resource_types,
                'priority': 'medium'
            }
            
        return None

    def _handle_discovery(self, discovery: Dict[str, Any]) -> Optional[Any]:
        """Gère une découverte selon sa priorité avec transitions optimisées"""
        discovery_type = discovery['type']
        priority = discovery.get('priority', 'low')
        
        if priority == 'high':
            if discovery_type == 'needed_resources':
                logger.info("[ExploreState] → Transition collecte ressources (nécessaires)")
                return self._transition_to_resource_collection()
            elif discovery_type == 'food':
                logger.info("[ExploreState] → Transition collecte nourriture (nécessaire)")
                return self._transition_to_food_collection()
        
        # Autres découvertes : continuer exploration un peu plus
        if priority == 'medium' and self.steps_since_last_find < 3:
            return None
        
        return None

    def _generate_exploration_pattern(self) -> Optional[Any]:
        """Génère le prochain pattern d'exploration adaptatif"""
        self.steps_since_last_find += 1
        
        # Changement pattern plus fréquent en mode survie
        change_threshold = 10 if self.survival_mode else 15
        if self.steps_since_last_find >= change_threshold:
            self._change_exploration_pattern()
        
        # Sélection pattern selon situation
        if self.survival_mode:
            return self._survival_exploration()
        elif self.exploration_pattern == "spiral":
            return self._spiral_exploration()
        elif self.exploration_pattern == "random":
            return self._random_exploration()
        elif self.exploration_pattern == "edge":
            return self._edge_exploration()
        else:
            return self._adaptive_exploration()

    def _survival_exploration(self) -> Optional[Any]:
        """Pattern d'exploration optimisé pour la survie"""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return self.cmd_mgr.look()
        
        # En mode survie, privilégier les mouvements forward (plus rapide)
        if random.random() < 0.6:
            return self._execute_exploration_command(CommandType.FORWARD)
        else:
            choices = [CommandType.LEFT, CommandType.RIGHT]
            exploration_cmd = random.choice(choices)
            return self._execute_exploration_command(exploration_cmd)

    def _adaptive_exploration(self) -> Optional[Any]:
        """Pattern d'exploration adaptatif selon contexte"""
        current_food = self.state.get_food_count()
        
        # Comportement selon niveau de nourriture
        if current_food >= FoodThresholds.ABUNDANT:
            # Mode exploration complète
            return self._spiral_exploration()
        elif current_food >= FoodThresholds.SUFFICIENT:
            # Mode équilibré
            return self._random_exploration()
        else:
            # Mode économie d'énergie
            return self._survival_exploration()

    def _change_exploration_pattern(self):
        """Change de pattern d'exploration selon contexte"""
        if self.survival_mode:
            patterns = ["survival", "random"]
        else:
            patterns = ["spiral", "random", "edge", "adaptive"]
        
        # Éviter de reprendre le même pattern
        available_patterns = [p for p in patterns if p != self.exploration_pattern]
        if available_patterns:
            new_pattern = random.choice(available_patterns)
        else:
            new_pattern = patterns[0]
        
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
        
        # Ajout d'aléatoire selon mode
        random_factor = 0.4 if self.survival_mode else 0.3
        if random.random() < random_factor:
            random_commands = [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]
            exploration_cmd = random.choice(random_commands)
            
        return self._execute_exploration_command(exploration_cmd)

    def _edge_exploration(self) -> Optional[Any]:
        """Pattern d'exploration des bords"""
        # En mode survie, privilégier forward
        if self.survival_mode:
            choices = [CommandType.FORWARD] * 3 + [CommandType.LEFT, CommandType.RIGHT]
        else:
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

    def _transition_to_reproduction(self) -> Optional[Any]:
        """Transition vers la reproduction"""
        from ai.strategy.state.reproduction import ReproductionState
        new_state = ReproductionState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _force_transition(self) -> Optional[Any]:
        """Force une transition pour éviter de rester en exploration"""
        current_food = self.state.get_food_count()
        
        # PRIORITÉ 1: Reproduction
        if self.state.should_reproduce():
            logger.info("[ExploreState] → Transition reproduction forcée")
            return self._transition_to_reproduction()
        
        # PRIORITÉ 2: Incantation si possible
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
        
        # PRIORITÉ 3: Collecte selon besoins
        missing_resources = self._get_missing_resources()
        if missing_resources and current_food >= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
            logger.info("[ExploreState] → Transition collecte ressources forcée")
            return self._transition_to_resource_collection()
        
        if current_food <= FoodThresholds.SUFFICIENT:
            logger.info("[ExploreState] → Transition collecte nourriture forcée")
            return self._transition_to_food_collection()
        
        # PRIORITÉ 4: Continuer exploration avec nouveau pattern
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
        """Gestion des événements en exploration avec priorité reproduction"""
        if event == Event.FOOD_EMERGENCY:
            logger.error("[ExploreState] Urgence alimentaire!")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)
            
        elif event == Event.SHOULD_REPRODUCE:
            logger.info(f"[ExploreState] 👶 Opportunité reproduction détectée!")
            from ai.strategy.state.reproduction import ReproductionState
            return ReproductionState(self.planner)
            
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
        
        logger.info(f"[ExploreState] 🗺️ ENTRÉE exploration optimisée")
        logger.info(f"[ExploreState] Food: {current_food}, Pattern: {self.exploration_pattern}, Mode survie: {self.survival_mode}")
        
        # Vérifications reproduction et opportunités
        if self.state.should_reproduce():
            logger.info(f"[ExploreState] 👶 Note: Reproduction possible niveau {self.state.level}")
        
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
        current_food = self.state.get_food_count()
        
        logger.info(f"[ExploreState] ✅ SORTIE exploration")
        logger.info(f"[ExploreState] Durée: {exploration_time:.1f}s, Mouvements: {self.total_moves}")
        logger.info(f"[ExploreState] Découvertes - Ressources: {self.resources_discovered}, Nourriture: {self.food_discovered} (ignorée: {self.food_discoveries_ignored})")
        logger.info(f"[ExploreState] Food final: {current_food}")
        
        self.exploration_commands.clear()