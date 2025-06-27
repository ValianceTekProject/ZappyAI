##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## fsm
##

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Any
from utils.logger import logger

class Event(Enum):
    """Événements du système FSM"""
    FOOD_EMERGENCY = "food_emergency"
    FOOD_LOW = "food_low"
    FOOD_SUFFICIENT = "food_sufficient"
    FOOD_FOUND = "food_found"
    NEED_VISION = "need_vision"
    NEED_INVENTORY = "need_inventory"
    RESOURCES_FOUND = "resources_found"
    RESOURCES_COLLECTED = "resources_collected"
    CAN_INCANT = "can_incant"
    INCANT_READY = "incant_ready"
    INCANT_SUCCESS = "incant_success"
    INCANT_FAILED = "incant_failed"
    SHOULD_REPRODUCE = "should_reproduce"
    REPRODUCTION_READY = "reproduction_ready"
    REPRODUCTION_SUCCESS = "reproduction_success"
    REPRODUCTION_FAILED = "reproduction_failed"
    LEVEL_UP = "level_up"
    LEVEL_2_ACHIEVED = "level_2_achieved"
    MAX_LEVEL_REACHED = "max_level_reached"
    MISSING_RESOURCES = "missing_resources"
    RESOURCES_COMPLETE = "resources_complete"
    BROADCAST_RECEIVED = "broadcast_received"
    HELPER_NEEDED = "helper_needed"
    HELPER_AVAILABLE = "helper_available"

class State(ABC):
    """Classe de base CORRIGÉE pour tous les états FSM."""
    def __init__(self, planner):
        self.planner = planner
        self.cmd_mgr = planner.cmd_mgr
        self.state = planner.state
        self.context = planner.get_context()
        self.role = getattr(self.state, 'role', 'unknown')

    @abstractmethod
    def execute(self) -> Optional[Any]:
        """Exécute la logique de l'état et retourne une action."""
        pass

    def on_enter(self):
        """Appelé quand l'état devient actif."""
        state_name = type(self).__name__
        logger.debug(f"[{state_name}] ⇒ Entrée")

    def on_exit(self):
        """Appelé quand l'état devient inactif."""
        state_name = type(self).__name__
        logger.debug(f"[{state_name}] ⇐ Sortie")

    def on_event(self, event: Event) -> Optional['State']:
        """Traite un événement et retourne un nouvel état si transition nécessaire."""
        return None

class StateMachine:
    """Machine à états CORRIGÉE avec gestion d'événements."""
    def __init__(self, initial_state: State):
        self.state = initial_state
        self.state.on_enter()
        logger.info(f"[FSM] Initialisé avec état: {type(initial_state).__name__}")

    def run(self) -> Optional[Any]:
        """Exécute l'état actuel."""
        try:
            return self.state.execute()
        except Exception as e:
            logger.error(f"[FSM] Erreur exécution état {type(self.state).__name__}: {e}")
            return None

    def handle_event(self, event: Event) -> bool:
        """Traite un événement et effectue une transition si nécessaire."""
        try:
            new_state = self.state.on_event(event)
            if new_state:
                self.transition_to(new_state)
                return True
            return False
        except Exception as e:
            logger.error(f"[FSM] Erreur traitement événement {event}: {e}")
            return False

    def transition_to(self, new_state: State):
        """Effectue une transition vers un nouvel état."""
        old_state_name = type(self.state).__name__
        new_state_name = type(new_state).__name__
        logger.info(f"[FSM] Transition: {old_state_name} → {new_state_name}")
        try:
            self.state.on_exit()
            self.state = new_state
            self.state.on_enter()
        except Exception as e:
            logger.error(f"[FSM] Erreur transition: {e}")

    def get_current_state_name(self) -> str:
        """Retourne le nom de l'état actuel."""
        return type(self.state).__name__

class StateFactory:
    """Factory pour créer des instances d'états"""
    @staticmethod
    def create_explore_state(planner):
        """Crée un état d'exploration."""
        from ai.strategy.state.explore import ExploreState
        return ExploreState(planner)

    @staticmethod
    def create_collect_food_state(planner):
        """Crée un état de collecte de nourriture."""
        from ai.strategy.state.collect_food import CollectFoodState
        return CollectFoodState(planner)

    @staticmethod
    def create_emergency_state(planner):
        """Crée un état d'urgence."""
        from ai.strategy.state.emergency import EmergencyState
        return EmergencyState(planner)

    @staticmethod
    def create_collect_resources_state(planner):
        """Crée un état de collecte de ressources."""
        from ai.strategy.state.collect_resources import CollectResourcesState
        return CollectResourcesState(planner)

    @staticmethod
    def create_incantation_state(planner):
        """Crée un état d'incantation."""
        from ai.strategy.state.incantation import IncantationState
        return IncantationState(planner)

    @staticmethod
    def create_reproduction_state(planner):
        """Crée un état de reproduction."""
        from ai.strategy.state.reproduction import ReproductionState
        return ReproductionState(planner)

    @staticmethod
    def create_state_by_name(state_name: str, planner):
        """Crée un état par son nom de classe."""
        factory_methods = {
            'ExploreState': StateFactory.create_explore_state,
            'CollectFoodState': StateFactory.create_collect_food_state,
            'EmergencyState': StateFactory.create_emergency_state,
            'CollectResourcesState': StateFactory.create_collect_resources_state,
            'IncantationState': StateFactory.create_incantation_state,
            'ReproductionState': StateFactory.create_reproduction_state
        }
        if state_name in factory_methods:
            return factory_methods[state_name](planner)
        else:
            raise ValueError(f"État inconnu: {state_name}")

    @staticmethod
    def get_all_available_states():
        """Retourne la liste de tous les états disponibles."""
        return [
            'ExploreState',
            'CollectFoodState', 
            'EmergencyState',
            'CollectResourcesState',
            'IncantationState',
            'ReproductionState'
        ]

    @staticmethod
    def create_state_by_priority(planner, priority_level: str):
        """Crée un état selon le niveau de priorité."""
        priority_mapping = {
            'critical': StateFactory.create_emergency_state,
            'food': StateFactory.create_collect_food_state,
            'progression': StateFactory.create_incantation_state,
            'reproduction': StateFactory.create_reproduction_state,
            'resources': StateFactory.create_collect_resources_state,
            'exploration': StateFactory.create_explore_state
        }
        if priority_level in priority_mapping:
            return priority_mapping[priority_level](planner)
        else:
            return StateFactory.create_explore_state(planner)

    @staticmethod
    def create_state_for_situation(planner, food_count: int, level: int, has_resources: bool):
        """Crée l'état le plus approprié selon la situation actuelle."""
        if food_count <= 10:
            return StateFactory.create_emergency_state(planner)
        if food_count <= 25:
            return StateFactory.create_collect_food_state(planner)
        if has_resources and food_count >= 35:
            return StateFactory.create_incantation_state(planner)
        if level >= 2 and food_count >= 45:
            return StateFactory.create_reproduction_state(planner)
        if not has_resources and food_count >= 30:
            return StateFactory.create_collect_resources_state(planner)
        return StateFactory.create_explore_state(planner)
