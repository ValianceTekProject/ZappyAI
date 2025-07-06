##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination_incantation - État de coordination avec protocole simplifié
##

import time
import random
from typing import Optional, Any, List, Dict
from ai.strategy.fsm import State, Event
from config import CommandType
from constant import (
    CoordinationProtocol, IncantationRequirements, AgentRoles, 
    BroadcastDirections, FoodThresholds, StateTransitionThresholds,
    SafetyLimits, MovementConstants
)
from teams.message import Message
from utils.logger import logger


class CoordinateIncantationState(State):
    """État de coordination avec protocole Zappy simplifié"""

    def __init__(self, planner):
        super().__init__(planner)
        
        self.coordination_mgr = planner.global_coordination_mgr
        self.role = self._determine_role()
        self.state.set_role(self.role)

        self.coordination_start_time = time.time()
        self.movement_commands = []
        
        self.last_broadcast_time = 0.0
        self.last_inventory_check = time.time()
        self.last_vision_check = time.time()
        self.received_direction = None
        
        logger.info(f"[CoordinateIncantationState] 🤝 Coordination - Rôle: {self.role}")

    def execute(self) -> Optional[Any]:
        """Logique de coordination avec protocole simplifié"""
        current_time = time.time()
        
        if not self._verify_safety_conditions():
            logger.warning("[CoordinateIncantationState] ⚠️ Conditions de sécurité perdues")
            return self._handle_coordination_failure()

        if current_time - self.coordination_start_time > SafetyLimits.MAX_COORDINATION_TIME:
            logger.warning(f"[CoordinateIncantationState] ⏰ Timeout coordination")
            return self._handle_coordination_failure()

        if self._should_check_inventory(current_time):
            self.last_inventory_check = current_time
            return self.cmd_mgr.inventory()

        if self._needs_vision_update(current_time):
            self.last_vision_check = current_time
            return self.cmd_mgr.look()

        if self.role == AgentRoles.INCANTER:
            return self._execute_incanter_logic()
        elif self.role == AgentRoles.HELPER:
            return self._execute_helper_logic()
        else:
            return self._handle_coordination_failure()

    def _execute_incanter_logic(self) -> Optional[Any]:
        """Logique pour l'incanteur - broadcast continu et vérifications locales"""
        current_time = time.time()

        players_on_tile = self._get_players_on_current_tile()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        here_count = self.coordination_mgr.get_helpers_here_count()
        
        logger.debug(f"[CoordinateIncantationState] 📊 Physiques={players_on_tile}/{required_players}, HERE={here_count}")

        if (players_on_tile >= required_players and 
            here_count >= required_players - 1):
            logger.info(f"[CoordinateIncantationState] ✅ CONDITIONS REMPLIES!")
            return self._launch_coordinated_incantation()

        if self._should_send_broadcast():
            self._send_incantation_broadcast()

        if self._should_abandon_coordination():
            abandon_reason = self._get_abandon_reason()
            logger.warning(f"[CoordinateIncantationState] Abandon: {abandon_reason}")
            return self._handle_coordination_failure()

        return None

    def _execute_helper_logic(self) -> Optional[Any]:
        """Logique pour les helpers - écoute et mouvement vers l'incanteur"""
        current_time = time.time()
        
        if current_time - self.coordination_start_time > SafetyLimits.MAX_HELPER_WAIT_TIME:
            logger.warning("[CoordinateIncantationState] Timeout helper")
            return self._handle_coordination_failure()

        if self.received_direction is None:
            logger.debug("[CoordinateIncantationState] 👂 En écoute des requêtes...")
            return None

        if self.received_direction == BroadcastDirections.HERE:
            logger.info("[CoordinateIncantationState] ✅ DÉJÀ SUR CASE INCANTEUR (K=0)")
            return None

        return self._move_towards_incanter()

    def _move_towards_incanter(self) -> Optional[Any]:
        """Déplace le helper vers l'incanteur selon la direction reçue"""
        if not self.movement_commands:
            self.movement_commands = self._plan_movement_to_incanter(self.received_direction)
            
        if self.movement_commands:
            next_cmd = self.movement_commands.pop(0)
            return self._execute_movement_command(next_cmd)
            
        return None

    def _plan_movement_to_incanter(self, direction: int) -> List[str]:
        """Planifie le mouvement selon le protocole Zappy"""
        if direction == BroadcastDirections.HERE:
            return []
        
        commands = MovementConstants.DIRECTION_TO_COMMANDS.get(direction, [])
        limited_commands = commands[:MovementConstants.MAX_MOVEMENT_COMMANDS]
        
        logger.info(f"[CoordinateIncantationState] 🧭 Direction {direction} → {limited_commands}")
        return limited_commands

    def _execute_movement_command(self, command_name: str) -> Optional[Any]:
        """Exécute une commande de mouvement spécifique"""
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

    def _get_players_on_current_tile(self) -> int:
        """Compte le nombre de joueurs physiques sur la tuile actuelle"""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return 1
            
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return data.players
                
        return 1

    def _launch_coordinated_incantation(self) -> Optional[Any]:
        """Lance l'incantation avec vérifications finales"""
        players_on_tile = self._get_players_on_current_tile()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        here_count = self.coordination_mgr.get_helpers_here_count()
        
        logger.info(f"[CoordinateIncantationState] 🔮✨ LANCEMENT INCANTATION COORDONNÉE!")
        logger.info(f"[CoordinateIncantationState] 👥 Validation finale: "
                   f"Physiques={players_on_tile}/{required_players}, "
                   f"HERE={here_count}/{required_players - 1}")
        
        if players_on_tile >= required_players and here_count >= required_players - 1:
            logger.info(f"[CoordinateIncantationState] ✅ TOUTES CONDITIONS OK - GO!")
            return self.cmd_mgr.incantation()
        else:
            logger.error(f"[CoordinateIncantationState] ❌ CONDITIONS PERDUES AU LANCEMENT")
            return None

    def _send_incantation_broadcast(self):
        """Envoie un broadcast d'incantation continu"""
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

            logger.debug(f"[CoordinateIncantationState] 📢 Broadcast niveau {level}")
            
        except Exception as e:
            logger.error(f"[CoordinateIncantationState] Erreur broadcast: {e}")

    def _should_send_broadcast(self) -> bool:
        """Détermine si on doit envoyer un broadcast"""
        if self.role != AgentRoles.INCANTER:
            return False

        current_time = time.time()
        return current_time - self.last_broadcast_time >= CoordinationProtocol.INCANTER_BROADCAST_COOLDOWN

    def _should_abandon_coordination(self) -> bool:
        """Vérification d'abandon avec seuils stricts"""
        current_food = self.state.get_food_count()
        duration = time.time() - self.coordination_start_time
        
        if current_food <= SafetyLimits.ABANDON_COORDINATION_THRESHOLD:
            return True
            
        if duration > SafetyLimits.MAX_COORDINATION_TIME:
            return True
            
        return False

    def _get_abandon_reason(self) -> str:
        """Retourne la raison d'abandon détaillée"""
        current_food = self.state.get_food_count()
        duration = time.time() - self.coordination_start_time
        
        if current_food <= SafetyLimits.ABANDON_COORDINATION_THRESHOLD:
            return f"Nourriture critique ({current_food})"
        elif duration > SafetyLimits.MAX_COORDINATION_TIME:
            return f"Timeout ({duration:.1f}s)"
        else:
            return "Conditions non remplies"

    def _should_check_inventory(self, current_time: float) -> bool:
        """Détermine si un check d'inventaire est nécessaire"""
        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= 4.0

    def _needs_vision_update(self, current_time: float) -> bool:
        """Détermine si une mise à jour de vision est nécessaire"""
        if (not self.state.get_vision().last_vision_data or 
            self.context.get('needs_vision_update', False) or
            getattr(self.state, 'needs_look', False)):
            return True
        
        time_since_last = current_time - self.last_vision_check
        return time_since_last >= 3.0

    def _verify_safety_conditions(self) -> bool:
        """Vérification des conditions de sécurité"""
        current_food = self.state.get_food_count()
        
        if current_food <= FoodThresholds.CRITICAL:
            return False
            
        if (self.role == AgentRoles.HELPER and 
            current_food <= SafetyLimits.MIN_FOOD_FOR_COORDINATION_SAFETY):
            return False
            
        return True

    def _handle_coordination_failure(self) -> Optional[Any]:
        """Gère l'échec de coordination avec transitions appropriées"""
        current_food = self.state.get_food_count()
        
        logger.warning(f"[CoordinateIncantationState] 🔄 Échec coordination - Food: {current_food}")
        
        self._clear_coordination_state()
        
        if current_food <= FoodThresholds.CRITICAL:
            from ai.strategy.state.emergency import EmergencyState
            new_state = EmergencyState(self.planner)
        elif current_food <= StateTransitionThresholds.ABANDON_COORDINATION_THRESHOLD:
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
        """Nettoie l'état de coordination"""
        self.state.set_role(AgentRoles.SURVIVOR)
        
        if hasattr(self.coordination_mgr, 'clear_coordination_data'):
            self.coordination_mgr.clear_coordination_data()

    def _determine_role(self) -> str:
        """Détermine le rôle avec logique équilibrée"""
        current_food = self.state.get_food_count()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)

        if self.state.level == 1:
            logger.error("[CoordinateIncantationState] ❌ Niveau 1 interdit en coordination")
            return AgentRoles.SURVIVOR

        if self.state.level >= 2 and required_players <= 1:
            logger.error(f"[CoordinateIncantationState] ❌ Niveau {self.state.level} nécessite coordination obligatoire")
            return AgentRoles.SURVIVOR

        if required_players <= 1:
            logger.error("[CoordinateIncantationState] ❌ Pas de coordination nécessaire")
            return AgentRoles.SURVIVOR

        if current_food < SafetyLimits.MIN_FOOD_FOR_COORDINATION_SAFETY:
            logger.warning(f"[CoordinateIncantationState] Nourriture insuffisante: {current_food}")
            return AgentRoles.SURVIVOR

        has_all_resources = not self.state.has_missing_resources()
        has_enough_food = current_food >= CoordinationProtocol.MIN_FOOD_TO_COORDINATE
        
        if has_all_resources and has_enough_food:
            incanter_probability = 0.25
        else:
            incanter_probability = 0.15

        chosen_role = AgentRoles.INCANTER if random.random() < incanter_probability else AgentRoles.HELPER
        
        logger.info(f"[CoordinateIncantationState] Rôle choisi: {chosen_role}")
        return chosen_role

    def handle_broadcast_message(self, sender_id: int, data: Dict[str, Any], direction: int):
        """Traite les messages de broadcast reçus (pour les helpers)"""
        if self.role != AgentRoles.HELPER:
            return
            
        try:
            if sender_id == self.state.agent_id:
                return
                
            level = data.get("level")
            if level != self.state.level:
                return
                
            self.received_direction = direction
            logger.debug(f"[CoordinateIncantationState] Direction reçue: K={direction}")
            
            if direction == BroadcastDirections.HERE:
                self._send_here_confirmation(sender_id, level)
                
        except Exception as e:
            logger.error(f"[CoordinateIncantationState] Erreur traitement broadcast: {e}")

    def _handle_incantation_request(self, sender_id: int, data: Dict[str, Any], direction: int):
        """Traite une requête d'incantation reçue (pour les helpers)"""
        if self.role != AgentRoles.HELPER:
            return
            
        try:
            if sender_id == self.state.agent_id:
                return
                
            level = data.get("level")
            if level != self.state.level:
                return
                
            current_food = self.state.get_food_count()
            if current_food < SafetyLimits.MIN_FOOD_FOR_COORDINATION_SAFETY:
                return
                
            self.received_direction = direction
            logger.debug(f"[CoordinateIncantationState] Requête incantation reçue, direction: K={direction}")
            
            if direction == BroadcastDirections.HERE:
                self._send_here_confirmation(sender_id, level)
                
        except Exception as e:
            logger.error(f"[CoordinateIncantationState] Erreur traitement requête: {e}")

    def _send_here_confirmation(self, incanter_id: int, level: int):
        """Envoie une confirmation 'here' si sur la même case"""
        try:
            encoded_message = Message.create_incantation_response(
                sender_id=self.state.agent_id,
                team_id=self.state.team_id,
                request_sender=incanter_id,
                response=CoordinationProtocol.RESPONSE_HERE,
                level=level
            )
            
            self.cmd_mgr.broadcast(encoded_message)
            logger.info(f"[CoordinateIncantationState] 📍 HERE confirmé à {incanter_id}")
            
        except Exception as e:
            logger.error(f"[CoordinateIncantationState] Erreur envoi HERE: {e}")

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes"""
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True

        if command_type == CommandType.INCANTATION:
            logger.info("[CoordinateIncantationState] 🎉 INCANTATION COORDONNÉE RÉUSSIE!")
            self._clear_coordination_state()

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes"""
        if command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.context['needs_vision_update'] = True

        if command_type == CommandType.INCANTATION:
            logger.error(f"[CoordinateIncantationState] 💥 INCANTATION ÉCHOUÉE: {response}")
            self._clear_coordination_state()

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements pendant la coordination"""
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
        """Actions à l'entrée de l'état"""
        super().on_enter()
        current_food = self.state.get_food_count()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)

        logger.info(f"[CoordinateIncantationState] 🤝 ENTRÉE coordination")
        logger.info(f"[CoordinateIncantationState] Rôle: {self.role}, Niveau: {self.state.level}")
        logger.info(f"[CoordinateIncantationState] Food: {current_food}, Joueurs requis: {required_players}")

        self.coordination_start_time = time.time()
        self.movement_commands.clear()
        self.last_broadcast_time = 0.0
        self.received_direction = None
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état"""
        super().on_exit()
        duration = time.time() - self.coordination_start_time
        here_count = self.coordination_mgr.get_helpers_here_count()
        players_on_tile = self._get_players_on_current_tile()

        logger.info(f"[CoordinateIncantationState] ✅ SORTIE coordination")
        logger.info(f"[CoordinateIncantationState] Rôle: {self.role}, Durée: {duration:.1f}s")
        logger.info(f"[CoordinateIncantationState] HERE: {here_count}, Physiques: {players_on_tile}")

        self._clear_coordination_state()
        self.movement_commands.clear()