##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## parser utilities for server responses
##

from typing import Dict, List, Union, Optional
from config import ResponseType
from utils.logger import logger

class Parser:
    @staticmethod
    def parse_look_response(response: str) -> List[List[str]]:
        """
        Parse la réponse à la commande 'Look'.
        Format attendu : "[ player food, linemate player, food ]"
        Retourne une liste de tuiles, chaque tuile étant une liste d'objets.
        """
        try:
            response = response.strip()
            if not (response.startswith('[') and response.endswith(']')):
                raise ValueError(f"Format invalide pour Look: {response}")

            content = response[1:-1].strip()
            if not content:
                return [[]]

            tiles: List[List[str]] = []
            for tile_content in content.split(','):
                items = tile_content.strip().split() if tile_content.strip() else []
                tiles.append(items)

            return tiles

        except Exception as e:
            logger.error(f"Erreur lors du parsing Look: {e}")
            return [[]]

    @staticmethod
    def parse_inventory_response(response: str) -> Dict[str, int]:
        """
        Parse la réponse à la commande 'Inventory'.
        Format attendu : "[ food 3, linemate 2, sibur 1 ]"
        Retourne un dictionnaire {ressource: quantité}.
        """
        try:
            inventory: Dict[str, int] = {}
            response = response.strip()

            if not (response.startswith('[') and response.endswith(']')):
                raise ValueError(f"Format invalide pour Inventory: {response}")

            content = response[1:-1].strip()
            if not content:
                return inventory

            for item in content.split(','):
                parts = item.strip().split()
                if len(parts) == 2:
                    resource, quantity = parts
                    inventory[resource] = int(quantity)

            return inventory

        except Exception as e:
            logger.error(f"Erreur lors du parsing Inventory: {e}")
            return {}

    @staticmethod
    def parse_broadcast_response(response: str) -> Optional[Dict[str, Union[int, str]]]:
        """
        Parse la réponse à un message broadcast.
        Format attendu : "message K, contenu"
        Retourne un dictionnaire avec la direction et le message.
        """
        try:
            if response.startswith("message "):
                parts = response[8:].split(', ', 1)
                if len(parts) == 2:
                    direction = int(parts[0])
                    message = parts[1]
                    return {"direction": direction, "message": message}
            return None

        except Exception as e:
            logger.error(f"Erreur lors du parsing Broadcast: {e}")
            return None

    @staticmethod
    def is_error_response(response: str) -> bool:
        """
        Vérifie si la réponse est une erreur : 'ko' ou 'eject ...'
        """
        s = response.strip().lower()
        return s == ResponseType.KO.value or s.startswith(ResponseType.EJECT.value)

    @staticmethod
    def is_success_response(response: str) -> bool:
        """
        Vérifie si la réponse est 'ok'.
        """
        return response.strip().lower() == ResponseType.OK.value

    @staticmethod
    def is_dead_response(response: str) -> bool:
        """
        Vérifie si la réponse est 'dead'.
        """
        return response.strip().lower() == ResponseType.DEAD.value

    @staticmethod
    def is_elevation_underway(response: str) -> bool:
        """
        Vérifie si la réponse est 'Elevation underway'.
        """
        return response.strip().lower() == ResponseType.ELEVATION_UNDERWAY.value

    @staticmethod
    def is_current_level_response(response: str) -> bool:
        """
        Vérifie si la réponse commence par 'Current level:'.
        """
        return response.strip().lower().startswith(ResponseType.CURRENT_LEVEL.value)

    @staticmethod
    def is_eject_response(response: str) -> bool:
        """
        Vérifie si la réponse est 'eject: X'.
        """
        return response.strip().lower().startswith(ResponseType.EJECT.value)

    @staticmethod
    def is_broadcast(response: str) -> bool:
        """
        Vérifie si la réponse est un message broadcast.
        """
        return response.strip().lower().startswith(ResponseType.BROADCAST.value)

    @staticmethod
    def parse_current_level(response: str) -> int:
        """
        Extrait l'entier X de la réponse 'Current level: X'.
        """
        try:
            return int(response.split(':', 1)[1].strip())
        except:
            logger.error(f"Impossible de parser le niveau dans '{response}'")
            return 0
