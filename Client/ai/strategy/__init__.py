##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## FSM Package initialization
##

"""
Package FSM pour la logique de survie intelligente de Zappy.

Ce package contient une machine à états finis (FSM) complète pour gérer
la survie de l'IA avec les composants suivants :

États principaux :
- EmergencyState : Gestion des situations critiques de survie
- CollectFoodState : Collecte préventive de nourriture
- CollectResourcesState : Collecte de ressources pour incantation
- ExploreState : Exploration intelligente et adaptative

Composants de support :
- FSMPlanner : Planificateur principal avec gestion d'événements
- EventDetector : Détection intelligente d'événements de jeu
- Pathfinder : Navigation et pathfinding optimisés

Usage :
    from ai.strategy.fsm_planner import FSMPlanner
    
    # Dans votre agent
    planner = FSMPlanner(command_manager, game_state, message_bus)
    action = planner.decide_next_action()
"""

from .fsm import Event, State, StateMachine, StateFactory
from .Basic_ai.fsm_planner import FSMPlanner
from .fsm_event import EventDetector
from .pathfinding import Pathfinder, RelativeTarget

# États disponibles
from .state.emergency import EmergencyState
from .state.collect_food import CollectFoodState
from .state.collect_resources import CollectResourcesState
from .state.explore import ExploreState

__version__ = "1.0.0"
__author__ = "Epitech Zappy Team"

__all__ = [
    # Core FSM
    'Event',
    'State', 
    'StateMachine',
    'StateFactory',
    
    # Main components
    'FSMPlanner',
    'EventDetector',
    'Pathfinder',
    'RelativeTarget',
    
    # States
    'EmergencyState',
    'CollectFoodState', 
    'CollectResourcesState',
    'ExploreState'
]

# Configuration par défaut
DEFAULT_CONFIG = {
    'food_thresholds': {
        'base_critical': 8,
        'base_safe': 20,
        'base_abundant': 35
    },
    'timing': {
        'inventory_check_interval': 10.0,
        'vision_check_interval': 15.0,
        'emergency_check_interval': 5.0
    },
    'pathfinding': {
        'max_commands_per_path': 12,
        'exploration_forward_bias': 0.4,
        'turn_penalty': 0.1
    },
    'fsm': {
        'max_stuck_attempts': 3,
        'pattern_change_threshold': 15,
        'log_interval': 30.0
    }
}

def create_survival_planner(command_manager, game_state, message_bus, config=None):
    """
    Factory function pour créer un planificateur de survie configuré.
    
    Args:
        command_manager: Gestionnaire de commandes
        game_state: État du jeu
        message_bus: Bus de messages
        config: Configuration optionnelle (utilise DEFAULT_CONFIG si None)
    
    Returns:
        FSMPlanner configuré et prêt à l'emploi
    """
    if config is None:
        config = DEFAULT_CONFIG
    
    planner = FSMPlanner(command_manager, game_state, message_bus)
    
    # Appliquer configuration si nécessaire
    # (pour l'instant, la configuration est intégrée dans les classes)
    
    return planner

def get_package_info():
    """Retourne les informations du package."""
    return {
        'name': 'Zappy FSM Survival',
        'version': __version__,
        'author': __author__,
        'description': 'Machine à états finis pour la survie intelligente dans Zappy',
        'states': len(__all__) - 4,  # Nombre d'états disponibles
        'config': DEFAULT_CONFIG
    }