##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## commands
##

import time
from typing import Optional, Any, Dict, List
from dataclasses import dataclass
from utils.logger import logger
from config import Constants, CommandType, CommandStatus
from utils.timing import TimingManager
from protocol.parser import Parser

@dataclass
class Command:
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
    def __init__(self, connection, timing_manager: TimingManager):
        self.conn = connection
        self.timing = timing_manager
        self.pending_commands: Dict[int, Command] = {}
        self.command_history = []
        self.command_id = 0
        self.response_queue = []

    def forward(self) -> Optional[Command]:
        """Commande avancer."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.FORWARD)
        return self.execute_command(cmd)

    def right(self) -> Optional[Command]:
        """Commande tourner à droite."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.RIGHT)
        return self.execute_command(cmd)

    def left(self) -> Optional[Command]:
        """Commande tourner à gauche."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.LEFT)
        return self.execute_command(cmd)

    def look(self) -> Optional[Command]:
        """Commande regarder."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.LOOK, priority=2)
        return self.execute_command(cmd)

    def inventory(self) -> Optional[Command]:
        """Commande inventaire."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.INVENTORY, priority=2)
        return self.execute_command(cmd)

    def take(self, obj: str) -> Optional[Command]:
        """Commande prendre objet."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.TAKE, [obj])
        return self.execute_command(cmd)

    def set(self, obj: str) -> Optional[Command]:
        """Commande poser objet."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.SET, [obj])
        return self.execute_command(cmd)

    def broadcast(self, msg: str) -> Optional[Command]:
        """Commande diffuser message."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.BROADCAST, [msg])
        return self.execute_command(cmd)

    def connect_nbr(self) -> Optional[Command]:
        """Commande nombre de connexions."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.CONNECT_NBR)
        return self.execute_command(cmd)

    def fork(self) -> Optional[Command]:
        """Commande fork."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.FORK, priority=3)
        return self.execute_command(cmd)

    def eject(self) -> Optional[Command]:
        """Commande éjecter."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.EJECT)
        return self.execute_command(cmd)

    def incantation(self) -> Optional[Command]:
        """Commande incantation."""
        if not self.timing.can_execute_action():
            return None
        cmd = Command(CommandType.INCANTATION, priority=4)
        return self.execute_command(cmd)

    def execute_command(self, cmd: Command) -> Optional[Command]:
        """Exécute une commande via la connexion."""
        if not self.conn.is_connected():
            logger.error("Cannot execute command: not connected")
            return None

        cmd.id = self.command_id
        self.command_id += 1

        success = self.conn.send_command(cmd.type, *cmd.args)
        if not success:
            cmd.status = CommandStatus.FAILED
            logger.error(f"Failed to send command: {cmd.type}")
            return cmd

        self.pending_commands[cmd.id] = cmd
        self.timing.register_action(cmd.type)

        logger.debug(f"Executed command {cmd.id}: {cmd.type}")
        return cmd

    def process_responses(self, responses: List[str]) -> List[Command]:
        """Traite les réponses du serveur et les associe aux commandes."""
        completed_commands = []

        for response in responses:
            if self.pending_commands:
                oldest_id = min(self.pending_commands.keys())
                cmd = self.pending_commands.pop(oldest_id)

                cmd.response = response
                if Parser.is_error_response(response):
                    cmd.status = CommandStatus.FAILED
                elif Parser.is_success_response(response) or self.is_valid_response(cmd.type, response):
                    cmd.status = CommandStatus.SUCCESS
                else:
                    cmd.status = CommandStatus.SUCCESS

                self.command_history.append(cmd)
                completed_commands.append(cmd)
                logger.debug(f"Command {cmd.id} completed with response: {response}")
            else:
                logger.warning(f"Unassociated response: {response}")

        current_time = time.time()
        timeout_ids = []
        for cmd_id, cmd in self.pending_commands.items():
            if current_time - cmd.timestamp > Constants.RESPONSE_TIMEOUT.value:
                cmd.status = CommandStatus.TIMEOUT
                timeout_ids.append(cmd_id)
                self.command_history.append(cmd)
                completed_commands.append(cmd)
                logger.warning(f"Command {cmd_id} timed out")

        for cmd_id in timeout_ids:
            del self.pending_commands[cmd_id]

        return completed_commands

    def is_valid_response(self, cmd_type: CommandType, response: str) -> bool:
        """Vérifie si la réponse est valide pour le type de commande."""
        if cmd_type == CommandType.LOOK:
            return response.startswith('[') and response.endswith(']')
        elif cmd_type == CommandType.INVENTORY:
            return response.startswith('[') and response.endswith(']')
        elif cmd_type == CommandType.CONNECT_NBR:
            return response.isdigit()
        return True

    def get_pending_count(self) -> int:
        """Retourne le nombre de commandes en attente."""
        return len(self.pending_commands)

    def has_pending_commands(self) -> bool:
        """Vérifie s'il y a des commandes en attente."""
        return len(self.pending_commands) > 0

    def get_last_completed_command(self, cmd_type: CommandType) -> Optional[Command]:
        """Retourne la dernière commande complétée d'un type donné."""
        for cmd in reversed(self.command_history):
            if cmd.type == cmd_type and cmd.status == CommandStatus.SUCCESS:
                return cmd
        return None
