##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## connection
##

import socket
import time
import select
from typing import List, Optional
from utils.logger import logger
from config import Constants, CommandType
from protocol.parser import Parser

class Connection:
    def __init__(self, host: str, port: int):
        """Initialise la connexion TCP avec le serveur."""
        self._host = host
        self._port = port
        self._sock = None
        self._connected = False

        self._send_buffer = []
        self._receive_buffer = ""

        self._map_width = None
        self._map_height = None
        self._nb_clients = None

        self._parser = Parser()

        self._connect()

    def _connect(self) -> bool:
        """Tente d'établir la connexion avec le serveur."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(Constants.SOCKET_TIMEOUT.value)
        self._sock.connect((self._host, self._port))
        self._connected = True
        logger.info(f"Connected to server {self._host}:{self._port}")
        return True

    def _reconnect(self) -> bool:
        """Effectue des tentatives de reconnexion."""
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
        """Effectue le handshake initial : WELCOME → team → slot → map size."""
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
        while client_num_msg.strip() == "":
            time.sleep(0.01)
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

    def send_raw(self, msg: str) -> bool:
        """Envoie un message brut (terminé par '\n')."""
        if not self._connected or not self._sock:
            logger.error("Cannot send: not connected")
            return False

        if not msg.endswith('\n'):
            msg += '\n'
        self._sock.send(msg.encode('utf-8'))
        return True

    def send_command(self, cmd_type: CommandType, *args) -> bool:
        """Construit et envoie une commande complète au serveur."""
        if not self._connected:
            logger.error("Cannot send command: not connected")
            return False

        cmd_parts = [cmd_type.value]
        cmd_parts.extend(str(arg) for arg in args)
        command = ' '.join(cmd_parts)
        return self.send_raw(command)

    def recv_line(self) -> str:
        """Lit une ligne terminée par '\n' et log les étapes pour debug."""
        if not self._connected or not self._sock:
            raise ConnectionError("Not connected")

        logger.debug("[recv_line] Start waiting for '\\n' in buffer...")
        logger.debug(f"[recv_line] Initial buffer: {repr(self._receive_buffer)}")

        while '\n' not in self._receive_buffer:
            try:
                data = self._sock.recv(1024)
                if not data:
                    logger.warning("[recv_line] Socket closed by server")
                    raise ConnectionError("Connection closed by server")
                logger.debug(f"[recv_line] Received raw: {repr(data)}")
                decoded = data.decode('utf-8')
                logger.debug(f"[recv_line] Decoded string: {repr(decoded)}")
                self._receive_buffer += decoded
                logger.debug(f"[recv_line] Updated buffer: {repr(self._receive_buffer)}")
            except socket.timeout:
                logger.warning("[recv_line] Timeout while waiting for data")
                time.sleep(0.01)
            except socket.error as e:
                logger.error(f"[recv_line] Socket error: {e}")
                raise ConnectionError(f"Socket error: {e}")

        line, self._receive_buffer = self._receive_buffer.split('\n', 1)
        logger.debug(f"[recv_line] Final line: {repr(line.strip())}")
        logger.debug(f"[recv_line] Remaining buffer: {repr(self._receive_buffer)}")

        return line.strip()

    def receive(self) -> List[str]:
        """Récupère toutes les lignes disponibles (mode non-bloquant, sans exceptions)."""
        if not self._connected or not self._sock:
            return []

        lines = []

        readable, _, _ = select.select([self._sock], [], [], 0.01)
        if not readable:
            return lines

        data = self._sock.recv(1024)
        if not data:
            self._connected = False
            return lines

        self._receive_buffer += data.decode('utf-8')

        while '\n' in self._receive_buffer:
            line, self._receive_buffer = self._receive_buffer.split('\n', 1)
            if line.strip():
                lines.append(line.strip())

        return lines

    def is_connected(self) -> bool:
        """Retourne l'état de la connexion."""
        return self._connected and self._sock is not None

    def get_serv_info(self) -> tuple[int, int, int]:
        """Retourne (largeur, hauteur, slots disponibles)."""
        if not self._connected:
            raise ConnectionError("Not connected")
        if None in (self._map_width, self._map_height, self._nb_clients):
            raise ValueError("Map info not available (handshake not completed)")
        return self._map_width, self._map_height, self._nb_clients

    def get_map_size(self) -> tuple[int, int]:
        """Retourne la taille de la carte."""
        return self._map_width, self._map_height

    def receive_raw(self) -> str:
        """Lecture brute sans bloquer. Utilisé pour du debug ou pré-traitement."""
        if not self._connected or not self._sock:
            return ""

        readable, _, _ = select.select([self._sock], [], [], 0.01)

        if readable:
            data = self._sock.recv(1024)
            if not data:
                self._connected = False
                return ""
            self._receive_buffer += data.decode('utf-8')

        return self._receive_buffer

    def split_responses(self, raw_data: str) -> List[str]:
        """Découpe les messages complets depuis le buffer."""
        responses = []
        while '\n' in self._receive_buffer:
            line, self._receive_buffer = self._receive_buffer.split('\n', 1)
            if line.strip():
                responses.append(line.strip())
        return responses

    def get_socket(self):
        """Expose le socket (utile pour un `select` externe)."""
        return self._sock

    def close(self) -> None:
        """Ferme proprement la connexion TCP."""
        if self._sock:
            self._sock.close()
            logger.info("Connection closed")
            self._sock = None
            self._connected = False
