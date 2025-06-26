##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## Package des états FSM - ai/strategy/state/__init__.py - ENHANCED
##

"""
Package des états FSM ENHANCED pour la survie et progression dans Zappy.

Ce package contient tous les états de la machine à états finis,
chacun gérant une stratégie spécifique de survie et progression :

États de survie :
- EmergencyState : Gestion des urgences alimentaires critiques
- CollectFoodState : Collecte préventive et sécurisée de nourriture  
- CollectResourcesState : Collecte de ressources pour progression
- ExploreState : Exploration intelligente et adaptative

États de progression (NOUVEAUX) :
- IncantationState : Gestion de l'incantation pour monter de niveau
- ReproductionState : Gestion de la reproduction (fork) après niveau 2

Chaque état hérite de la classe State de base et implémente :
- execute() : Logique principale de l'état
- on_enter() : Actions à l'entrée de l'état
- on_exit() : Actions à la sortie de l'état
- on_event() : Gestion des événements et transitions
- on_command_success() : Traitement des succès de commandes
- on_command_failed() : Traitement des échecs de commandes
"""

from .emergency import EmergencyState
from .collect_food import CollectFoodState
from .collect_resources import CollectResourcesState
from .explore import ExploreState
from .incantation import IncantationState
from .reproduction import ReproductionState

__all__ = [
    'EmergencyState',
    'CollectFoodState', 
    'CollectResourcesState',
    'ExploreState',
    'IncantationState',
    'ReproductionState'
]

# Métadonnées des états ENHANCED
STATE_METADATA = {
    'EmergencyState': {
        'priority': 1,  # Priorité maximale
        'description': 'Gestion des urgences alimentaires critiques',
        'triggers': ['FOOD_EMERGENCY'],
        'color': '🚨',
        'safety_level': 'CRITICAL',
        'category': 'survival'
    },
    'CollectFoodState': {
        'priority': 2,
        'description': 'Collecte préventive de nourriture',
        'triggers': ['FOOD_LOW'],
        'color': '🍖',
        'safety_level': 'WARNING',
        'category': 'survival'
    },
    'IncantationState': {
        'priority': 3,  # Priorité élevée pour la progression
        'description': 'Incantation pour progression de niveau',
        'triggers': ['CAN_INCANT', 'RESOURCES_COMPLETE'],
        'color': '🔮',
        'safety_level': 'NORMAL',
        'category': 'progression'
    },
    'ReproductionState': {
        'priority': 4,
        'description': 'Reproduction après niveau 2',
        'triggers': ['LEVEL_2_ACHIEVED', 'SHOULD_REPRODUCE'],
        'color': '👶',
        'safety_level': 'NORMAL',
        'category': 'progression'
    },
    'CollectResourcesState': {
        'priority': 5,
        'description': 'Collecte de ressources pour progression',
        'triggers': ['RESOURCES_FOUND', 'MISSING_RESOURCES'],
        'color': '⚒️',
        'safety_level': 'NORMAL',
        'category': 'preparation'
    },
    'ExploreState': {
        'priority': 6,  # Priorité la plus basse
        'description': 'Exploration intelligente',
        'triggers': ['FOOD_SUFFICIENT', 'NO_TARGETS'],
        'color': '🗺️',
        'safety_level': 'SAFE',
        'category': 'exploration'
    }
}

def get_state_info(state_name: str) -> dict:
    """Retourne les métadonnées d'un état."""
    return STATE_METADATA.get(state_name, {})

def get_all_states():
    """Retourne toutes les classes d'états disponibles."""
    return {
        'EmergencyState': EmergencyState,
        'CollectFoodState': CollectFoodState,
        'CollectResourcesState': CollectResourcesState,
        'ExploreState': ExploreState,
        'IncantationState': IncantationState,
        'ReproductionState': ReproductionState
    }

def get_states_by_category(category: str) -> dict:
    """Retourne les états d'une catégorie donnée."""
    states = {}
    for state_name, metadata in STATE_METADATA.items():
        if metadata.get('category') == category:
            states[state_name] = get_all_states()[state_name]
    return states

def create_state_by_name(state_name: str, planner):
    """Factory pour créer un état par son nom."""
    states = get_all_states()
    if state_name in states:
        return states[state_name](planner)
    raise ValueError(f"État inconnu: {state_name}")

def get_state_priority_order():
    """Retourne les états triés par priorité (urgence décroissante)."""
    return sorted(STATE_METADATA.items(), key=lambda x: x[1]['priority'])

def describe_state_transitions():
    """Retourne une description des transitions possibles entre états - ENHANCED."""
    return {
        'EmergencyState': {
            'to': ['CollectFoodState'],
            'condition': 'FOOD_SUFFICIENT'
        },
        'CollectFoodState': {
            'to': ['EmergencyState', 'IncantationState', 'ReproductionState', 'ExploreState', 'CollectResourcesState'],
            'condition': 'FOOD_EMERGENCY | CAN_INCANT | SHOULD_REPRODUCE | FOOD_SUFFICIENT | RESOURCES_FOUND'
        },
        'IncantationState': {
            'to': ['EmergencyState', 'ReproductionState', 'ExploreState'],
            'condition': 'FOOD_EMERGENCY | INCANT_SUCCESS | INCANT_FAILED'
        },
        'ReproductionState': {
            'to': ['EmergencyState', 'CollectFoodState', 'IncantationState', 'ExploreState'],
            'condition': 'FOOD_EMERGENCY | FOOD_LOW | CAN_INCANT | REPRODUCTION_COMPLETE'
        },
        'CollectResourcesState': {
            'to': ['EmergencyState', 'CollectFoodState', 'IncantationState', 'ExploreState'],
            'condition': 'FOOD_EMERGENCY | FOOD_LOW | CAN_INCANT | RESOURCES_COLLECTED'
        },
        'ExploreState': {
            'to': ['EmergencyState', 'CollectFoodState', 'IncantationState', 'ReproductionState', 'CollectResourcesState'],
            'condition': 'FOOD_EMERGENCY | FOOD_LOW | CAN_INCANT | SHOULD_REPRODUCE | RESOURCES_FOUND'
        }
    }

def get_progression_states():
    """Retourne les états liés à la progression."""
    return get_states_by_category('progression')

def get_survival_states():
    """Retourne les états liés à la survie."""
    return get_states_by_category('survival')

def validate_state_transition(from_state: str, to_state: str) -> bool:
    """Valide qu'une transition entre états est logique."""
    if from_state not in STATE_METADATA or to_state not in STATE_METADATA:
        return False
    
    from_priority = STATE_METADATA[from_state]['priority']
    to_priority = STATE_METADATA[to_state]['priority']
    
    # Les urgences peuvent toujours prendre le dessus
    if to_priority <= 2:  # Emergency ou CollectFood
        return True
    
    # Sinon, transition normale selon logique métier
    transitions = describe_state_transitions()
    allowed_transitions = transitions.get(from_state, {}).get('to', [])
    
    return to_state in allowed_transitions

def get_state_flow_summary():
    """Retourne un résumé du flux d'états."""
    return {
        'categories': {
            'survival': ['EmergencyState', 'CollectFoodState'],
            'progression': ['IncantationState', 'ReproductionState'],
            'preparation': ['CollectResourcesState'],
            'exploration': ['ExploreState']
        },
        'priority_order': [state for state, _ in get_state_priority_order()],
        'typical_flow': [
            'ExploreState',
            'CollectResourcesState', 
            'IncantationState',
            'ReproductionState',
            'ExploreState'
        ],
        'emergency_flow': [
            'EmergencyState',
            'CollectFoodState',
            'ExploreState'
        ]
    }