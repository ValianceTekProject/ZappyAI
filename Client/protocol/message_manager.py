## EPITECH PROJECT, 2025
## Zappy
## File description:
## protocol.message_manager (amélioré)

import time
from typing import List, Any, Optional, Tuple
from utils.logger import logger
from teams.message import Message, MessageType
from protocol.parser import Parser

class MessageManager:
    """
    Gère l'envoi et la réception des commandes et des broadcasts.

    - Remplace l'ancien usage direct de Parser et MessageBus à
      l'aide de la nouvelle classe centralisée Message
    """
    def __init__(self, cmd_mgr, bus):
        self.cmd_mgr = cmd_mgr
        self.bus = bus
        self.is_dead = False

    def process_responses(self, raw_responses: List[str]) -> Optional[List[str]]:
        """
        Parcourt la liste des réponses brutes du serveur :
        - Si mort, marque is_dead
        - Si broadcast, décapsule avec Message.decode_msg(), vérifie expiration,
          puis publie sur le bus
        - Sinon, conserve la réponse pour CommandManager
        """
        command_responses = []
        for response in raw_responses:
            response = response.strip()
            if Parser.is_dead_response(response):
                self.is_dead = True
                return
            if Parser.is_broadcast(response):
                dir_, token = Parser.parse_broadcast_response(response).values()
                self.bus.publish_raw(dir_, token)
            else:
                command_responses.append(response)
        return self.cmd_mgr.process_responses(command_responses)

    def broadcast_message(self,
                          msg_type: MessageType,
                          sender_id: str,
                          team_id: str,
                          **kwargs: Any) -> None:
        """
        Méthode utilitaire pour envoyer un broadcast via Message
        Exemples:
            broadcast_message(
                MessageType.INCANTATION_REQUEST,
                sender_id=self.state.team_id,
                team_id=self.state.team_id,
                level=self.state.level,
                required_players=needed
            )
        """
        token = Message.encode_msg(msg_type, sender_id, {
            'team_id': team_id,
            **kwargs,
            'timestamp': time.time()
        })
        self.cmd_mgr.broadcast(token)
