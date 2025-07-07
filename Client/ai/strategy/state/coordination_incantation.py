##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination_incantation - État de coordination avec logique corrigée
##

import time
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
    """État de coordination avec protocole Zappy corrigé pour éviter les changements d'état"""

    def __init__(self, planner):
        super().__init__(planner)
        
        self.coordination_mgr = planner.global_coordination_mgr
        self.role = self._determine_role()
        self.state.set_role(self.role)

        self.coordination_start_time = time.time()
        self.movement_commands = []
        
        self.last_inventory_check = time.time()
        self.last_vision_check = time.time()
        self.last_broadcast_time = 0.0
        
        # Variables pour helpers - COORDINATION DÉDIÉE
        self.received_direction = None
        self.is_moving_to_incanter = False
        self.completed_movement_sequences = 0
        self.last_movement_completion_time = 0.0
        
        # Variables pour éviter les boucles infinies
        self.vision_update_pending = False
        self.inventory_update_pending = False
        
        logger.info(f"[CoordinateIncantationState] 🤝 Coordination DÉDIÉE - Rôle: {self.role}")

    def execute(self) -> Optional[Any]:
        """Logique de coordination avec mode dédié pour helpers"""
        current_time = time.time()
        
        if not self._verify_safety_conditions():
            logger.warning("[CoordinateIncantationState] ⚠️ Conditions de sécurité perdues")
            return self._handle_coordination_failure()

        if current_time - self.coordination_start_time > SafetyLimits.MAX_COORDINATION_TIME:
            logger.warning(f"[CoordinateIncantationState] ⏰ Timeout coordination")
            return self._handle_coordination_failure()

        # Gestion prioritaire des mises à jour d'état (minimal)
        if self._should_check_inventory(current_time):
            return self._request_inventory_update()

        if self._needs_vision_update(current_time):
            return self._request_vision_update()

        # Logique spécifique selon le rôle
        if self.role == AgentRoles.INCANTER:
            return self._execute_incanter_logic(current_time)
        elif self.role == AgentRoles.HELPER:
            return self._execute_helper_logic_dedicated()
        else:
            logger.error(f"[CoordinateIncantationState] ❌ Rôle invalide: {self.role}")
            return self._handle_coordination_failure()

    def _execute_helper_logic_dedicated(self) -> Optional[Any]:
        """Logique DÉDIÉE pour les helpers - reste en coordination jusqu'au bout"""
        current_time = time.time()
        
        # Timeout seulement si pas de progression
        if current_time - self.coordination_start_time > SafetyLimits.MAX_HELPER_WAIT_TIME:
            if self.completed_movement_sequences == 0:
                logger.warning("[CoordinateIncantationState] Timeout helper sans progression")
                return self._handle_coordination_failure()

        # Vérifier si une nouvelle demande de coordination a été reçue
        if self.state.join_incantation:
            new_direction = self.state.direction_incant
            logger.info(f"[CoordinateIncantationState] 📨 Nouvelle direction reçue: K={new_direction}")
            
            # Si déjà sur la case de l'incanteur (K=0)
            if new_direction == BroadcastDirections.HERE:
                logger.info("[CoordinateIncantationState] ✅ SUR CASE INCANTEUR - envoi HERE")
                self._send_here_confirmation_to_incanter()
                self.state.reset_coordination_flags()
                return None
            
            # Si on n'était pas en train de bouger ou nouvelle direction différente
            if not self.is_moving_to_incanter or new_direction != self.received_direction:
                self.received_direction = new_direction
                self.is_moving_to_incanter = True
                self.movement_commands = self._plan_movement_to_incanter(new_direction)
                logger.info(f"[CoordinateIncantationState] 🎯 Nouveau mouvement planifié vers K={new_direction}: {self.movement_commands}")
            
            self.state.reset_coordination_flags()

        # Si on est en train de bouger, continuer la séquence
        if self.is_moving_to_incanter and self.movement_commands:
            next_cmd = self.movement_commands.pop(0)
            logger.info(f"[CoordinateIncantationState] ▶️ Mouvement: {next_cmd} (reste: {len(self.movement_commands)})")
            return self._execute_movement_command(next_cmd)
        
        # Si on a terminé une séquence de mouvement
        if self.is_moving_to_incanter and not self.movement_commands:
            self.is_moving_to_incanter = False
            self.completed_movement_sequences += 1
            self.last_movement_completion_time = current_time
            logger.info(f"[CoordinateIncantationState] ✅ Séquence mouvement terminée #{self.completed_movement_sequences}")
        
        # Sinon, attendre en mode coordination (pas de changement d'état)
        return None

    def _execute_incanter_logic(self, current_time: float) -> Optional[Any]:
        """Logique pour l'incanteur - broadcast continu et vérifications"""
        players_on_tile = self._get_players_on_current_tile()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        here_count = self.coordination_mgr.get_helpers_here_count()
        
        logger.debug(f"[CoordinateIncantationState] Physiques={players_on_tile}/{required_players}, HERE={here_count}")

        # Vérification si on peut lancer l'incantation
        if (players_on_tile >= required_players and 
            here_count >= required_players - 1):
            logger.info(f"[CoordinateIncantationState] ✅ CONDITIONS REMPLIES!")
            return self._launch_coordinated_incantation()

        # Broadcast obligatoire et régulier
        if self._should_broadcast(current_time):
            self._send_broadcast_request()
            self.last_broadcast_time = current_time

        # Vérification d'abandon
        if self._should_abandon_coordination():
            abandon_reason = self._get_abandon_reason()
            logger.warning(f"[CoordinateIncantationState] Abandon: {abandon_reason}")
            return self._handle_coordination_failure()

        return None

    def _send_here_confirmation_to_incanter(self):
        """Envoie une confirmation 'here' automatique quand on reçoit K=0"""
        try:
            # On ne connaît pas l'ID exact de l'incanteur, on utilise un ID générique
            encoded_message = Message.create_incantation_response(
                sender_id=self.state.agent_id,
                team_id=self.state.team_id,
                request_sender=0,  # ID générique
                response=CoordinationProtocol.RESPONSE_HERE,
                level=self.state.level
            )
            
            self.cmd_mgr.broadcast(encoded_message)
            logger.info(f"[CoordinateIncantationState] 📍 HERE envoyé automatiquement")
            
        except Exception as e:
            logger.error(f"[CoordinateIncantationState] Erreur envoi HERE automatique: {e}")

    def _should_broadcast(self, current_time: float) -> bool:
        """Détermine si l'incanteur doit broadcaster maintenant"""
        if self.last_broadcast_time == 0.0:
            return True
        
        time_since_last = current_time - self.last_broadcast_time
        return time_since_last >= CoordinationProtocol.INCANTER_BROADCAST_COOLDOWN

    def _send_broadcast_request(self):
        """Envoie une requête d'incantation via le gestionnaire de coordination"""
        try:
            self.coordination_mgr.send_incantation_request()
            logger.debug(f"[CoordinateIncantationState] 📢 Broadcast envoyé")
        except Exception as e:
            logger.error(f"[CoordinateIncantationState] Erreur broadcast: {e}")

    def _plan_movement_to_incanter(self, direction: int) -> List[str]:
        """Planifie le mouvement selon le protocole Zappy CORRIGÉ"""
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
            logger.info(f"[CoordinateIncantationState] ▶️ {command_name}")
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
        
        return self.cmd_mgr.incantation()

    def _should_check_inventory(self, current_time: float) -> bool:
        """Détermine si un check d'inventaire est nécessaire - RÉDUIT"""
        if self.inventory_update_pending:
            return False
            
        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= (CoordinationProtocol.INVENTORY_CHECK_INTERVAL * 2)  # Moins fréquent

    def _needs_vision_update(self, current_time: float) -> bool:
        """Détermine si une mise à jour de vision est nécessaire - RÉDUIT"""
        if self.vision_update_pending:
            return False
            
        # Seulement si vraiment nécessaire
        if (not self.state.get_vision().last_vision_data or 
            getattr(self.state, 'needs_look', False)):
            return True
        
        # Moins fréquent pendant coordination
        time_since_last = current_time - self.last_vision_check
        return time_since_last >= (CoordinationProtocol.VISION_CHECK_INTERVAL * 2)

    def _request_inventory_update(self) -> Optional[Any]:
        """Demande une mise à jour d'inventaire"""
        self.inventory_update_pending = True
        self.last_inventory_check = time.time()
        logger.debug("[CoordinateIncantationState] 📋 Check inventaire")
        return self.cmd_mgr.inventory()

    def _request_vision_update(self) -> Optional[Any]:
        """Demande une mise à jour de vision"""
        self.vision_update_pending = True
        self.last_vision_check = time.time()
        if hasattr(self.state, 'needs_look'):
            self.state.needs_look = False
        logger.debug("[CoordinateIncantationState] 👁️ Update vision")
        return self.cmd_mgr.look()

    def _should_abandon_coordination(self) -> bool:
        """Vérification d'abandon avec seuils CORRIGÉS"""
        current_food = self.state.get_food_count()
        duration = time.time() - self.coordination_start_time
        
        # Seuil plus bas pour rester plus longtemps
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

    def _verify_safety_conditions(self) -> bool:
        """Vérification des conditions de sécurité avec seuils CORRIGÉS"""
        current_food = self.state.get_food_count()
        
        # Seuil critique plus bas
        if current_food <= FoodThresholds.CRITICAL:
            return False
            
        # Pour helpers, seuil encore plus bas
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
            self.state.join_incantation = False
            logger.error("[CoordinateIncantationState] ❌ Niveau 1 interdit en coordination")
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
            incanter_probability = 0.6
        else:
            incanter_probability = 0.4

        import random
        is_incanter = random.random() < incanter_probability
        chosen_role = AgentRoles.INCANTER if is_incanter else AgentRoles.HELPER
        
        logger.info(f"[CoordinateIncantationState] 🎯 Rôle choisi: {chosen_role}")
        return chosen_role

    def handle_broadcast_message(self, sender_id: int, data: Dict[str, Any], direction: int):
        """Traite les messages de broadcast reçus (pour les helpers)"""
        logger.info("[CoordinateIncantationState] 📨 Broadcast reçu")
            
        try:
            if sender_id == self.state.agent_id:
                return
                
            level = data.get("level")
            if level != self.state.level:
                return
                
            # Pour un helper, enregistrer la direction reçue
            if self.role == AgentRoles.HELPER:
                self.state.join_incantation = True
                self.state.direction_incant = direction
                logger.info(f"[CoordinateIncantationState] Direction enregistrée: K={direction}")
                
        except Exception as e:
            logger.error(f"[CoordinateIncantationState] Erreur traitement broadcast: {e}")

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes"""
        if command_type == CommandType.LOOK:
            self.vision_update_pending = False
            
        elif command_type == CommandType.INVENTORY:
            self.inventory_update_pending = False
            
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.vision_update_pending = False

        elif command_type == CommandType.INCANTATION:
            logger.info("[CoordinateIncantationState] 🎉 INCANTATION COORDONNÉE RÉUSSIE!")
            self._clear_coordination_state()

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes"""
        if command_type == CommandType.LOOK:
            self.vision_update_pending = False
            
        elif command_type == CommandType.INVENTORY:
            self.inventory_update_pending = False
            
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.vision_update_pending = False

        elif command_type == CommandType.INCANTATION:
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

        logger.info(f"[CoordinateIncantationState] 🤝 ENTRÉE coordination DÉDIÉE")
        logger.info(f"[CoordinateIncantationState] Rôle: {self.role}, Niveau: {self.state.level}")
        logger.info(f"[CoordinateIncantationState] Food: {current_food}, Joueurs requis: {required_players}")

        self.coordination_start_time = time.time()
        self.movement_commands.clear()
        self.received_direction = None
        self.is_moving_to_incanter = False
        self.completed_movement_sequences = 0
        self.last_broadcast_time = 0.0
        self.vision_update_pending = False
        self.inventory_update_pending = False

    def on_exit(self):
        """Actions à la sortie de l'état"""
        super().on_exit()
        duration = time.time() - self.coordination_start_time
        here_count = self.coordination_mgr.get_helpers_here_count()
        players_on_tile = self._get_players_on_current_tile()

        logger.info(f"[CoordinateIncantationState] ✅ SORTIE coordination")
        logger.info(f"[CoordinateIncantationState] Rôle: {self.role}, Durée: {duration:.1f}s")
        logger.info(f"[CoordinateIncantationState] Séquences: {self.completed_movement_sequences}, HERE: {here_count}, Physiques: {players_on_tile}")

        self._clear_coordination_state()
        self.movement_commands.clear()