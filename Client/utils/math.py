##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## math utilities - CORRIGÉ
##

import math
from typing import Tuple, List
from config import Orientation, CommandType

class MathUtils:
    @staticmethod
    def distance(x1: int, y1: int, x2: int, y2: int) -> float:
        """Calcule la distance euclidienne entre deux points."""
        return math.hypot(x2 - x1, y2 - y1)

    @staticmethod
    def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
        """Calcule la distance de Manhattan entre deux points."""
        return abs(x2 - x1) + abs(y2 - y1)

    @staticmethod
    def compute_relative_positions(vision_range: int, orientation: int) -> List[Tuple[int, int]]:
        """
        Génère les positions relatives dans l'ordre de la commande Look du serveur Zappy.

        Le serveur renvoie les tuiles dans l'ordre suivant :
        - D'abord la tuile courante (0,0)
        - Puis par "ligne" croissante de distance, de gauche-à-droite relativement à l'orientation

        Exemple pour vision_range=2, orientation=NORTH (0):
        Distance 0: [(0,0)]
        Distance 1: [(-1,-1), (0,-1), (1,-1)]
        Distance 2: [(-2,-2), (-1,-2), (0,-2), (1,-2), (2,-2)]
        """
        positions = []

        positions.append((0, 0))

        for distance in range(1, vision_range + 1):
            line_positions = []

            for x_offset in range(-distance, distance + 1):
                base_pos = (x_offset, -distance)
                rotated_pos = MathUtils._rotate_position(base_pos, orientation)
                line_positions.append(rotated_pos)

            positions.extend(line_positions)

        return positions

    @staticmethod
    def _rotate_position(pos: Tuple[int, int], orientation: int) -> Tuple[int, int]:
        """
        Effectue une rotation des coordonnées selon l'orientation.
        0: NORTH (pas de rotation)
        1: EAST (rotation 90° horaire)
        2: SOUTH (rotation 180°)
        3: WEST (rotation 90° anti-horaire)
        """
        x, y = pos

        if orientation == Orientation.NORTH:
            return (x, -y)
        elif orientation == Orientation.EAST:
            return (-y, x)
        elif orientation == Orientation.SOUTH:
            return (-x, -y)
        elif orientation == Orientation.WEST:
            return (y, -x)
        else:
            return (x, y)

    @staticmethod
    def get_direction_vector(orientation: int) -> Tuple[int, int]:
        """Retourne le vecteur directionnel pour une orientation donnée."""
        vectors = {
            Orientation.NORTH: (0, -1),
            Orientation.EAST: (1, 0),
            Orientation.SOUTH: (0, 1),
            Orientation.WEST: (-1, 0)
        }
        return vectors.get(orientation, (0, -1))

    @staticmethod
    def calculate_rotation_needed(current_ori: int, target_ori: int) -> Tuple[str, int]:
        """
        Calcule la rotation nécessaire pour passer de current_ori à target_ori.
        Retourne (direction, nombre_de_rotations)
        """
        diff = (target_ori - current_ori) % 4

        if diff == 0:
            return ("none", 0)
        elif diff == 1:
            return ("right", 1)
        elif diff == 2:
            return ("right", 2) if diff <= 2 else ("left", 2)
        elif diff == 3:
            return ("left", 1)
        return ("none", 0)
