##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## message
##

import json
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
    def encode_msg(msg_type: MessageType, sender_id: str, data: Dict[str, Any]) -> str:
        """Sérialise un message pour broadcast."""
        pass

    @staticmethod
    def decode_msg(raw: str) -> Optional[Tuple[MessageType, str, Dict[str, Any]]]:
        """Parse un message broadcast reçu."""
        pass

    @staticmethod
    def create_status_message(sender_id: str, level: int, position: Tuple[int, int], 
                            inventory: Dict[str, int]) -> str:
        """Crée un message de statut."""
        pass

    @staticmethod
    def create_incantation_request(sender_id: str, level: int, position: Tuple[int, int],
                                 required_players: int) -> str:
        """Crée une requête d'incantation."""
        pass

    @staticmethod
    def create_resource_share(sender_id: str, resource_type: str, 
                            quantity: int, position: Tuple[int, int]) -> str:
        """Crée un message de partage de ressource."""
        pass

    @staticmethod
    def create_help_request(sender_id: str, help_type: str, 
                          position: Tuple[int, int], urgency: int) -> str:
        """Crée une demande d'aide."""
        pass

    @staticmethod
    def validate_message(msg_data: Dict[str, Any]) -> bool:
        """Valide la structure d'un message."""
        pass

    @staticmethod
    def get_message_age(timestamp: float) -> float:
        """Retourne l'âge d'un message en secondes."""
        pass