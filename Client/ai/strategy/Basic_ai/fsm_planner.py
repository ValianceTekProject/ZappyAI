##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## fsm_planner
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
from utils.logger import logger
from config import Constants

class FSMPlanner:
    """
    Planificateur FSM ENHANCED - CORRIGÉ pour éviter blocage en reproduction.
    """

    def __init__(self, command_manager, game_state, message_bus):
        """Initialisation du FSMPlanner enhanced."""
        self.cmd_mgr = command_manager
        self.state = game_state
        self.bus = message_bus

        self.agent_thread = getattr(game_state, 'agent_thread', None)
        if self.agent_thread is None:
            logger.warning("[FSMPlanner] Aucun agent_thread trouvé - reproduction ne fonctionnera pas")
        else:
            logger.debug("[FSMPlanner] agent_thread récupéré depuis game_state")

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
            'last_level': self.state.level
        }

        self._update_food_thresholds()

        initial_state = self._determine_initial_state()
        self.fsm = StateMachine(initial_state)

        self.decision_count = 0
        self.last_state_change = time.time()
        self.last_level_check = self.state.level

        logger.info(f"[FSMPlanner] Enhanced FSM initialisé avec état: {self.fsm.get_current_state_name()}")

    def _determine_initial_state(self):
        """Détermine l'état initial selon la situation actuelle."""
        current_food = self.state.get_food_count()

        if current_food <= self.food_thresholds['critical']:
            logger.warning(f"[FSMPlanner] Démarrage en mode URGENCE (food: {current_food})")
            return EmergencyState(self)

        if self._should_attempt_reproduction():
            logger.info(f"[FSMPlanner] Démarrage en reproduction (niveau {self.state.level})")
            return ReproductionState(self)

        if current_food <= self.food_thresholds['safe']:
            logger.info(f"[FSMPlanner] Démarrage en collecte de nourriture (food: {current_food})")
            return CollectFoodState(self)

        if self.state.has_missing_resources():
            logger.info(f"[FSMPlanner] Démarrage en collecte de ressources")
            return CollectResourcesState(self)

        logger.info(f"[FSMPlanner] Démarrage en exploration (food: {current_food})")
        return ExploreState(self)

    def _can_attempt_incantation(self) -> bool:
        """Vérification CONDITIONS RÉDUITES pour faciliter l'incantation."""
        current_state_name = self.fsm.get_current_state_name()

        if self.state.level >= 2:
            required_players = self.state.get_required_player_count()
            if required_players > 1:
                logger.debug(f"Incantation bloquée niveau {self.state.level}: nécessite {required_players} joueurs")
                return False

        if current_state_name == 'IncantationState':
            return True

        min_food_for_incant = 25
        if self.state.get_food_count() < min_food_for_incant:
            return False

        requirements = self.state.get_incantation_requirements()
        inventory = self.state.get_inventory()

        for resource, needed in requirements.items():
            if inventory.get(resource, 0) < needed:
                return False

        if self.state.level >= Constants.MAX_LEVEL.value:
            return False

        return True

    def _should_attempt_reproduction(self) -> bool:
        """Vérifie si on devrait tenter une reproduction."""
        if self.state.level < 2:
            return False

        min_food_for_fork = self._get_min_food_for_reproduction()
        if self.state.get_food_count() < min_food_for_fork:
            return False

        if getattr(self.state, 'needs_repro', False):
            return True

        return self.state.level >= 2

    def _get_min_food_for_incantation(self) -> int:
        """Calcule la nourriture minimale pour une incantation."""
        base = 35
        if self.state.level >= 4:
            return int(base * 1.5)
        return base

    def _get_min_food_for_reproduction(self) -> int:
        """Calcule la nourriture minimale pour une reproduction."""
        base = 20
        if self.state.level >= 3:
            return int(base * 1.3)
        return base

    def _update_food_thresholds(self):
        """Met à jour les seuils de nourriture selon le niveau."""
        base_critical = 8
        base_safe = 20

        level = self.state.level
        if level >= 7:
            multiplier = 2.5
        elif level >= 4:
            multiplier = 1.8
        else:
            multiplier = 1.0

        self.food_thresholds = {
            'critical': int(base_critical * multiplier),
            'safe': int(base_safe * multiplier),
            'abundant': int(base_safe * multiplier * 1.5)
        }

        logger.debug(f"[FSMPlanner] Seuils nourriture niveau {level}: {self.food_thresholds}")

    def decide_next_action(self) -> Optional[Any]:
        """Point d'entrée principal - CORRIGÉ avec détection fin de reproduction."""
        self.decision_count += 1

        current_food = self.state.get_food_count()
        requirements = self.state.get_incantation_requirements()
        inventory = self.state.get_inventory()
        missing = {}
        for res, needed in requirements.items():
            current_inv = inventory.get(res, 0)
            if current_inv < needed:
                missing[res] = f"{current_inv}/{needed}"

        if self.decision_count % 10 == 0:
            logger.info(f"[FSMPlanner] 🔍 DEBUG - Food: {current_food}, "
                        f"Manque: {missing}, CanIncant: {self._can_attempt_incantation()}")

        if not self._can_make_decision():
            return None

        try:
            if self.state.level != self.last_level_check:
                self._on_level_change()

            self._update_food_thresholds()

            if self._should_transition_from_reproduction():
                return None

            events = self.event_detector.detect_events()
            self._handle_events(events)

            self._check_progression_opportunities()

            action = self.fsm.run()

            if self.decision_count % 20 == 0:
                self._log_status()

            return action

        except Exception as e:
            logger.error(f"[FSMPlanner] Erreur lors de la décision: {e}")
            return self.cmd_mgr.look()

    def _should_transition_from_reproduction(self) -> bool:
        """Détecte si on doit sortir de l'état de reproduction."""
        current_state_name = self.fsm.get_current_state_name()

        if current_state_name != 'ReproductionState':
            return False

        current_state = self.fsm.state
        if hasattr(current_state, 'is_reproduction_complete') and current_state.is_reproduction_complete():
            logger.info("[FSMPlanner] 🎉 Reproduction terminée, transition vers exploration")
            self._transition_after_reproduction()
            return True

        if hasattr(current_state, 'fork_stage') and current_state.fork_stage == 4:
            logger.info("[FSMPlanner] 🎉 Reproduction terminée (fork_stage=4), transition vers exploration")
            self._transition_after_reproduction()
            return True

        return False

    def _transition_after_reproduction(self):
        """Gère la transition après reproduction terminée."""
        current_food = self.state.get_food_count()

        if current_food <= self.food_thresholds['critical']:
            logger.warning("[FSMPlanner] → Transition vers urgence après reproduction")
            new_state = EmergencyState(self)
        elif current_food <= self.food_thresholds['safe']:
            logger.info("[FSMPlanner] → Transition vers collecte nourriture après reproduction")
            new_state = CollectFoodState(self)
        elif self._can_attempt_incantation():
            logger.info("[FSMPlanner] → Transition vers incantation après reproduction")
            new_state = IncantationState(self)
        elif self.state.has_missing_resources():
            logger.info("[FSMPlanner] → Transition vers collecte ressources après reproduction")
            new_state = CollectResourcesState(self)
        else:
            logger.info("[FSMPlanner] → Transition vers exploration après reproduction")
            new_state = ExploreState(self)

        self.fsm.transition_to(new_state)
        self.last_state_change = time.time()

    def _on_level_change(self):
        """Gère le changement de niveau."""
        old_level = self.last_level_check
        new_level = self.state.level

        logger.info(f"[FSMPlanner] 🆙 LEVEL UP! {old_level} → {new_level}")
        self.last_level_check = new_level

        if new_level >= 2 and not getattr(self.state, 'needs_repro', False):
            logger.info(f"[FSMPlanner] Déclenchement reproduction pour niveau {new_level}")
            self.state.needs_repro = True
            self.context['should_reproduce'] = True

    def _check_progression_opportunities(self):
        """Vérification PLUS AGRESSIVE des opportunités de progression - CORRIGÉE."""
        current_state_name = self.fsm.get_current_state_name()

        if current_state_name in ['IncantationState', 'EmergencyState', 'ReproductionState']:
            return

        if self._can_attempt_incantation():
            logger.info("[FSMPlanner] 🔮 TRANSITION FORCÉE vers incantation")
            new_state = IncantationState(self)
            self.fsm.transition_to(new_state)
            return

        current_food = self.state.get_food_count()
        if current_food >= 25 and self.state.has_missing_resources():
            if current_state_name != 'CollectResourcesState':
                new_state = CollectResourcesState(self)
                missing = new_state._get_missing_resources()
                logger.info(f"[FSMPlanner] 🔍 TRANSITION FORCÉE vers collecte: {missing}")
                self.fsm.transition_to(new_state)
                return

    def _can_make_decision(self) -> bool:
        """Vérifie si on peut prendre une décision."""
        if self.state.command_already_send:
            return False

        if self.cmd_mgr.get_pending_count() >= 8:
            return False

        return True

    def _handle_events(self, events: list):
        """Gestion des événements avec transitions d'état appropriées."""
        current_food = self.state.get_food_count()
        current_state_name = self.fsm.get_current_state_name()

        for event in events:
            if event == Event.FOOD_EMERGENCY:
                if current_state_name != 'EmergencyState':
                    logger.warning(f"[FSMPlanner] URGENCE ALIMENTAIRE! Transition vers Emergency (food: {current_food})")
                    new_state = EmergencyState(self)
                    self.fsm.transition_to(new_state)
                    self.last_state_change = time.time()
                    break

            elif event == Event.FOOD_LOW:
                if current_state_name not in ['EmergencyState', 'CollectFoodState', 'IncantationState', 'ReproductionState']:
                    logger.info(f"[FSMPlanner] Nourriture faible, collecte nécessaire (food: {current_food})")
                    new_state = CollectFoodState(self)
                    self.fsm.transition_to(new_state)
                    self.last_state_change = time.time()
                    break

            elif event == Event.FOOD_SUFFICIENT:
                if current_state_name in ['EmergencyState', 'CollectFoodState']:
                    logger.info(f"[FSMPlanner] Nourriture suffisante, vérification progression (food: {current_food})")

                    if self._can_attempt_incantation():
                        new_state = IncantationState(self)
                    elif self._should_attempt_reproduction():
                        new_state = ReproductionState(self)
                    else:
                        new_state = ExploreState(self)

                    self.fsm.transition_to(new_state)
                    self.last_state_change = time.time()
                    break

            elif event == Event.NEED_VISION:
                self.context['needs_vision_update'] = True
                logger.debug("[FSMPlanner] Vision update nécessaire")

            elif event == Event.NEED_INVENTORY:
                self.context['needs_inventory_check'] = True
                logger.debug("[FSMPlanner] Inventory check nécessaire")

    def _handle_post_incantation(self):
        """Gère la transition après une incantation réussie."""
        current_level = self.state.level
        current_food = self.state.get_food_count()

        logger.info(f"[FSMPlanner] 📋 Post-incantation niveau {current_level}, food: {current_food}")

        if current_level >= 2 and current_food >= 20 and getattr(self.state, 'needs_repro', False):
            logger.info("[FSMPlanner] → Transition vers reproduction après incantation")
            new_state = ReproductionState(self)
            self.fsm.transition_to(new_state)

        elif current_food >= 25:
            logger.info("[FSMPlanner] → Transition vers exploration après incantation")
            new_state = ExploreState(self)
            self.fsm.transition_to(new_state)

        else:
            logger.info("[FSMPlanner] → Transition vers collecte nourriture après incantation")
            new_state = CollectFoodState(self)
            self.fsm.transition_to(new_state)

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
            self._handle_post_incantation()

    def on_command_failed(self, command_type, response=None):
        """Appelé quand une commande échoue."""
        self.context['stuck_counter'] += 1
        logger.warning(f"[FSMPlanner] Commande {command_type} échouée, stuck_counter: {self.context['stuck_counter']}")

        if self.context['stuck_counter'] >= 3:
            current_state_name = self.fsm.get_current_state_name()
            if current_state_name not in ['EmergencyState', 'IncantationState']:
                logger.warning("[FSMPlanner] Trop d'échecs, reset vers exploration")
                self.context['current_target'] = None
                self.context['command_queue'].clear()

                new_state = ExploreState(self)
                self.fsm.transition_to(new_state)

        if hasattr(self.fsm.state, 'on_command_failed'):
            self.fsm.state.on_command_failed(command_type, response)

    def _log_status(self):
        """Log périodique pour debug."""
        current_food = self.state.get_food_count()
        state_name = self.fsm.get_current_state_name()
        target = self.context.get('current_target')
        queue_size = len(self.context.get('command_queue', []))

        can_incant = self._can_attempt_incantation()
        should_repro = self._should_attempt_reproduction()

        logger.info(f"[FSMPlanner] État: {state_name}, Food: {current_food}, "
                   f"Niveau: {self.state.level}, Target: {target.resource_type if target else None}, "
                   f"Queue: {queue_size}, CanIncant: {can_incant}, ShouldRepro: {should_repro}, "
                   f"Decisions: {self.decision_count}")

    def get_current_strategy_info(self) -> Dict[str, Any]:
        """Retourne les informations de stratégie pour debug."""
        return {
            'state': self.fsm.get_current_state_name(),
            'food_count': self.state.get_food_count(),
            'food_thresholds': self.food_thresholds,
            'level': self.state.level,
            'target': self.context.get('current_target'),
            'queue_size': len(self.context.get('command_queue', [])),
            'stuck_counter': self.context.get('stuck_counter', 0),
            'decisions': self.decision_count,
            'last_state_change': time.time() - self.last_state_change,
            'can_incant': self._can_attempt_incantation(),
            'should_reproduce': self._should_attempt_reproduction(),
            'missing_resources': self.state.has_missing_resources(),
            'incant_requirements': self.state.get_incantation_requirements(),
            'inventory': self.state.get_inventory()
        }
