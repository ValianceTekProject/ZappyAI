##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## math utilities
##

import math
from typing import Tuple, List

class MathUtils:
    @staticmethod
    def distance(x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Calcule la distance euclidienne entre deux points.
        """
        return math.hypot(x2 - x1, y2 - y1)

    @staticmethod
    def rotate(dx: int, dy: int, orientation: int) -> Tuple[int, int]:
        """
        Effectue une rotation des coordonnées (dx, dy) selon une orientation :
        0: Nord, 1: Est, 2: Sud, 3: Ouest
        """
        match orientation:
            case 0:
                return dx, -dy
            case 1:
                return dy, dx
            case 2:
                return -dx, dy
            case 3:
                return -dy, -dx
            case _:
                return dx, dy

    @staticmethod
    def compute_relative_positions(vision_range: int, orientation: int) -> List[Tuple[int, int]]:
        """
        Génère les positions relatives visibles selon le niveau de vision et l’orientation.
        """
        positions = []
        for depth in range(vision_range + 1):
            for lateral in range(-depth, depth + 1):
                rel_pos = MathUtils.rotate(lateral, depth, orientation)
                positions.append(rel_pos)
        return positions
