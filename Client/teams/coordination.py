##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination
##

import time
from typing import Dict, List, Any, Optional, Tuple
from protocol.commands import CommandManager, CommandStatus
from utils.logger import logger
from utils.game_state import GameState
from protocol.parser import Parser
from teams.message import Message, MessageType
from teams.message_checker import MessageBus
from config import CommandType

class TeamMember:
    def __init__(self, member_id: str):
        self.id = member_id
        self.level = 1
        self.position = (0, 0)
        self.inventory = {}
        self.last_seen = time.time()
        self.status = "active"  # active, busy, dead

    def update_from_status(self, data: Dict[str, Any]):
        """Met à jour les infos d'un membre depuis un message status."""
        self.level = data.get("level", self.level)
        self.position = data.get("position", self.position)
        self.inventory = data.get("inventory", self.inventory)
        self.last_seen = time.time()

from teams.message import Message, MessageType

class CoordinationManager:
    def __init__(self, bus: MessageBus, cmd_mgr, game_state):
        self.bus = bus
        self.cmd_mgr = cmd_mgr
        self.state = game_state
        self.helpers = set()

        # Souscription aux messages qui nous intéressent
        bus.subscribe(MessageType.INCANTATION_REQUEST,  self._on_inc_req)
        bus.subscribe(MessageType.INCANTATION_RESPONSE, self._on_inc_resp)
        bus.subscribe(MessageType.HELP_REQUEST,          self._on_help_req)

    def _on_inc_req(self, sender_id, data, direction):
        """
        Réception d'une requête d'incantation.
        Si même niveau et food ok -> coming ou here; sinon busy.
        """
        can_help = (self.state.level == data['level'] and
                    self.state.get_food_count() > 20 and
                    not self._am_busy())
        if not can_help:
            resp_text = 'busy'
            eta = None
        else:
            if direction == 0:
                resp_text = 'here'
                eta = 0
            else:
                resp_text = 'coming'
                eta = max(1, direction) * 7
        logger.info(f"[Coordo] reply to {sender_id}: '{resp_text}' (eta={eta})")
        token = Message.create_incantation_response(
            sender_id=self.state.team_id,
            request_sender=sender_id,
            response=resp_text,
            eta=eta
        )
        self.cmd_mgr.broadcast(token)

    def _on_inc_resp(self, sender_id, data, direction):
        resp = data.get('response')
        if resp == 'here':
            self.helpers.add(sender_id)
        logger.debug(f"[Coordo] Received response '{resp}' from {sender_id}")

    def _on_help_req(self, sender_id, data, direction):
        # Par exemple, on stocke ou on réagit directement
        print(f"Help requested: {data}")

    def request_incant_help(self):
        self.helpers.clear()
        msg = Message.create_incantation_request(
            sender_id=self.state.team_id,
            level=self.state.level,
            required_players=self.state.get_required_player_count()
        )
        logger.debug(f"[Coordo] request help: {msg}")
        self.cmd_mgr.broadcast(msg)

    def send_incant_request(self):
        # initiateur broadcast
        self.helpers.clear()
        token = Message.create_incantation_request(
            sender_id=self.state.team_id,
            level=self.state.level,
            required_players=self.state.get_required_player_count()
        )
        logger.info(f"[Coordo] broadcast incant_req: {token}")
        self.cmd_mgr.broadcast(token)

    def send_incant_response(self, to_id: str, response: str, eta: Any):
        # réponse directe du helper
        token = Message.create_incantation_response(
            sender_id=self.state.team_id,
            request_sender=to_id,
            response=response,
            eta=eta
        )
        self.cmd_mgr.broadcast(token)

    def get_helpers(self):
        return list(self.helpers)

    def _am_busy(self):
        # vrai si déjà en train de préparer une incant, etc.
        return False

    def _estimate_eta(self, direction):
        # logique simplifiée
        return max(1, direction) * 7
