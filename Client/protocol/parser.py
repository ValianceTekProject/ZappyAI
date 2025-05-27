##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## parser
##

import re
from enum import Enum
from typing import Dict, List, Union, Optional
from utils.logger import logger

class ResponseType(Enum):
    OK = 'ok'
    KO = 'ko'
    DEAD = 'dead'
    MESSAGE = 'message'
    CURRENT_LEVEL = 'current level:'
    EJECT = 'eject:'
    BROADCAST = 'message'

class Parser:
    @staticmethod
    def parse_look_response(response: str) -> List[List[str]]:
        """Parse: [ player food, linemate player, food ]"""
        try:
            response = response.strip()
            if not (response.startswith('[') and response.endswith(']')):
                raise ValueError(f"Format invalide pour Look: {response}")

            content = response[1:-1].strip()
            if not content:
                return [[]]

            tiles = []
            for tile_content in content.split(','):
                tile_content = tile_content.strip()
                if tile_content:
                    items = tile_content.split()
                    tiles.append(items)
                else:
                    tiles.append([])

            return tiles
        except Exception as e:
            print(f"Erreur parsing Look: {e}")
            return [[]]

    @staticmethod
    def parse_inventory_response(response: str) -> Dict[str, int]:
        """Parse: [ food 3, linemate 2, sibur 1 ]"""
        try:
            inventory = {}
            response = response.strip()
            if not (response.startswith('[') and response.endswith(']')):
                raise ValueError(f"Format invalide pour Inventory: {response}")

            content = response[1:-1].strip()
            if not content:
                return inventory

            for item in content.split(','):
                item = item.strip()
                if item:
                    parts = item.split()
                    if len(parts) == 2:
                        resource, quantity = parts
                        inventory[resource] = int(quantity)

            return inventory
        except Exception as e:
            print(f"Erreur parsing Inventory: {e}")
            return {}

    @staticmethod
    def parse_broadcast_response(response: str) -> Optional[Dict[str, Union[int, str]]]:
        """Parse: message K, message"""
        try:
            if response.startswith("message "):
                parts = response[8:].split(', ', 1)
                if len(parts) == 2:
                    direction = int(parts[0])
                    message = parts[1]
                    return {"direction": direction, "message": message}
            return None
        except Exception as e:
            print(f"Erreur parsing Broadcast: {e}")
            return None

    @staticmethod
    def is_error_response(response: str) -> bool:
        """Vérifie si la réponse est une erreur."""
        error_responses = ["ko", "dead", "eject"]
        return response.strip().lower() in error_responses

    @staticmethod
    def is_success_response(response: str) -> bool:
        """Vérifie si la réponse indique un succès."""
        return response.strip().lower() == "ok"
