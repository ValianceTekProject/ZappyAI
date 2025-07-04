##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## fsm_planner - Planificateur FSM corrigé sans boucles infinies
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
from utils.logger import logger
from constant import (
    FoodThresholds, IncantationRequirements, AgentRoles, 
    StateTransitionThresholds, GameplayConstants, ReproductionRules
)


class FSMPlanner:
    """Planificateur FSM corrigé avec gestion stricte des level ups."""

    def __init__(self, command_manager, game_state, message_bus):
        """
        Initialise le FSMPlanner.
        
        Args:
            command_manager: Gestionnaire de commandes
            game_state: État du jeu
            message_bus: Bus de messages
        """
        self.cmd_mgr = command_manager
        self.state = game_state
        self.bus = message_bus

        self.agent_thread = getattr(game_state, 'agent_thread', None)
        self.event_detector = EventDetector(self.state)

        # Contexte simplifié
        self.context = {
            'last_state_type': None,
            'state_change_time': time.time(),
            'food_to_resources_transitions': 0,
            'resources_to_food_transitions': 0,
            'last_transition_reset': time.time(),
            'forced_exploration_until': 0.0,
            'coordination_failures': 0,
            'last_coordination_attempt': 0.0,
            'explore_food_spam_count': 0,
            'last_explore_food_spam': 0.0,
            'level_up_processed': False  # NOUVEAU: évite les boucles
        }

        initial_state = self._determine_initial_state()
        self.fsm = StateMachine(initial_state)

        self.decision_count = 0
        self.last_level = self.state.level

        logger.info(f"[FSMPlanner] FSM initialisé avec état: {self.fsm.get_current_state_name()}")

    def _determine_initial_state(self):
        """
        Détermine l'état initial selon les règles strictes.
        
        Returns:
            État initial approprié
        """
        current_food = self.state.get_food_count()

        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            logger.warning(f"[FSMPlanner] Démarrage URGENCE (food: {current_food})")
            return EmergencyState(self)

        if self.state.should_reproduce() and self.state.level == ReproductionRules.TRIGGER_LEVEL:
            logger.info("[FSMPlanner] Démarrage reproduction (niveau 2)")
            return ReproductionState(self)

        if current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
            logger.info(f"[FSMPlanner] Démarrage collecte nourriture (food: {current_food})")
            return CollectFoodState(self)

        if self._can_attempt_incantation():
            if self.state.level == 1:
                logger.info("[FSMPlanner] Démarrage incantation solo (niveau 1)")
                return IncantationState(self)
            else:
                logger.info(f"[FSMPlanner] Démarrage coordination (niveau {self.state.level})")
                return CoordinateIncantationState(self)

        if self.state.has_missing_resources():
            logger.info("[FSMPlanner] Démarrage collecte ressources")
            return CollectResourcesState(self)

        logger.info(f"[FSMPlanner] Démarrage exploration (food: {current_food})")
        return ExploreState(self)

    def decide_next_action(self) -> Optional[Any]:
        """
        Point d'entrée principal avec gestion corrigée des level ups.
        
        Returns:
            Action à exécuter ou None
        """
        self.decision_count += 1

        if not self._can_make_decision():
            return None

        try:
            current_time = time.time()

            # Reset périodique des compteurs
            if current_time - self.context['last_transition_reset'] > 60.0:
                self._reset_transition_counters()

            # CRITIQUE: Gestion du changement de niveau CORRIGÉE
            if self.state.level != self.last_level:
                return self._handle_level_change_corrected()

            # Spam d'exploration
            if self._detect_explore_food_spam():
                return self._handle_explore_food_spam()

            # Vérification d'exploration forcée
            if self._is_in_forced_exploration():
                return self.fsm.run()

            # Gestion des événements avec priorités
            self._handle_priority_events()

            # Vérification des opportunités de progression
            self._check_progression_opportunities()

            # Prévention des boucles infinies
            self._check_and_prevent_infinite_loops()

            return self.fsm.run()

        except Exception as e:
            logger.error(f"[FSMPlanner] Erreur lors de la décision: {e}")
            return self.cmd_mgr.look()

    def _handle_level_change_corrected(self) -> Optional[Any]:
        """
        Gestion CORRIGÉE du changement de niveau sans boucles infinites.
        
        Returns:
            Action appropriée ou None
        """
        old_level = self.last_level
        new_level = self.state.level

        logger.info(f"[FSMPlanner] 🆙 LEVEL UP! {old_level} → {new_level}")
        self.last_level = new_level
        
        # Reset des échecs de coordination
        self.context['coordination_failures'] = 0
        self._reset_transition_counters()
        self.context['level_up_processed'] = True

        current_food = self.state.get_food_count()

        # RÈGLE 1: Niveau 2 = Reproduction IMMÉDIATE si nourriture suffisante
        if new_level == ReproductionRules.TRIGGER_LEVEL and not self.state.reproduction_completed:
            if current_food >= ReproductionRules.MIN_FOOD_REQUIRED:
                logger.info(f"[FSMPlanner] 🔥 REPRODUCTION IMMÉDIATE (food: {current_food})")
                self._force_transition_to_reproduction()
                return self.fsm.run()
            else:
                logger.info(f"[FSMPlanner] 🍖 Collecte food pour reproduction (need: {ReproductionRules.MIN_FOOD_REQUIRED}, have: {current_food})")
                self._force_transition_to_food_collection()
                return self.fsm.run()

        # RÈGLE 2: Niveau ≥ 3 = Préparation coordination
        elif new_level >= 3:
            if current_food < StateTransitionThresholds.MIN_FOOD_FOR_COORDINATION:
                logger.info(f"[FSMPlanner] 🍖 Collecte food pour coordination (food: {current_food})")
                self._force_transition_to_food_collection()
            elif self.state.has_missing_resources():
                logger.info(f"[FSMPlanner] ⚒️ Collecte ressources pour coordination (niveau {new_level})")
                self._force_transition_to_resource_collection()
            else:
                logger.info(f"[FSMPlanner] 🤝 Coordination OBLIGATOIRE (niveau {new_level})")
                self._force_transition_to_coordination()
            return self.fsm.run()

        return None

    def _force_transition_to_reproduction(self):
        """Force la transition vers la reproduction."""
        logger.info("[FSMPlanner] 👶 Transition FORCÉE vers reproduction")
        self._transition_to_state(ReproductionState(self))

    def _force_transition_to_coordination(self):
        """Force la transition vers la coordination."""
        logger.info("[FSMPlanner] 🤝 Transition FORCÉE vers coordination")
        self._transition_to_state(CoordinateIncantationState(self))

    def _force_transition_to_resource_collection(self):
        """Force la transition vers la collecte de ressources."""
        logger.info("[FSMPlanner] ⚒️ Transition FORCÉE vers collecte ressources")
        self._transition_to_state(CollectResourcesState(self))

    def _force_transition_to_food_collection(self):
        """Force la transition vers la collecte de nourriture."""
        logger.info("[FSMPlanner] 🍖 Transition FORCÉE vers collecte nourriture")
        self._transition_to_state(CollectFoodState(self))

    def _detect_explore_food_spam(self) -> bool:
        """
        Détecte le spam de découverte de nourriture en exploration.
        
        Returns:
            True si spam détecté
        """
        current_state_name = self.fsm.get_current_state_name()
        current_time = time.time()
        
        if current_state_name == 'ExploreState':
            if current_time - self.context['last_explore_food_spam'] < 5.0:
                self.context['explore_food_spam_count'] += 1
            else:
                self.context['explore_food_spam_count'] = 0
                
            self.context['last_explore_food_spam'] = current_time
            
            return self.context['explore_food_spam_count'] > 20
            
        return False

    def _handle_explore_food_spam(self) -> Optional[Any]:
        """
        Gère le spam d'exploration en forçant une transition.
        
        Returns:
            Commande ou transition forcée
        """
        current_food = self.state.get_food_count()
        
        logger.warning(f"[FSMPlanner] 🔄 SPAM détecté en exploration! Food: {current_food}")
        
        self.context['explore_food_spam_count'] = 0
        
        if current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
            logger.info("[FSMPlanner] → Collecte nourriture forcée (spam)")
            self._transition_to_state(CollectFoodState(self))
            return self.fsm.run()
        
        if self._can_attempt_incantation():
            logger.info("[FSMPlanner] → Incantation forcée (spam)")
            if self.state.level == 1:
                self._transition_to_state(IncantationState(self))
            else:
                self._transition_to_state(CoordinateIncantationState(self))
            return self.fsm.run()
        
        self._force_exploration(15.0)
        return self.fsm.run()

    def _can_attempt_incantation(self) -> bool:
        """
        Vérification centralisée pour l'incantation avec protocole strict.
        
        Returns:
            True si incantation possible
        """
        if self.state.level >= GameplayConstants.MAX_LEVEL:
            return False

        if self.state.has_missing_resources():
            return False

        current_food = self.state.get_food_count()
        if self.state.level == 1:
            min_food_required = StateTransitionThresholds.MIN_FOOD_FOR_LEVEL_1_INCANTATION
        else:
            min_food_required = StateTransitionThresholds.MIN_FOOD_FOR_COORDINATION
            
        return current_food >= min_food_required

    def _handle_priority_events(self):
        """Gère les événements prioritaires avec transitions immédiates."""
        current_food = self.state.get_food_count()
        current_state_name = self.fsm.get_current_state_name()

        # Priorité 1: Urgence alimentaire
        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            if current_state_name != 'EmergencyState':
                logger.warning(f"[FSMPlanner] ⚠️ URGENCE! Transition Emergency (food: {current_food})")
                self._transition_to_state(EmergencyState(self))

        # Priorité 2: Reproduction strictement au niveau 2
        elif (self.state.should_reproduce() and 
              self.state.level == ReproductionRules.TRIGGER_LEVEL and 
              current_state_name != 'ReproductionState' and
              current_food >= ReproductionRules.MIN_FOOD_REQUIRED):
            logger.info("[FSMPlanner] 👶 PRIORITÉ: Transition reproduction (niveau 2)")
            self._force_transition_to_reproduction()

        # Priorité 3: Nourriture faible mais pas critique
        elif (current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD and 
              current_state_name not in ['EmergencyState', 'CollectFoodState', 'IncantationState', 'ReproductionState']):
            
            time_since_last_transition = time.time() - self.context['state_change_time']
            if time_since_last_transition > 5.0:
                logger.info(f"[FSMPlanner] 🍖 Transition collecte nourriture (food: {current_food})")
                self._track_transition('to_food')
                self._transition_to_state(CollectFoodState(self))

    def _check_progression_opportunities(self):
        """Vérification des opportunités de progression avec protocole strict."""
        current_state_name = self.fsm.get_current_state_name()
        current_time = time.time()

        # Ne pas interrompre certains états critiques
        if current_state_name in ['IncantationState', 'EmergencyState', 'ReproductionState']:
            return

        # Éviter le spam de coordination
        if (current_state_name == 'CoordinateIncantationState' and 
            current_time - self.context['state_change_time'] < 10.0):
            return

        # Incantation si possible avec PROTOCOLE STRICT
        if self._can_attempt_incantation():
            if (self.context['coordination_failures'] < 3 and
                current_time - self.context['last_coordination_attempt'] > 15.0):
                
                # RÈGLE STRICTE: Niveau 1 = solo UNIQUEMENT, niveau ≥ 2 = coordination OBLIGATOIRE
                if self.state.level == 1:
                    logger.info("[FSMPlanner] 🔮 TRANSITION vers incantation solo (niveau 1)")
                    self._transition_to_state(IncantationState(self))
                else:
                    logger.info(f"[FSMPlanner] 🤝 TRANSITION vers coordination OBLIGATOIRE (niveau {self.state.level})")
                    self.context['last_coordination_attempt'] = current_time
                    self._transition_to_state(CoordinateIncantationState(self))
                return

        # Collecte de ressources (avec prévention de boucles)
        current_food = self.state.get_food_count()
        if (current_food >= StateTransitionThresholds.FOOD_TO_EXPLORATION_THRESHOLD and 
            self.state.has_missing_resources() and 
            current_state_name not in ['CollectResourcesState', 'ExploreState'] and
            self.context['resources_to_food_transitions'] < 3):
            
            logger.info("[FSMPlanner] ⚒️ TRANSITION vers collecte ressources")
            self._track_transition('to_resources')
            self._transition_to_state(CollectResourcesState(self))

    def _check_and_prevent_infinite_loops(self):
        """Prévient les boucles infinies entre collecte food/ressources."""
        food_transitions = self.context['food_to_resources_transitions']
        resource_transitions = self.context['resources_to_food_transitions']
        
        if food_transitions >= 3 or resource_transitions >= 3:
            logger.warning(f"[FSMPlanner] 🔄 Boucle détectée! Food→Res: {food_transitions}, Res→Food: {resource_transitions}")
            self._force_exploration(30.0)

    def _track_transition(self, transition_type: str):
        """
        Suit les transitions pour détecter les boucles.
        
        Args:
            transition_type: Type de transition ('to_food' ou 'to_resources')
        """
        if transition_type == 'to_food':
            self.context['resources_to_food_transitions'] += 1
        elif transition_type == 'to_resources':
            self.context['food_to_resources_transitions'] += 1

    def _reset_transition_counters(self):
        """Reset les compteurs de transition."""
        self.context['food_to_resources_transitions'] = 0
        self.context['resources_to_food_transitions'] = 0
        self.context['explore_food_spam_count'] = 0
        self.context['last_transition_reset'] = time.time()
        self.context['level_up_processed'] = False
        logger.debug("[FSMPlanner] Compteurs de transition reset")

    def _force_exploration(self, duration: float):
        """
        Force l'exploration pendant une durée donnée.
        
        Args:
            duration: Durée de l'exploration forcée en secondes
        """
        self.context['forced_exploration_until'] = time.time() + duration
        current_state_name = self.fsm.get_current_state_name()
        
        if current_state_name != 'ExploreState':
            logger.info(f"[FSMPlanner] 🔄 Exploration forcée ({duration}s)")
            self._transition_to_state(ExploreState(self))
            self._reset_transition_counters()

    def _is_in_forced_exploration(self) -> bool:
        """
        Vérifie si on est en période d'exploration forcée.
        
        Returns:
            True si exploration forcée active
        """
        return time.time() < self.context['forced_exploration_until']

    def _transition_to_state(self, new_state):
        """
        Effectue une transition d'état avec suivi.
        
        Args:
            new_state: Nouvel état
        """
        old_state_name = self.fsm.get_current_state_name()
        new_state_name = type(new_state).__name__
        
        self.context['last_state_type'] = old_state_name
        self.context['state_change_time'] = time.time()
        
        self.fsm.transition_to(new_state)
        logger.debug(f"[FSMPlanner] Transition: {old_state_name} → {new_state_name}")

    def _can_make_decision(self) -> bool:
        """
        Vérifie si on peut prendre une décision.
        
        Returns:
            True si décision possible
        """
        if self.state.command_already_send:
            return False

        if self.cmd_mgr.get_pending_count() >= GameplayConstants.MAX_PENDING_COMMANDS:
            return False

        return True

    def get_context(self) -> Dict[str, Any]:
        """
        Retourne le contexte partagé entre les états.
        
        Returns:
            Dictionnaire du contexte
        """
        return self.context

    def on_command_success(self, command_type, response=None):
        """
        Appelé quand une commande réussit.
        
        Args:
            command_type: Type de commande
            response: Réponse du serveur
        """
        if hasattr(self.fsm.state, 'on_command_success'):
            self.fsm.state.on_command_success(command_type, response)

        # CRITIQUE: Détecter les level ups pour déclencher les actions appropriées
        if command_type.value == 'Incantation':
            logger.info(f"[FSMPlanner] 🎉 INCANTATION RÉUSSIE! Nouveau niveau: {self.state.level}")

    def on_command_failed(self, command_type, response=None):
        """
        Appelé quand une commande échoue.
        
        Args:
            command_type: Type de commande
            response: Réponse du serveur
        """
        current_state_name = self.fsm.get_current_state_name()
        
        # Gestion spéciale des échecs de coordination
        if (current_state_name == 'CoordinateIncantationState' and 
            command_type.value == 'Broadcast'):
            self.context['coordination_failures'] += 1
            logger.warning(f"[FSMPlanner] Échec coordination {self.context['coordination_failures']}")

        if hasattr(self.fsm.state, 'on_command_failed'):
            self.fsm.state.on_command_failed(command_type, response)

    def get_current_strategy_info(self) -> Dict[str, Any]:
        """
        Retourne les informations de stratégie pour debug.
        
        Returns:
            Dictionnaire des informations de stratégie
        """
        return {
            'state': self.fsm.get_current_state_name(),
            'food_count': self.state.get_food_count(),
            'food_thresholds': {
                'critical': FoodThresholds.CRITICAL,
                'sufficient': FoodThresholds.SUFFICIENT,
                'abundant': FoodThresholds.ABUNDANT
            },
            'level': self.state.level,
            'decisions': self.decision_count,
            'can_incant': self._can_attempt_incantation(),
            'should_reproduce': self.state.should_reproduce(),
            'missing_resources': self.state.has_missing_resources(),
            'coordination_failures': self.context['coordination_failures'],
            'forced_exploration': self._is_in_forced_exploration(),
            'explore_spam_count': self.context['explore_food_spam_count'],
            'level_up_processed': self.context['level_up_processed'],
            'transition_counters': {
                'food_to_resources': self.context['food_to_resources_transitions'],
                'resources_to_food': self.context['resources_to_food_transitions']
            },
            'required_players': IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1),
            'time_since_state_change': time.time() - self.context['state_change_time']
        }