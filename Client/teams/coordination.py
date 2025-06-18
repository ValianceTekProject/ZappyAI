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

        self.last_requester = None
        self.incantation_id = 0

        # Souscription aux messages qui nous intéressent
        bus.subscribe(MessageType.INCANTATION_REQUEST,  self._on_inc_req)
        bus.subscribe(MessageType.INCANTATION_RESPONSE, self._on_inc_resp)
        bus.subscribe(MessageType.HELP_REQUEST,          self._on_help_req)

    def _on_inc_req(self, sender_id, data, direction):
        self.last_requester = sender_id
        if self.state.level != data["level"] or self._am_busy():
            resp, eta = "busy", None
        else:
            needed = self.state.estimate_food_needed_for_incant()
            have = self.state.get_food_count()
            if have < needed:
                resp, eta = "busy", None
            else:
                if direction == 0:
                    resp, eta = "here", 0
                else:
                    # approximativement, on renvoie « coming »; on peut donner un ETA grosso modo
                    # ETA approximatif en time units : distance max *7 => en ticks ou en time units ?
                    # Pour que l’initiateur sache si le helper peut arriver bientôt, on peut renvoyer:
                    eta = ( (self.state.dimension_map[0]//2 + self.state.dimension_map[1]//2) * 7 )
                    resp, eta = "coming", eta
        token = Message.create_incantation_response(
            sender_id=self.state.team_id,
            request_sender=sender_id,
            response=resp,
            eta=eta
        )
        self.cmd_mgr.broadcast(token)

    def _on_inc_resp(self, sender_id, data, direction):
        resp = data.get('response')
        if resp == 'here':
            self.helpers.add(sender_id)

    def _on_help_req(self, sender_id, data, direction):
        logger.info(f"HELP REQUEST from {sender_id}")

    def request_incant_help(self):
        self.helpers.clear()
        msg = Message.create_incantation_request(
            sender_id=self.state.team_id,
            level=self.state.level,
            required_players=self.state.get_required_player_count()
        )
        self.cmd_mgr.broadcast(msg)

    def send_incant_request(self):
        # initiateur broadcast
        self.helpers.clear()
        token = Message.create_incantation_request(
            sender_id=self.state.team_id,
            level=self.state.level,
            required_players=self.state.get_required_player_count()
        )
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
