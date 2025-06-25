##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## FSM base classes CORRIGÉES avec gestion d'événements et pathfinding
##

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Any
from utils.logger import logger

class Event(Enum):
    """Événements du système FSM - COMPLETS."""
    
    # Événements alimentaires
    FOOD_EMERGENCY = "food_emergency"
    FOOD_LOW = "food_low"
    FOOD_SUFFICIENT = "food_sufficient"
    FOOD_FOUND = "food_found"
    
    # Événements de vision
    NEED_VISION = "need_vision"
    NEED_INVENTORY = "need_inventory"
    
    # Événements de ressources
    RESOURCES_FOUND = "resources_found"
    RESOURCES_COLLECTED = "resources_collected"

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

# ✅ NOUVEAU: Factory pour créer des états
class StateFactory:
    """Factory pour créer des instances d'états."""
    
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