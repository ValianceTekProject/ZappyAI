##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## agent
##

import time
import select
from typing import Tuple
from protocol.connection import Connection
from protocol.commands import CommandManager, CommandStatus
from utils.timing import TimingManager
from utils.game_state import GameState
from utils.logger import logger
from config import CommandType
from ai.strategy.planner import Planner

class Agent:
    def __init__(self, connection: Connection, freq: int):
        """
        Initialise un nouvel agent"
        """
        self.conn = connection
        self.freq = freq
        self.timing = TimingManager(self.freq)
        self.state = GameState()
        self.commands = CommandManager(self.conn, self.timing, self.state)
        self.planner = Planner(self.commands, self.state)
        self.initialized = False
        self.init_stage = 0

    def run_loop(self):
        """
        Boucle principale de l'agent :
         - lit les réponses entrantes,
         - traite les commandes terminées,
         - met à jour l'état,
         - planifie de nouvelles actions.
        """
        while True:
            responses = self.read_non_blocking()
            completed = self.commands.process_responses(responses)

            for cmd in completed:
                if cmd.status == CommandStatus.DEAD:
                    logger.info(f"Agent is dead at level {self.state.level}")
                    return

                if cmd.type == CommandType.LOOK:
                    self.state.update_vision(cmd.response, self.state.get_position(), self.state.get_orientation())

                print(f"CMD {cmd.type.name} completed with status {cmd.status.name}, response: {cmd.response}")
                self.state.update(cmd)

            if not self.initialized:
                self.initialize_agent()
                continue

            if self.initialized and not self.state.command_already_send and self.commands.get_pending_count() < 10:
                self.planner.decide_next_action()

    def initialize_agent(self):
        """
        Initialise l'agent par étapes :
         1. LOOK : pour avoir une vision de départ.
         2. INVENTORY : pour connaître les ressources initiales.
        """
        if self.init_stage == 0:
            if not self.commands.has_pending():
                self.commands.look()
                self.init_stage = 1

        elif self.init_stage == 1:
            if not self.commands.has_pending():
                self.commands.inventory()
                self.init_stage = 2

        elif self.init_stage == 2:
            self.initialized = True

    def read_non_blocking(self) -> list:
        """
        Lit les données réseau sans bloquer l'exécution.
        Utilise `select` pour vérifier si le socket est prêt à lire.
        """
        sock = self.conn.get_socket()
        if not sock:
            logger.warning("Socket non initialisé, skip lecture")
            return []

        ready = select.select([sock], [], [], 0)
        responses = []

        if ready[0]:
            data = self.conn.receive_raw()
            responses = self.conn.split_responses(data)

        return responses
