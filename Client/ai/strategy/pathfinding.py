##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## pathfinding
##

import random
from typing import List, Optional, Tuple, Dict, Any
from config import CommandType, Constants
from utils.logger import logger

class RelativeTarget:
    """Représente une cible relative dans la vision."""
    def __init__(self, rel_position: Tuple[int, int], resource_type: str, distance: int = None):
        self.rel_position = rel_position
        self.resource_type = resource_type
        self.distance = distance if distance is not None else abs(rel_position[0]) + abs(rel_position[1])

class Pathfinder:
    """
    Pathfinding optimisé pour la navigation dans Zappy.
    Gère les déplacements relatifs et l'exploration intelligente.
    """
    def __init__(self):
        self.exploration_preferences = {
            'forward_bias': 0.4,
            'turn_penalty': 0.1,
            'random_factor': 0.2
        }
        self.recent_directions = []
        self.max_history = 5
        logger.debug("[Pathfinder] Initialisé avec exploration intelligente")

    def get_commands_to_target(self, target: RelativeTarget, current_orientation: int, vision_data: List[Any]) -> List[CommandType]:
        """
        Calcule la séquence de commandes pour atteindre une cible.
        """
        if not target or target.rel_position == (0, 0):
            return []

        target_x, target_y = target.rel_position
        commands = []

        optimal_direction = self._calculate_optimal_direction(target_x, target_y)
        rotation_commands = self._get_rotation_commands(current_orientation, optimal_direction)
        commands.extend(rotation_commands)

        movement_commands = self._get_movement_commands(target_x, target_y, optimal_direction)
        commands.extend(movement_commands)

        commands = self._optimize_command_sequence(commands)

        logger.debug(f"[Pathfinder] Chemin vers {target.resource_type} à {target.rel_position}: {len(commands)} commandes")
        return commands[:12]

    def _calculate_optimal_direction(self, target_x: int, target_y: int) -> int:
        """Calcule la direction optimale pour atteindre la cible."""
        abs_x, abs_y = abs(target_x), abs(target_y)
        if abs_x > abs_y:
            return 1 if target_x > 0 else 3
        else:
            return 0 if target_y < 0 else 2

    def _get_rotation_commands(self, current_orientation: int, target_orientation: int) -> List[CommandType]:
        """Calcule les commandes de rotation nécessaires."""
        if current_orientation == target_orientation:
            return []
        diff = (target_orientation - current_orientation) % 4
        if diff == 1:
            return [CommandType.RIGHT]
        elif diff == 2:
            return [CommandType.RIGHT, CommandType.RIGHT]
        elif diff == 3:
            return [CommandType.LEFT]
        return []

    def _get_movement_commands(self, target_x: int, target_y: int, orientation: int) -> List[CommandType]:
        """Calcule les commandes de mouvement vers la cible."""
        commands = []
        abs_x, abs_y = abs(target_x), abs(target_y)
        if orientation == 0 and target_y < 0:
            commands.extend([CommandType.FORWARD] * abs_y)
        elif orientation == 1 and target_x > 0:
            commands.extend([CommandType.FORWARD] * abs_x)
        elif orientation == 2 and target_y > 0:
            commands.extend([CommandType.FORWARD] * abs_y)
        elif orientation == 3 and target_x < 0:
            commands.extend([CommandType.FORWARD] * abs_x)
        remaining_distance = max(abs_x, abs_y) - len(commands)
        if remaining_distance > 0:
            commands.extend([CommandType.FORWARD] * min(remaining_distance, 3))
        return commands

    def _optimize_command_sequence(self, commands: List[CommandType]) -> List[CommandType]:
        """Optimise la séquence de commandes."""
        if not commands:
            return commands
        optimized = []
        consecutive_forwards = 0
        for cmd in commands:
            if cmd == CommandType.FORWARD:
                consecutive_forwards += 1
                if consecutive_forwards <= 5:
                    optimized.append(cmd)
            else:
                consecutive_forwards = 0
                optimized.append(cmd)
        return optimized

    def find_target_in_vision(self, vision_data: List[Any], resource_type: str) -> Optional[RelativeTarget]:
        """
        Trouve la meilleure cible d'un type de ressource dans la vision.
        """
        candidates = []
        for data in vision_data:
            if data.rel_pos == (0, 0):
                continue
            if resource_type in data.resources and data.resources[resource_type] > 0:
                distance = abs(data.rel_pos[0]) + abs(data.rel_pos[1])
                target = RelativeTarget(data.rel_pos, resource_type, distance)
                candidates.append(target)
        if not candidates:
            return None
        best_target = min(candidates, key=lambda t: t.distance)
        logger.debug(f"[Pathfinder] Cible {resource_type} trouvée à {best_target.rel_position} (distance: {best_target.distance})")
        return best_target

    def get_exploration_direction(self, current_orientation: int, vision_data: List[Any]) -> CommandType:
        """
        Détermine la meilleure direction d'exploration.
        """
        environment_analysis = self._analyze_exploration_environment(vision_data)
        if random.random() < self.exploration_preferences['forward_bias']:
            if environment_analysis['forward_clear']:
                self._add_to_history(CommandType.FORWARD)
                return CommandType.FORWARD
        available_turns = []
        if environment_analysis['left_promising']:
            available_turns.append(CommandType.LEFT)
        if environment_analysis['right_promising']:
            available_turns.append(CommandType.RIGHT)
        available_turns = [cmd for cmd in available_turns if cmd not in self.recent_directions[-2:]]
        if available_turns:
            chosen = random.choice(available_turns)
            self._add_to_history(chosen)
            return chosen
        fallback_options = [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]
        chosen = random.choice(fallback_options)
        self._add_to_history(chosen)
        logger.debug(f"[Pathfinder] Exploration: {chosen} (fallback)")
        return chosen

    def _analyze_exploration_environment(self, vision_data: List[Any]) -> Dict[str, bool]:
        """Analyse l'environnement pour l'exploration."""
        analysis = {
            'forward_clear': True,
            'left_promising': True,
            'right_promising': True,
            'resources_visible': False
        }
        if not vision_data:
            return analysis
        for data in vision_data:
            if data.rel_pos != (0, 0) and data.resources:
                analysis['resources_visible'] = True
                break
        occupied_positions = set()
        for data in vision_data:
            if data.players > 0 and data.rel_pos != (0, 0):
                occupied_positions.add(data.rel_pos)
        if (0, -1) in occupied_positions:
            analysis['forward_clear'] = False
        return analysis

    def _add_to_history(self, command: CommandType):
        """Ajoute une commande à l'historique récent."""
        self.recent_directions.append(command)
        if len(self.recent_directions) > self.max_history:
            self.recent_directions.pop(0)

    def get_resource_priority_list(self, requirements: Dict[str, int], inventory: Dict[str, int]) -> List[str]:
        """
        Retourne la liste des ressources par ordre de priorité de collecte.
        """
        missing = {}
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current
        rarity_order = [
            Constants.THYSTAME.value,
            Constants.PHIRAS.value,
            Constants.MENDIANE.value,
            Constants.SIBUR.value,
            Constants.DERAUMERE.value,
            Constants.LINEMATE.value
        ]
        priority_list = [res for res in rarity_order if res in missing]
        logger.debug(f"[Pathfinder] Priorité collecte: {priority_list}")
        return priority_list

    def calculate_path_cost(self, target: RelativeTarget, current_orientation: int) -> int:
        """
        Calcule le coût approximatif pour atteindre une cible.
        """
        if not target:
            return float('inf')
        target_x, target_y = target.rel_position
        optimal_direction = self._calculate_optimal_direction(target_x, target_y)
        rotation_cost = len(self._get_rotation_commands(current_orientation, optimal_direction))
        movement_cost = abs(target_x) + abs(target_y)
        total_cost = rotation_cost + movement_cost
        logger.debug(f"[Pathfinder] Coût pour {target.resource_type} à {target.rel_position}: {total_cost}")
        return total_cost

    def find_best_target_by_cost(self, targets: List[RelativeTarget], current_orientation: int) -> Optional[RelativeTarget]:
        """
        Trouve la meilleure cible selon le coût de déplacement.
        """
        if not targets:
            return None
        target_costs = []
        for target in targets:
            cost = self.calculate_path_cost(target, current_orientation)
            target_costs.append((target, cost))
        target_costs.sort(key=lambda x: x[1])
        best_target = target_costs[0][0]
        logger.debug(f"[Pathfinder] Meilleure cible: {best_target.resource_type} à {best_target.rel_position}")
        return best_target

    def clear_history(self):
        """Efface l'historique des directions récentes."""
        self.recent_directions.clear()
        logger.debug("[Pathfinder] Historique effacé")

    def get_pathfinding_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de pathfinding."""
        return {
            'recent_directions': list(self.recent_directions),
            'history_size': len(self.recent_directions),
            'exploration_preferences': self.exploration_preferences.copy()
        }
