##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## fsm_planner - Planificateur FSM avec coordination CORRIGÉE
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
    SafetyLimits, CoordinationProtocol
)


class FSMPlanner:
    """Planificateur FSM avec coordination CORRIGÉE."""

    def __init__(self, command_manager, game_state, message_bus):
        """
        Initialise le FSMPlanner avec coordination optimisée.
        
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

        # CoordinationManager GLOBAL pour réponses automatiques
        self.global_coordination_mgr = CoordinationManager(
            self.bus, 
            self.cmd_mgr, 
            self.state
        )

        # Contexte CORRIGÉ avec seuils appropriés
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
            'level_up_processed': False,
            'emergency_transitions': 0,
            'last_emergency_transition': 0.0,
            'coordination_food_threshold': FoodThresholds.COORDINATION_MIN,
            # CORRIGÉ: Seuils moins agressifs pour la coordination
            'coordination_abandon_threshold': 5,  # Était 3, maintenant 5
            'coordination_abandon_count': 0,
            'last_coordination_abandon': 0.0,
            'coordination_cooldown_until': 0.0,
            'successful_coordinations': 0,
            'coordination_state_time': 0.0,  # NOUVEAU: Temps passé en coordination
        }

        initial_state = self._determine_initial_state()
        self.fsm = StateMachine(initial_state)

        self.decision_count = 0
        self.last_level = self.state.level

        logger.info(f"[FSMPlanner] FSM CORRIGÉ initialisé avec état: {self.fsm.get_current_state_name()}")
        logger.info(f"[FSMPlanner] Seuils coordination CORRIGÉS: Critical={FoodThresholds.CRITICAL}, "
                   f"Coordination={FoodThresholds.COORDINATION_MIN}, Abandon={self.context['coordination_abandon_threshold']}")

    def _determine_initial_state(self):
        """
        Détermine l'état initial avec logique de survie améliorée.
        
        Returns:
            État initial approprié
        """
        current_food = self.state.get_food_count()

        # Priorité absolue: Urgence alimentaire
        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            logger.warning(f"[FSMPlanner] Démarrage URGENCE (food: {current_food})")
            return EmergencyState(self)

        # Reproduction au niveau 2 si conditions remplies
        if (self.state.should_reproduce() and 
            self.state.level == ReproductionRules.TRIGGER_LEVEL and
            current_food >= ReproductionRules.MIN_FOOD_REQUIRED):
            logger.info("[FSMPlanner] Démarrage reproduction (niveau 2)")
            return ReproductionState(self)

        # Collecte nourriture si insuffisante pour coordination
        if current_food < FoodThresholds.COORDINATION_MIN:
            logger.info(f"[FSMPlanner] Démarrage collecte nourriture (food: {current_food})")
            return CollectFoodState(self)

        # Incantation/Coordination si possible
        if self._can_attempt_incantation():
            if self.state.level == 1:
                logger.info("[FSMPlanner] Démarrage incantation solo (niveau 1)")
                return IncantationState(self)
            else:
                logger.info(f"[FSMPlanner] Démarrage coordination (niveau {self.state.level})")
                return CoordinateIncantationState(self)

        # Collecte ressources si nourriture suffisante
        if (current_food >= StateTransitionThresholds.FOOD_SUFFICIENT_THRESHOLD and 
            self.state.has_missing_resources()):
            logger.info("[FSMPlanner] Démarrage collecte ressources")
            return CollectResourcesState(self)

        logger.info(f"[FSMPlanner] Démarrage exploration (food: {current_food})")
        return ExploreState(self)

    def decide_next_action(self) -> Optional[Any]:
        """
        Point d'entrée principal avec coordination CORRIGÉE.
        
        Returns:
            Action à exécuter ou None
        """
        self.decision_count += 1

        if not self._can_make_decision():
            return None

        try:
            current_time = time.time()
            current_food = self.state.get_food_count()

            # Reset périodique des compteurs
            if current_time - self.context['last_transition_reset'] > 60.0:
                self._reset_transition_counters()

            # PRIORITÉ 1: Gestion critique de survie
            survival_action = self._handle_critical_survival(current_food)
            if survival_action:
                return survival_action

            # PRIORITÉ 2: Gestion du changement de niveau
            if self.state.level != self.last_level:
                return self._handle_level_change_corrected()

            # PRIORITÉ 3: Détection spam coordination CORRIGÉE
            if self._detect_coordination_spam_corrected():
                return self._handle_coordination_spam_corrected()

            # PRIORITÉ 4: Détection spam exploration
            if self._detect_explore_food_spam():
                return self._handle_explore_food_spam()

            # PRIORITÉ 5: Vérification d'exploration forcée
            if self._is_in_forced_exploration():
                return self.fsm.run()

            # PRIORITÉ 6: Gestion des événements et opportunités
            self._handle_priority_events()
            self._check_progression_opportunities_corrected()
            self._check_and_prevent_infinite_loops()

            return self.fsm.run()

        except Exception as e:
            logger.error(f"[FSMPlanner] Erreur lors de la décision: {e}")
            return self.cmd_mgr.look()

    def _detect_coordination_spam_corrected(self) -> bool:
        """
        Détection CORRIGÉE du spam de coordination moins agressive.
        
        Returns:
            True si spam détecté
        """
        current_time = time.time()
        current_state_name = self.fsm.get_current_state_name()
        
        # CORRIGÉ: Ne considérer comme abandon que si vraiment en échec
        if current_state_name == 'CoordinateIncantationState':
            # Temps passé en coordination
            time_in_coordination = current_time - self.context['state_change_time']
            self.context['coordination_state_time'] = time_in_coordination
            
            # CORRIGÉ: Seuil moins agressif - seulement après échec répétés ET temps suffisant
            if (self.context['coordination_failures'] >= 3 and 
                time_in_coordination > CoordinationProtocol.COORDINATION_TIMEOUT):
                self.context['coordination_abandon_count'] += 1
                self.context['last_coordination_abandon'] = current_time
                logger.warning(f"[FSMPlanner] Abandon coordination compté (total: {self.context['coordination_abandon_count']})")
        
        # CORRIGÉ: Seuil plus élevé pour déclencher le spam
        spam_threshold = self.context['coordination_abandon_threshold']  # 5 au lieu de 3
        recent_abandons = (current_time - self.context['last_coordination_abandon'] < 30.0 and 
                          self.context['coordination_abandon_count'] >= spam_threshold)
        
        return recent_abandons

    def _handle_coordination_spam_corrected(self) -> Optional[Any]:
        """
        Gestion CORRIGÉE du spam de coordination moins punitive.
        
        Returns:
            Action appropriée
        """
        current_food = self.state.get_food_count()
        current_time = time.time()
        
        logger.warning(f"[FSMPlanner] 🔄 COORDINATION DIFFICILE détectée (food: {current_food})")
        
        # CORRIGÉ: Cooldown plus court et plus flexible
        self.context['coordination_cooldown_until'] = current_time + 15.0  # Était 30s, maintenant 15s
        self.context['coordination_abandon_count'] = max(0, self.context['coordination_abandon_count'] - 1)  # Décrémente
        
        # CORRIGÉ: Transition plus intelligente selon la situation
        if current_food < FoodThresholds.COORDINATION_MIN:
            logger.info("[FSMPlanner] → Collecte nourriture (coordination difficile)")
            self._transition_to_state(CollectFoodState(self))
        elif self.state.has_missing_resources():
            logger.info("[FSMPlanner] → Collecte ressources (coordination difficile)")
            self._transition_to_state(CollectResourcesState(self))
        else:
            # CORRIGÉ: Exploration plus courte
            logger.info("[FSMPlanner] → Exploration courte (coordination difficile)")
            self._force_exploration(10.0)  # Était 20s, maintenant 10s
            
        return self.fsm.run()

    def _is_coordination_in_cooldown(self) -> bool:
        """
        Vérifie si la coordination est en cooldown.
        
        Returns:
            True si en cooldown
        """
        return time.time() < self.context['coordination_cooldown_until']

    def _handle_critical_survival(self, current_food: int) -> Optional[Any]:
        """
        Gestion critique de la survie avec coordination respectée.
        
        Args:
            current_food: Nourriture actuelle
            
        Returns:
            Action de survie ou None
        """
        current_state_name = self.fsm.get_current_state_name()
        current_time = time.time()

        # URGENCE: Nourriture critique
        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            if current_state_name != 'EmergencyState':
                self.context['emergency_transitions'] += 1
                self.context['last_emergency_transition'] = current_time
                logger.error(f"[FSMPlanner] 🚨 URGENCE CRITIQUE! Food: {current_food}")
                self._transition_to_state(EmergencyState(self))
                return self.fsm.run()

        # CORRIGÉ: Abandon coordination plus strict mais pas trop agressif
        elif (current_state_name == 'CoordinateIncantationState' and 
              current_food <= SafetyLimits.ABANDON_COORDINATION_THRESHOLD):
            time_in_state = current_time - self.context['state_change_time']
            # CORRIGÉ: Laisser plus de temps avant abandon
            if time_in_state > 15.0:  # Était 5s, maintenant 15s
                logger.warning(f"[FSMPlanner] ⚠️ Abandon coordination (food: {current_food}, temps: {time_in_state:.1f}s)")
                self._record_coordination_abandon()
                self._transition_to_state(CollectFoodState(self))
                return self.fsm.run()

        # COLLECTE: Nourriture faible mais pas critique
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

    def _record_coordination_abandon(self):
        """Enregistre un abandon de coordination avec limite."""
        # CORRIGÉ: Limite le compteur pour éviter l'accumulation
        max_abandon_count = 3
        self.context['coordination_abandon_count'] = min(
            self.context['coordination_abandon_count'] + 1, 
            max_abandon_count
        )
        self.context['last_coordination_abandon'] = time.time()
        logger.debug(f"[FSMPlanner] Abandon coordination enregistré ({self.context['coordination_abandon_count']}/{max_abandon_count})")

    def _handle_level_change_corrected(self) -> Optional[Any]:
        """
        Gestion CORRIGÉE du changement de niveau.
        
        Returns:
            Action appropriée ou None
        """
        old_level = self.last_level
        new_level = self.state.level
        current_food = self.state.get_food_count()

        logger.info(f"[FSMPlanner] 🆙 LEVEL UP! {old_level} → {new_level} (food: {current_food})")
        self.last_level = new_level
        
        # CORRIGÉ: Reset complet des échecs de coordination après level up
        self.context['coordination_failures'] = 0
        self.context['coordination_abandon_count'] = 0
        self.context['coordination_cooldown_until'] = 0.0
        self._reset_transition_counters()
        self.context['level_up_processed'] = True

        # Ajuster le seuil de coordination selon le niveau
        if new_level >= 3:
            self.context['coordination_food_threshold'] = FoodThresholds.COORDINATION_MIN + 2
        else:
            self.context['coordination_food_threshold'] = FoodThresholds.COORDINATION_MIN

        # RÈGLE 1: Niveau 2 = Reproduction si nourriture suffisante
        if new_level == ReproductionRules.TRIGGER_LEVEL and not self.state.reproduction_completed:
            if current_food >= ReproductionRules.MIN_FOOD_REQUIRED:
                logger.info(f"[FSMPlanner] 👶 REPRODUCTION IMMÉDIATE (food: {current_food})")
                self._force_transition_to_reproduction()
                return self.fsm.run()
            else:
                logger.info(f"[FSMPlanner] 🍖 Collecte food pour reproduction")
                self._force_transition_to_food_collection()
                return self.fsm.run()

        # RÈGLE 2: Niveau ≥ 3 = Préparation coordination avec gestion de survie
        elif new_level >= 3:
            min_food_for_coord = self.context['coordination_food_threshold']
            
            if current_food < min_food_for_coord:
                logger.info(f"[FSMPlanner] 🍖 Collecte food pour coordination (need: {min_food_for_coord})")
                self._force_transition_to_food_collection()
            elif self.state.has_missing_resources():
                logger.info(f"[FSMPlanner] ⚒️ Collecte ressources pour coordination (niveau {new_level})")
                self._force_transition_to_resource_collection()
            else:
                logger.info(f"[FSMPlanner] 🤝 Coordination niveau {new_level}")
                self._force_transition_to_coordination()
            return self.fsm.run()

        return None

    def _can_attempt_coordination(self) -> bool:
        """
        Vérifie si on peut tenter une coordination CORRIGÉE.
        
        Returns:
            True si coordination possible
        """
        if self.state.level == 1:
            return self._can_attempt_incantation()
        
        # CORRIGÉ: Vérifier le cooldown mais de manière moins restrictive
        if self._is_coordination_in_cooldown():
            remaining_cooldown = self.context['coordination_cooldown_until'] - time.time()
            if remaining_cooldown > 5.0:  # Seulement si cooldown significatif
                logger.debug(f"[FSMPlanner] Coordination en cooldown: {remaining_cooldown:.1f}s")
                return False
        
        return (
            self.state.level >= 2 and
            not self.state.has_missing_resources() and
            self.context['coordination_failures'] < 4  # CORRIGÉ: Plus tolérant (était 3)
        )

    def _check_progression_opportunities_corrected(self):
        """Vérification CORRIGÉE des opportunités de progression."""
        current_state_name = self.fsm.get_current_state_name()
        current_time = time.time()
        current_food = self.state.get_food_count()

        if current_state_name in ['IncantationState', 'EmergencyState', 'ReproductionState']:
            return

        if (current_state_name == 'CoordinateIncantationState' and 
            current_time - self.context['state_change_time'] < 20.0):  # Était 8s, maintenant 20s
            return

        if (self._can_attempt_incantation() and 
            current_food >= self.context['coordination_food_threshold'] and
            not self._is_coordination_in_cooldown()):
            
            time_since_last_attempt = current_time - self.context['last_coordination_attempt']
            if (self.context['coordination_failures'] < 3 and
                time_since_last_attempt > 20.0):
                
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
            
            return self.context['explore_food_spam_count'] > 15
            
        return False

    def _handle_explore_food_spam(self) -> Optional[Any]:
        """
        Gère le spam d'exploration avec priorité à la survie.
        
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
        
        if self._can_attempt_coordination():
            logger.info("[FSMPlanner] → Coordination forcée (spam)")
            if self.state.level == 1:
                self._transition_to_state(IncantationState(self))
            else:
                self._transition_to_state(CoordinateIncantationState(self))
            return self.fsm.run()
        
        self._force_exploration(10.0)
        return self.fsm.run()

    def _can_attempt_incantation(self) -> bool:
        """
        Vérification centralisée pour l'incantation avec gestion de survie.
        
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
            min_food_required = self.context['coordination_food_threshold']
            
        return current_food >= min_food_required

    def _handle_priority_events(self):
        """Gère les événements prioritaires avec logique de survie."""
        current_food = self.state.get_food_count()
        current_state_name = self.fsm.get_current_state_name()

        if (self.state.should_reproduce() and 
            self.state.level == ReproductionRules.TRIGGER_LEVEL and 
            current_state_name != 'ReproductionState' and
            current_food >= ReproductionRules.MIN_FOOD_REQUIRED):
            logger.info("[FSMPlanner] 👶 PRIORITÉ: Transition reproduction (niveau 2)")
            self._force_transition_to_reproduction()

    def _check_and_prevent_infinite_loops(self):
        """Prévient les boucles infinies avec gestion de survie."""
        food_transitions = self.context['food_to_resources_transitions']
        resource_transitions = self.context['resources_to_food_transitions']
        
        if food_transitions >= 3 or resource_transitions >= 3:
            logger.warning(f"[FSMPlanner] 🔄 Boucle détectée! Food→Res: {food_transitions}, Res→Food: {resource_transitions}")
            self._force_exploration(15.0)  # Durée réduite

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
        self.context['emergency_transitions'] = 0
        self.context['last_transition_reset'] = time.time()
        self.context['level_up_processed'] = False
        # CORRIGÉ: Reset partiel des échecs de coordination
        if self.context['coordination_failures'] > 0:
            self.context['coordination_failures'] = max(0, self.context['coordination_failures'] - 1)
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

        if command_type.value == 'Incantation':
            logger.info(f"[FSMPlanner] 🎉 INCANTATION RÉUSSIE! Nouveau niveau: {self.state.level}")
            self.context['successful_coordinations'] += 1
            self.context['coordination_failures'] = 0

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
            command_type.value == 'Incantation'):
            self.context['coordination_failures'] += 1
            logger.warning(f"[FSMPlanner] Échec incantation coordonnée {self.context['coordination_failures']}")

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
                'coordination_min': FoodThresholds.COORDINATION_MIN,
                'sufficient': FoodThresholds.SUFFICIENT,
                'abundant': FoodThresholds.ABUNDANT
            },
            'level': self.state.level,
            'decisions': self.decision_count,
            'can_incant': self._can_attempt_incantation(),
            'can_coordinate': self._can_attempt_coordination(),
            'should_reproduce': self.state.should_reproduce(),
            'missing_resources': self.state.has_missing_resources(),
            'coordination_failures': self.context['coordination_failures'],
            'coordination_food_threshold': self.context['coordination_food_threshold'],
            'emergency_transitions': self.context['emergency_transitions'],
            'forced_exploration': self._is_in_forced_exploration(),
            'level_up_processed': self.context['level_up_processed'],
            'coordination_abandon_count': self.context['coordination_abandon_count'],
            'coordination_cooldown': max(0, self.context['coordination_cooldown_until'] - time.time()),
            'successful_coordinations': self.context['successful_coordinations'],
            'coordination_state_time': self.context.get('coordination_state_time', 0),
            'transition_counters': {
                'food_to_resources': self.context['food_to_resources_transitions'],
                'resources_to_food': self.context['resources_to_food_transitions']
            },
            'required_players': IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1),
            'time_since_state_change': time.time() - self.context['state_change_time'],
            'global_coordination_active': True
        }