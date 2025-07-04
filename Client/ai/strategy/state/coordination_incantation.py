##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordinate_incantation - État de coordination d'incantation amélioré
##

import time
import random
from typing import Optional, Any, Dict, List
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder
from config import Constants, CommandType
from constant import (
    CoordinationMessages, IncantationRequirements, AgentRoles, 
    TimingConstants, CoordinationStrategy
)
from utils.logger import logger
from teams.coordination import CoordinationManager


class CoordinateIncantationState(State):
    """
    État de coordination pour les incantations de groupe avec mécanismes de récupération.

    Gère :
    - Le rôle d'incanteur (initie et coordonne) avec timeout
    - Le rôle d'helper (aide un incanteur) avec abandon automatique
    - La communication via le protocole de coordination
    - Les mécanismes de fallback en cas d'échec
    """

    def __init__(self, planner):
        super().__init__(planner)
        self.coordination_mgr = CoordinationManager(
            planner.bus, 
            planner.cmd_mgr, 
            planner.state
        )

        self.role = self._determine_role()
        self.state.role = self.role

        self.coordination_start_time = time.time()
        self.last_broadcast_time = 0.0
        self.waiting_for_helpers = False
        self.target_incanter_direction = None
        self.movement_commands = []
        self.pathfinder = Pathfinder()
        
        # Compteurs pour les mécanismes de récupération
        self.coordination_attempts = 0
        self.max_coordination_attempts = CoordinationStrategy.MAX_COORDINATION_ATTEMPTS
        self.last_retry_time = 0.0
        self.helpers_found_count = 0
        self.fallback_triggered = False

        logger.info(f"[CoordinateIncantationState] 🤝 Coordination activée - Rôle: {self.role}")

    def execute(self) -> Optional[Any]:
        """
        Logique de coordination avec mécanismes de récupération améliorés.
        """
        current_time = time.time()
        
        # Vérification du timeout global avec fallback
        if self._is_coordination_timeout():
            logger.warning("[CoordinateIncantationState] Timeout coordination, fallback")
            return self._handle_coordination_failure()

        # Vérification des conditions de base
        if not self._verify_coordination_conditions():
            logger.warning("[CoordinateIncantationState] Conditions perdues, fallback")
            return self._handle_coordination_failure()

        self._cleanup_old_data()

        if self.role == AgentRoles.INCANTER:
            return self._execute_incanter_logic()
        elif self.role == AgentRoles.HELPER:
            return self._execute_helper_logic()

        # Si aucun rôle valide, fallback
        return self._handle_coordination_failure()

    def _determine_role(self) -> str:
        """
        Détermine le rôle de l'agent avec logique probabiliste améliorée.
        """
        current_food = self.state.get_food_count()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)

        # Niveau 1 : toujours incanteur (solo autorisé)
        if self.state.level == 1:
            return AgentRoles.INCANTER

        # Si pas de coordination nécessaire
        if required_players <= 1:
            return AgentRoles.INCANTER

        # Vérifications de base pour être incanteur
        can_be_incanter = (
            not self.state.has_missing_resources() and 
            current_food >= CoordinationMessages.MIN_FOOD_TO_INITIATE
        )

        # Vérifications de base pour être helper
        can_be_helper = (
            current_food >= CoordinationMessages.MIN_FOOD_TO_HELP and 
            self.state.level > 1
        )

        # Si on ne peut être ni l'un ni l'autre
        if not can_be_incanter and not can_be_helper:
            return AgentRoles.SURVIVOR

        # Si on ne peut être qu'incanteur
        if can_be_incanter and not can_be_helper:
            return AgentRoles.INCANTER

        # Si on ne peut être qu'helper
        if can_be_helper and not can_be_incanter:
            return AgentRoles.HELPER

        # Si on peut être les deux, utiliser la logique probabiliste
        incanter_probability = CoordinationStrategy.INCANTER_PROBABILITY_BASE

        # Bonus si on a toutes les ressources (plus de chance d'être incanteur)
        if not self.state.has_missing_resources():
            incanter_probability += 0.2

        # Bonus selon la nourriture (plus de nourriture = plus de chance d'être incanteur)
        food_ratio = current_food / CoordinationMessages.MIN_FOOD_TO_INITIATE
        incanter_probability += min(0.2, food_ratio * 0.1)

        # Décision aléatoire
        if random.random() < incanter_probability:
            return AgentRoles.INCANTER
        else:
            return AgentRoles.HELPER

    def _verify_coordination_conditions(self) -> bool:
        """
        Vérifie que les conditions de coordination sont toujours valides.
        """
        current_food = self.state.get_food_count()
        
        if self.role == AgentRoles.INCANTER:
            return (
                current_food >= CoordinationMessages.MIN_FOOD_TO_INITIATE and
                not self.state.has_missing_resources()
            )
        elif self.role == AgentRoles.HELPER:
            return current_food >= CoordinationMessages.MIN_FOOD_TO_HELP
            
        return False

    def _execute_incanter_logic(self) -> Optional[Any]:
        """
        Logique pour un incanteur avec timeouts et fallbacks.
        """
        current_time = time.time()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)

        # Niveau 1 : incantation solo immédiate
        if self.state.level == 1:
            logger.info("[CoordinateIncantationState] Niveau 1 - Transition incantation solo")
            return self._transition_to_incantation()

        # Vérification de la vision
        if self._needs_vision_update():
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()

        # Envoyer des requêtes d'incantation périodiquement
        if self._should_send_broadcast():
            self.coordination_mgr.send_incant_request()
            self.last_broadcast_time = current_time
            self.waiting_for_helpers = True
            self.coordination_attempts += 1
            logger.info(f"[CoordinateIncantationState] 📢 Requête {self.coordination_attempts}/{self.max_coordination_attempts} envoyée")

        # Vérifier si on a assez d'helpers
        if self.waiting_for_helpers:
            helpers_here = self.coordination_mgr.get_helpers_here()
            helpers_coming = self.coordination_mgr.get_coming_helpers()
            
            if self.coordination_mgr.has_enough_helpers():
                logger.info("[CoordinateIncantationState] ✅ Assez d'helpers, lancement incantation")
                return self._transition_to_incantation()

            # Log du progrès des helpers
            if len(helpers_here) != self.helpers_found_count:
                self.helpers_found_count = len(helpers_here)
                logger.info(f"[CoordinateIncantationState] Helpers: {len(helpers_here)} ici, {len(helpers_coming)} en route")

            # Timeout d'attente des helpers
            wait_time = current_time - self.last_broadcast_time
            if wait_time > CoordinationStrategy.MAX_WAIT_FOR_HELPERS:
                logger.warning(f"[CoordinateIncantationState] Timeout attente helpers ({wait_time:.1f}s)")
                return self._handle_coordination_failure()

        # Si trop de tentatives échouées
        if self.coordination_attempts >= self.max_coordination_attempts:
            logger.error("[CoordinateIncantationState] Trop de tentatives de coordination")
            return self._handle_coordination_failure()

        return None

    def _execute_helper_logic(self) -> Optional[Any]:
        """
        Logique pour un helper avec timeout et abandon automatique.
        """
        current_time = time.time()
        
        # Timeout d'attente comme helper
        wait_time = current_time - self.coordination_start_time
        if wait_time > CoordinationStrategy.MAX_WAIT_AS_HELPER:
            logger.warning(f"[CoordinateIncantationState] Timeout attente comme helper ({wait_time:.1f}s)")
            return self._handle_coordination_failure()

        # Vérifier si on a choisi un incanteur à aider
        if not self.coordination_mgr.chosen_incanter:
            logger.debug("[CoordinateIncantationState] 👂 En écoute des requêtes...")
            return None

        # Obtenir la direction vers l'incanteur choisi
        target_direction = self.coordination_mgr.get_chosen_incanter_direction()

        if target_direction is None:
            logger.warning("[CoordinateIncantationState] ❌ Direction incanteur perdue, reset")
            self.coordination_mgr.reset_helper_choice()
            return None

        # Si on est déjà sur la bonne case (direction 0)
        if target_direction == 0:
            logger.info("[CoordinateIncantationState] ✅ Arrivé chez l'incanteur, attente")
            return None

        # Se déplacer vers l'incanteur
        return self._move_towards_incanter(target_direction)

    def _move_towards_incanter(self, direction: int) -> Optional[Any]:
        """
        Se déplace vers l'incanteur selon la direction du broadcast.
        """
        if not self.movement_commands:
            self.movement_commands = self._plan_movement_to_incanter(direction)

        if self.movement_commands:
            next_cmd = self.movement_commands.pop(0)
            return self._execute_movement_command(next_cmd)

        return None

    def _plan_movement_to_incanter(self, direction: int) -> List[CommandType]:
        """
        Planifie le mouvement vers l'incanteur selon la direction du broadcast.
        Optimisé pour réduire le nombre de commandes.
        """
        # Mapping simplifié direction -> commandes
        direction_to_commands = {
            1: [CommandType.FORWARD],  # Devant
            2: [CommandType.RIGHT, CommandType.FORWARD],  # Droite-devant
            3: [CommandType.RIGHT, CommandType.FORWARD],  # Droite
            4: [CommandType.RIGHT, CommandType.RIGHT, CommandType.FORWARD],  # Droite-arrière
            5: [CommandType.RIGHT, CommandType.RIGHT, CommandType.FORWARD],  # Arrière
            6: [CommandType.LEFT, CommandType.LEFT, CommandType.FORWARD],  # Gauche-arrière
            7: [CommandType.LEFT, CommandType.FORWARD],  # Gauche
            8: [CommandType.LEFT, CommandType.FORWARD],  # Gauche-devant
        }
        
        return direction_to_commands.get(direction, [CommandType.FORWARD])

    def _execute_movement_command(self, command_type: CommandType) -> Optional[Any]:
        """Exécute une commande de mouvement."""
        command_map = {
            CommandType.FORWARD: self.cmd_mgr.forward,
            CommandType.LEFT: self.cmd_mgr.left,
            CommandType.RIGHT: self.cmd_mgr.right,
        }
        
        command_func = command_map.get(command_type)
        if command_func:
            return command_func()
        
        logger.warning(f"[CoordinateIncantationState] Commande inconnue: {command_type}")
        return None

    def _should_send_broadcast(self) -> bool:
        """Détermine si on doit envoyer une requête de broadcast."""
        if self.role != AgentRoles.INCANTER:
            return False

        current_time = time.time()
        
        # Cooldown entre les broadcasts
        if current_time - self.last_broadcast_time < CoordinationMessages.BROADCAST_COOLDOWN:
            return False

        # Ne pas dépasser le nombre maximum de tentatives
        if self.coordination_attempts >= self.max_coordination_attempts:
            return False

        return True

    def _needs_vision_update(self) -> bool:
        """Détermine si une mise à jour de vision est nécessaire."""
        return (
            not self.state.get_vision().last_vision_data or 
            self.context.get('needs_vision_update', False) or
            getattr(self.state, 'needs_look', False)
        )

    def _cleanup_old_data(self):
        """Nettoie les données de coordination obsolètes."""
        self.coordination_mgr.cleanup_old_data()

    def _is_coordination_timeout(self) -> bool:
        """Vérifie si la coordination a expiré."""
        return (time.time() - self.coordination_start_time > TimingConstants.COORDINATION_TIMEOUT)

    def _handle_coordination_failure(self) -> Optional[Any]:
        """
        Gère l'échec de coordination avec fallback approprié.
        """
        if self.fallback_triggered:
            return None
            
        self.fallback_triggered = True
        current_food = self.state.get_food_count()
        
        logger.warning(f"[CoordinateIncantationState] 🔄 Fallback coordination - Food: {current_food}")
        
        # Si pas assez de nourriture, collecter
        if current_food < CoordinationMessages.MIN_FOOD_TO_INITIATE:
            logger.info("[CoordinateIncantationState] → Fallback vers collecte nourriture")
            from ai.strategy.state.collect_food import CollectFoodState
            new_state = CollectFoodState(self.planner)
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()
        
        # Si des ressources manquent, les collecter
        if self.state.has_missing_resources():
            logger.info("[CoordinateIncantationState] → Fallback vers collecte ressources")
            from ai.strategy.state.collect_resources import CollectResourcesState
            new_state = CollectResourcesState(self.planner)
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()
        
        # Sinon, retourner en exploration
        logger.info("[CoordinateIncantationState] → Fallback vers exploration")
        from ai.strategy.state.explore import ExploreState
        new_state = ExploreState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _transition_to_incantation(self) -> Optional[Any]:
        """Transition vers l'état d'incantation."""
        logger.info("[CoordinateIncantationState] → Transition vers incantation")
        from ai.strategy.state.incantation import IncantationState
        new_state = IncantationState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes."""
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True

        if command_type == CommandType.BROADCAST:
            logger.debug("[CoordinateIncantationState] ✅ Broadcast envoyé")

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes."""
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.movement_commands.clear()
            self.context['needs_vision_update'] = True

        if command_type == CommandType.BROADCAST:
            logger.warning("[CoordinateIncantationState] ❌ Échec broadcast")

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements pendant la coordination."""
        if event == Event.FOOD_EMERGENCY:
            logger.error("[CoordinateIncantationState] URGENCE ALIMENTAIRE! Abandon coordination")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)

        elif event == Event.FOOD_LOW:
            current_food = self.state.get_food_count()
            if (self.role == AgentRoles.HELPER and 
                current_food < CoordinationMessages.MIN_FOOD_TO_HELP):
                logger.warning("[CoordinateIncantationState] Nourriture insuffisante, abandon aide")
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

        # Reset des compteurs
        self.coordination_start_time = time.time()
        self.last_broadcast_time = 0.0
        self.waiting_for_helpers = False
        self.target_incanter_direction = None
        self.movement_commands.clear()
        self.coordination_attempts = 0
        self.helpers_found_count = 0
        self.fallback_triggered = False
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état."""
        super().on_exit()
        duration = time.time() - self.coordination_start_time

        logger.info(f"[CoordinateIncantationState] ✅ SORTIE coordination - "
                   f"Rôle: {self.role}, Durée: {duration:.1f}s, "
                   f"Tentatives: {self.coordination_attempts}")

        # Nettoyage
        if self.role == AgentRoles.INCANTER:
            self.coordination_mgr.clear_helpers()
        else:
            self.coordination_mgr.reset_helper_choice()

        self.movement_commands.clear()