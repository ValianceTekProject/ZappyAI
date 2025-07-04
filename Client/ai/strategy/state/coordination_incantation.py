##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination_incantation - État de coordination nettoyé et corrigé
##

import time
import random
from typing import Optional, Any, List
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder
from config import CommandType
from constant import (
    CoordinationProtocol, IncantationRequirements, AgentRoles, 
    BroadcastDirections, FoodThresholds, StateTransitionThresholds,
    CoordinationMessages
)
from utils.logger import logger
from teams.coordination import CoordinationManager


class CoordinateIncantationState(State):
    """État de coordination pour incantations multi-joueurs selon protocole Zappy."""

    def __init__(self, planner):
        """
        Initialise l'état de coordination.
        
        Args:
            planner: Planificateur FSM
        """
        super().__init__(planner)
        self.coordination_mgr = CoordinationManager(
            planner.bus, 
            planner.cmd_mgr, 
            planner.state
        )

        self.role = self._determine_role()
        self.state.set_role(self.role)

        self.coordination_start_time = time.time()
        self.movement_commands = []
        self.pathfinder = Pathfinder()
        
        self.coordination_attempts = 0
        self.fallback_triggered = False
        self.last_broadcast_time = 0.0
        self.helpers_needed = self._calculate_helpers_needed()

        logger.info(f"[CoordinateIncantationState] 🤝 Coordination activée - Rôle: {self.role}, "
                   f"Niveau: {self.state.level}, Helpers requis: {self.helpers_needed}")

    def execute(self) -> Optional[Any]:
        """
        Logique de coordination selon le protocole Zappy strict.
        
        Returns:
            Commande à exécuter ou None
        """
        current_time = time.time()
        
        # Vérification timeout global avec fallback immédiat
        if self._is_coordination_timeout():
            logger.warning("[CoordinateIncantationState] Timeout coordination")
            return self._handle_coordination_failure()

        # Vérification des conditions de base strictes
        if not self._verify_coordination_conditions():
            logger.warning("[CoordinateIncantationState] Conditions perdues")
            return self._handle_coordination_failure()

        self._cleanup_old_data()

        if self.role == AgentRoles.INCANTER:
            return self._execute_incanter_logic()
        elif self.role == AgentRoles.HELPER:
            return self._execute_helper_logic()

        return self._handle_coordination_failure()

    def _determine_role(self) -> str:
        """
        Détermine le rôle selon les règles Zappy avec logique simplifiée.
        
        Returns:
            Rôle de l'agent (INCANTER ou HELPER)
        """
        current_food = self.state.get_food_count()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)

        # Niveau 1 : Ne devrait JAMAIS arriver ici (solo uniquement)
        if self.state.level == 1:
            logger.error("[CoordinateIncantationState] ❌ VIOLATION: Niveau 1 ne doit pas utiliser coordination")
            return AgentRoles.SURVIVOR

        # Si pas de coordination nécessaire
        if required_players <= 1:
            logger.error("[CoordinateIncantationState] ❌ VIOLATION: Pas de coordination nécessaire")
            return AgentRoles.SURVIVOR

        # Vérifications strictes des conditions minimales
        has_all_resources = not self.state.has_missing_resources()
        has_enough_food_for_incanter = current_food >= CoordinationProtocol.MIN_FOOD_TO_INITIATE
        has_enough_food_for_helper = current_food >= CoordinationProtocol.MIN_FOOD_TO_HELP

        # Si on ne peut être ni l'un ni l'autre, retourner SURVIVOR
        if not has_enough_food_for_helper:
            logger.warning(f"[CoordinateIncantationState] Nourriture insuffisante: {current_food}")
            return AgentRoles.SURVIVOR

        # Logique simplifiée : 70% incanteur si ressources complètes, sinon 30%
        if has_all_resources and has_enough_food_for_incanter:
            incanter_probability = 0.7
        else:
            incanter_probability = 0.3

        chosen_role = AgentRoles.INCANTER if random.random() < incanter_probability else AgentRoles.HELPER
        
        logger.info(f"[CoordinateIncantationState] Sélection rôle - "
                   f"Ressources: {has_all_resources}, Food: {current_food}, Rôle: {chosen_role}")
        
        return chosen_role

    def _calculate_helpers_needed(self) -> int:
        """
        Calcule le nombre d'helpers nécessaires.
        
        Returns:
            Nombre d'helpers requis
        """
        total_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        return max(0, total_players - 1)  # -1 pour l'incanteur

    def _verify_coordination_conditions(self) -> bool:
        """
        Vérification stricte du respect du protocole Zappy.
        
        Returns:
            True si le protocole est respecté
        """
        current_food = self.state.get_food_count()
        
        if self.role == AgentRoles.INCANTER:
            return (
                current_food >= CoordinationProtocol.MIN_FOOD_TO_INITIATE and
                not self.state.has_missing_resources()
            )
        elif self.role == AgentRoles.HELPER:
            return current_food >= CoordinationProtocol.MIN_FOOD_TO_HELP
        elif self.role == AgentRoles.SURVIVOR:
            return False
            
        return False

    def _execute_incanter_logic(self) -> Optional[Any]:
        """
        Logique pour un incanteur selon le protocole Zappy.
        
        Returns:
            Commande à exécuter ou None
        """
        current_time = time.time()

        # Vérification de la vision pour coordination
        if self._needs_vision_update():
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()

        # Envoyer des requêtes d'incantation selon le protocole
        if self._should_send_broadcast():
            self._send_incantation_broadcast()
            self.coordination_attempts += 1
            logger.info(f"[CoordinateIncantationState] 📢 Requête envoyée (tentative {self.coordination_attempts})")

        # Vérifier si on a assez d'helpers confirmés
        confirmed_helpers = self._count_confirmed_helpers()
        if confirmed_helpers >= self.helpers_needed:
            logger.info(f"[CoordinateIncantationState] ✅ Assez d'helpers: {confirmed_helpers}/{self.helpers_needed}")
            return self._transition_to_incantation()

        # Timeout ou trop de tentatives
        if (self.coordination_attempts >= CoordinationProtocol.MAX_COORDINATION_ATTEMPTS or
            current_time - self.coordination_start_time > CoordinationProtocol.COORDINATION_TIMEOUT):
            logger.warning("[CoordinateIncantationState] Timeout incanteur")
            return self._handle_coordination_failure()

        return None

    def _execute_helper_logic(self) -> Optional[Any]:
        """
        Logique pour un helper selon le protocole Zappy.
        
        Returns:
            Commande à exécuter ou None
        """
        current_time = time.time()
        
        # Timeout d'attente
        if current_time - self.coordination_start_time > CoordinationProtocol.COORDINATION_TIMEOUT:
            logger.warning("[CoordinateIncantationState] Timeout helper")
            return self._handle_coordination_failure()

        # Vérifier si on a choisi un incanteur à rejoindre
        target_direction = self.coordination_mgr.get_chosen_incanter_direction()
        
        if target_direction is None:
            logger.debug("[CoordinateIncantationState] 👂 En écoute des requêtes...")
            return None

        # Si on est déjà sur la bonne case (direction 0 = HERE)
        if target_direction == BroadcastDirections.HERE:
            logger.info("[CoordinateIncantationState] ✅ Sur la tuile de l'incanteur")
            return None

        # Se déplacer vers l'incanteur selon la direction du broadcast
        return self._move_towards_incanter(target_direction)

    def _send_incantation_broadcast(self):
        """Envoie un broadcast de requête d'incantation."""
        level = self.state.level
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(level, 1)
        
        # Format de message standardisé
        message = CoordinationMessages.format_request(level, required_players)
        
        self.cmd_mgr.broadcast(message)
        self.last_broadcast_time = time.time()
        
        logger.info(f"[CoordinateIncantationState] 📢 Broadcast envoyé: {message}")

    def _count_confirmed_helpers(self) -> int:
        """
        Compte les helpers confirmés présents.
        
        Returns:
            Nombre de helpers confirmés
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return 0

        # Compter les joueurs sur la tuile actuelle
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                current_players = data.players
                # -1 pour l'incanteur lui-même
                helpers_here = max(0, current_players - 1)
                logger.debug(f"[CoordinateIncantationState] Joueurs sur tuile: {current_players}, Helpers: {helpers_here}")
                return min(helpers_here, self.helpers_needed)
        
        return 0

    def _move_towards_incanter(self, direction: int) -> Optional[Any]:
        """
        Se déplace vers l'incanteur selon la direction du broadcast Zappy.
        
        Args:
            direction: Direction du broadcast (1-8)
            
        Returns:
            Commande de mouvement
        """
        if not self.movement_commands:
            self.movement_commands = self._plan_movement_to_incanter(direction)

        if self.movement_commands:
            next_cmd = self.movement_commands.pop(0)
            return self._execute_movement_command(next_cmd)

        return None

    def _plan_movement_to_incanter(self, direction: int) -> List[CommandType]:
        """
        Planifie le mouvement selon les directions Zappy (PDF page 7).
        
        Args:
            direction: Direction du broadcast (1-8)
            
        Returns:
            Liste des commandes de mouvement
        """
        direction_to_commands = {
            BroadcastDirections.FRONT: [CommandType.FORWARD],
            BroadcastDirections.FRONT_RIGHT: [CommandType.RIGHT, CommandType.FORWARD],
            BroadcastDirections.RIGHT: [CommandType.RIGHT, CommandType.FORWARD],
            BroadcastDirections.BACK_RIGHT: [CommandType.RIGHT, CommandType.RIGHT, CommandType.FORWARD],
            BroadcastDirections.BACK: [CommandType.RIGHT, CommandType.RIGHT, CommandType.FORWARD],
            BroadcastDirections.BACK_LEFT: [CommandType.LEFT, CommandType.LEFT, CommandType.FORWARD],
            BroadcastDirections.LEFT: [CommandType.LEFT, CommandType.FORWARD],
            BroadcastDirections.FRONT_LEFT: [CommandType.LEFT, CommandType.FORWARD],
        }
        
        commands = direction_to_commands.get(direction, [CommandType.FORWARD])
        logger.info(f"[CoordinateIncantationState] Mouvement vers direction {direction}: {commands}")
        return commands

    def _execute_movement_command(self, command_type: CommandType) -> Optional[Any]:
        """
        Exécute une commande de mouvement.
        
        Args:
            command_type: Type de commande
            
        Returns:
            Commande exécutée
        """
        command_map = {
            CommandType.FORWARD: self.cmd_mgr.forward,
            CommandType.LEFT: self.cmd_mgr.left,
            CommandType.RIGHT: self.cmd_mgr.right,
        }
        
        command_func = command_map.get(command_type)
        if command_func:
            return command_func()
        
        return None

    def _should_send_broadcast(self) -> bool:
        """
        Détermine si on doit envoyer une requête de broadcast.
        
        Returns:
            True si broadcast nécessaire
        """
        if self.role != AgentRoles.INCANTER:
            return False

        current_time = time.time()
        
        # Cooldown entre broadcasts
        if current_time - self.last_broadcast_time < CoordinationProtocol.BROADCAST_COOLDOWN:
            return False

        # Limiter le nombre de tentatives
        if self.coordination_attempts >= CoordinationProtocol.MAX_COORDINATION_ATTEMPTS:
            return False

        return True

    def _needs_vision_update(self) -> bool:
        """
        Détermine si une mise à jour de vision est nécessaire.
        
        Returns:
            True si vision à mettre à jour
        """
        return (
            not self.state.get_vision().last_vision_data or 
            self.context.get('needs_vision_update', False) or
            getattr(self.state, 'needs_look', False)
        )

    def _cleanup_old_data(self):
        """Nettoie les données de coordination obsolètes."""
        if hasattr(self.coordination_mgr, 'cleanup_old_data'):
            self.coordination_mgr.cleanup_old_data()

    def _is_coordination_timeout(self) -> bool:
        """
        Vérifie si la coordination a expiré.
        
        Returns:
            True si timeout dépassé
        """
        return (time.time() - self.coordination_start_time > CoordinationProtocol.COORDINATION_TIMEOUT)

    def _handle_coordination_failure(self) -> Optional[Any]:
        """
        Gère l'échec de coordination avec fallback approprié selon les règles strictes.
        
        Returns:
            Transition vers nouvel état
        """
        if self.fallback_triggered:
            return None
            
        self.fallback_triggered = True
        current_food = self.state.get_food_count()
        
        logger.warning(f"[CoordinateIncantationState] 🔄 Fallback coordination - Food: {current_food}")
        
        # Priorités de fallback strictes
        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            logger.info("[CoordinateIncantationState] → URGENCE ALIMENTAIRE")
            from ai.strategy.state.emergency import EmergencyState
            new_state = EmergencyState(self.planner)
        elif current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
            logger.info("[CoordinateIncantationState] → COLLECTE NOURRITURE")
            from ai.strategy.state.collect_food import CollectFoodState
            new_state = CollectFoodState(self.planner)
        elif self.state.has_missing_resources():
            logger.info("[CoordinateIncantationState] → COLLECTE RESSOURCES")
            from ai.strategy.state.collect_resources import CollectResourcesState
            new_state = CollectResourcesState(self.planner)
        else:
            logger.info("[CoordinateIncantationState] → EXPLORATION (attente)")
            from ai.strategy.state.explore import ExploreState
            new_state = ExploreState(self.planner)
        
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _transition_to_incantation(self) -> Optional[Any]:
        """
        Transition vers l'état d'incantation coordonnée.
        
        Returns:
            Exécution du nouvel état
        """
        logger.info("[CoordinateIncantationState] → Transition vers incantation coordonnée")
        
        # Pour niveau ≥ 2, on lance l'incantation directement
        logger.info("[CoordinateIncantationState] 🔮 Lancement incantation coordonnée")
        return self.cmd_mgr.incantation()

    def on_command_success(self, command_type, response=None):
        """
        Gestion du succès des commandes.
        
        Args:
            command_type: Type de commande
            response: Réponse du serveur
        """
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True

        if command_type == CommandType.BROADCAST:
            logger.debug("[CoordinateIncantationState] ✅ Broadcast envoyé avec succès")

        if command_type == CommandType.INCANTATION:
            logger.info("[CoordinateIncantationState] 🎉 INCANTATION COORDONNÉE RÉUSSIE!")

    def on_command_failed(self, command_type, response=None):
        """
        Gestion des échecs de commandes.
        
        Args:
            command_type: Type de commande
            response: Réponse du serveur
        """
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.movement_commands.clear()
            self.context['needs_vision_update'] = True

        if command_type == CommandType.BROADCAST:
            logger.warning("[CoordinateIncantationState] ❌ Échec broadcast")

        if command_type == CommandType.INCANTATION:
            logger.error(f"[CoordinateIncantationState] 💥 INCANTATION COORDONNÉE ÉCHOUÉE: {response}")
            self.coordination_attempts = 0
            self.last_broadcast_time = 0

    def on_event(self, event: Event) -> Optional[State]:
        """
        Gestion des événements pendant la coordination.
        
        Args:
            event: Événement reçu
            
        Returns:
            Nouvel état ou None
        """
        if event == Event.FOOD_EMERGENCY:
            logger.error("[CoordinateIncantationState] URGENCE ALIMENTAIRE!")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)

        elif event == Event.FOOD_LOW:
            current_food = self.state.get_food_count()
            if (self.role == AgentRoles.HELPER and 
                current_food < CoordinationProtocol.MIN_FOOD_TO_HELP):
                logger.warning("[CoordinateIncantationState] Nourriture insuffisante helper")
                from ai.strategy.state.collect_food import CollectFoodState
                return CollectFoodState(self.planner)

        return None

    def on_enter(self):
        """Actions à l'entrée de l'état."""
        super().on_enter()
        current_food = self.state.get_food_count()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)

        logger.info(f"[CoordinateIncantationState] 🤝 ENTRÉE coordination - "
                   f"Rôle: {self.role}, Niveau: {self.state.level}, "
                   f"Food: {current_food}, Joueurs requis: {required_players}")

        # Vérification critique à l'entrée
        if self.state.level == 1:
            logger.error("[CoordinateIncantationState] ❌ ERREUR: Niveau 1 ne doit pas utiliser coordination!")

        # Reset des variables
        self.coordination_start_time = time.time()
        self.movement_commands.clear()
        self.coordination_attempts = 0
        self.fallback_triggered = False
        self.last_broadcast_time = 0.0
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état."""
        super().on_exit()
        duration = time.time() - self.coordination_start_time

        logger.info(f"[CoordinateIncantationState] ✅ SORTIE coordination - "
                   f"Rôle: {self.role}, Durée: {duration:.1f}s, "
                   f"Tentatives: {self.coordination_attempts}")

        # Nettoyage
        if hasattr(self.coordination_mgr, 'clear_coordination_data'):
            self.coordination_mgr.clear_coordination_data()
        self.movement_commands.clear()