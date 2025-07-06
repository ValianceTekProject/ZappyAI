##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination_incantation - État de coordination avec gestion d'abandon corrigée
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
    SafetyLimits
)
from teams.message import Message, MessageType
from utils.logger import logger


class CoordinateIncantationState(State):
    """État de coordination pour incantations multi-joueurs avec gestion d'abandon corrigée."""

    def __init__(self, planner):
        """
        Initialise l'état de coordination.
        
        Args:
            planner: Planificateur FSM
        """
        super().__init__(planner)
        
        # Utilisation du CoordinationManager GLOBAL du FSMPlanner
        self.coordination_mgr = planner.global_coordination_mgr

        self.role = self._determine_role()
        self.state.set_role(self.role)

        self.coordination_start_time = time.time()
        self.movement_commands = []
        self.pathfinder = Pathfinder()
        
        self.coordination_attempts = 0
        self.fallback_triggered = False
        self.last_broadcast_time = 0.0
        self.helpers_needed = self._calculate_helpers_needed()
        self.last_safety_check = time.time()
        self.last_inventory_check = time.time()
        self.broadcasts_without_response = 0
        self.last_helpers_count = 0
        self.food_threshold_violations = 0

        logger.info(f"[CoordinateIncantationState] 🤝 Coordination activée - Rôle: {self.role}, "
                   f"Niveau: {self.state.level}, Helpers requis: {self.helpers_needed}")

    def execute(self) -> Optional[Any]:
        """
        Logique de coordination avec priorisation de la survie et gestion d'inventaire.
        
        Returns:
            Commande à exécuter ou None
        """
        current_time = time.time()
        
        # PRIORITÉ 1: Vérification critique de survie
        if self._is_survival_critical():
            logger.error("[CoordinateIncantationState] 🚨 SURVIE CRITIQUE! Abandon coordination immédiat")
            return self._emergency_transition()

        # PRIORITÉ 2: Check d'inventaire périodique (NOUVEAU)
        if self._should_check_inventory(current_time):
            self.last_inventory_check = current_time
            return self.cmd_mgr.inventory()

        # PRIORITÉ 3: Vérifications de sécurité périodiques
        if current_time - self.last_safety_check >= 2.0:
            if not self._verify_safety_conditions():
                logger.warning("[CoordinateIncantationState] ⚠️ Conditions de sécurité perdues")
                return self._handle_coordination_failure()
            self.last_safety_check = current_time

        # PRIORITÉ 4: Timeout coordination (CORRIGÉ)
        if self._is_coordination_timeout():
            logger.warning("[CoordinateIncantationState] ⏰ Timeout coordination")
            return self._handle_coordination_failure()

        # Nettoyage des données anciennes
        self._cleanup_old_data()

        # Logique selon le rôle
        if self.role == AgentRoles.INCANTER:
            return self._execute_incanter_logic()
        elif self.role == AgentRoles.HELPER:
            return self._execute_helper_logic()

        return self._handle_coordination_failure()

    def _should_check_inventory(self, current_time: float) -> bool:
        """
        Détermine si un check d'inventaire est nécessaire pendant la coordination.
        
        Args:
            current_time: Temps actuel
            
        Returns:
            True si vérification nécessaire
        """
        # Check périodique toutes les 3 secondes pendant la coordination
        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= 3.0

    def _is_survival_critical(self) -> bool:
        """
        Vérification critique de survie immédiate.
        
        Returns:
            True si survie en danger immédiat
        """
        current_food = self.state.get_food_count()
        
        # Seuil critique strict
        if current_food <= FoodThresholds.CRITICAL:
            return True
            
        # Vérification pour helpers avec seuil plus strict
        if (self.role == AgentRoles.HELPER and 
            current_food <= SafetyLimits.ABANDON_COORDINATION_THRESHOLD):
            return True
            
        return False

    def _verify_safety_conditions(self) -> bool:
        """
        Vérification des conditions de sécurité pour continuer la coordination.
        
        Returns:
            True si conditions sûres
        """
        current_food = self.state.get_food_count()
        
        # CORRIGÉ: Vérification des seuils plus flexible
        if current_food <= SafetyLimits.ABANDON_COORDINATION_THRESHOLD:
            self.food_threshold_violations += 1
            logger.warning(f"[CoordinateIncantationState] Violation seuil nourriture: {current_food} <= {SafetyLimits.ABANDON_COORDINATION_THRESHOLD}")
            return self.food_threshold_violations < 3  # Tolérer quelques violations
        else:
            self.food_threshold_violations = 0  # Reset si nourriture OK
            
        if self.role == AgentRoles.INCANTER:
            has_resources = not self.state.has_missing_resources()
            return current_food >= SafetyLimits.MIN_FOOD_FOR_INCANTATION_SAFETY and has_resources
            
        elif self.role == AgentRoles.HELPER:
            return current_food >= SafetyLimits.MIN_FOOD_FOR_COORDINATION_SAFETY
            
        return False

    def _execute_incanter_logic(self) -> Optional[Any]:
        """
        Logique pour un incanteur avec gestion d'abandon corrigée.
        
        Returns:
            Commande à exécuter ou None
        """
        current_time = time.time()
        current_food = self.state.get_food_count()

        # Vérification vision si nécessaire
        if self._needs_vision_update():
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()

        # Envoi de broadcast avec limite d'attempts CORRIGÉE
        max_attempts = self._get_dynamic_max_attempts(current_food)
        if (self._should_send_broadcast() and 
            self.coordination_attempts < max_attempts):
            self._send_incantation_broadcast()
            self.coordination_attempts += 1
            logger.info(f"[CoordinateIncantationState] 📢 Requête envoyée (tentative {self.coordination_attempts}/{max_attempts})")

        # Vérification des helpers
        confirmed_helpers = self._count_confirmed_helpers()
        
        # Tracker les broadcasts sans réponse
        if confirmed_helpers == 0 and self.coordination_attempts > 0:
            self.broadcasts_without_response = self.coordination_attempts
        elif confirmed_helpers > self.last_helpers_count:
            self.broadcasts_without_response = 0
        self.last_helpers_count = confirmed_helpers
        
        if confirmed_helpers >= self.helpers_needed:
            logger.info(f"[CoordinateIncantationState] ✅ Assez d'helpers: {confirmed_helpers}/{self.helpers_needed}")
            return self._transition_to_incantation()

        # CORRIGÉ: Conditions d'abandon plus intelligentes
        coordination_duration = current_time - self.coordination_start_time
        
        # Abandon uniquement si vraiment nécessaire
        should_abandon = self._should_abandon_coordination(current_food, coordination_duration, confirmed_helpers)
        if should_abandon:
            abandon_reason = self._get_abandon_reason(current_food, coordination_duration, confirmed_helpers)
            logger.warning(f"[CoordinateIncantationState] Abandon coordination: {abandon_reason}")
            return self._handle_coordination_failure()

        return None

    def _get_dynamic_max_attempts(self, current_food: int) -> int:
        """
        Calcule le nombre maximum de tentatives selon la nourriture disponible.
        
        Args:
            current_food: Nourriture actuelle
            
        Returns:
            Nombre maximum de tentatives
        """
        if current_food >= FoodThresholds.ABUNDANT:
            return 5  # Plus de tentatives si beaucoup de nourriture
        elif current_food >= FoodThresholds.SUFFICIENT:
            return 4
        elif current_food >= FoodThresholds.COORDINATION_MIN:
            return 3
        else:
            return 2

    def _should_abandon_coordination(self, current_food: int, duration: float, confirmed_helpers: int) -> bool:
        """
        Détermine si on doit abandonner la coordination selon des critères stricts.
        
        Args:
            current_food: Nourriture actuelle
            duration: Durée de coordination
            confirmed_helpers: Nombre d'helpers confirmés
            
        Returns:
            True si abandon nécessaire
        """
        max_attempts = self._get_dynamic_max_attempts(current_food)
        
        # 1. Nourriture critique
        if current_food <= SafetyLimits.ABANDON_COORDINATION_THRESHOLD:
            return True
            
        # 2. Timeout absolu
        if duration > SafetyLimits.MAX_COORDINATION_TIME:
            return True
            
        # 3. Trop de tentatives ET aucune aide
        if (self.coordination_attempts >= max_attempts and 
            confirmed_helpers == 0 and 
            duration > 8.0):
            return True
            
        # 4. Broadcasts sans réponse ET temps écoulé
        if (self.broadcasts_without_response >= 3 and 
            duration > 10.0 and
            confirmed_helpers == 0):
            return True
            
        return False

    def _get_abandon_reason(self, current_food: int, duration: float, confirmed_helpers: int) -> str:
        """
        Retourne la raison de l'abandon pour debug.
        
        Args:
            current_food: Nourriture actuelle
            duration: Durée de coordination
            confirmed_helpers: Nombre d'helpers confirmés
            
        Returns:
            Raison de l'abandon
        """
        if current_food <= SafetyLimits.ABANDON_COORDINATION_THRESHOLD:
            return f"Nourriture critique ({current_food})"
        elif duration > SafetyLimits.MAX_COORDINATION_TIME:
            return f"Timeout ({duration:.1f}s)"
        elif confirmed_helpers == 0:
            return f"Aucune aide après {self.coordination_attempts} tentatives"
        else:
            return "Conditions non remplies"

    def _execute_helper_logic(self) -> Optional[Any]:
        """
        Logique pour un helper avec vérifications de survie strictes.
        
        Returns:
            Commande à exécuter ou None
        """
        current_time = time.time()
        
        # Timeout helper plus strict
        if current_time - self.coordination_start_time > SafetyLimits.MAX_HELPER_WAIT_TIME:
            logger.warning("[CoordinateIncantationState] Timeout helper (survie)")
            return self._handle_coordination_failure()

        target_direction = self.coordination_mgr.get_chosen_incanter_direction()
        
        if target_direction is None:
            logger.debug("[CoordinateIncantationState] 👂 En écoute des requêtes...")
            return None

        if target_direction == BroadcastDirections.HERE:
            logger.info("[CoordinateIncantationState] ✅ Sur la tuile de l'incanteur")
            return None

        return self._move_towards_incanter(target_direction)

    def _send_incantation_broadcast(self):
        """Envoie un broadcast de requête d'incantation."""
        try:
            level = self.state.level
            required_players = IncantationRequirements.REQUIRED_PLAYERS.get(level, 1)

            encoded_message = Message.create_incantation_request(
                sender_id=self.state.agent_id,
                team_id=self.state.team_id,
                level=level,
                required_players=required_players
            )

            self.cmd_mgr.broadcast(encoded_message)
            self.last_broadcast_time = time.time()

            logger.info(f"[CoordinateIncantationState] 📢 Broadcast envoyé pour niveau {level}")
            
        except Exception as e:
            logger.error(f"[CoordinateIncantationState] Erreur envoi broadcast: {e}")

    def _count_confirmed_helpers(self) -> int:
        """
        Compte les helpers confirmés présents.
        
        Returns:
            Nombre de helpers confirmés
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return 0

        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                current_players = data.players
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
        Planifie le mouvement selon les directions Zappy.
        
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
        
        if current_time - self.last_broadcast_time < CoordinationProtocol.BROADCAST_COOLDOWN:
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

    def _emergency_transition(self) -> Optional[Any]:
        """
        Transition d'urgence vers la survie.
        
        Returns:
            Transition vers état d'urgence
        """
        logger.error("[CoordinateIncantationState] 🚨 TRANSITION URGENCE IMMÉDIATE")
        self._clear_coordination_state()
        from ai.strategy.state.emergency import EmergencyState
        new_state = EmergencyState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _handle_coordination_failure(self) -> Optional[Any]:
        """
        Gère l'échec de coordination avec nettoyage complet.
        
        Returns:
            Transition vers nouvel état
        """
        if self.fallback_triggered:
            return None
            
        self.fallback_triggered = True
        current_food = self.state.get_food_count()
        
        logger.warning(f"[CoordinateIncantationState] 🔄 Fallback coordination - Food: {current_food}")
        
        # IMPORTANT: Nettoyer l'état de coordination
        self._clear_coordination_state()
        
        # Priorité absolue: survie
        if current_food <= FoodThresholds.CRITICAL:
            logger.info("[CoordinateIncantationState] → URGENCE ALIMENTAIRE")
            from ai.strategy.state.emergency import EmergencyState
            new_state = EmergencyState(self.planner)
        elif current_food <= StateTransitionThresholds.COORDINATION_ABANDON_THRESHOLD:
            logger.info("[CoordinateIncantationState] → COLLECTE NOURRITURE")
            from ai.strategy.state.collect_food import CollectFoodState
            new_state = CollectFoodState(self.planner)
        elif self.state.has_missing_resources():
            logger.info("[CoordinateIncantationState] → COLLECTE RESSOURCES")
            from ai.strategy.state.collect_resources import CollectResourcesState
            new_state = CollectResourcesState(self.planner)
        else:
            logger.info("[CoordinateIncantationState] → EXPLORATION")
            from ai.strategy.state.explore import ExploreState
            new_state = ExploreState(self.planner)
        
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _clear_coordination_state(self):
        """Nettoie complètement l'état de coordination."""
        # Reset du rôle à survivor
        self.state.set_role(AgentRoles.SURVIVOR)
        
        # Nettoyer le coordination manager
        if hasattr(self.coordination_mgr, 'clear_coordination_data'):
            self.coordination_mgr.clear_coordination_data()
            
        # Reset des variables locales
        self.coordination_attempts = 0
        self.broadcasts_without_response = 0
        self.last_helpers_count = 0
        self.food_threshold_violations = 0
        
        logger.debug("[CoordinateIncantationState] État de coordination nettoyé")

    def _transition_to_incantation(self) -> Optional[Any]:
        """
        Transition vers l'état d'incantation coordonnée.
        
        Returns:
            Exécution du nouvel état
        """
        logger.info("[CoordinateIncantationState] 🔮 Lancement incantation coordonnée")
        return self.cmd_mgr.incantation()

    def _determine_role(self) -> str:
        """
        Détermine le rôle selon les règles Zappy avec vérifications de sécurité.
        
        Returns:
            Rôle de l'agent (INCANTER ou HELPER)
        """
        current_food = self.state.get_food_count()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)

        # Vérification niveau
        if self.state.level == 1:
            logger.error("[CoordinateIncantationState] ❌ VIOLATION: Niveau 1 ne doit pas utiliser coordination")
            return AgentRoles.SURVIVOR

        if required_players <= 1:
            logger.error("[CoordinateIncantationState] ❌ VIOLATION: Pas de coordination nécessaire")
            return AgentRoles.SURVIVOR

        # Vérification survie
        if current_food <= SafetyLimits.MIN_FOOD_FOR_COORDINATION_SAFETY:
            logger.warning(f"[CoordinateIncantationState] Nourriture insuffisante pour coordination: {current_food}")
            return AgentRoles.SURVIVOR

        # Logique de sélection de rôle
        has_all_resources = not self.state.has_missing_resources()
        has_enough_food_for_incanter = current_food >= CoordinationProtocol.MIN_FOOD_TO_INITIATE
        
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
        return max(0, total_players - 1)

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
            self._clear_coordination_state()

        if command_type == CommandType.INVENTORY:
            logger.debug("[CoordinateIncantationState] ✅ Inventaire vérifié pendant coordination")

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
            self._clear_coordination_state()

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
            self._clear_coordination_state()
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)

        elif event == Event.FOOD_LOW:
            current_food = self.state.get_food_count()
            if current_food < SafetyLimits.MIN_FOOD_FOR_COORDINATION_SAFETY:
                logger.warning(f"[CoordinateIncantationState] Nourriture faible pour coordination: {current_food}")
                self._clear_coordination_state()
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

        if self.state.level == 1:
            logger.error("[CoordinateIncantationState] ❌ ERREUR: Niveau 1 ne doit pas utiliser coordination!")

        self.coordination_start_time = time.time()
        self.movement_commands.clear()
        self.coordination_attempts = 0
        self.fallback_triggered = False
        self.last_broadcast_time = 0.0
        self.last_safety_check = time.time()
        self.last_inventory_check = time.time()
        self.broadcasts_without_response = 0
        self.last_helpers_count = 0
        self.food_threshold_violations = 0
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état."""
        super().on_exit()
        duration = time.time() - self.coordination_start_time

        logger.info(f"[CoordinateIncantationState] ✅ SORTIE coordination - "
                   f"Rôle: {self.role}, Durée: {duration:.1f}s, "
                   f"Tentatives: {self.coordination_attempts}")

        # Nettoyage final
        self._clear_coordination_state()
        self.movement_commands.clear()