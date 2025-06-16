# agent_pool.py

import threading
import time
from typing import List
from protocol.connection import Connection
from utils.timing import TimingManager
from utils.logger import logger
from ai.agent import Agent

class AgentThreads:
    """
    Maintient un ensemble d'agents (threads) actifs.
    À la création d'un fork, on réplique un nouvel Agent dans un thread.
    On supprime proprement les threads dont l'Agent est mort.
    """

    def __init__(self, host: str, port: int, team_name: str, freq: int):
        self.host = host
        self.port = port
        self.team_name = team_name
        self.freq = freq

        self._threads: List[threading.Thread] = []
        self._agents: List[Agent] = []
        self._lock = threading.Lock()

    def start_initial_agent(self):
        """
        Lance le premier agent (agent "mère") dans un thread.
        """
        conn = Connection(self.host, self.port)
        conn.handshake(self.team_name)

        agent = Agent(conn, self.freq, self.team_name, self)
        t = threading.Thread(target=agent.run_loop, daemon=True)
        with self._lock:
            self._threads.append(t)
            self._agents.append(agent)
        t.start()
        logger.info("Agent mère démarré.")

    def create_new_agent(self):
        """
        Appelé par un Agent lorsqu'il exécute `fork` et
        que le serveur a accepté (nouvel œuf créé).
        Crée un nouveau client + thread sur le même team_name.
        """
        conn = Connection(self.host, self.port)
        conn.handshake(self.team_name)

        agent = Agent(conn, self.freq, self.team_name ,self)
        t = threading.Thread(target=agent.run_loop, daemon=True)
        with self._lock:
            self._threads.append(t)
            self._agents.append(agent)
        t.start()
        logger.info("Nouvel agent (fork) démarré sur un thread séparé.")

    def agent_dead(self, agent: "Agent"):
        """
        Notification provenant d'un Agent lorsque sa boucle run_loop() se termine
        (mort). On supprime l'agent et son thread de nos listes.
        """
        with self._lock:
            if agent in self._agents:
                idx = self._agents.index(agent)
                self._agents.pop(idx)
                self._threads.pop(idx)
        logger.info(f"Agent {agent.agent_id} retiré (dead).")

    def close_client(self):
        """
        Attend la fin de tous les threads (en cas de shutdown général).
        """
        with self._lock:
            threads = list(self._threads)
        for t in threads:
            t.join()
