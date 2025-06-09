##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## pathfinding - CORРИГÉ - BFS amélioré avec validation de la grille
##

from typing import Optional, List, Tuple, Dict, Set
from collections import deque
from dataclasses import dataclass
from config import CommandType, Orientation, Constants
from utils.logger import logger

@dataclass
class RelativeTarget:
    """Cible définie par sa position relative et le type de ressource."""
    rel_position: Tuple[int, int]
    resource_type: str
    distance: int

    def __post_init__(self):
        self.distance = abs(self.rel_position[0]) + abs(self.rel_position[1])


class Pathfinder:
    """
    Pathfinding basé sur un BFS local avec validation de la grille de vision.
    """

    def __init__(self):
        self.vision_range = Constants.VISION_RANGE.value
        self.cardinal_directions: List[Tuple[int, int]] = [
            (0, -1),  # 0 → Nord
            (1, 0),   # 1 → Est
            (0, 1),   # 2 → Sud
            (-1, 0)   # 3 → Ouest
        ]
        self.exploration_history: List[int] = []
        self.max_history_size = 10

    def find_target_in_vision(self, vision_data, target_resource: str) -> Optional[RelativeTarget]:
        """
        Trouve dans vision_data la ressource target_resource la plus proche.
        """
        logger.debug(f"Recherche de {target_resource} dans vision")
        targets: List[RelativeTarget] = []

        for tile_data in vision_data:
            resource_count = tile_data.resources.get(target_resource, 0)
            if resource_count > 0:
                pos = tile_data.rel_pos
                if pos != (0, 0):
                    targets.append(RelativeTarget(
                        rel_position=pos,
                        resource_type=target_resource,
                        distance=abs(pos[0]) + abs(pos[1])
                    ))
                    logger.debug(f"  Trouvé {target_resource} à {pos} (distance {abs(pos[0]) + abs(pos[1])})")

        if not targets:
            logger.debug(f"  Aucun {target_resource} trouvé dans la vision")
            return None

        closest = min(targets, key=lambda t: t.distance)
        logger.debug(f"  Cible la plus proche: {target_resource} à {closest.rel_position}")
        return closest

    def get_resource_priority_list(self, requirements: Dict[str, int],
                                   current_inventory: Dict[str, int]) -> List[str]:
        """
        Retourne la liste des ressources manquantes triées par priorité.
        1. Food en priorité absolue
        2. Puis par déficit décroissant
        """
        missing: List[Tuple[str, int, int]] = []  # (resource, deficit, priority)

        for resource, needed in requirements.items():
            current_count = current_inventory.get(resource, 0)
            if current_count < needed:
                deficit = needed - current_count
                priority = 10 if resource == "food" else deficit
                missing.append((resource, deficit, priority))

        missing.sort(key=lambda x: x[2], reverse=True)
        return [res for res, _, _ in missing]

    def get_commands_to_target(self,
                               target: RelativeTarget,
                               current_orientation: int,
                               vision_data) -> Optional[List[CommandType]]:
        """
        Retourne la liste des commandes pour atteindre une cible.
        Utilise BFS avec validation stricte de la grille de vision.
        """
        dest = target.rel_position
        logger.debug(f"Calcul du chemin vers {dest} depuis orientation {current_orientation}")
        valid_positions: Set[Tuple[int, int]] = set()
        for tile_data in vision_data:
            valid_positions.add(tile_data.rel_pos)

        logger.debug(f"Positions valides dans la vision: {valid_positions}")

        if dest not in valid_positions:
            logger.warning(f"Cible {dest} hors de la vision valide")
            return None

        start_state = (0, 0, current_orientation)
        parent_map: Dict[Tuple[int,int,int], Tuple[Optional[Tuple[int,int,int]], Optional[CommandType]]] = {}
        queue = deque([start_state])
        parent_map[start_state] = (None, None)

        found_state: Optional[Tuple[int,int,int]] = None

        while queue:
            x, y, ori = queue.popleft()
            if (x, y) == dest:
                found_state = (x, y, ori)
                logger.debug(f"Destination trouvée à l'état {found_state}")
                break

            transitions = self._get_valid_transitions(x, y, ori, valid_positions)
            for next_state, command in transitions:
                if next_state not in parent_map:
                    parent_map[next_state] = ((x, y, ori), command)
                    queue.append(next_state)

        if found_state is None:
            logger.warning(f"Aucun chemin trouvé vers {dest}")
            return None
        commands = self._reconstruct_path(parent_map, start_state, found_state)
        logger.debug(f"Chemin trouvé: {commands}")
        return commands

    def _get_valid_transitions(self, x: int, y: int, ori: int, 
                              valid_positions: Set[Tuple[int, int]]) -> List[Tuple[Tuple[int,int,int], CommandType]]:
        """
        Génère toutes les transitions valides depuis un état donné.
        """
        transitions = []
        dx, dy = self.cardinal_directions[ori]
        next_x, next_y = x + dx, y + dy
        if (next_x, next_y) in valid_positions:
            transitions.append(((next_x, next_y, ori), CommandType.FORWARD))

        left_ori = (ori - 1) % 4
        transitions.append(((x, y, left_ori), CommandType.LEFT))
        right_ori = (ori + 1) % 4
        transitions.append(((x, y, right_ori), CommandType.RIGHT))

        return transitions

    def _reconstruct_path(self, parent_map: Dict, start_state: Tuple[int,int,int], 
                         end_state: Tuple[int,int,int]) -> List[CommandType]:
        """
        Reconstitue le chemin de commandes depuis la map des parents.
        """
        path_commands = []
        current_state = end_state

        while current_state != start_state:
            parent_state, command = parent_map[current_state]
            if command is not None:
                path_commands.append(command)
            current_state = parent_state

        path_commands.reverse()
        return path_commands

    def get_exploration_direction(self, current_orientation: int, vision_data) -> CommandType:
        """
        Retourne une direction d'exploration sûre.
        """
        safe_orientations = self._get_safe_directions(vision_data)
        if not safe_orientations:
            return CommandType.RIGHT

        preferred = self._filter_exploration_directions(safe_orientations)
        target_ori = preferred[0] if preferred else safe_orientations[0]

        self._update_exploration_history(target_ori)
        return self._get_rotation_command(current_orientation, target_ori)

    def _get_safe_directions(self, vision_data) -> List[int]:
        """
        Identifie les directions où la case adjacente est libre de joueurs.
        """
        safe_directions = []

        for ori in range(4):
            dx, dy = self.cardinal_directions[ori]
            adjacent_pos = (dx, dy)

            is_safe = True
            for tile_data in vision_data:
                if tile_data.rel_pos == adjacent_pos and tile_data.players > 0:
                    is_safe = False
                    break

            if is_safe:
                safe_directions.append(ori)

        return safe_directions

    def _filter_exploration_directions(self, safe_directions: List[int]) -> List[int]:
        """
        Filtre les directions d'exploration pour éviter les boucles.
        """
        if not self.exploration_history:
            return safe_directions

        recent_dirs = set(self.exploration_history[-3:]) if len(self.exploration_history) >= 3 else set()

        filtered = [d for d in safe_directions if d not in recent_dirs]

        return filtered if filtered else safe_directions

    def _update_exploration_history(self, direction: int):
        """Met à jour l'historique des directions d'exploration."""
        self.exploration_history.append(direction)
        if len(self.exploration_history) > self.max_history_size:
            self.exploration_history.pop(0)

    def _get_rotation_command(self, current_orientation: int, target_orientation: int) -> CommandType:
        """
        Calcule la commande de rotation optimale.
        """
        if current_orientation == target_orientation:
            return CommandType.FORWARD

        diff = (target_orientation - current_orientation) % 4

        if diff == 1 or diff == 3:
            return CommandType.RIGHT if diff == 1 else CommandType.LEFT
        elif diff == 2:
            return CommandType.RIGHT

        return CommandType.FORWARD

    def clear_exploration_history(self):
        """Vide l'historique d'exploration."""
        self.exploration_history.clear()