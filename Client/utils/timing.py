##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## timing
##

import time
from utils.logger import logger
from config import CommandType
from constant import FoodThresholds


class TimingManager:
    """Gestionnaire de timing optimisé pour la survie."""

    def __init__(self):
        """Initialise le gestionnaire de timing."""
        self.last_action_time = 0.0
        self.min_command_interval = 0.04
        self.emergency_mode = False
        self.emergency_interval = 0.015

        logger.debug(f"[TimingManager] Timing optimisé: normal={self.min_command_interval}s, urgence={self.emergency_interval}s")

    def can_execute_action(self) -> bool:
        """
        Vérifie si on peut envoyer une action avec timing adaptatif.
        
        Returns:
            True si action possible
        """
        interval = self.emergency_interval if self.emergency_mode else self.min_command_interval
        return time.time() >= self.last_action_time + interval

    def register_action(self, cmd_type: CommandType) -> None:
        """
        Enregistre une action envoyée.
        
        Args:
            cmd_type: Type de commande envoyée
        """
        self.last_action_time = time.time()

    def set_emergency_mode(self, is_emergency: bool):
        """
        Active/désactive le mode urgence.
        
        Args:
            is_emergency: True pour activer le mode urgence
        """
        if is_emergency != self.emergency_mode:
            self.emergency_mode = is_emergency
            interval = self.emergency_interval if is_emergency else self.min_command_interval
            logger.info(f"[TimingManager] Mode urgence: {is_emergency}, interval: {interval}s")

    def get_sleep_time(self) -> float:
        """
        Retourne le temps d'attente avec timing adaptatif.
        
        Returns:
            Temps d'attente en secondes
        """
        interval = self.emergency_interval if self.emergency_mode else self.min_command_interval
        next_available = self.last_action_time + interval
        return max(0.0, next_available - time.time())

    def update_from_food_level(self, food_count: int):
        """
        Met à jour le mode timing selon le niveau de nourriture.
        
        Args:
            food_count: Niveau de nourriture actuel
        """
        should_be_emergency = food_count <= FoodThresholds.CRITICAL
        self.set_emergency_mode(should_be_emergency)