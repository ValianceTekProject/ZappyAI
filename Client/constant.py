##
## EPITECH PROJECT, 2025
## ZappyAI
## File description:
## constant
##

from enum import Enum


class FoodThresholds:
    CRITICAL = 10
    SUFFICIENT = 20
    ABUNDANT = 35
    COORDINATION_MIN = 12
    REPRODUCTION_MIN = 25
    SAFE_ABANDON_THRESHOLD = 8


class IncantationRequirements:
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
    RESPONSE_HERE = "here"
    RESPONSE_COMING = "coming"
    RESPONSE_BUSY = "busy"

    BROADCAST_TIMEOUT = 45.0
    COORDINATION_TIMEOUT = 35.0
    BROADCAST_COOLDOWN = 2.0

    MAX_COORDINATION_ATTEMPTS = 6
    MIN_FOOD_TO_HELP = 10
    MIN_FOOD_TO_INITIATE = FoodThresholds.COORDINATION_MIN


class ReproductionRules:
    TRIGGER_LEVEL = 2
    MIN_FOOD_REQUIRED = FoodThresholds.REPRODUCTION_MIN
    MAX_ATTEMPTS = 3
    TIMEOUT = 30.0


class AgentRoles:
    INCANTER = "incanter"
    HELPER = "helper"
    SURVIVOR = "survivor"


class GameplayConstants:
    FOOD_SURVIVAL_TIME = 126
    MAX_LEVEL = 8
    BASE_VISION_RANGE = 3
    MAX_PENDING_COMMANDS = 10

    INVENTORY_CHECK_INTERVAL = 8.0
    VISION_UPDATE_INTERVAL = 5.0

    MAX_STUCK_ATTEMPTS = 4
    MAX_COLLECTION_ATTEMPTS = 3


class TimingConstants:
    COMMAND_TIMEOUT = 6.0
    INCANTATION_TIMEOUT = 60.0
    COORDINATION_TIMEOUT = CoordinationProtocol.COORDINATION_TIMEOUT
    FALLBACK_TIMEOUT = 20.0


class ResourceNames:
    FOOD = "food"
    LINEMATE = "linemate"
    DERAUMERE = "deraumere"
    SIBUR = "sibur"
    MENDIANE = "mendiane"
    PHIRAS = "phiras"
    THYSTAME = "thystame"


class StateTransitionThresholds:
    FOOD_EMERGENCY_THRESHOLD = FoodThresholds.CRITICAL
    FOOD_LOW_THRESHOLD = FoodThresholds.SUFFICIENT
    FOOD_SUFFICIENT_THRESHOLD = FoodThresholds.ABUNDANT

    MIN_FOOD_FOR_LEVEL_1_INCANTATION = 15
    MIN_FOOD_FOR_COORDINATION = FoodThresholds.COORDINATION_MIN
    MIN_FOOD_FOR_REPRODUCTION = FoodThresholds.REPRODUCTION_MIN

    FOOD_TO_EXPLORATION_THRESHOLD = FoodThresholds.ABUNDANT
    RESOURCES_TO_FOOD_THRESHOLD = FoodThresholds.SUFFICIENT
    COORDINATION_ABANDON_THRESHOLD = FoodThresholds.SAFE_ABANDON_THRESHOLD

    EMERGENCY_EXIT_THRESHOLD = FoodThresholds.CRITICAL


class BroadcastDirections:
    HERE = 0
    FRONT = 1
    FRONT_RIGHT = 2
    RIGHT = 3
    BACK_RIGHT = 4
    BACK = 5
    BACK_LEFT = 6
    LEFT = 7
    FRONT_LEFT = 8


class SafetyLimits:
    MIN_FOOD_FOR_COORDINATION_SAFETY = 9
    MIN_FOOD_FOR_INCANTATION_SAFETY = FoodThresholds.COORDINATION_MIN
    ABANDON_COORDINATION_THRESHOLD = FoodThresholds.SAFE_ABANDON_THRESHOLD
    EMERGENCY_TRANSITION_THRESHOLD = FoodThresholds.CRITICAL

    MAX_COORDINATION_TIME = 30.0
    MAX_INCANTATION_ATTEMPTS = 3
    MAX_HELPER_WAIT_TIME = 25.0


class MovementConstants:
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


class CoordinationHelperSettings:
    INCANTER_PROBABILITY_BASE = 0.25
    HELPER_PROBABILITY_BASE = 0.75

    RESPONSE_DELAY_MIN = 0.3
    RESPONSE_DELAY_MAX = 1.5

    MOVEMENT_RETRY_COUNT = 2
    MOVEMENT_SUCCESS_WAIT = 0.8

    HERE_CONFIRMATION_INTERVAL = 2.5
    COMING_TO_HERE_TIMEOUT = 8.0


class SpamPrevention:
    MAX_FOOD_TO_RESOURCES_TRANSITIONS = 3
    MAX_RESOURCES_TO_FOOD_TRANSITIONS = 3
    MAX_EXPLORE_FOOD_SPAM_COUNT = 15

    MAX_COORDINATION_ABANDON_COUNT = 2
    COORDINATION_SPAM_COOLDOWN = 15.0

    TRANSITION_RESET_INTERVAL = 60.0
    STATE_CHANGE_MIN_INTERVAL = 1.5
