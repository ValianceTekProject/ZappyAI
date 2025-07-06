##
## EPITECH PROJECT, 2025
## ZappyAI
## File description:
## constant - Constantes centralisées sans magic numbers
##

from enum import Enum


class FoodThresholds:
    """Seuils de nourriture centralisés selon spécifications"""
    CRITICAL = 10
    SUFFICIENT = 20
    ABUNDANT = 35
    COORDINATION_MIN = 12
    REPRODUCTION_MIN = 25


class IncantationRequirements:
    """Requirements pour les incantations par niveau"""
    REQUIRED_PLAYERS = {
        1: 1,
        2: 2,
        3: 2,
        4: 4,
        5: 4,
        6: 6,
        7: 6
    }

    REQUIRED_RESOURCES = {
        1: {'linemate': 1},
        2: {'linemate': 1, 'deraumere': 1, 'sibur': 1},
        3: {'linemate': 2, 'sibur': 1, 'phiras': 2},
        4: {'linemate': 1, 'deraumere': 1, 'sibur': 2, 'phiras': 1},
        5: {'linemate': 1, 'deraumere': 2, 'sibur': 1, 'mendiane': 3},
        6: {'linemate': 1, 'deraumere': 2, 'sibur': 3, 'phiras': 1},
        7: {'linemate': 2, 'deraumere': 2, 'sibur': 2, 'mendiane': 2, 'phiras': 2, 'thystame': 1}
    }


class CoordinationProtocol:
    """Protocole de coordination simplifié"""
    RESPONSE_HERE = "here"
    BROADCAST_INTERVAL = 3.0
    COORDINATION_TIMEOUT = 45.0
    MAX_COORDINATION_TIME = 60.0
    INCANTER_BROADCAST_COOLDOWN = 2.0
    MIN_FOOD_TO_COORDINATE = FoodThresholds.COORDINATION_MIN


class ReproductionRules:
    """Règles de reproduction strictes"""
    TRIGGER_LEVEL = 2
    MIN_FOOD_REQUIRED = FoodThresholds.REPRODUCTION_MIN
    MAX_ATTEMPTS = 3
    TIMEOUT = 30.0


class AgentRoles:
    """Rôles des agents"""
    INCANTER = "incanter"
    HELPER = "helper"
    SURVIVOR = "survivor"


class GameplayConstants:
    """Constantes de gameplay"""
    FOOD_SURVIVAL_TIME = 126
    MAX_LEVEL = 8
    BASE_VISION_RANGE = 3
    MAX_PENDING_COMMANDS = 10
    INVENTORY_CHECK_INTERVAL = 8.0
    VISION_UPDATE_INTERVAL = 5.0
    MAX_STUCK_ATTEMPTS = 4
    MAX_COLLECTION_ATTEMPTS = 3


class TimingConstants:
    """Constantes de timing"""
    COMMAND_TIMEOUT = 6.0
    INCANTATION_TIMEOUT = 60.0
    COORDINATION_TIMEOUT = CoordinationProtocol.COORDINATION_TIMEOUT
    FALLBACK_TIMEOUT = 20.0


class ResourceNames:
    """Noms des ressources"""
    FOOD = "food"
    LINEMATE = "linemate"
    DERAUMERE = "deraumere"
    SIBUR = "sibur"
    MENDIANE = "mendiane"
    PHIRAS = "phiras"
    THYSTAME = "thystame"


class StateTransitionThresholds:
    """Seuils pour les transitions d'état basés sur FoodThresholds"""
    FOOD_EMERGENCY_THRESHOLD = FoodThresholds.CRITICAL
    FOOD_LOW_THRESHOLD = FoodThresholds.SUFFICIENT
    FOOD_SUFFICIENT_THRESHOLD = FoodThresholds.ABUNDANT
    MIN_FOOD_FOR_LEVEL_1_INCANTATION = 15
    MIN_FOOD_FOR_COORDINATION = FoodThresholds.COORDINATION_MIN
    MIN_FOOD_FOR_REPRODUCTION = FoodThresholds.REPRODUCTION_MIN
    FOOD_TO_EXPLORATION_THRESHOLD = FoodThresholds.ABUNDANT
    RESOURCES_TO_FOOD_THRESHOLD = FoodThresholds.SUFFICIENT
    EMERGENCY_EXIT_THRESHOLD = FoodThresholds.CRITICAL
    ABANDON_COORDINATION_THRESHOLD = 8


class BroadcastDirections:
    """Directions des broadcasts selon le protocole Zappy"""
    HERE = 0
    FRONT = 1
    FRONT_RIGHT = 2
    RIGHT = 3
    BACK_RIGHT = 4
    BACK = 5
    BACK_LEFT = 6
    LEFT = 7
    FRONT_LEFT = 8


class MovementConstants:
    """Constantes pour les mouvements selon les directions Zappy"""
    DIRECTION_TO_COMMANDS = {
        BroadcastDirections.HERE: [],
        BroadcastDirections.FRONT: ["Forward"],
        BroadcastDirections.FRONT_RIGHT: ["Right", "Forward"],
        BroadcastDirections.RIGHT: ["Right", "Forward"],
        BroadcastDirections.BACK_RIGHT: ["Right", "Right", "Forward"],
        BroadcastDirections.BACK: ["Right", "Right", "Forward"],
        BroadcastDirections.BACK_LEFT: ["Left", "Forward"],
        BroadcastDirections.LEFT: ["Left", "Forward"],
        BroadcastDirections.FRONT_LEFT: ["Left", "Forward"],
    }
    MAX_MOVEMENT_COMMANDS = 3
    MOVEMENT_TIMEOUT = 12.0


class SafetyLimits:
    """Limites de sécurité pour éviter la mort"""
    MIN_FOOD_FOR_COORDINATION_SAFETY = 9
    MIN_FOOD_FOR_INCANTATION_SAFETY = FoodThresholds.COORDINATION_MIN
    ABANDON_COORDINATION_THRESHOLD = StateTransitionThresholds.ABANDON_COORDINATION_THRESHOLD
    EMERGENCY_TRANSITION_THRESHOLD = FoodThresholds.CRITICAL
    MAX_COORDINATION_TIME = CoordinationProtocol.MAX_COORDINATION_TIME
    MAX_INCANTATION_ATTEMPTS = 3
    MAX_HELPER_WAIT_TIME = 25.0