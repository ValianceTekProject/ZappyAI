##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination
##

import time
from typing import Dict, List, Any, Optional
from protocol.commands import CommandManager
from utils.logger import logger
from utils.game_state import GameState
from teams.message import Message, MessageType
from teams.message_checker import MessageBus

class TeamMember:
    def __init__(self, member_id: str):
        """
        Initialise un membre d’équipe avec un identifiant, niveau, position, inventaire et statut.
        """
        self.id = member_id
        self.level = 1
        self.position = (0, 0)
        self.inventory = {}
        self.last_seen = time.time()
        self.status = "active"  # active, busy, dead

    def update_from_status(self, data: Dict[str, Any]):
        """
        Met à jour les informations du membre (niveau, position, inventaire) à partir d’un dictionnaire de statut.
        """
        self.level = data.get("level", self.level)
        self.position = data.get("position", self.position)
        self.inventory = data.get("inventory", self.inventory)
        self.last_seen = time.time()


class CoordinationManager:
    def __init__(self, bus: MessageBus, cmd_mgr: CommandManager, game_state: GameState):
        """
        Initialise le gestionnaire de coordination :
        - bus : MessageBus pour la souscription et l’envoi de messages
        - cmd_mgr : CommandManager pour émettre des broadcasts
        - game_state : état du jeu local
        """
        self.bus = bus
        self.cmd_mgr = cmd_mgr
        self.state = game_state
        self.helpers_info: Dict[str, Dict[str, Any]] = {}
        self.last_requester: Optional[str] = None
        self.incantation_id = 0

        bus.subscribe(MessageType.INCANTATION_REQUEST,  self._on_inc_req)
        bus.subscribe(MessageType.INCANTATION_RESPONSE, self._on_inc_resp)
        bus.subscribe(MessageType.HELP_REQUEST,          self._on_help_req)

    def _on_inc_req(self, sender_id: str, data: Dict[str, Any], direction: int):
        """
        Traite un message d’INCANTATION_REQUEST :
        - stocke l’initiateur
        - évalue si l’agent peut aider (même niveau, pas occupé, assez de nourriture)
        - envoie un INCANTATION_RESPONSE approprié ("here", "coming" ou "busy") avec un ETA si pertinent
        """
        self.last_requester = sender_id
        if self.state.level != data["level"] or self._am_busy():
            resp, eta = "busy", None
        else:
            needed_food = self.state.estimate_food_needed_for_incant()
            have = self.state.get_food_count()
            if have < needed_food:
                resp, eta = "busy", None
            else:
                if direction == 0:
                    resp, eta = "here", 0
                else:
                    # Estimation grosso modo du temps pour rejoindre (distance max possible)
                    max_dist = (self.state.dimension_map[0] // 2 + self.state.dimension_map[1] // 2)
                    eta = max_dist * 7
                    resp, eta = "coming", eta
        token = Message.create_incantation_response(
            sender_id=self.state.team_id,
            request_sender=sender_id,
            response=resp,
            eta=eta
        )
        self.cmd_mgr.broadcast(token)

    def _on_inc_resp(self, sender_id: str, data: Dict[str, Any], direction: int):
        """
        Traite un message d’INCANTATION_RESPONSE :
        - mémorise le statut et l’ETA du helper
        """
        resp = data.get('response')
        eta = data.get('eta')
        self.helpers_info[sender_id] = {
            'status': resp,
            'eta': eta,
            'timestamp': time.time()
        }

    def _on_help_req(self, sender_id: str, data: Dict[str, Any], direction: int):
        """
        Traite un HELP_REQUEST (utile si vous implémentez ce mécanisme).
        """
        logger.info(f"HELP REQUEST from {sender_id}")

    def request_incant_help(self):
        """
        Broadcast d’une demande d’aide à l’incantation (en tant qu’initiateur).
        """
        self.helpers_info.clear()
        msg = Message.create_incantation_request(
            sender_id=self.state.team_id,
            level=self.state.level,
            required_players=self.state.get_required_player_count()
        )
        self.cmd_mgr.broadcast(msg)

    def send_incant_request(self):
        """
        Envoie un broadcast INCANTATION_REQUEST (initiateur).
        """
        self.helpers_info.clear()
        token = Message.create_incantation_request(
            sender_id=self.state.team_id,
            level=self.state.level,
            required_players=self.state.get_required_player_count()
        )
        self.cmd_mgr.broadcast(token)

    def send_incant_response(self, to_id: str, response: str, eta: Any):
        """
        Envoie un INCANTATION_RESPONSE ciblé (helper).
        """
        token = Message.create_incantation_response(
            sender_id=self.state.team_id,
            request_sender=to_id,
            response=response,
            eta=eta
        )
        self.cmd_mgr.broadcast(token)

    def get_helpers(self) -> List[str]:
        """
        Retourne la liste de tous les helpers connus (statuts divers) récents.
        """
        now = time.time()
        # Nettoyage des anciennes entrées (>10s)
        stale = [hid for hid, info in self.helpers_info.items() if now - info['timestamp'] > 10.0]
        for hid in stale:
            del self.helpers_info[hid]
        return list(self.helpers_info.keys())

    def get_helpers_here(self) -> List[str]:
        """
        Retourne la liste des helpers ayant répondu 'here' dans un délai récent.
        """
        now = time.time()
        stale = [hid for hid, info in self.helpers_info.items() if now - info['timestamp'] > 10.0]
        for hid in stale:
            del self.helpers_info[hid]
        return [hid for hid, info in self.helpers_info.items() if info['status'] == 'here']

    def _am_busy(self) -> bool:
        """
        Indique si l’agent est occupé :
        - en préparation d’incantation (state.needs_repro True)
        - ou en pleine exécution d’une commande bloquante (state.command_already_send True)
        """
        if getattr(self.state, 'command_already_send', False):
            return True
        if getattr(self.state, 'needs_repro', False):
            return True
        return False

    def clear_helpers(self):
        """
        Réinitialise les informations sur les helpers.
        """
        self.helpers_info.clear()
