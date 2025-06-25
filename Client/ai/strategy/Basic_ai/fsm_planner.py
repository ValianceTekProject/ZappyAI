##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## FSM Planner COMPLET - Stratégie de survie optimisée
##

import time
from typing import Optional, Any, Dict
from ai.strategy.fsm import StateMachine, Event, StateFactory
from ai.strategy.fsm_event import EventDetector
from ai.strategy.state.emergency import EmergencyState
from ai.strategy.state.collect_food import CollectFoodState
from ai.strategy.state.collect_resources import CollectResourcesState
from ai.strategy.state.explore import ExploreState
from utils.logger import logger
from config import Constants

class FSMPlanner:
    """
    Planificateur FSM pour la survie de l'IA.
    Gère les transitions entre états selon les besoins critiques.
    """
    
    def __init__(self, command_manager, game_state, message_bus):
        """Initialisation du FSMPlanner avec détection d'événements."""
        self.cmd_mgr = command_manager
        self.state = game_state
        self.bus = message_bus
        
        # Détecteur d'événements pour surveiller l'état du jeu
        self.event_detector = EventDetector(self.state)
        
        # Context partagé entre les états
        self.context = {
            'current_target': None,
            'command_queue': [],
            'stuck_counter': 0,
            'last_position': None,
            'needs_vision_update': False,
            'needs_inventory_check': False,
            'last_inventory_time': time.time(),
            'last_vision_time': time.time()
        }
        
        # Seuils de nourriture adaptatifs selon le niveau
        self._update_food_thresholds()
        
        # Initialisation avec état d'urgence ou collecte de nourriture
        initial_state = self._determine_initial_state()
        self.fsm = StateMachine(initial_state)
        
        # Compteurs pour debug et optimisation
        self.decision_count = 0
        self.last_state_change = time.time()
        
        logger.info(f"[FSMPlanner] Initialisé avec état: {self.fsm.get_current_state_name()}")

    def _determine_initial_state(self):
        """Détermine l'état initial selon la situation actuelle."""
        current_food = self.state.get_food_count()
        
        if current_food <= self.food_thresholds['critical']:
            logger.warning(f"[FSMPlanner] Démarrage en mode URGENCE (food: {current_food})")
            return EmergencyState(self)
        elif current_food <= self.food_thresholds['safe']:
            logger.info(f"[FSMPlanner] Démarrage en collecte de nourriture (food: {current_food})")
            return CollectFoodState(self)
        else:
            logger.info(f"[FSMPlanner] Démarrage en exploration (food: {current_food})")
            return ExploreState(self)

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
        """Point d'entrée principal - logique de décision FSM."""
        self.decision_count += 1
        current_time = time.time()
        
        # Vérification préliminaire des conditions d'envoi
        if not self._can_make_decision():
            return None
            
        try:
            # Mise à jour des seuils si le niveau a changé
            self._update_food_thresholds()
            
            # Détection et traitement des événements
            events = self.event_detector.detect_events()
            self._handle_events(events)
            
            # Exécution de l'état actuel
            action = self.fsm.run()
            
            # Log périodique pour debug
            if self.decision_count % 20 == 0:
                self._log_status()
                
            return action
            
        except Exception as e:
            logger.error(f"[FSMPlanner] Erreur lors de la décision: {e}")
            # En cas d'erreur, forcer un LOOK pour récupérer l'état
            return self.cmd_mgr.look()

    def _can_make_decision(self) -> bool:
        """Vérifie si on peut prendre une décision."""
        if self.state.command_already_send:
            return False
            
        if self.cmd_mgr.get_pending_count() >= 8:  # Limite conservative
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
                if current_state_name not in ['EmergencyState', 'CollectFoodState']:
                    logger.info(f"[FSMPlanner] Nourriture faible, collecte nécessaire (food: {current_food})")
                    new_state = CollectFoodState(self)
                    self.fsm.transition_to(new_state)
                    self.last_state_change = time.time()
                    break
                    
            elif event == Event.FOOD_SUFFICIENT:
                if current_state_name in ['EmergencyState', 'CollectFoodState']:
                    logger.info(f"[FSMPlanner] Nourriture suffisante, transition vers exploration (food: {current_food})")
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

    def get_context(self) -> Dict[str, Any]:
        """Retourne le contexte partagé entre les états."""
        return self.context

    def update_context(self, key: str, value: Any):
        """Met à jour le contexte partagé."""
        self.context[key] = value

    def on_command_success(self, command_type, response=None):
        """Appelé quand une commande réussit."""
        self.context['stuck_counter'] = 0
        
        # Notification à l'état actuel
        if hasattr(self.fsm.state, 'on_command_success'):
            self.fsm.state.on_command_success(command_type, response)

    def on_command_failed(self, command_type, response=None):
        """Appelé quand une commande échoue."""
        self.context['stuck_counter'] += 1
        logger.warning(f"[FSMPlanner] Commande {command_type} échouée, stuck_counter: {self.context['stuck_counter']}")
        
        # Si trop d'échecs, forcer exploration
        if self.context['stuck_counter'] >= 3:
            logger.warning("[FSMPlanner] Trop d'échecs, reset vers exploration")
            self.context['current_target'] = None
            self.context['command_queue'].clear()
            
            if self.fsm.get_current_state_name() != 'EmergencyState':
                new_state = ExploreState(self)
                self.fsm.transition_to(new_state)
        
        # Notification à l'état actuel
        if hasattr(self.fsm.state, 'on_command_failed'):
            self.fsm.state.on_command_failed(command_type, response)

    def _log_status(self):
        """Log périodique pour debug."""
        current_food = self.state.get_food_count()
        state_name = self.fsm.get_current_state_name()
        target = self.context.get('current_target')
        queue_size = len(self.context.get('command_queue', []))
        
        logger.info(f"[FSMPlanner] État: {state_name}, Food: {current_food}, "
                   f"Target: {target.resource_type if target else None}, "
                   f"Queue: {queue_size}, Decisions: {self.decision_count}")

    def get_current_strategy_info(self) -> Dict[str, Any]:
        """Retourne les informations de stratégie pour debug."""
        return {
            'state': self.fsm.get_current_state_name(),
            'food_count': self.state.get_food_count(),
            'food_thresholds': self.food_thresholds,
            'target': self.context.get('current_target'),
            'queue_size': len(self.context.get('command_queue', [])),
            'stuck_counter': self.context.get('stuck_counter', 0),
            'decisions': self.decision_count,
            'last_state_change': time.time() - self.last_state_change
        }