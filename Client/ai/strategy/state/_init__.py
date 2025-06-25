##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## Package des états FSM - ai/strategy/state/__init__.py
##

"""
Package des états FSM pour la survie dans Zappy.

Ce package contient tous les états de la machine à états finis,
chacun gérant une stratégie spécifique de survie :

États disponibles :
- EmergencyState : Gestion des urgences alimentaires critiques
- CollectFoodState : Collecte préventive et sécurisée de nourriture  
- CollectResourcesState : Collecte de ressources pour progression
- ExploreState : Exploration intelligente et adaptative

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

__all__ = [
    'EmergencyState',
    'CollectFoodState', 
    'CollectResourcesState',
    'ExploreState'
]

# Métadonnées des états
STATE_METADATA = {
    'EmergencyState': {
        'priority': 1,  # Priorité maximale
        'description': 'Gestion des urgences alimentaires critiques',
        'triggers': ['FOOD_EMERGENCY'],
        'color': '🚨',
        'safety_level': 'CRITICAL'
    },
    'CollectFoodState': {
        'priority': 2,
        'description': 'Collecte préventive de nourriture',
        'triggers': ['FOOD_LOW'],
        'color': '🍖',
        'safety_level': 'WARNING'
    },
    'CollectResourcesState': {
        'priority': 3,
        'description': 'Collecte de ressources pour progression',
        'triggers': ['RESOURCES_FOUND', 'FOOD_SUFFICIENT'],
        'color': '⚒️',
        'safety_level': 'NORMAL'
    },
    'ExploreState': {
        'priority': 4,
        'description': 'Exploration intelligente',
        'triggers': ['FOOD_SUFFICIENT', 'NO_TARGETS'],
        'color': '🗺️',
        'safety_level': 'SAFE'
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
        'ExploreState': ExploreState
    }

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
    """Retourne une description des transitions possibles entre états."""
    return {
        'EmergencyState': {
            'to': ['CollectFoodState'],
            'condition': 'FOOD_SUFFICIENT'
        },
        'CollectFoodState': {
            'to': ['EmergencyState', 'ExploreState', 'CollectResourcesState'],
            'condition': 'FOOD_EMERGENCY | FOOD_SUFFICIENT | RESOURCES_FOUND'
        },
        'CollectResourcesState': {
            'to': ['EmergencyState', 'CollectFoodState', 'ExploreState'],
            'condition': 'FOOD_EMERGENCY | FOOD_LOW | RESOURCES_COLLECTED'
        },
        'ExploreState': {
            'to': ['EmergencyState', 'CollectFoodState', 'CollectResourcesState'],
            'condition': 'FOOD_EMERGENCY | FOOD_LOW | RESOURCES_FOUND'
        }
    }