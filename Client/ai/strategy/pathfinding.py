##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## Pathfinding optimisé pour la FSM de survie
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
        # Préférences de direction pour l'exploration
        self.exploration_preferences = {
            'forward_bias': 0.4,     # Préférence pour avancer
            'turn_penalty': 0.1,     # Pénalité pour les rotations
            'random_factor': 0.2     # Facteur d'aléatoire
        }
        
        # Historique des directions récentes (éviter répétitions)
        self.recent_directions = []
        self.max_history = 5
        
        logger.debug("[Pathfinder] Initialisé avec exploration intelligente")

    def get_commands_to_target(self, target: RelativeTarget, current_orientation: int, 
                             vision_data: List[Any]) -> List[CommandType]:
        """
        Calcule la séquence de commandes pour atteindre une cible.
        
        Args:
            target: Cible à atteindre
            current_orientation: Orientation actuelle (0=N, 1=E, 2=S, 3=W)
            vision_data: Données de vision pour éviter obstacles
            
        Returns:
            Liste des commandes à exécuter
        """
        if not target or target.rel_position == (0, 0):
            return []
        
        target_x, target_y = target.rel_position
        commands = []
        
        # Calculer direction optimale
        optimal_direction = self._calculate_optimal_direction(target_x, target_y)
        
        # Calculer rotations nécessaires
        rotation_commands = self._get_rotation_commands(current_orientation, optimal_direction)
        commands.extend(rotation_commands)
        
        # Calculer déplacements
        movement_commands = self._get_movement_commands(target_x, target_y, optimal_direction)
        commands.extend(movement_commands)
        
        # Limiter et optimiser
        commands = self._optimize_command_sequence(commands)
        
        logger.debug(f"[Pathfinder] Chemin vers {target.resource_type} à {target.rel_position}: {len(commands)} commandes")
        return commands[:12]  # Limite sécurisée

    def _calculate_optimal_direction(self, target_x: int, target_y: int) -> int:
        """Calcule la direction optimale pour atteindre la cible."""
        # Prioriser l'axe avec la plus grande distance
        abs_x, abs_y = abs(target_x), abs(target_y)
        
        if abs_x > abs_y:
            # Mouvement horizontal prioritaire
            return 1 if target_x > 0 else 3  # Est ou Ouest
        else:
            # Mouvement vertical prioritaire
            return 0 if target_y < 0 else 2  # Nord ou Sud

    def _get_rotation_commands(self, current_orientation: int, target_orientation: int) -> List[CommandType]:
        """Calcule les commandes de rotation nécessaires."""
        if current_orientation == target_orientation:
            return []
        
        # Calculer rotation la plus courte
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
        
        # Stratégie simple : déplacement en L
        if orientation == 0 and target_y < 0:  # Nord
            commands.extend([CommandType.FORWARD] * abs_y)
        elif orientation == 1 and target_x > 0:  # Est
            commands.extend([CommandType.FORWARD] * abs_x)
        elif orientation == 2 and target_y > 0:  # Sud
            commands.extend([CommandType.FORWARD] * abs_y)
        elif orientation == 3 and target_x < 0:  # Ouest
            commands.extend([CommandType.FORWARD] * abs_x)
        
        # Ajouter ajustements pour l'autre axe si nécessaire
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
                # Limiter les forwards consécutifs
                if consecutive_forwards <= 5:
                    optimized.append(cmd)
            else:
                consecutive_forwards = 0
                optimized.append(cmd)
        
        return optimized

    def find_target_in_vision(self, vision_data: List[Any], resource_type: str) -> Optional[RelativeTarget]:
        """
        Trouve la meilleure cible d'un type de ressource dans la vision.
        
        Args:
            vision_data: Données de vision
            resource_type: Type de ressource recherché
            
        Returns:
            RelativeTarget ou None si aucune cible trouvée
        """
        candidates = []
        
        for data in vision_data:
            if data.rel_pos == (0, 0):  # Ignorer tuile actuelle
                continue
                
            if resource_type in data.resources and data.resources[resource_type] > 0:
                distance = abs(data.rel_pos[0]) + abs(data.rel_pos[1])
                target = RelativeTarget(data.rel_pos, resource_type, distance)
                candidates.append(target)
        
        if not candidates:
            return None
        
        # Choisir la cible la plus proche
        best_target = min(candidates, key=lambda t: t.distance)
        logger.debug(f"[Pathfinder] Cible {resource_type} trouvée à {best_target.rel_position} (distance: {best_target.distance})")
        
        return best_target

    def get_exploration_direction(self, current_orientation: int, vision_data: List[Any]) -> CommandType:
        """
        Détermine la meilleure direction d'exploration.
        
        Args:
            current_orientation: Orientation actuelle
            vision_data: Données de vision pour éviter obstacles
            
        Returns:
            Commande de mouvement pour exploration
        """
        # Analyser l'environnement visible
        environment_analysis = self._analyze_exploration_environment(vision_data)
        
        # Choisir direction selon stratégie
        if random.random() < self.exploration_preferences['forward_bias']:
            # Préférer avancer
            if environment_analysis['forward_clear']:
                self._add_to_history(CommandType.FORWARD)
                return CommandType.FORWARD
        
        # Choisir rotation si forward bloqué ou par stratégie
        available_turns = []
        if environment_analysis['left_promising']:
            available_turns.append(CommandType.LEFT)
        if environment_analysis['right_promising']:
            available_turns.append(CommandType.RIGHT)
        
        # Éviter répétitions récentes
        available_turns = [cmd for cmd in available_turns if cmd not in self.recent_directions[-2:]]
        
        if available_turns:
            chosen = random.choice(available_turns)
            self._add_to_history(chosen)
            return chosen
        
        # Fallback : forward ou rotation aléatoire
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
        
        # Vérifier présence de ressources
        for data in vision_data:
            if data.rel_pos != (0, 0) and data.resources:
                analysis['resources_visible'] = True
                break
        
        # Analyse simplifiée des directions
        # (En réalité, cela nécessiterait une analyse plus complexe de la vision relative)
        occupied_positions = set()
        for data in vision_data:
            if data.players > 0 and data.rel_pos != (0, 0):
                occupied_positions.add(data.rel_pos)
        
        # Heuristiques simples
        if (0, -1) in occupied_positions:  # Position devant bloquée
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
        
        Args:
            requirements: Ressources requises pour incantation
            inventory: Inventaire actuel
            
        Returns:
            Liste ordonnée des ressources à collecter
        """
        # Calculer manques
        missing = {}
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current
        
        # Ordonner par rareté (priorité aux plus rares)
        rarity_order = [
            Constants.THYSTAME.value,    # Le plus rare
            Constants.PHIRAS.value,
            Constants.MENDIANE.value,
            Constants.SIBUR.value,
            Constants.DERAUMERE.value,
            Constants.LINEMATE.value     # Le plus commun
        ]
        
        # Filtrer et ordonner
        priority_list = [res for res in rarity_order if res in missing]
        
        logger.debug(f"[Pathfinder] Priorité collecte: {priority_list}")
        return priority_list

    def calculate_path_cost(self, target: RelativeTarget, current_orientation: int) -> int:
        """
        Calcule le coût approximatif pour atteindre une cible.
        
        Returns:
            Coût en nombre de commandes approximatif
        """
        if not target:
            return float('inf')
        
        target_x, target_y = target.rel_position
        
        # Coût de rotation
        optimal_direction = self._calculate_optimal_direction(target_x, target_y)
        rotation_cost = len(self._get_rotation_commands(current_orientation, optimal_direction))
        
        # Coût de déplacement (distance Manhattan)
        movement_cost = abs(target_x) + abs(target_y)
        
        total_cost = rotation_cost + movement_cost
        
        logger.debug(f"[Pathfinder] Coût pour {target.resource_type} à {target.rel_position}: {total_cost}")
        return total_cost

    def find_best_target_by_cost(self, targets: List[RelativeTarget], current_orientation: int) -> Optional[RelativeTarget]:
        """
        Trouve la meilleure cible selon le coût de déplacement.
        
        Args:
            targets: Liste des cibles possibles
            current_orientation: Orientation actuelle
            
        Returns:
            Meilleure cible ou None
        """
        if not targets:
            return None
        
        # Calculer coût pour chaque cible
        target_costs = []
        for target in targets:
            cost = self.calculate_path_cost(target, current_orientation)
            target_costs.append((target, cost))
        
        # Trier par coût croissant
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