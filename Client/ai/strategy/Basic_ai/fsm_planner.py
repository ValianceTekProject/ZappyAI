##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## fsm_planner - Planificateur FSM amélioré avec coordination optimisée
##

import time
from typing import Optional, Any, Dict
from ai.strategy.fsm import StateMachine, Event, StateFactory
from ai.strategy.fsm_event import EventDetector
from ai.strategy.state.emergency import EmergencyState
from ai.strategy.state.collect_food import CollectFoodState
from ai.strategy.state.collect_resources import CollectResourcesState
from ai.strategy.state.explore import ExploreState
from ai.strategy.state.incantation import IncantationState
from ai.strategy.state.reproduction import ReproductionState
from ai.strategy.state.coordination_incantation import CoordinateIncantationState
from ai.strategy.state.wait_incantation import WaitIncantationState
from utils.logger import logger
from config import Constants
from constant import (
    FoodThresholds, IncantationRequirements, AgentRoles, CoordinationMessages,
    StateTransitionThresholds, GameplayConstants, ReproductionConstants,
    CoordinationStrategy
)


class FSMPlanner:
    """
    Planificateur FSM avec coordination d'incantation optimisée.
    """

    def __init__(self, command_manager, game_state, message_bus):
        """Initialisation du FSMPlanner avec coordination améliorée."""
        self.cmd_mgr = command_manager
        self.state = game_state
        self.bus = message_bus

        self.agent_thread = getattr(game_state, 'agent_thread', None)
        if self.agent_thread is None:
            logger.warning("[FSMPlanner] Aucun agent_thread trouvé - reproduction limitée")

        self.event_detector = EventDetector(self.state)

        self.context = {
            'current_target': None,
            'command_queue': [],
            'stuck_counter': 0,
            'last_position': None,
            'needs_vision_update': False,
            'needs_inventory_check': False,
            'last_inventory_time': time.time(),
            'last_vision_time': time.time(),
            'can_incant': False,
            'should_reproduce': False,
            'last_level': self.state.level,
            'coordination_failures': 0,
            'last_coordination_attempt': 0.0,
            'forced_exploration_until': 0.0
        }

        self._update_food_thresholds()

        initial_state = self._determine_initial_state()
        self.fsm = StateMachine(initial_state)

        self.decision_count = 0
        self.last_state_change = time.time()
        self.last_level_check = self.state.level

        logger.info(f"[FSMPlanner] FSM optimisé initialisé avec état: {self.fsm.get_current_state_name()}")

    def _determine_initial_state(self):
        """Détermine l'état initial selon la situation actuelle avec logique optimisée."""
        current_food = self.state.get_food_count()

        # Urgence alimentaire
        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            logger.warning(f"[FSMPlanner] Démarrage mode URGENCE (food: {current_food})")
            return EmergencyState(self)

        # Reproduction prioritaire pour niveau 2+
        if self._should_attempt_reproduction():
            logger.info(f"[FSMPlanner] Démarrage reproduction (niveau {self.state.level})")
            return ReproductionState(self)

        # Collecte de nourriture si insuffisante
        if current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
            logger.info(f"[FSMPlanner] Démarrage collecte nourriture (food: {current_food})")
            return CollectFoodState(self)

        # Incantation si possible
        if self._can_attempt_incantation():
            if self.state.level == 1:
                logger.info("[FSMPlanner] Démarrage incantation solo (niveau 1)")
                return IncantationState(self)
            else:
                logger.info(f"[FSMPlanner] Démarrage coordination (niveau {self.state.level})")
                return CoordinateIncantationState(self)

        # Collecte de ressources si manquantes
        if self.state.has_missing_resources():
            logger.info("[FSMPlanner] Démarrage collecte ressources")
            return CollectResourcesState(self)

        # Exploration par défaut
        logger.info(f"[FSMPlanner] Démarrage exploration (food: {current_food})")
        return ExploreState(self)

    def _can_attempt_incantation(self) -> bool:
        """Vérification optimisée pour l'incantation."""
        if self.state.level >= GameplayConstants.MAX_LEVEL:
            return False

        # Vérifier les ressources
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        if not requirements:
            return False
            
        inventory = self.state.get_inventory()
        for resource, needed in requirements.items():
            if inventory.get(resource, 0) < needed:
                return False

        # Vérifier la nourriture selon le niveau
        current_food = self.state.get_food_count()
        if self.state.level == 1:
            min_food_required = StateTransitionThresholds.MIN_FOOD_FOR_LEVEL_1_INCANTATION
        else:
            min_food_required = StateTransitionThresholds.MIN_FOOD_FOR_COORDINATION
            
        return current_food >= min_food_required

    def _should_attempt_reproduction(self) -> bool:
        """Vérifie si on devrait tenter une reproduction avec priorité élevée."""
        if self.state.level < ReproductionConstants.MIN_LEVEL_FOR_REPRODUCTION:
            return False

        min_food_for_fork = self._get_min_food_for_reproduction()
        if self.state.get_food_count() < min_food_for_fork:
            return False

        # Priorité absolue pour la reproduction après level up
        if getattr(self.state, 'needs_repro', False):
            return True

        # Reproduction automatique pour niveau 2
        return self.state.level == 2

    def _get_min_food_for_reproduction(self) -> int:
        """Calcule la nourriture minimale pour une reproduction."""
        base = ReproductionConstants.MIN_FOOD_FOR_FORK_BASE
        if self.state.level >= 3:
            return int(base * 1.2)  # Réduit le multiplicateur
        return base

    def _update_food_thresholds(self):
        """Met à jour les seuils de nourriture selon le niveau."""
        level = self.state.level
        if level >= 7:
            multiplier = FoodThresholds.MULTIPLIER_HIGH_LEVEL
        elif level >= 4:
            multiplier = FoodThresholds.MULTIPLIER_MID_LEVEL
        else:
            multiplier = FoodThresholds.MULTIPLIER_LOW_LEVEL

        self.food_thresholds = {
            'critical': int(FoodThresholds.BASE_CRITICAL * multiplier),
            'safe': int(FoodThresholds.BASE_SAFE * multiplier),
            'abundant': int(FoodThresholds.BASE_ABUNDANT * multiplier),
            'exploration_return': int(FoodThresholds.BASE_EXPLORATION_THRESHOLD * multiplier),
            'coordination': int(FoodThresholds.BASE_COORDINATION_THRESHOLD * multiplier)
        }

        logger.debug(f"[FSMPlanner] Seuils niveau {level}: {self.food_thresholds}")

    def decide_next_action(self) -> Optional[Any]:
        """Point d'entrée principal avec coordination optimisée."""
        self.decision_count += 1

        if not self._can_make_decision():
            return None

        try:
            current_time = time.time()

            # Gestion du changement de niveau
            if self.state.level != self.last_level_check:
                self._on_level_change()

            self._update_food_thresholds()

            # Gestion spéciale des états de reproduction terminée
            if self._should_transition_from_reproduction():
                return None

            # Vérification si on est en exploration forcée
            if self._is_in_forced_exploration():
                return None

            # Détection d'événements
            events = self.event_detector.detect_events()
            self._handle_events(events)

            # Vérification des opportunités de progression
            self._check_progression_opportunities()

            action = self.fsm.run()

            return action

        except Exception as e:
            logger.error(f"[FSMPlanner] Erreur lors de la décision: {e}")
            return self.cmd_mgr.look()

    def _check_progression_opportunities(self):
        """Vérification optimisée des opportunités de progression."""
        current_state_name = self.fsm.get_current_state_name()
        current_time = time.time()

        # Ne pas interrompre certains états critiques
        if current_state_name in ['IncantationState', 'EmergencyState', 'ReproductionState']:
            return

        # Éviter les boucles de coordination
        if (current_state_name == 'CoordinateIncantationState' and 
            current_time - self.last_state_change < CoordinationStrategy.COORDINATION_RETRY_COOLDOWN):
            return

        # Priorité 1: Reproduction après level up
        if self._should_attempt_reproduction() and current_state_name != 'ReproductionState':
            logger.info("[FSMPlanner] 👶 PRIORITÉ: Transition vers reproduction")
            new_state = ReproductionState(self)
            self.fsm.transition_to(new_state)
            self.last_state_change = current_time
            return

        # Priorité 2: Incantation si possible
        if self._can_attempt_incantation():
            # Vérifier si on n'a pas trop échoué récemment en coordination
            if (self.state.level > 1 and 
                self.context['coordination_failures'] < CoordinationStrategy.MAX_COORDINATION_ATTEMPTS and
                current_time - self.context['last_coordination_attempt'] > CoordinationStrategy.COORDINATION_RETRY_COOLDOWN):
                
                required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
                
                if self.state.level == 1:
                    logger.info("[FSMPlanner] 🔮 TRANSITION vers incantation solo (niveau 1)")
                    new_state = IncantationState(self)
                elif required_players > 1:
                    logger.info(f"[FSMPlanner] 🤝 TRANSITION vers coordination (niveau {self.state.level})")
                    new_state = CoordinateIncantationState(self)
                    self.context['last_coordination_attempt'] = current_time
                else:
                    logger.info("[FSMPlanner] 🔮 TRANSITION vers incantation directe")
                    new_state = IncantationState(self)
                
                self.fsm.transition_to(new_state)
                self.last_state_change = current_time
                return

        # Priorité 3: Collecte de ressources si manquantes et assez de nourriture
        current_food = self.state.get_food_count()
        if (current_food >= StateTransitionThresholds.FOOD_LOW_THRESHOLD and 
            self.state.has_missing_resources() and 
            current_state_name != 'CollectResourcesState'):
            
            missing = self._get_missing_resources()
            logger.info(f"[FSMPlanner] ⚒️ TRANSITION vers collecte ressources: {missing}")
            new_state = CollectResourcesState(self)
            self.fsm.transition_to(new_state)
            self.last_state_change = current_time
            return

    def _get_missing_resources(self) -> dict:
        """Retourne les ressources manquantes pour l'incantation."""
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        inventory = self.state.get_inventory()
        missing = {}
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current
        return missing

    def _should_transition_from_reproduction(self) -> bool:
        """Détecte si on doit sortir de l'état de reproduction."""
        current_state_name = self.fsm.get_current_state_name()

        if current_state_name != 'ReproductionState':
            return False

        current_state = self.fsm.state
        
        # Vérifier si la reproduction est terminée
        is_complete = (
            (hasattr(current_state, 'is_reproduction_complete') and current_state.is_reproduction_complete()) or
            (hasattr(current_state, 'fork_stage') and current_state.fork_stage == 4)
        )

        if is_complete:
            logger.info("[FSMPlanner] 🎉 Reproduction terminée, transition")
            self._transition_after_reproduction()
            return True

        return False

    def _transition_after_reproduction(self):
        """Gère la transition après reproduction terminée avec priorités optimisées."""
        current_food = self.state.get_food_count()

        # Priorité 1: Urgence alimentaire
        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            logger.warning("[FSMPlanner] → Emergency après reproduction")
            new_state = EmergencyState(self)
        
        # Priorité 2: Incantation si possible et ressources complètes
        elif self._can_attempt_incantation():
            if self.state.level == 1:
                logger.info("[FSMPlanner] → Incantation solo après reproduction")
                new_state = IncantationState(self)
            else:
                logger.info("[FSMPlanner] → Coordination après reproduction")
                new_state = CoordinateIncantationState(self)
        
        # Priorité 3: Collecte selon les besoins
        elif current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
            logger.info("[FSMPlanner] → Collecte nourriture après reproduction")
            new_state = CollectFoodState(self)
        elif self.state.has_missing_resources():
            logger.info("[FSMPlanner] → Collecte ressources après reproduction")
            new_state = CollectResourcesState(self)
        
        # Priorité 4: Exploration
        else:
            logger.info("[FSMPlanner] → Exploration après reproduction")
            new_state = ExploreState(self)

        self.fsm.transition_to(new_state)
        self.last_state_change = time.time()

    def _on_level_change(self):
        """Gère le changement de niveau avec actions appropriées."""
        old_level = self.last_level_check
        new_level = self.state.level

        logger.info(f"[FSMPlanner] 🆙 LEVEL UP! {old_level} → {new_level}")
        self.last_level_check = new_level

        # Priorité reproduction pour niveau 2+
        if new_level >= 2 and not getattr(self.state, 'needs_repro', False):
            logger.info(f"[FSMPlanner] Déclenchement reproduction prioritaire niveau {new_level}")
            self.state.needs_repro = True
            self.context['should_reproduce'] = True

        # Reset des échecs de coordination précédents
        self.context['coordination_failures'] = 0

    def _is_in_forced_exploration(self) -> bool:
        """Vérifie si on est en période d'exploration forcée."""
        current_time = time.time()
        return current_time < self.context['forced_exploration_until']

    def _force_exploration(self, duration: float):
        """Force l'exploration pendant une durée donnée."""
        self.context['forced_exploration_until'] = time.time() + duration
        current_state_name = self.fsm.get_current_state_name()
        
        if current_state_name != 'ExploreState':
            logger.info(f"[FSMPlanner] 🔄 Exploration forcée ({duration}s)")
            new_state = ExploreState(self)
            self.fsm.transition_to(new_state)
            self.last_state_change = time.time()

    def _can_make_decision(self) -> bool:
        """Vérifie si on peut prendre une décision."""
        if self.state.command_already_send:
            return False

        if self.cmd_mgr.get_pending_count() >= GameplayConstants.MAX_PENDING_COMMANDS:
            return False

        return True

    def _handle_events(self, events: list):
        """Gestion optimisée des événements avec transitions appropriées."""
        current_food = self.state.get_food_count()
        current_state_name = self.fsm.get_current_state_name()

        for event in events:
            if event == Event.FOOD_EMERGENCY:
                if current_state_name != 'EmergencyState':
                    logger.warning(f"[FSMPlanner] ⚠️ URGENCE! Transition Emergency (food: {current_food})")
                    new_state = EmergencyState(self)
                    self.fsm.transition_to(new_state)
                    self.last_state_change = time.time()
                    break

            elif event == Event.FOOD_LOW:
                # Ne pas interrompre certains états critiques
                if current_state_name not in ['EmergencyState', 'CollectFoodState', 'IncantationState', 
                                            'ReproductionState']:
                    logger.info(f"[FSMPlanner] 🍖 Transition collecte nourriture (food: {current_food})")
                    new_state = CollectFoodState(self)
                    self.fsm.transition_to(new_state)
                    self.last_state_change = time.time()
                    break

            elif event == Event.FOOD_SUFFICIENT:
                if current_state_name in ['EmergencyState', 'CollectFoodState']:
                    self._transition_after_food_collection()
                    break

            elif event == Event.NEED_VISION:
                self.context['needs_vision_update'] = True

            elif event == Event.NEED_INVENTORY:
                self.context['needs_inventory_check'] = True

    def _transition_after_food_collection(self):
        """Transition optimisée après collecte de nourriture suffisante."""
        # Priorité 1: Reproduction si nécessaire
        if self._should_attempt_reproduction():
            new_state = ReproductionState(self)

        # Priorité 2: Incantation si possible
        elif self._can_attempt_incantation():
            if self.state.level == 1:
                new_state = IncantationState(self)
            else:
                new_state = CoordinateIncantationState(self)

        # Priorité 3: Collecte de ressources si manquantes
        elif self.state.has_missing_resources():
            new_state = CollectResourcesState(self)

        # Priorité 4: Exploration
        else:
            new_state = ExploreState(self)

        self.fsm.transition_to(new_state)
        self.last_state_change = time.time()

    def get_context(self) -> Dict[str, Any]:
        """Retourne le contexte partagé entre les états."""
        return self.context

    def update_context(self, key: str, value: Any):
        """Met à jour le contexte partagé."""
        self.context[key] = value

    def on_command_success(self, command_type, response=None):
        """Appelé quand une commande réussit."""
        self.context['stuck_counter'] = 0

        if hasattr(self.fsm.state, 'on_command_success'):
            self.fsm.state.on_command_success(command_type, response)

        if command_type.value == 'Incantation':
            logger.info(f"[FSMPlanner] 🎉 INCANTATION RÉUSSIE! Nouveau niveau: {self.state.level}")
            self._on_level_change()

    def on_command_failed(self, command_type, response=None):
        """Appelé quand une commande échoue avec gestion améliorée."""
        self.context['stuck_counter'] += 1
        current_state_name = self.fsm.get_current_state_name()
        
        logger.warning(f"[FSMPlanner] ❌ Échec {command_type}, stuck: {self.context['stuck_counter']}")

        # Gestion spéciale des échecs de coordination
        if (current_state_name == 'CoordinateIncantationState' and 
            command_type.value == 'Broadcast'):
            self.context['coordination_failures'] += 1
            logger.warning(f"[FSMPlanner] Échec coordination {self.context['coordination_failures']}")

        # Déblocage après trop d'échecs
        if self.context['stuck_counter'] >= GameplayConstants.MAX_STUCK_ATTEMPTS:
            if current_state_name not in ['EmergencyState', 'IncantationState']:
                self.context['current_target'] = None
                self.context['command_queue'].clear()
                self._force_exploration(CoordinationStrategy.COORDINATION_RETRY_COOLDOWN)

        if hasattr(self.fsm.state, 'on_command_failed'):
            self.fsm.state.on_command_failed(command_type, response)

    def get_current_strategy_info(self) -> Dict[str, Any]:
        """Retourne les informations de stratégie optimisées pour debug."""
        return {
            'state': self.fsm.get_current_state_name(),
            'food_count': self.state.get_food_count(),
            'food_thresholds': self.food_thresholds,
            'level': self.state.level,
            'decisions': self.decision_count,
            'can_incant': self._can_attempt_incantation(),
            'should_reproduce': self._should_attempt_reproduction(),
            'missing_resources': self.state.has_missing_resources(),
            'coordination_failures': self.context['coordination_failures'],
            'forced_exploration': self._is_in_forced_exploration(),
            'last_state_change': time.time() - self.last_state_change,
            'required_players': IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1),
            'stuck_counter': self.context['stuck_counter']
        }