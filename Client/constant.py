##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## constants - Configuration centralisée unifiée
##

from enum import Enum


class FoodThresholds:
    """Seuils de nourriture unifiés pour tout le système."""
    CRITICAL = 10
    SUFFICIENT = 20
    ABUNDANT = 35
    COORDINATION_MIN = 25
    REPRODUCTION_MIN = 25  # Corrigé : était 30, maintenant 25


class IncantationRequirements:
    """Exigences pour les incantations selon le niveau (Zappy PDF)."""

    REQUIRED_PLAYERS = {
        1: 1,  # SOLO autorisé pour niveau 1 uniquement
        2: 2,  # Coordination OBLIGATOIRE
        3: 2,  # Coordination OBLIGATOIRE
        4: 4,  # Coordination OBLIGATOIRE
        5: 4,  # Coordination OBLIGATOIRE
        6: 6,  # Coordination OBLIGATOIRE
        7: 6   # Coordination OBLIGATOIRE
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
    """Protocole de coordination pour les incantations multi-joueurs."""
    
    RESPONSE_HERE = "here"
    RESPONSE_COMING = "coming"
    RESPONSE_BUSY = "busy"
    
    BROADCAST_TIMEOUT = 30.0
    COORDINATION_TIMEOUT = 45.0
    BROADCAST_COOLDOWN = 3.0
    
    MAX_COORDINATION_ATTEMPTS = 3
    MIN_FOOD_TO_HELP = FoodThresholds.COORDINATION_MIN
    MIN_FOOD_TO_INITIATE = FoodThresholds.COORDINATION_MIN


class ReproductionRules:
    """Règles strictes pour la reproduction."""
    TRIGGER_LEVEL = 2  # Reproduction activée UNIQUEMENT au niveau 2
    MIN_FOOD_REQUIRED = FoodThresholds.REPRODUCTION_MIN  # 25 au lieu de 30
    MAX_ATTEMPTS = 2
    TIMEOUT = 30.0


class AgentRoles:
    """Rôles des agents dans le système de coordination."""
    INCANTER = "incanter"
    HELPER = "helper"
    SURVIVOR = "survivor"


class GameplayConstants:
    """Constantes de gameplay du Zappy (Zappy PDF)."""
    
    FOOD_SURVIVAL_TIME = 126
    MAX_LEVEL = 8
    BASE_VISION_RANGE = 3
    MAX_PENDING_COMMANDS = 10
    
    INVENTORY_CHECK_INTERVAL = 10.0
    VISION_UPDATE_INTERVAL = 6.0
    
    MAX_STUCK_ATTEMPTS = 3
    MAX_COLLECTION_ATTEMPTS = 2


class TimingConstants:
    """Constantes de timing pour les commandes."""
    COMMAND_TIMEOUT = 5.0
    INCANTATION_TIMEOUT = 60.0
    COORDINATION_TIMEOUT = CoordinationProtocol.COORDINATION_TIMEOUT
    FALLBACK_TIMEOUT = 20.0


class StateTransitionThresholds:
    """Seuils pour les transitions d'états avec hystérésis."""
    
    FOOD_EMERGENCY_THRESHOLD = FoodThresholds.CRITICAL
    FOOD_LOW_THRESHOLD = FoodThresholds.SUFFICIENT
    FOOD_SUFFICIENT_THRESHOLD = FoodThresholds.ABUNDANT
    
    MIN_FOOD_FOR_LEVEL_1_INCANTATION = 15
    MIN_FOOD_FOR_COORDINATION = FoodThresholds.COORDINATION_MIN
    MIN_FOOD_FOR_REPRODUCTION = FoodThresholds.REPRODUCTION_MIN
    
    # Hystérésis pour éviter les boucles
    FOOD_TO_EXPLORATION_THRESHOLD = FoodThresholds.ABUNDANT + 5  # 40
    RESOURCES_TO_FOOD_THRESHOLD = FoodThresholds.SUFFICIENT - 5  # 15


class BroadcastDirections:
    """Directions pour le système de broadcast (Zappy PDF)."""
    HERE = 0
    FRONT = 1
    FRONT_RIGHT = 2
    RIGHT = 3
    BACK_RIGHT = 4
    BACK = 5
    BACK_LEFT = 6
    LEFT = 7
    FRONT_LEFT = 8


class CoordinationMessages:
    """Messages standardisés pour la coordination."""
    
    REQUEST_PREFIX = "INCANT_REQ"
    RESPONSE_PREFIX = "INCANT_RESP"
    
    @staticmethod
    def format_request(level: int, required_players: int) -> str:
        """
        Formate une requête d'incantation.
        
        Args:
            level: Niveau de l'incantation
            required_players: Nombre de joueurs requis
            
        Returns:
            Message formaté
        """
        return f"{CoordinationMessages.REQUEST_PREFIX}:{level}:{required_players}"
    
    @staticmethod
    def format_response(request_id: str, response: str) -> str:
        """
        Formate une réponse d'incantation.
        
        Args:
            request_id: ID de la requête
            response: Réponse (here/coming/busy)
            
        Returns:
            Message formaté
        """
        return f"{CoordinationMessages.RESPONSE_PREFIX}:{request_id}:{response}"