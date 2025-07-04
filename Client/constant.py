##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## constants - Constantes optimisées sans magic numbers
##

from enum import Enum


class FoodThresholds:
    """Seuils de nourriture optimisés selon le niveau."""
    # Seuils de base considérablement réduits pour accélérer la progression
    BASE_CRITICAL = 10
    BASE_SAFE = 20
    BASE_ABUNDANT = 35
    BASE_EXPLORATION_THRESHOLD = 32  # Réduit de 32 à 15
    BASE_COORDINATION_THRESHOLD = 18  # Nouveau : seuil pour débuter la coordination

    # Multiplicateurs plus conservateurs
    MULTIPLIER_HIGH_LEVEL = 1.8  # Réduit de 2.5 à 1.8
    MULTIPLIER_MID_LEVEL = 1.4   # Réduit de 1.8 à 1.4
    MULTIPLIER_LOW_LEVEL = 1.0   # Inchangé


class IncantationRequirements:
    """Exigences pour les incantations selon le niveau."""

    # Nombre de joueurs requis par niveau (selon le PDF Zappy)
    REQUIRED_PLAYERS = {
        1: 1,  # SOLO autorisé pour niveau 1 uniquement
        2: 2,  # Coordination OBLIGATOIRE
        3: 2,  # Coordination OBLIGATOIRE
        4: 4,  # Coordination OBLIGATOIRE
        5: 4,  # Coordination OBLIGATOIRE
        6: 6,  # Coordination OBLIGATOIRE
        7: 6   # Coordination OBLIGATOIRE
    }

    # Ressources requises par niveau (selon le PDF Zappy)
    REQUIRED_RESOURCES = {
        1: {'linemate': 1},
        2: {'linemate': 1, 'deraumere': 1, 'sibur': 1},
        3: {'linemate': 2, 'sibur': 1, 'phiras': 2},
        4: {'linemate': 1, 'deraumere': 1, 'sibur': 2, 'phiras': 1},
        5: {'linemate': 1, 'deraumere': 2, 'sibur': 1, 'mendiane': 3},
        6: {'linemate': 1, 'deraumere': 2, 'sibur': 3, 'phiras': 1},
        7: {'linemate': 2, 'deraumere': 2, 'sibur': 2, 'mendiane': 2, 'phiras': 2, 'thystame': 1}
    }


class CoordinationMessages:
    """Messages de coordination pour les incantations."""

    # Réponses possibles à une demande d'incantation
    RESPONSE_HERE = "here"
    RESPONSE_COMING = "coming"
    RESPONSE_BUSY = "busy"

    # Timeouts optimisés pour éviter les blocages
    MESSAGE_TIMEOUT = 30.0  # Réduit de 60 à 30 secondes
    BROADCAST_COOLDOWN = 3.0  # Réduit de 5 à 3 secondes
    CLEANUP_INTERVAL = 15.0  # Réduit de 30 à 15 secondes

    # Seuils de nourriture pour coordination plus agressifs
    MIN_FOOD_TO_HELP = 15  # Réduit de 25 à 15
    HELP_OVERHEAD = 8  # Réduit de 15 à 8
    MIN_FOOD_TO_INITIATE = 22  # Réduit de 40 à 22


class AgentRoles:
    """Rôles des agents dans le système de coordination."""
    INCANTER = "incanter"
    HELPER = "helper"
    SURVIVOR = "survivor"


class TimingConstants:
    """Constantes de timing optimisées."""
    COMMAND_TIMEOUT = 3.0  # Réduit de 5 à 3 secondes
    INCANTATION_TIMEOUT = 45.0  # Réduit de 60 à 45 secondes
    COORDINATION_TIMEOUT = 25.0  # Réduit de 45 à 25 secondes
    MAX_COLLECTION_ATTEMPTS = 2  # Réduit de 3 à 2
    MAX_INCANTATION_ATTEMPTS = 2  # Inchangé
    COORDINATION_RETRY_DELAY = 5.0  # Nouveau : délai avant retry
    FALLBACK_TIMEOUT = 15.0  # Nouveau : timeout avant fallback


class VisionConstants:
    """Constantes pour la vision."""
    MAX_COMMANDS_IN_PATH = 8  # Réduit de 10 à 8
    MAX_FAILED_ATTEMPTS = 2  # Réduit de 3 à 2
    EXPLORATION_PATTERN_CHANGE_THRESHOLD = 10  # Réduit de 15 à 10


class ReproductionConstants:
    """Constantes pour la reproduction."""
    MIN_LEVEL_FOR_REPRODUCTION = 2
    MIN_FOOD_FOR_FORK_BASE = 18  # Réduit de 25 à 18
    REPRODUCTION_TIMEOUT = 20.0  # Réduit de 30 à 20 secondes
    MAX_FORK_ATTEMPTS = 2  # Inchangé


class StateTransitionThresholds:
    """Seuils pour les transitions d'états optimisés."""
    
    # Seuils de nourriture différenciés pour éviter les boucles
    FOOD_EMERGENCY_THRESHOLD = 6  # Réduit de 10 à 6
    FOOD_LOW_THRESHOLD = 12  # Réduit de 20 à 12
    FOOD_SUFFICIENT_THRESHOLD = 20  # Réduit de 35 à 20
    FOOD_EXPLORATION_RETURN_THRESHOLD = 14  # Réduit de 28 à 14
    RESOURCES_TO_FOOD_THRESHOLD = 10  # Nouveau : seuil pour passer collecte ressources → nourriture
    
    # Seuils pour incantation
    MIN_FOOD_FOR_LEVEL_1_INCANTATION = 12  # Réduit de 25 à 12
    MIN_FOOD_FOR_COORDINATION = 18  # Réduit de 40 à 18
    
    # Seuils pour reproduction
    MIN_FOOD_FOR_REPRODUCTION = 25  # Réduit de 45 à 25


class GameplayConstants:
    """Constantes de gameplay."""
    
    # Temps de survie avec 1 unité de nourriture (selon PDF Zappy)
    FOOD_SURVIVAL_TIME = 126
    
    # Niveaux maximum (selon PDF Zappy)
    MAX_LEVEL = 8
    
    # Vision (selon PDF Zappy)
    BASE_VISION_RANGE = 3
    
    # Commandes en attente maximum optimisé
    MAX_PENDING_COMMANDS = 6  # Réduit de 8 à 6
    
    # Tentatives maximum avant abandon
    MAX_STUCK_ATTEMPTS = 2  # Réduit de 3 à 2
    
    # Intervalles de vérification optimisés
    INVENTORY_CHECK_INTERVAL = 8.0  # Réduit de 12 à 8 secondes
    VISION_UPDATE_INTERVAL = 5.0  # Réduit de 8 à 5 secondes


class CoordinationStrategy:
    """Constantes pour la stratégie de coordination."""
    
    # Probabilité de devenir incanteur vs helper
    INCANTER_PROBABILITY_BASE = 0.4  # 40% de chance d'être incanteur
    INCANTER_PROBABILITY_BONUS_PER_RESOURCE = 0.1  # +10% par ressource manquante chez les autres
    
    MAX_WAIT_FOR_HELPERS = 20.0  # Maximum 20 secondes d'attente des helpers
    MAX_WAIT_AS_HELPER = 15.0  # Maximum 15 secondes d'attente comme helper
    
    MAX_COORDINATION_ATTEMPTS = 3
    
    COORDINATION_RETRY_COOLDOWN = 8.0