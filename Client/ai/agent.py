##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## agent
##

import time
from typing import Dict
from protocol.commands import CommandManager, CommandType
from ai.strategy.mcts import MCTSPlanner
from ai.strategy.pathfinding import ToroidalGrid
from utils.vision import Vision
from utils.logger import logger
from config import Constants, Orientation
from utils.timing import TimingManager

class Agent:
    def __init__(self, connection, freq: int):
        self.connect = connection
        self.time_manager = TimingManager(freq)
        self.cmd = CommandManager(connection, self.time_manager)
        self.cmd_type = CommandType
        self.mcts = MCTSPlanner()
        self.freq = freq
        self.time_per_action = 1.0 / freq

        # Game state
        map_width, map_height, _ = connection.get_map_info()
        self.grid = ToroidalGrid(map_width, map_height)
        self.vision = Vision()

        # Agent state
        self.position = (0, 0)
        self.orientation = Orientation.SOUTH
        self.level = 1
        self.inventory = {}
        self.alive = True

        # AI state
        self.current_goal = None
        self.planned_path = []
        self.last_action_time = 0

    def run_loop(self):
        """Boucle principale : read, decide, act."""
        logger.info("Starting agent main loop")
        while True:
            try:
                self.process_server_responses()

                sleep_time = self.time_manager.calculate_action_duration(self.cmd_type)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                break

    def process_server_responses(self) -> None:
        """Traite les réponses du serveur."""
        pass
