##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## constant
##

from enum import Enum


class FoodThresholds:
    """Seuils de nourriture unifiés avec logique de coordination optimisée."""
    CRITICAL = 8  # Urgence absolue
    SUFFICIENT = 15  # Suffisant pour actions normales
    ABUNDANT = 25  # Abondant pour incantation
    COORDINATION_MIN = 12  # Minimum pour participer à la coordination
    REPRODUCTION_MIN = 20  # Minimum pour reproduction
    SAFE_ABANDON_THRESHOLD = 10  # Seuil d'abandon sécurisé


class IncantationRequirements:
    """Exigences pour les incantations selon le niveau (Zappy PDF)."""

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
    """Protocole de coordination pour les incantations multi-joueurs CORRIGÉ."""
    
    RESPONSE_HERE = "here"
    RESPONSE_COMING = "coming" 
    RESPONSE_BUSY = "busy"
    
    BROADCAST_TIMEOUT = 30.0
    COORDINATION_TIMEOUT = 25.0
    BROADCAST_COOLDOWN = 2.0
    
    MAX_COORDINATION_ATTEMPTS = 5
    MIN_FOOD_TO_HELP = FoodThresholds.COORDINATION_MIN
    MIN_FOOD_TO_INITIATE = FoodThresholds.COORDINATION_MIN


class ReproductionRules:
    """Règles strictes pour la reproduction."""
    TRIGGER_LEVEL = 2
    MIN_FOOD_REQUIRED = FoodThresholds.REPRODUCTION_MIN
    MAX_ATTEMPTS = 3
    TIMEOUT = 30.0


class AgentRoles:
    """Rôles des agents dans le système de coordination."""
    INCANTER = "incanter"
    HELPER = "helper"
    SURVIVOR = "survivor"


class GameplayConstants:
    """Constantes de gameplay du Zappy."""
    
    FOOD_SURVIVAL_TIME = 126
    MAX_LEVEL = 8
    BASE_VISION_RANGE = 3
    MAX_PENDING_COMMANDS = 10
    
    INVENTORY_CHECK_INTERVAL = 8.0
    VISION_UPDATE_INTERVAL = 5.0
    
    MAX_STUCK_ATTEMPTS = 3
    MAX_COLLECTION_ATTEMPTS = 2


class TimingConstants:
    """Constantes de timing pour les commandes."""
    COMMAND_TIMEOUT = 6.0
    INCANTATION_TIMEOUT = 60.0
    COORDINATION_TIMEOUT = CoordinationProtocol.COORDINATION_TIMEOUT
    FALLBACK_TIMEOUT = 15.0

class ResourceNames:
    """Noms des ressources pour une meilleure lisibilité."""
    FOOD = "food"
    LINEMATE = "linemate"
    DERAUMERE = "deraumere"
    SIBUR = "sibur"
    MENDIANE = "mendiane"
    PHIRAS = "phiras"
    THYSTAME = "thystame"

class StateTransitionThresholds:
    """Seuils pour les transitions d'états avec hystérésis optimisée CORRIGÉS."""
    
    FOOD_EMERGENCY_THRESHOLD = FoodThresholds.CRITICAL
    FOOD_LOW_THRESHOLD = FoodThresholds.SUFFICIENT
    FOOD_SUFFICIENT_THRESHOLD = FoodThresholds.ABUNDANT

    MIN_FOOD_FOR_LEVEL_1_INCANTATION = 12
    MIN_FOOD_FOR_COORDINATION = FoodThresholds.COORDINATION_MIN
    MIN_FOOD_FOR_REPRODUCTION = FoodThresholds.REPRODUCTION_MIN
    
    FOOD_TO_EXPLORATION_THRESHOLD = FoodThresholds.ABUNDANT
    RESOURCES_TO_FOOD_THRESHOLD = FoodThresholds.SUFFICIENT
    COORDINATION_ABANDON_THRESHOLD = FoodThresholds.COORDINATION_MIN

    EMERGENCY_EXIT_THRESHOLD = FoodThresholds.CRITICAL

class BroadcastDirections:
    """Directions pour le système de broadcast (Zappy PDF page 7)."""
    HERE = 0
    FRONT = 1
    FRONT_RIGHT = 2
    RIGHT = 3
    BACK_RIGHT = 4
    BACK = 5
    BACK_LEFT = 6
    LEFT = 7
    FRONT_LEFT = 8

class MessageValidation:
    """Constantes pour la validation des messages."""
    MAX_MESSAGE_AGE = CoordinationProtocol.BROADCAST_TIMEOUT
    MIN_TEAM_NAME_LENGTH = 1
    MAX_TEAM_NAME_LENGTH = 50
    MESSAGE_ENCODING = 'utf-8'


class ResourcePriorities:
    """Priorités de collecte des ressources par rareté."""
    RARITY_ORDER = [
        'thystame',
        'phiras',
        'mendiane', 
        'sibur',
        'deraumere',
        'linemate'
    ]


class CoordinationStates:
    """États possibles dans le processus de coordination."""
    SEARCHING = "searching"
    REQUEST_SENT = "request_sent"
    RESPONSE_RECEIVED = "response_received"
    HELPERS_GATHERING = "helpers_gathering"
    READY_TO_INCANT = "ready_to_incant"
    INCANTING = "incanting"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class SafetyLimits:
    """Limites de sécurité pour éviter la mort des agents CORRIGÉES."""
    MIN_FOOD_FOR_COORDINATION_SAFETY = FoodThresholds.COORDINATION_MIN
    MIN_FOOD_FOR_INCANTATION_SAFETY = FoodThresholds.COORDINATION_MIN
    ABANDON_COORDINATION_THRESHOLD = FoodThresholds.SAFE_ABANDON_THRESHOLD
    EMERGENCY_TRANSITION_THRESHOLD = FoodThresholds.CRITICAL
    
    MAX_COORDINATION_TIME = 20.0
    MAX_INCANTATION_ATTEMPTS = 2
    MAX_HELPER_WAIT_TIME = 15.0

class DebugLevels:
    """Niveaux de debug pour les logs."""
    CRITICAL = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5


class NetworkConstants:
    """Constantes réseau pour les connexions."""
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 4242
    CONNECTION_TIMEOUT = 10.0
    RECONNECT_ATTEMPTS = 3
    HEARTBEAT_INTERVAL = 30.0


class PerformanceConstants:
    """Constantes pour l'optimisation des performances."""
    MAX_COMMAND_HISTORY = 50
    MAX_VISION_HISTORY = 10
    CLEANUP_INTERVAL = 60.0
    MEMORY_CLEANUP_THRESHOLD = 1000


class ErrorConstants:
    """Constantes pour la gestion d'erreurs."""
    MAX_CONSECUTIVE_ERRORS = 5
    ERROR_RECOVERY_DELAY = 2.0
    CRITICAL_ERROR_THRESHOLD = 3
    AUTO_RECOVERY_TIMEOUT = 30.0