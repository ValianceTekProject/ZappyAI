##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## connection
##

import socket
import time
from typing import List, Optional
from utils.logger import logger
from config import Constants, CommandType
from protocol.parser import Parser

class Connection:
    def __init__(self, host: str, port: int):
        """Initialise la connexion TCP avec le serveur Zappy."""
        self._host = host
        self._port = port
        self._sock = None
        self._map_width = None
        self._map_height = None
        self._nb_clients = None
        self._send_buffer = []
        self._receive_buffer = ""
        self._connected = False
        self._parser = Parser()
        self._connect()

    def _connect(self) -> bool:
        """Établit la connexion initiale."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(Constants.SOCKET_TIMEOUT.value)
        self._sock.connect((self._host, self._port))
        self._connected = True
        logger.info(f"Connected to server {self._host}:{self._port}")
        return True

    def _reconnect(self) -> bool:
        """Tente une reconnexion avec backoff exponentiel."""
        if self._sock:
            self._sock.close()

        for attempt in range(Constants.RECONNECT_MAX_RETRIES.value):
            delay = Constants.RECONNECT_BASE_DELAY.value * (2 ** attempt)
            logger.info(f"Reconnection attempt {attempt + 1}/{Constants.RECONNECT_MAX_RETRIES.value} in {delay}s")
            time.sleep(delay)

            if self._connect():
                return True

        logger.error("Failed to reconnect after all attempts")
        return False

    def handshake(self, team_name: str) -> None:
        """Effectue le handshake initial avec le serveur Zappy."""
        if not self._connected:
            raise ConnectionError("Not connected to server")

        welcome_msg = self.recv_line()
        if welcome_msg != "WELCOME":
            raise ValueError(f"Expected WELCOME, got: {welcome_msg}")
        logger.info("Received WELCOME from server")

        if not self.send_raw(team_name):
            raise ConnectionError("Failed to send team name")
        logger.info(f"Sent team name: {team_name}")

        client_num_msg = self.recv_line()
        if self._parser.is_error_response(client_num_msg):
            raise ValueError("error response from server because team is full or unknown")
        self._nb_clients = int(client_num_msg)
        logger.info(f"Available client slots: {self._nb_clients}")

        map_info = self.recv_line()
        dimensions = map_info.split()
        if len(dimensions) != 2:
            raise ValueError("Invalid map dimensions format")
        self._map_width = int(dimensions[0])
        self._map_height = int(dimensions[1])
        logger.info(f"Map dimensions: {self._map_width}x{self._map_height}")

        logger.info("Handshake completed successfully")

    def send_raw(self, msg: str) -> bool:
        """Envoie un message brut avec gestion d'erreur."""
        if not self._connected or not self._sock:
            logger.error("Cannot send: not connected")
            return False

        if not msg.endswith('\n'):
            msg += '\n'

        self._sock.send(msg.encode('utf-8'))
        return True

    def send_command(self, cmd_type: CommandType, *args) -> bool:
        """Envoie une commande avec gestion d'erreur."""
        if not self._connected:
            logger.error("Cannot send command: not connected")
            return False

        cmd_parts = [cmd_type.value]
        cmd_parts.extend(str(arg) for arg in args)
        command = ' '.join(cmd_parts)

        return self.send_raw(command)

    def recv_line(self) -> str:
        """Lit une ligne complète terminée par '\n'."""
        if not self._connected or not self._sock:
            raise ConnectionError("Not connected")

        while '\n' not in self._receive_buffer:
            data = self._sock.recv(1024)
            if not data:
                raise ConnectionError("Connection closed by server")
            self._receive_buffer += data.decode('utf-8')

        line, self._receive_buffer = self._receive_buffer.split('\n', 1)
        line = line.strip()
        return line

    def receive(self) -> List[str]:
        """Lit les lignes envoyées par le serveur (non-bloquant)."""
        if not self._connected or not self._sock:
            return []

        lines = []
        self._sock.settimeout(0.01)

        while True:
            data = self._sock.recv(1024)
            if not data:
                self._connected = False
                break
            self._receive_buffer += data.decode('utf-8')

            while '\n' in self._receive_buffer:
                line, self._receive_buffer = self._receive_buffer.split('\n', 1)
                line = line.strip()
                if line:
                    lines.append(line)

        if self._sock:
            self._sock.settimeout(Constants.SOCKET_TIMEOUT.value)
        return lines

    def is_connected(self) -> bool:
        """Vérifie si la connexion est active."""
        return self._connected and self._sock is not None

    def get_map_info(self) -> tuple[int, int, int]:
        """Retourne les informations de la map (width, height, nb_clients)."""
        if not self._connected:
            raise ConnectionError("Not connected")
        if None in (self._map_width, self._map_height, self._nb_clients):
            raise ValueError("Map info not available (handshake not completed)")
        return self._map_width, self._map_height, self._nb_clients

    def close(self) -> None:
        """Ferme proprement la connexion."""
        if self._sock:
            self._sock.close()
            logger.info("Connection closed")
            self._sock = None
            self._connected = False
