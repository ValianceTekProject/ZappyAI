##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## commands (version refactorisée)
##

import time
from typing import Optional, List
from dataclasses import dataclass
from utils.logger import logger
from config import Constants, CommandType, CommandStatus
from utils.timing import TimingManager
from protocol.parser import Parser
from protocol.connection import Connection

@dataclass
class Command:
    """
    Représente une commande envoyée au serveur.
    """
    type: CommandType
    args: list
    priority: int
    status: CommandStatus
    timestamp: float
    response: Optional[str]
    id: int

    def __init__(self, cmd_type: CommandType, args: list = None, priority: int = 1):
        self.type = cmd_type
        self.args = args or []
        self.priority = priority
        self.status = CommandStatus.PENDING
        self.timestamp = time.time()
        self.response = None
        self.id = 0

class CommandManager:
    """
    Gère l'envoi des commandes, la réception des réponses et leur traitement.
    """
    def __init__(self, connection: Connection, timing_manager: TimingManager, state):
        self.conn = connection
        self.timing = timing_manager
        self.state = state
        self.pending_responses: List[Command] = []
        self.command_history: List[Command] = []
        self.command_id = 0

    def _can_send(self) -> bool:
        """
        Vérifie si une commande peut être envoyée :
        - La connexion est active
        - Moins de 10 commandes sont en attente
        """
        return self.conn.is_connected() and len(self.pending_responses) < 10

    def _build_command(self, cmd_type: CommandType, args=None, priority=1) -> Optional[Command]:
        """
        Construit une commande si les conditions d'envoi sont remplies.
        """
        if not self.timing.can_execute_action() or not self._can_send():
            return None
        cmd = Command(cmd_type, args, priority)
        cmd.id = self.command_id
        self.command_id += 1
        return cmd

    def _send(self, cmd: Command) -> Optional[Command]:
        """
        Envoie une commande via la connexion, l'ajoute aux réponses en attente.
        """
        success = self.conn.send_command(cmd.type, *cmd.args)
        if not success:
            cmd.status = CommandStatus.FAILED
            logger.error(f"Échec de l’envoi de la commande: {cmd.type}")
            return cmd
        self.pending_responses.append(cmd)
        self.state.command_already_send = True
        self.timing.register_action(cmd.type)
        logger.debug(f"Commande envoyée {cmd.id}: {cmd.type}")
        return cmd

    def forward(self):
        cmd = self._build_command(CommandType.FORWARD)
        if cmd is not None:
            return self._send(cmd)

    def right(self):
        cmd = self._build_command(CommandType.RIGHT)
        if cmd is not None:
            return self._send(cmd)

    def left(self):
        cmd = self._build_command(CommandType.LEFT)
        if cmd is not None:
            return self._send(cmd)

    def look(self):
        cmd = self._build_command(CommandType.LOOK, priority=2)
        if cmd is not None:
            return self._send(cmd)

    def inventory(self):
        cmd = self._build_command(CommandType.INVENTORY, priority=2)
        if cmd is not None:
            return self._send(cmd)

    def take(self, obj):
        cmd = self._build_command(CommandType.TAKE, [obj])
        if cmd is not None:
            return self._send(cmd)

    def set(self, obj):
        cmd = self._build_command(CommandType.SET, [obj])
        if cmd is not None:
            return self._send(cmd)

    def broadcast(self, msg):
        cmd = self._build_command(CommandType.BROADCAST, [msg])
        if cmd is not None:
            return self._send(cmd)

    def connect_nbr(self):
        cmd = self._build_command(CommandType.CONNECT_NBR)
        if cmd is not None:
            return self._send(cmd)

    def fork(self):
        cmd = self._build_command(CommandType.FORK, priority=3)
        if cmd is not None:
            return self._send(cmd)

    def eject(self):
        cmd = self._build_command(CommandType.EJECT)
        if cmd is not None:
            return self._send(cmd)

    def incantation(self):
        cmd = self._build_command(CommandType.INCANTATION, priority=4)
        if cmd is not None:
            return self._send(cmd)

    def process_responses(self, responses: List[str]) -> List[Command]:
        """
        Traite une liste brute de réponses venant du serveur.
        Retourne la liste des commandes complétées.
        """
        completed = []
        for raw in responses:
            response = raw.strip()

            if self._handle_dead(response, completed):
                continue
            if self._handle_elevation_underway(response):
                continue
            if self._handle_current_level(response, completed):
                continue
            if self._handle_general_response(response, completed):
                continue

            logger.warning(f"Aucune commande en attente ne correspond à: {response!r}")

        self._handle_timeouts(completed)
        return completed

    def _handle_dead(self, response: str, completed: List[Command]) -> bool:
        """
        Gère une réponse 'dead' (mort du joueur).
        """
        if Parser.is_dead_response(response):
            if self.pending_responses:
                cmd = self.pending_responses.pop(0)
                cmd.response = response
                cmd.status = CommandStatus.DEAD
                self.command_history.append(cmd)
                completed.append(cmd)
                logger.debug(f"Commande {cmd.id} DEAD: {response}")
            else:
                logger.warning("Réception de 'dead' sans commande en attente.")
            return True
        return False

    def _handle_elevation_underway(self, response: str) -> bool:
        """
        Ignore la réponse intermédiaire 'Elevation underway'.
        """
        if Parser.is_elevation_underway(response):
            logger.debug(f"Ignorée: incantation intermédiaire: {response}")
            return True
        return False

    def _handle_current_level(self, response: str, completed: List[Command]) -> bool:
        """
        Marque une incantation comme réussie suite à 'Current level: X'.
        """
        if Parser.is_current_level_response(response):
            for idx, cmd in enumerate(self.pending_responses):
                if cmd.type == CommandType.INCANTATION:
                    picked = self.pending_responses.pop(idx)
                    picked.response = response
                    picked.status = CommandStatus.SUCCESS
                    self.command_history.append(picked)
                    completed.append(picked)
                    logger.debug(f"Incantation terminée: {picked.id} -> {response}")
                    return True
            logger.warning(f"'Current level' sans incantation en attente: {response}")
            return True
        return False

    def _handle_general_response(self, response: str, completed: List[Command]) -> bool:
        """
        Gère les réponses normales pour toutes commandes standard.
        """
        for idx, cmd in enumerate(self.pending_responses):
            if cmd.type in {CommandType.LOOK, CommandType.INVENTORY}:
                if response.startswith('[') and response.endswith(']'):
                    return self._finalize_command(idx, response, completed)
                continue

            if Parser.is_error_response(response) or Parser.is_success_response(response) \
               or self.is_valid_response(cmd.type, response):
                return self._finalize_command(idx, response, completed)

        return False

    def _finalize_command(self, idx: int, response: str, completed: List[Command]) -> bool:
        """
        Marque une commande comme réussie ou échouée.
        """
        cmd = self.pending_responses.pop(idx)
        cmd.response = response
        cmd.status = CommandStatus.FAILED if Parser.is_error_response(response) else CommandStatus.SUCCESS
        self.command_history.append(cmd)
        completed.append(cmd)
        logger.debug(f"Commande {cmd.id} terminée: {cmd.status.name} ({response})")
        return True

    def _handle_timeouts(self, completed: List[Command]) -> None:
        """
        Gère les commandes expirées (timeout).
        """
        now = time.time()
        still_pending = []
        for cmd in self.pending_responses:
            if now - cmd.timestamp > Constants.RESPONSE_TIMEOUT.value:
                cmd.status = CommandStatus.TIMEOUT
                self.command_history.append(cmd)
                completed.append(cmd)
                logger.warning(f"Commande {cmd.id} expirée (timeout)")
            else:
                still_pending.append(cmd)
        self.pending_responses = still_pending

    def is_valid_response(self, cmd_type: CommandType, response: str) -> bool:
        """
        Vérifie si une réponse est valide selon le type de commande.
        """
        if cmd_type in {CommandType.LOOK, CommandType.INVENTORY}:
            return response.startswith('[') and response.endswith(']')
        if cmd_type == CommandType.CONNECT_NBR:
            return response.isdigit()
        return True

    def has_pending(self) -> bool:
        """
        Indique s"il reste des commandes en attente.
        """
        return len(self.pending_responses) > 0

    def get_last_success(self, cmd_type: CommandType) -> Optional[Command]:
        """
        Récupère la dernière commande réussie d'un type donné.
        """
        for cmd in reversed(self.command_history):
            if cmd.type == cmd_type and cmd.status == CommandStatus.SUCCESS:
                return cmd
        return None

    def get_pending_count(self) -> int:
        """
        Nombre de commandes en attente de réponse.
        """
        return len(self.pending_responses)
