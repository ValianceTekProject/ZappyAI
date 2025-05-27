##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## game_state
##

import time
from typing import Dict, List, Any, Optional, Tuple
from config import Constants, Orientation
from utils.logger import logger

class ResourceTracker:
    def __init__(self):
        self.collected = {}  # Dict[str, int]
        self.consumed = {}   # Dict[str, int]
        self.efficiency = {} # Dict[str, float] - resources per minute

    def track_collection(self, resource: str, amount: int = 1) -> None:
        """Enregistre la collecte d'une ressource."""
        pass

    def track_consumption(self, resource: str, amount: int = 1) -> None:
        """Enregistre la consommation d'une ressource."""
        pass

    def get_efficiency(self, resource: str) -> float:
        """Retourne l'efficacité de collecte d'une ressource."""
        pass

class GameState:
    def __init__(self):
        # Player state
        self.level = 1
        self.position = (0, 0)
        self.orientation = Orientation.SOUTH
        self.inventory = {resource: 0 for resource in Constants.RESOURCES.value}
        self.alive = True

        # Game info
        self.map_width = 0
        self.map_height = 0
        self.team_slots = 0

        # Performance tracking
        self.resource_tracker = ResourceTracker()
        self.actions_taken = 0
        self.successful_actions = 0
        self.deaths = 0
        self.level_ups = 0

        # Time tracking
        self.game_start_time = time.time()
        self.last_action_time = 0
        self.time_per_level = {}
        
        # Statistics
        self.tiles_explored = set()
        self.players_encountered = set()
        self.broadcasts_sent = 0
        self.broadcasts_received = 0

    def update_position(self, x: int, y: int) -> None:
        """Met à jour la position du joueur."""
        pass

    def update_inventory(self, new_inventory: Dict[str, int]) -> None:
        """Met à jour l'inventaire."""
        pass

    def level_up(self) -> None:
        """Gère une montée de niveau."""
        pass

    def die(self) -> None:
        """Gère la mort du joueur."""
        pass

    def can_level_up(self) -> bool:
        """Vérifie si le joueur peut monter de niveau."""
        pass

    def get_missing_resources(self) -> Dict[str, int]:
        """Retourne les ressources manquantes pour le level up."""
        pass
