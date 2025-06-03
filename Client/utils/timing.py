##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## timing
##

import time
from utils.logger import logger
from config import Constants, CommandType

class TimingManager:
    """Gère le timing des actions et la consommation de nourriture."""

    def __init__(self, freq: int = Constants.FREQ_DEFAULT.value):
        self.freq = freq
        self.time_unit = 1.0 / freq
        self.last_action_time = 0.0
        self.last_food_tick_time = time.time()

    def calculate_action_duration(self, cmd_type: CommandType) -> float:
        """
        Calcule la durée d'une action en fonction du type de commande
        et de la fréquence du serveur.
        """
        duration_map = {
            CommandType.FORWARD: Constants.DUR_FORWARD.value,
            CommandType.RIGHT: Constants.DUR_TURN.value,
            CommandType.LEFT: Constants.DUR_TURN.value,
            CommandType.LOOK: Constants.DUR_LOOK.value,
            CommandType.INVENTORY: Constants.DUR_INVENTORY.value,
            CommandType.BROADCAST: Constants.DUR_BROADCAST.value,
            CommandType.FORK: Constants.DUR_FORK.value,
            CommandType.INCANTATION: Constants.DUR_INCANTATION.value,
            CommandType.TAKE: Constants.DUR_TURN.value,
            CommandType.SET: Constants.DUR_TURN.value,
            CommandType.EJECT: Constants.DUR_TURN.value,
            CommandType.CONNECT_NBR: Constants.DUR_INVENTORY.value,
        }
        base_duration = duration_map.get(cmd_type, 1)
        return base_duration * self.time_unit

    def can_execute_action(self) -> bool:
        """
        Vérifie si le délai depuis la dernière action est écoulé,
        donc si une nouvelle action peut être lancée.
        """
        return time.time() >= self.last_action_time

    def register_action(self, cmd_type: CommandType) -> None:
        """
        Enregistre une nouvelle action et calcule la prochaine fenêtre
        de disponibilité en fonction de sa durée.
        """
        duration = self.calculate_action_duration(cmd_type)
        self.last_action_time = time.time() + duration

    def get_sleep_time(self) -> float:
        """
        Retourne le temps d'attente (en secondes) avant de pouvoir
        exécuter la prochaine action.
        """
        return max(0.0, self.last_action_time - time.time())

    def has_lost_food(self) -> bool:
        """
        Vérifie si un tick de consommation de nourriture est passé.
        Renvoie True si le joueur perd une unité de nourriture.
        """
        current_time = time.time()
        food_interval = Constants.FOODS_LOSS_TIME.value * self.time_unit

        if current_time - self.last_food_tick_time >= food_interval:
            self.last_food_tick_time = current_time
            return True
        return False
