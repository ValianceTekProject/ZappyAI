##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## vision
##

import time
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from config import Constants
from utils.logger import logger
from utils.math import MathUtils
from protocol.parser import Parser

# Représentation des déplacements associés à chaque orientation
DIRECTION_VECTORS = {
    0: (0, -1),  # NORD
    1: (1, 0),   # EST
    2: (0, 1),   # SUD
    3: (-1, 0)   # OUEST
}

class VisionData:
    """Contient les informations visuelles d'une tuile visible par le joueur."""
    def __init__(self, distance: int, angle: int, content: List[str], rel_pos: Tuple[int, int]):
        self.distance = distance
        self.angle = angle
        self.content = content
        self.rel_pos = rel_pos
        self.resources: Dict[str, int] = {}
        self.players: int = 0
        self.timestamp = time.time()
        self.parse_content()

    def parse_content(self) -> None:
        """Remplit `players` et `resources` à partir du contenu brut de la tuile."""
        for item in self.content:
            if item == "player":
                self.players += 1
            else:
                self.resources[item] = self.resources.get(item, 0) + 1

class Vision:
    """Gère la perception visuelle d’un agent, avec logique de parsing et d’analyse de la vue."""
    def __init__(self):
        self.vision_range = Constants.VISION_RANGE.value
        self.last_vision_data: List[VisionData] = []
        self.math = MathUtils()

    @staticmethod
    def parse_look_matrix(text: str) -> List[List[str]]:
        """Parse la réponse brute du serveur à la commande `Look`."""
        return Parser.parse_look_response(text)

    def process_vision(self, look_response: str, agent_pos: Tuple[int, int], agent_orientation: int) -> List[VisionData]:
        """Transforme la réponse du serveur en données structurées de vision."""
        matrix = self.parse_look_matrix(look_response)
        self.clear()

        relative_positions = self.math.compute_relative_positions(self.vision_range, agent_orientation)

        for idx, rel_pos in enumerate(relative_positions):
            content = matrix[idx] if idx < len(matrix) else []
            dist = abs(rel_pos[0]) + abs(rel_pos[1])
            vision_data = VisionData(distance=dist, angle=0, content=content, rel_pos=rel_pos)
            self.last_vision_data.append(vision_data)
        for idx, data in enumerate(self.last_vision_data):
            logger.debug("idx=%d → rel_pos=%s content=%s", idx, data.rel_pos, data.content)


        return self.last_vision_data

    def clear(self):
        """Réinitialise la vision précédente."""
        self.last_vision_data.clear()

    def get_visible_resources(self) -> Dict[str, List[Tuple[int, int]]]:
        """Retourne les positions relatives de toutes les ressources visibles, triées par type."""
        result = defaultdict(list)
        for data in self.last_vision_data:
            for resource, count in data.resources.items():
                result[resource].extend([data.rel_pos] * count)
        return dict(result)

    def get_visible_players(self) -> List[Tuple[int, int]]:
        """Retourne les positions relatives de tous les joueurs visibles."""
        return [data.rel_pos for data in self.last_vision_data for _ in range(data.players)]

    def find_closest_resource(self, resource: str) -> Optional[Tuple[int, int]]:
        """Trouve la position relative de la ressource la plus proche (distance de Manhattan)."""
        candidates = self.get_visible_resources().get(resource, [])
        if not candidates:
            return None
        return min(candidates, key=lambda pos: abs(pos[0]) + abs(pos[1]))

    def detect_threats(self) -> List[Tuple[int, int]]:
        """Retourne les positions des joueurs ennemis visibles."""
        return self.get_visible_players()

    def get_safe_directions(self) -> List[int]:
        """Retourne les directions "sûres" (0=avant, 1=gauche, 2=droite) sans joueur directement visible."""
        threats = self.get_visible_players()
        safe_dirs = []
        dir_mapping = {
            0: (0, -1),  # avant
            1: (-1, 0),  # gauche
            2: (1, 0)    # droite
        }
        for d, vec in dir_mapping.items():
            if vec not in threats:
                safe_dirs.append(d)
        return safe_dirs

    def is_tile_empty(self, relative_pos: Tuple[int, int]) -> bool:
        """Vérifie si une tuile est vide (aucun joueur, aucune ressource)."""
        for data in self.last_vision_data:
            if data.rel_pos == relative_pos:
                return data.players == 0 and not data.resources
        return True

    def count_resources_in_vision(self) -> Dict[str, int]:
        """Compte toutes les ressources visibles par type."""
        count = defaultdict(int)
        for data in self.last_vision_data:
            for res, qty in data.resources.items():
                count[res] += qty
        return dict(count)

    def add_resource_at(self, rel_pos: Tuple[int, int], resource: str):
        """Ajoute artificiellement une ressource à une tuile donnée (ex: pour simulation)."""
        for data in self.last_vision_data:
            if data.rel_pos == rel_pos:
                data.resources[resource] = data.resources.get(resource, 0) + 1
                break

    def remove_resource_at(self, rel_pos: Tuple[int, int], resource: str):
        """Supprime artificiellement une ressource d’une tuile donnée."""
        for data in self.last_vision_data:
            if data.rel_pos == rel_pos:
                if resource in data.resources:
                    data.resources[resource] -= 1
                    if data.resources[resource] <= 0:
                        del data.resources[resource]
                break
