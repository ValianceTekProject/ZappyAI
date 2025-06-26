##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## message_checker
##

import time
from typing import Callable, Dict, List
from teams.message import MessageType, Message
from utils.logger import logger

class MessageBus:
    def __init__(self, my_level: int, team_id: str, ttl: float = 60.0):
        self.subscribers: Dict[MessageType, List[Callable]] = {}
        self.my_level = my_level
        self.team_id = team_id
        self.ttl = ttl

    def subscribe(self, msg_type: MessageType, handler: Callable):
        """Register handler, replacing any existing handler for this type."""
        if msg_type not in self.subscribers:
            self.subscribers[msg_type] = []
        self.subscribers[msg_type].append(handler)

    def publish_raw(self, direction: int, token: str):
        """
        Reçoit le token Base64, décode, filtre niveau/team/TTL, puis dispatch.
        """
        decoded = Message.decode_msg(token)
        if not decoded:
            return
        msg_type, sender_id, payload = decoded

        if payload.get("team_id") != self.team_id:
            return

        ts = payload.get("timestamp", payload.get("time", None))
        if ts and (time.time() - ts) > self.ttl:
            return

        for handler in self.subscribers.get(msg_type, []):
            handler(sender_id=sender_id,
                    data=payload,
                    direction=direction)
