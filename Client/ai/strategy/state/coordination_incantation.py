##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination_incantation - État de coordination avec logique HERE/COMING corrigée
##

import time
import random
from typing import Optional, Any, List
from ai.strategy.fsm import State, Event
from config import CommandType
from constant import (
    CoordinationProtocol, IncantationRequirements, AgentRoles, 
    BroadcastDirections, FoodThresholds, StateTransitionThresholds,
    SafetyLimits, MovementConstants, CoordinationHelperSettings
)
from teams.message import Message, MessageType
from utils.logger import logger


class CoordinateIncantationState(State):
    """État de coordination avec logique HERE/COMING strictement conforme au protocole Zappy."""

    def __init__(self, planner):
        super().__init__(planner)
        
        self.coordination_mgr = planner.global_coordination_mgr
        self.role = self._determine_role_optimized()
        self.state.set_role(self.role)

        self.coordination_start_time = time.time()
        self.movement_commands = []
        
        self.coordination_attempts = 0
        self.fallback_triggered = False
        self.last_broadcast_time = 0.0
        self.helpers_needed = self._calculate_helpers_needed()
        self.last_inventory_check = time.time()
        
        # Variables pour le mouvement CORRIGÉES
        self.target_direction = None
        self.movement_completed = False
        self.last_movement_time = time.time()
        self.movement_attempts = 0
        self.max_movement_attempts = CoordinationHelperSettings.MOVEMENT_RETRY_COUNT
        self.here_confirmation_sent = False
        
        # État strict selon protocole
        self.is_on_incanter_tile = False
        self.last_physical_check = time.time()
        self.physical_check_interval = 1.5  # CORRIGÉ: Moins fréquent
        
        logger.info(f"[CoordinateIncantationState] 🤝 Coordination - Rôle: {self.role}, "
                   f"Niveau: {self.state.level}, Helpers requis: {self.helpers_needed}")

    def execute(self) -> Optional[Any]:
        """Logique de coordination avec protocole Zappy strict."""
        current_time = time.time()
        
        # Vérifications de survie critiques
        if not self._verify_safety_conditions():
            logger.warning("[CoordinateIncantationState] ⚠️ Conditions de sécurité perdues")
            return self._handle_coordination_failure()

        # Timeout global
        if current_time - self.coordination_start_time > SafetyLimits.MAX_COORDINATION_TIME:
            logger.warning(f"[CoordinateIncantationState] ⏰ Timeout coordination")
            return self._handle_coordination_failure()

        # Check d'inventaire périodique
        if self._should_check_inventory(current_time):
            self.last_inventory_check = current_time
            return self.cmd_mgr.inventory()

        # Mise à jour vision si nécessaire
        if self._needs_vision_update():
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()

        # Logique selon le rôle
        if self.role == AgentRoles.INCANTER:
            return self._execute_incanter_logic()
        elif self.role == AgentRoles.HELPER:
            return self._execute_helper_logic()
        else:
            return self._handle_coordination_failure()

    def _execute_incanter_logic(self) -> Optional[Any]:
        """Logique STRICTE pour l'incanteur - reste sur place et broadcast."""
        current_time = time.time()

        # L'incanteur reste TOUJOURS sur place
        logger.debug("[CoordinateIncantationState] 🔒 Incanteur en position fixe")

        # Vérification physique stricte
        players_on_tile = self._get_players_on_current_tile()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        here_count = self.coordination_mgr.get_helpers_here_count()
        
        logger.debug(f"[CoordinateIncantationState] 📊 Validation: "
                    f"Physiques={players_on_tile}/{required_players}, "
                    f"HERE={here_count}/{self.helpers_needed}")

        # CRITIQUE: Lancement uniquement si conditions remplies
        if (players_on_tile >= required_players and 
            here_count >= self.helpers_needed):
            logger.info(f"[CoordinateIncantationState] ✅ CONDITIONS REMPLIES!")
            logger.info(f"[CoordinateIncantationState] 🚀 LANCEMENT INCANTATION")
            return self._launch_coordinated_incantation()

        # Broadcast pour attirer les helpers avec fréquence adaptée
        if self._should_send_broadcast():
            self._send_incantation_broadcast()
            self.coordination_attempts += 1

        # Vérifier abandon avec seuils stricts
        if self._should_abandon_coordination():
            abandon_reason = self._get_abandon_reason()
            logger.warning(f"[CoordinateIncantationState] Abandon: {abandon_reason}")
            return self._handle_coordination_failure()

        return None

    def _execute_helper_logic(self) -> Optional[Any]:
        """Logique STRICTE pour les helpers selon protocole Zappy."""
        current_time = time.time()
        
        # Timeout helper
        if current_time - self.coordination_start_time > SafetyLimits.MAX_HELPER_WAIT_TIME:
            logger.warning("[CoordinateIncantationState] Timeout helper")
            return self._handle_coordination_failure()

        # Obtenir la direction vers l'incanteur
        if self.target_direction is None:
            self.target_direction = self.coordination_mgr.get_chosen_incanter_direction()
            if self.target_direction is not None:
                logger.debug(f"[CoordinateIncantationState] Direction reçue: K={self.target_direction}")
        
        if self.target_direction is None:
            logger.debug("[CoordinateIncantationState] 👂 En écoute des requêtes...")
            return None

        # PROTOCOLE ZAPPY STRICT: Direction 0 = déjà sur la case
        if self.target_direction == BroadcastDirections.HERE:
            if not self.here_confirmation_sent:
                self.is_on_incanter_tile = True
                self.movement_completed = True
                self.here_confirmation_sent = True
                logger.info("[CoordinateIncantationState] ✅ DÉJÀ SUR CASE INCANTEUR (K=0)")
                self._send_here_confirmation()
            return None

        # Direction != 0: Mouvement requis
        if not self.movement_completed:
            return self._move_towards_incanter()

        return None

    def _validate_helper_arrival(self) -> bool:
        """Valide que le helper est arrivé sur la case de l'incanteur."""
        time_since_movement = time.time() - self.last_movement_time
        if time_since_movement < CoordinationHelperSettings.MOVEMENT_SUCCESS_WAIT:
            return False
            
        return self.movement_completed

    def _get_players_on_current_tile(self) -> int:
        """Compte STRICTEMENT le nombre de joueurs physiques sur la tuile."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            logger.debug("[CoordinateIncantationState] ❌ Pas de données vision")
            return 1
            
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                player_count = data.players
                logger.debug(f"[CoordinateIncantationState] 👥 Joueurs physiques: {player_count}")
                return player_count
                
        return 1

    def _move_towards_incanter(self) -> Optional[Any]:
        """Mouvement vers l'incanteur avec logique simplifiée."""
        current_time = time.time()
        
        # Planifier mouvement si nécessaire
        if not self.movement_commands and self.movement_attempts < self.max_movement_attempts:
            self.movement_commands = self._plan_movement_to_incanter(self.target_direction)
            self.movement_attempts += 1
            
            if not self.movement_commands:
                self.movement_completed = True
                logger.info("[CoordinateIncantationState] ✅ Pas de mouvement requis")
                return None
            
            logger.info(f"[CoordinateIncantationState] 🎯 Mouvement planifié (#{self.movement_attempts}): {self.movement_commands}")

        # Exécuter commandes de mouvement
        if self.movement_commands:
            next_cmd = self.movement_commands.pop(0)
            
            # Timeout de mouvement
            if current_time - self.last_movement_time > MovementConstants.MOVEMENT_TIMEOUT:
                logger.warning("[CoordinateIncantationState] ⏰ Timeout mouvement")
                if self.movement_attempts < self.max_movement_attempts:
                    logger.info("[CoordinateIncantationState] 🔄 Retry mouvement")
                    self.movement_commands.clear()
                    return None
                else:
                    self.movement_completed = True
                    logger.warning("[CoordinateIncantationState] ❌ Abandon mouvement")
                    return None
                
            self.last_movement_time = current_time
            return self._execute_movement_command(next_cmd)
        else:
            self.movement_completed = True
            logger.info("[CoordinateIncantationState] ✅ Mouvement terminé")
            return None

    def _plan_movement_to_incanter(self, direction: int) -> List[str]:
        """Planifie le mouvement selon le protocole Zappy (page 7)."""
        if direction == BroadcastDirections.HERE:
            return []
        
        # Utiliser le mapping optimisé des constantes
        commands = MovementConstants.DIRECTION_TO_COMMANDS.get(direction, [])
        limited_commands = commands[:MovementConstants.MAX_MOVEMENT_COMMANDS]
        
        logger.info(f"[CoordinateIncantationState] 🧭 Direction {direction} → {limited_commands}")
        return limited_commands

    def _execute_movement_command(self, command_name: str) -> Optional[Any]:
        """Exécute une commande de mouvement."""
        command_map = {
            "Forward": self.cmd_mgr.forward,
            "Left": self.cmd_mgr.left,
            "Right": self.cmd_mgr.right,
        }
        
        command_func = command_map.get(command_name)
        if command_func:
            logger.debug(f"[CoordinateIncantationState] ▶️ {command_name}")
            return command_func()
        else:
            logger.error(f"[CoordinateIncantationState] ❌ Commande inconnue: {command_name}")
            return None

    def _send_here_confirmation(self):
        """Envoie une confirmation 'here' stricte."""
        try:
            chosen_incanter = self.coordination_mgr.chosen_incanter_id
            if chosen_incanter:
                encoded_message = Message.create_incantation_response(
                    sender_id=self.state.agent_id,
                    team_id=self.state.team_id,
                    request_sender=int(chosen_incanter),
                    response=CoordinationProtocol.RESPONSE_HERE,
                    level=self.state.level
                )
                self.cmd_mgr.broadcast(encoded_message)
                logger.info(f"[CoordinateIncantationState] 📤 HERE confirmé → {chosen_incanter}")
            else:
                logger.warning("[CoordinateIncantationState] ❌ Pas d'incanteur pour HERE")
        except Exception as e:
            logger.error(f"[CoordinateIncantationState] Erreur envoi HERE: {e}")

    def _launch_coordinated_incantation(self) -> Optional[Any]:
        """Lance l'incantation avec vérifications finales STRICTES."""
        players_on_tile = self._get_players_on_current_tile()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        here_count = self.coordination_mgr.get_helpers_here_count()
        
        logger.info(f"[CoordinateIncantationState] 🔮✨ LANCEMENT INCANTATION COORDONNÉE!")
        logger.info(f"[CoordinateIncantationState] 👥 Validation finale: "
                   f"Physiques={players_on_tile}/{required_players}, "
                   f"HERE={here_count}/{self.helpers_needed}")
        
        # Vérification finale STRICTE
        if players_on_tile >= required_players and here_count >= self.helpers_needed:
            logger.info(f"[CoordinateIncantationState] ✅ TOUTES CONDITIONS OK - GO!")
            return self.cmd_mgr.incantation()
        else:
            logger.error(f"[CoordinateIncantationState] ❌ CONDITIONS PERDUES AU LANCEMENT")
            return None

    def _send_incantation_broadcast(self):
        """Envoie un broadcast d'incantation."""
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

            logger.info(f"[CoordinateIncantationState] 📢 Broadcast niveau {level} (#{self.coordination_attempts})")
            
        except Exception as e:
            logger.error(f"[CoordinateIncantationState] Erreur broadcast: {e}")

    def _should_send_broadcast(self) -> bool:
        """Détermine si on doit envoyer un broadcast - CORRIGÉ."""
        if self.role != AgentRoles.INCANTER:
            return False

        current_time = time.time()
        
        # Fréquence adaptée selon le nombre de helpers
        here_count = self.coordination_mgr.get_helpers_here_count()
        coming_count = self.coordination_mgr.get_helpers_coming_count()
        
        if here_count >= self.helpers_needed:
            return False  # Pas besoin de plus de helpers
        
        # Broadcast plus fréquent si des helpers sont en route
        if coming_count > 0:
            broadcast_cooldown = CoordinationProtocol.BROADCAST_COOLDOWN * 0.8  # Plus fréquent
        else:
            broadcast_cooldown = CoordinationProtocol.BROADCAST_COOLDOWN
        
        return current_time - self.last_broadcast_time >= broadcast_cooldown

    def _should_abandon_coordination(self) -> bool:
        """Vérification d'abandon avec seuils stricts."""
        current_food = self.state.get_food_count()
        duration = time.time() - self.coordination_start_time
        
        # Abandon immédiat si nourriture critique
        if current_food <= SafetyLimits.ABANDON_COORDINATION_THRESHOLD:
            return True
            
        # Timeout global
        if duration > SafetyLimits.MAX_COORDINATION_TIME:
            return True
            
        # Conditions spécifiques par rôle
        if self.role == AgentRoles.INCANTER:
            max_attempts = CoordinationProtocol.MAX_COORDINATION_ATTEMPTS
            min_time = 15.0  # CORRIGÉ: Moins de temps d'attente
            
            if (self.coordination_attempts >= max_attempts and 
                self.coordination_mgr.get_helpers_here_count() == 0 and 
                duration > min_time):
                return True
        
        elif self.role == AgentRoles.HELPER:
            if (self.movement_attempts >= self.max_movement_attempts and 
                not self.movement_completed and 
                duration > 12.0):  # CORRIGÉ: Moins de temps d'attente
                return True
                
        return False

    def _get_abandon_reason(self) -> str:
        """Raison d'abandon détaillée."""
        current_food = self.state.get_food_count()
        duration = time.time() - self.coordination_start_time
        here_count = self.coordination_mgr.get_helpers_here_count()
        
        if current_food <= SafetyLimits.ABANDON_COORDINATION_THRESHOLD:
            return f"Nourriture critique ({current_food})"
        elif duration > SafetyLimits.MAX_COORDINATION_TIME:
            return f"Timeout ({duration:.1f}s)"
        elif self.role == AgentRoles.INCANTER and here_count == 0:
            return f"Aucun HERE après {self.coordination_attempts} tentatives"
        elif self.role == AgentRoles.HELPER and self.movement_attempts >= self.max_movement_attempts:
            return f"Échec mouvement ({self.movement_attempts} tentatives)"
        else:
            return "Conditions non remplies"

    def _should_check_inventory(self, current_time: float) -> bool:
        """Check d'inventaire périodique."""
        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= 4.0  # CORRIGÉ: Plus fréquent

    def _verify_safety_conditions(self) -> bool:
        """Vérification des conditions de sécurité."""
        current_food = self.state.get_food_count()
        
        if current_food <= FoodThresholds.CRITICAL:
            return False
            
        if (self.role == AgentRoles.HELPER and 
            current_food <= SafetyLimits.MIN_FOOD_FOR_COORDINATION_SAFETY):
            return False
            
        return True

    def _needs_vision_update(self) -> bool:
        """Détermine si vision doit être mise à jour."""
        return (
            not self.state.get_vision().last_vision_data or 
            self.context.get('needs_vision_update', False) or
            getattr(self.state, 'needs_look', False)
        )

    def _handle_coordination_failure(self) -> Optional[Any]:
        """Gère l'échec de coordination."""
        if self.fallback_triggered:
            return None
            
        self.fallback_triggered = True
        current_food = self.state.get_food_count()
        
        logger.warning(f"[CoordinateIncantationState] 🔄 Échec coordination - Food: {current_food}")
        
        self._clear_coordination_state()
        
        # Transitions selon priorité CORRIGÉES
        if current_food <= FoodThresholds.CRITICAL:
            from ai.strategy.state.emergency import EmergencyState
            new_state = EmergencyState(self.planner)
        elif current_food <= StateTransitionThresholds.COORDINATION_ABANDON_THRESHOLD:
            from ai.strategy.state.collect_food import CollectFoodState
            new_state = CollectFoodState(self.planner)
        elif self.state.has_missing_resources():
            from ai.strategy.state.collect_resources import CollectResourcesState
            new_state = CollectResourcesState(self.planner)
        else:
            from ai.strategy.state.explore import ExploreState
            new_state = ExploreState(self.planner)
        
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _clear_coordination_state(self):
        """Nettoie l'état de coordination."""
        self.state.set_role(AgentRoles.SURVIVOR)
        
        if hasattr(self.coordination_mgr, 'clear_coordination_data'):
            self.coordination_mgr.clear_coordination_data()
            
        self.coordination_attempts = 0
        self.movement_completed = False
        self.target_direction = None
        self.here_confirmation_sent = False
        self.movement_attempts = 0
        self.is_on_incanter_tile = False

    def _determine_role_optimized(self) -> str:
        """Détermine le rôle avec logique équilibrée CORRIGÉE."""
        current_food = self.state.get_food_count()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)

        # Vérifications de base
        if self.state.level == 1:
            logger.error("[CoordinateIncantationState] ❌ Niveau 1 interdit en coordination")
            return AgentRoles.SURVIVOR

        if required_players <= 1:
            logger.error("[CoordinateIncantationState] ❌ Pas de coordination nécessaire")
            return AgentRoles.SURVIVOR

        if current_food <= SafetyLimits.MIN_FOOD_FOR_COORDINATION_SAFETY:
            logger.warning(f"[CoordinateIncantationState] Nourriture insuffisante: {current_food}")
            return AgentRoles.SURVIVOR

        # Distribution équilibrée des rôles CORRIGÉE
        has_all_resources = not self.state.has_missing_resources()
        has_enough_food = current_food >= CoordinationProtocol.MIN_FOOD_TO_INITIATE
        
        if has_all_resources and has_enough_food:
            incanter_probability = CoordinationHelperSettings.INCANTER_PROBABILITY_BASE
        else:
            incanter_probability = 0.3

        chosen_role = AgentRoles.INCANTER if random.random() < incanter_probability else AgentRoles.HELPER
        
        logger.info(f"[CoordinateIncantationState] Rôle: {chosen_role}")
        return chosen_role

    def _calculate_helpers_needed(self) -> int:
        """Calcule le nombre d'helpers nécessaires."""
        total_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        return max(0, total_players - 1)

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes."""
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True
            if self.role == AgentRoles.HELPER:
                logger.debug(f"[CoordinateIncantationState] ✅ Mouvement: {command_type}")
                self.last_movement_time = time.time()

        if command_type == CommandType.INCANTATION:
            logger.info("[CoordinateIncantationState] 🎉 INCANTATION COORDONNÉE RÉUSSIE!")
            self._clear_coordination_state()

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes."""
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            if self.role == AgentRoles.HELPER:
                logger.warning(f"[CoordinateIncantationState] ❌ Mouvement échoué: {command_type}")
                if self.movement_attempts < self.max_movement_attempts:
                    logger.info("[CoordinateIncantationState] 🔄 Retry mouvement")
                else:
                    self.movement_completed = True
                    if not self.here_confirmation_sent:
                        self.here_confirmation_sent = True
                        self._send_here_confirmation()
            self.context['needs_vision_update'] = True

        if command_type == CommandType.INCANTATION:
            logger.error(f"[CoordinateIncantationState] 💥 INCANTATION ÉCHOUÉE: {response}")
            self._clear_coordination_state()

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements."""
        if event == Event.FOOD_EMERGENCY:
            logger.error("[CoordinateIncantationState] URGENCE ALIMENTAIRE!")
            self._clear_coordination_state()
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)

        elif event == Event.FOOD_LOW:
            current_food = self.state.get_food_count()
            if current_food < SafetyLimits.MIN_FOOD_FOR_COORDINATION_SAFETY:
                logger.warning(f"[CoordinateIncantationState] Nourriture faible: {current_food}")
                self._clear_coordination_state()
                from ai.strategy.state.collect_food import CollectFoodState
                return CollectFoodState(self.planner)

        return None

    def on_enter(self):
        """Actions à l'entrée."""
        super().on_enter()
        current_food = self.state.get_food_count()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)

        logger.info(f"[CoordinateIncantationState] 🤝 ENTRÉE coordination")
        logger.info(f"[CoordinateIncantationState] Rôle: {self.role}, Niveau: {self.state.level}")
        logger.info(f"[CoordinateIncantationState] Food: {current_food}, Joueurs requis: {required_players}")

        # Reset complet
        self.coordination_start_time = time.time()
        self.movement_commands.clear()
        self.coordination_attempts = 0
        self.fallback_triggered = False
        self.last_broadcast_time = 0.0
        self.movement_completed = False
        self.target_direction = None
        self.last_movement_time = time.time()
        self.movement_attempts = 0
        self.here_confirmation_sent = False
        self.is_on_incanter_tile = False
        self.last_physical_check = time.time()
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie."""
        super().on_exit()
        duration = time.time() - self.coordination_start_time
        here_count = self.coordination_mgr.get_helpers_here_count()
        players_on_tile = self._get_players_on_current_tile()

        logger.info(f"[CoordinateIncantationState] ✅ SORTIE coordination")
        logger.info(f"[CoordinateIncantationState] Rôle: {self.role}, Durée: {duration:.1f}s")
        logger.info(f"[CoordinateIncantationState] HERE: {here_count}, Physiques: {players_on_tile}")

        self._clear_coordination_state()
        self.movement_commands.clear()