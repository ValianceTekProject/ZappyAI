##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## message
##

import json
import base64
import time
from typing import Dict, List, Any, Tuple, Optional
from enum import Enum
from utils.logger import logger

class MessageType(Enum):
    STATUS = "status"
    INCANTATION_REQUEST = "incant_req"
    INCANTATION_RESPONSE = "incant_resp"
    RESOURCE_SHARE = "resource_share"
    HELP_REQUEST = "help_req"
    POSITION_UPDATE = "pos_update"
    DEATH_NOTICE = "death"

class Message:
    @staticmethod
    def encode_msg(msg_type: MessageType, sender_level: int, payload: Dict) -> str:
        """
        Sérialise en JSON minimal, encode en Base64 (pas d'espaces)
        et logge le token.
        """
        message = {
            "type": msg_type.value,
            "sender_level": sender_level,
            "payload": payload
        }
        raw = json.dumps(message, separators=(',', ':'))
        token = base64.b64encode(raw.encode('utf-8')).decode('ascii')
        return token

    @staticmethod
    def decode_msg(token: str) -> Optional[Tuple[MessageType,int,Dict]]:
        """
        Décode le token Base64, parse JSON, convertit le type,
        et logge le résultat.
        """
        raw = base64.b64decode(token).decode('utf-8')
        msg = json.loads(raw)
        msg_type = MessageType(msg["type"])
        sender_level = msg["sender_level"]
        payload = msg["payload"]
        return msg_type, sender_level, payload

    @staticmethod
    def create_status_message(sender_id: str, level: int, position: Tuple[int, int], 
                            inventory: Dict[str, int]) -> str:
        """Crée un message de statut."""
        data = {
            "level": level,
            "position": position,
            "inventory": inventory,
            "food": inventory.get("food", 0)
        }
        return Message.encode_msg(MessageType.STATUS, sender_id, data)

    @staticmethod
    def create_incantation_request(sender_id: str, level: int, required_players: int) -> str:
        """Crée une requête d'incantation."""
        data = {
            "sender_id":       sender_id,
            "team_id":         sender_id,
            "level":           level,
            "required_players": required_players,
            "urgency":         "high",
            "timestamp":       time.time()
        }
        return Message.encode_msg(MessageType.INCANTATION_REQUEST, sender_id, data)

    @staticmethod
    def create_incantation_response(sender_id: str, request_sender: str, 
                                  response: str, eta: Optional[int] = None) -> str:
        """Crée une réponse à une requête d'incantation."""
        data = {
            "sender_id":       sender_id,
            "team_id":         sender_id,
            "request_sender": request_sender,
            "response": response,  # "coming", "busy", "here"
            "eta": eta
        }
        return Message.encode_msg(MessageType.INCANTATION_RESPONSE, sender_id, data)

    @staticmethod
    def create_resource_share(sender_id: str, resource_type: str, 
                            quantity: int, position: Tuple[int, int]) -> str:
        """Crée un message de partage de ressource."""
        data = {
            "resource": resource_type,
            "quantity": quantity,
            "position": position,
            "action": "drop"  # "drop" ou "available"
        }
        return Message.encode_msg(MessageType.RESOURCE_SHARE, sender_id, data)

    @staticmethod
    def create_help_request(sender_id: str, help_type: str, 
                          position: Tuple[int, int], urgency: int) -> str:
        """Crée une demande d'aide."""
        data = {
            "help_type": help_type,  # "food", "transport", "protection"
            "position": position,
            "urgency": min(max(urgency, 1), 10)  # Clampé entre 1 et 10
        }
        return Message.encode_msg(MessageType.HELP_REQUEST, sender_id, data)

    @staticmethod
    def create_position_update(sender_id: str, old_pos: Tuple[int, int], 
                             new_pos: Tuple[int, int]) -> str:
        """Crée un message de mise à jour de position."""
        data = {
            "old_position": old_pos,
            "new_position": new_pos
        }
        return Message.encode_msg(MessageType.POSITION_UPDATE, sender_id, data)

    @staticmethod
    def create_death_notice(sender_id: str, position: Tuple[int, int], 
                          cause: str = "starvation") -> str:
        """Crée un avis de décès."""
        data = {
            "position": position,
            "cause": cause,
            "final_message": "goodbye"
        }
        return Message.encode_msg(MessageType.DEATH_NOTICE, sender_id, data)

    @staticmethod
    def validate_message(msg_data: Dict[str, Any]) -> bool:
        """Valide la structure d'un message."""
        try:
            required = ["type", "sender", "timestamp", "data"]
            if not all(key in msg_data for key in required):
                return False
            
            # Vérifie que le timestamp est récent (moins de 5 minutes)
            age = time.time() - msg_data["timestamp"]
            if age > 300:  # 5 minutes
                return False
            
            # Vérifie que le sender n'est pas vide
            if not msg_data["sender"] or not isinstance(msg_data["sender"], str):
                return False
            
            return True
        except Exception:
            return False

    @staticmethod
    def get_message_age(timestamp: float) -> float:
        """Retourne l'âge d'un message en secondes."""
        return time.time() - timestamp

    @staticmethod
    def is_message_expired(timestamp: float, max_age: float = 60.0) -> bool:
        """Vérifie si un message a expiré."""
        return Message.get_message_age(timestamp) > max_age
