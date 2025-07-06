##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## fsm_planner - Planificateur FSM simplifié et nettoyé
##

import time
from typing import Optional, Any, Dict
from ai.strategy.fsm import StateMachine
from ai.strategy.fsm_event import EventDetector
from ai.strategy.state.emergency import EmergencyState
from ai.strategy.state.collect_food import CollectFoodState
from ai.strategy.state.collect_resources import CollectResourcesState
from ai.strategy.state.explore import ExploreState
from ai.strategy.state.incantation import IncantationState
from ai.strategy.state.reproduction import ReproductionState
from ai.strategy.state.coordination_incantation import CoordinateIncantationState
from teams.coordination import CoordinationManager
from utils.logger import logger
from constant import (
    FoodThresholds, IncantationRequirements, AgentRoles, 
    StateTransitionThresholds, GameplayConstants, ReproductionRules,
    CoordinationProtocol
)


class FSMPlanner:
    """Planificateur FSM simplifié avec coordination"""

    def __init__(self, command_manager, game_state, message_bus):
        self.cmd_mgr = command_manager
        self.state = game_state
        self.bus = message_bus

        self.event_detector = EventDetector(self.state)
        self.global_coordination_mgr = CoordinationManager(
            self.bus, 
            self.cmd_mgr, 
            self.state
        )

        self.context = {
            'last_state_type': None,
            'state_change_time': time.time(),
            'food_to_resources_transitions': 0,
            'resources_to_food_transitions': 0,
            'last_transition_reset': time.time(),
            'coordination_failures': 0,
            'emergency_transitions': 0,
        }

        initial_state = self._determine_initial_state()
        self.fsm = StateMachine(initial_state)

        self.decision_count = 0
        self.last_level = self.state.level

        logger.info(f"[FSMPlanner] FSM initialisé avec état: {self.fsm.get_current_state_name()}")

    def _determine_initial_state(self):
        """Détermine l'état initial avec logique de survie"""
        current_food = self.state.get_food_count()

        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            logger.warning(f"[FSMPlanner] Démarrage URGENCE (food: {current_food})")
            return EmergencyState(self)

        if (self.state.should_reproduce() and 
            self.state.level == ReproductionRules.TRIGGER_LEVEL and
            current_food >= ReproductionRules.MIN_FOOD_REQUIRED):
            logger.info("[FSMPlanner] Démarrage reproduction (niveau 2)")
            return ReproductionState(self)

        if current_food < FoodThresholds.COORDINATION_MIN:
            logger.info(f"[FSMPlanner] Démarrage collecte nourriture (food: {current_food})")
            return CollectFoodState(self)

        if self._can_attempt_incantation():
            if self.state.level == 1:
                logger.info("[FSMPlanner] Démarrage incantation solo (niveau 1)")
                return IncantationState(self)
            else:
                logger.info(f"[FSMPlanner] Démarrage coordination (niveau {self.state.level})")
                return CoordinateIncantationState(self)

        if (current_food >= StateTransitionThresholds.FOOD_SUFFICIENT_THRESHOLD and 
            self.state.has_missing_resources()):
            logger.info("[FSMPlanner] Démarrage collecte ressources")
            return CollectResourcesState(self)

        logger.info(f"[FSMPlanner] Démarrage exploration (food: {current_food})")
        return ExploreState(self)

    def decide_next_action(self) -> Optional[Any]:
        """Point d'entrée principal simplifié"""
        self.decision_count += 1

        if not self._can_make_decision():
            return None

        try:
            current_time = time.time()
            current_food = self.state.get_food_count()

            if current_time - self.context['last_transition_reset'] > 60.0:
                self._reset_transition_counters()

            survival_action = self._handle_critical_survival(current_food)
            if survival_action:
                return survival_action

            if self.state.level != self.last_level:
                return self._handle_level_change()

            if self._detect_transition_loops():
                return self._handle_transition_loops()

            self._check_progression_opportunities()

            return self.fsm.run()

        except Exception as e:
            logger.error(f"[FSMPlanner] Erreur lors de la décision: {e}")
            return self.cmd_mgr.look()

    def _handle_critical_survival(self, current_food: int) -> Optional[Any]:
        """Gestion critique de la survie"""
        current_state_name = self.fsm.get_current_state_name()
        current_time = time.time()

        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            if current_state_name != 'EmergencyState':
                self.context['emergency_transitions'] += 1
                logger.error(f"[FSMPlanner] 🚨 URGENCE CRITIQUE! Food: {current_food}")
                self._transition_to_state(EmergencyState(self))
                return self.fsm.run()

        elif (current_state_name == 'CoordinateIncantationState' and 
              current_food <= FoodThresholds.CRITICAL):
            logger.warning(f"[FSMPlanner] ⚠️ Abandon coordination (food: {current_food})")
            self._transition_to_state(CollectFoodState(self))
            return self.fsm.run()

        elif (current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD and 
              current_state_name not in ['EmergencyState', 'CollectFoodState', 
                                        'IncantationState', 'CoordinateIncantationState']):
            
            time_since_last_transition = current_time - self.context['state_change_time']
            if time_since_last_transition > 3.0:
                logger.info(f"[FSMPlanner] 🍖 Transition collecte nourriture (food: {current_food})")
                self._track_transition('to_food')
                self._transition_to_state(CollectFoodState(self))
                return self.fsm.run()

        return None

    def _handle_level_change(self) -> Optional[Any]:
        """Gestion du changement de niveau"""
        old_level = self.last_level
        new_level = self.state.level
        current_food = self.state.get_food_count()

        logger.info(f"[FSMPlanner] 🆙 LEVEL UP! {old_level} → {new_level} (food: {current_food})")
        self.last_level = new_level
        
        self.context['coordination_failures'] = 0
        self._reset_transition_counters()

        if new_level == ReproductionRules.TRIGGER_LEVEL and not self.state.reproduction_completed:
            if current_food >= ReproductionRules.MIN_FOOD_REQUIRED:
                logger.info(f"[FSMPlanner] 👶 REPRODUCTION IMMÉDIATE (food: {current_food})")
                self._transition_to_state(ReproductionState(self))
                return self.fsm.run()
            else:
                logger.info(f"[FSMPlanner] 🍖 Collecte food pour reproduction")
                self._transition_to_state(CollectFoodState(self))
                return self.fsm.run()

        elif new_level >= 3:
            if current_food < FoodThresholds.COORDINATION_MIN:
                logger.info(f"[FSMPlanner] 🍖 Collecte food pour coordination")
                self._transition_to_state(CollectFoodState(self))
            elif self.state.has_missing_resources():
                logger.info(f"[FSMPlanner] ⚒️ Collecte ressources pour coordination")
                self._transition_to_state(CollectResourcesState(self))
            else:
                logger.info(f"[FSMPlanner] 🤝 Coordination niveau {new_level}")
                self._transition_to_state(CoordinateIncantationState(self))
            return self.fsm.run()

        return None

    def _detect_transition_loops(self) -> bool:
        """Détecte les boucles de transition"""
        food_transitions = self.context['food_to_resources_transitions']
        resource_transitions = self.context['resources_to_food_transitions']
        
        return food_transitions >= 3 or resource_transitions >= 3

    def _handle_transition_loops(self) -> Optional[Any]:
        """Gère les boucles de transition"""
        current_food = self.state.get_food_count()
        
        logger.warning(f"[FSMPlanner] 🔄 Boucle détectée! Food: {current_food}")
        self._reset_transition_counters()
        
        if current_food >= FoodThresholds.ABUNDANT:
            if self._can_attempt_incantation():
                if self.state.level == 1:
                    self._transition_to_state(IncantationState(self))
                else:
                    self._transition_to_state(CoordinateIncantationState(self))
            else:
                self._transition_to_state(ExploreState(self))
        else:
            self._transition_to_state(CollectFoodState(self))
            
        return self.fsm.run()

    def _can_attempt_incantation(self) -> bool:
        """Vérification pour l'incantation"""
        if self.state.level >= GameplayConstants.MAX_LEVEL:
            return False

        if self.state.has_missing_resources():
            return False

        current_food = self.state.get_food_count()
        if self.state.level == 1:
            min_food_required = StateTransitionThresholds.MIN_FOOD_FOR_LEVEL_1_INCANTATION
        else:
            min_food_required = FoodThresholds.COORDINATION_MIN
            
        return current_food >= min_food_required

    def _check_progression_opportunities(self):
        """Vérification des opportunités de progression"""
        current_state_name = self.fsm.get_current_state_name()
        current_time = time.time()
        current_food = self.state.get_food_count()

        if current_state_name in ['IncantationState', 'EmergencyState', 'ReproductionState']:
            return

        if (current_state_name == 'CoordinateIncantationState' and 
            current_time - self.context['state_change_time'] < 20.0):
            return

        if (self.state.should_reproduce() and 
            self.state.level == ReproductionRules.TRIGGER_LEVEL and 
            current_state_name != 'ReproductionState' and
            current_food >= ReproductionRules.MIN_FOOD_REQUIRED):
            logger.info("[FSMPlanner] 👶 PRIORITÉ: Transition reproduction (niveau 2)")
            self._transition_to_state(ReproductionState(self))
            return

        if (self._can_attempt_incantation() and 
            current_food >= FoodThresholds.COORDINATION_MIN and
            self.context['coordination_failures'] < 3):
            
            time_since_last_attempt = current_time - self.context.get('last_coordination_attempt', 0)
            if time_since_last_attempt > 20.0:
                
                if self.state.level == 1:
                    logger.info("[FSMPlanner] 🔮 TRANSITION vers incantation solo (niveau 1)")
                    self._transition_to_state(IncantationState(self))
                else:
                    logger.info(f"[FSMPlanner] 🤝 TRANSITION vers coordination (niveau {self.state.level})")
                    self.context['last_coordination_attempt'] = current_time
                    self._transition_to_state(CoordinateIncantationState(self))
                return

        if (current_food >= StateTransitionThresholds.FOOD_SUFFICIENT_THRESHOLD and 
            self.state.has_missing_resources() and 
            current_state_name not in ['CollectResourcesState', 'ExploreState'] and
            self.context['resources_to_food_transitions'] < 3):
            
            logger.info("[FSMPlanner] ⚒️ TRANSITION vers collecte ressources")
            self._track_transition('to_resources')
            self._transition_to_state(CollectResourcesState(self))

    def _track_transition(self, transition_type: str):
        """Suit les transitions pour détecter les boucles"""
        if transition_type == 'to_food':
            self.context['resources_to_food_transitions'] += 1
        elif transition_type == 'to_resources':
            self.context['food_to_resources_transitions'] += 1

    def _reset_transition_counters(self):
        """Reset les compteurs de transition"""
        self.context['food_to_resources_transitions'] = 0
        self.context['resources_to_food_transitions'] = 0
        self.context['emergency_transitions'] = 0
        self.context['last_transition_reset'] = time.time()
        
        if self.context['coordination_failures'] > 0:
            self.context['coordination_failures'] = max(0, self.context['coordination_failures'] - 1)
        
        logger.debug("[FSMPlanner] Compteurs de transition reset")

    def _transition_to_state(self, new_state):
        """Effectue une transition d'état avec suivi"""
        old_state_name = self.fsm.get_current_state_name()
        new_state_name = type(new_state).__name__
        
        self.context['last_state_type'] = old_state_name
        self.context['state_change_time'] = time.time()
        
        self.fsm.transition_to(new_state)
        logger.debug(f"[FSMPlanner] Transition: {old_state_name} → {new_state_name}")

    def _can_make_decision(self) -> bool:
        """Vérifie si on peut prendre une décision"""
        if self.state.command_already_send:
            return False

        if self.cmd_mgr.get_pending_count() >= GameplayConstants.MAX_PENDING_COMMANDS:
            return False

        return True

    def get_context(self) -> Dict[str, Any]:
        """Retourne le contexte partagé entre les états"""
        return self.context

    def on_command_success(self, command_type, response=None):
        """Appelé quand une commande réussit"""
        if hasattr(self.fsm.state, 'on_command_success'):
            self.fsm.state.on_command_success(command_type, response)

        if command_type.value == 'Incantation':
            logger.info(f"[FSMPlanner] 🎉 INCANTATION RÉUSSIE! Nouveau niveau: {self.state.level}")
            self.context['coordination_failures'] = 0

    def on_command_failed(self, command_type, response=None):
        """Appelé quand une commande échoue"""
        current_state_name = self.fsm.get_current_state_name()
        
        if (current_state_name == 'CoordinateIncantationState' and 
            command_type.value == 'Incantation'):
            self.context['coordination_failures'] += 1
            logger.warning(f"[FSMPlanner] Échec incantation coordonnée {self.context['coordination_failures']}")

        if hasattr(self.fsm.state, 'on_command_failed'):
            self.fsm.state.on_command_failed(command_type, response)

    def get_current_strategy_info(self) -> Dict[str, Any]:
        """Retourne les informations de stratégie pour debug"""
        return {
            'state': self.fsm.get_current_state_name(),
            'food_count': self.state.get_food_count(),
            'food_thresholds': {
                'critical': FoodThresholds.CRITICAL,
                'coordination_min': FoodThresholds.COORDINATION_MIN,
                'sufficient': FoodThresholds.SUFFICIENT,
                'abundant': FoodThresholds.ABUNDANT
            },
            'level': self.state.level,
            'decisions': self.decision_count,
            'can_incant': self._can_attempt_incantation(),
            'should_reproduce': self.state.should_reproduce(),
            'missing_resources': self.state.has_missing_resources(),
            'coordination_failures': self.context['coordination_failures'],
            'emergency_transitions': self.context['emergency_transitions'],
            'transition_counters': {
                'food_to_resources': self.context['food_to_resources_transitions'],
                'resources_to_food': self.context['resources_to_food_transitions']
            },
            'required_players': IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1),
            'time_since_state_change': time.time() - self.context['state_change_time']
        }