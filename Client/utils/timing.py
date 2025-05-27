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
    def __init__(self, freq= Constants.FREQ_DEFAULT.value):
        self.freq = freq
        self.time_unit = 1.0 / freq
        self.last_action_time = 0
        self.action_queue = []

    def calculate_action_duration(self, cmd_type: CommandType) -> float:
        """Calcule la durée d'une action selon la fréquence du serveur."""
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
        """Vérifie si on peut exécuter une nouvelle action."""
        current_time = time.time()
        return current_time >= self.last_action_time

    def register_action(self, cmd_type: CommandType) -> None:
        """Enregistre une action et calcule le prochain moment d'exécution."""
        duration = self.calculate_action_duration(cmd_type)
        self.last_action_time = time.time() + duration

    def get_sleep_time(self) -> float:
        """Retourne le temps d'attente avant la prochaine action."""
        current_time = time.time()
        return max(0, self.last_action_time - current_time)