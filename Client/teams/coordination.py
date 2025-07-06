##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination
##

import time
from typing import Dict, List, Any, Optional
from protocol.commands import CommandManager
from utils.logger import logger
from utils.game_state import GameState
from teams.message_checker import MessageBus
from teams.message import Message, MessageType
from constant import (
    CoordinationProtocol, IncantationRequirements, AgentRoles,
    BroadcastDirections, SafetyLimits, CoordinationHelperSettings
)


class CoordinationManager:
    """Gestionnaire de coordination avec logique optimisée pour succès."""
    
    def __init__(self, bus: MessageBus, cmd_mgr: CommandManager, game_state: GameState):
        self.bus = bus
        self.cmd_mgr = cmd_mgr
        self.state = game_state
        
        self._last_broadcast_time = 0.0
        
        self.received_requests: Dict[str, Dict[str, Any]] = {}
        self.sent_responses: Dict[str, Dict[str, Any]] = {}
        
        self.chosen_incanter_id: Optional[str] = None
        self.chosen_incanter_direction: Optional[int] = None
        
        self.coordination_start_time: Optional[float] = None
        self.confirmed_helpers: List[str] = []
        self.auto_response_enabled = True
        self.last_auto_response_time = 0.0
        
        self.pending_coordination_level: Optional[int] = None
        self.coordination_busy_until: float = 0.0
        
        self.here_responses: Dict[str, Dict[str, Any]] = {}
        self.coming_responses: Dict[str, Dict[str, Any]] = {}
        self.last_cleanup = time.time()
        
        self.response_history: Dict[str, List[float]] = {}
        self.max_response_history = 10
        
        self._register_message_handlers()
        
        logger.debug("[CoordinationManager] Initialisé avec protocole optimisé")

    def _register_message_handlers(self):
        """Enregistre les handlers pour les messages."""
        self.bus.subscribe(MessageType.INCANTATION_REQUEST, self._handle_incantation_request_message)
        self.bus.subscribe(MessageType.INCANTATION_RESPONSE, self._handle_incantation_response_message)

    def _handle_incantation_request_message(self, sender_id: int, data: Dict[str, Any], direction: int):
        """Handler optimisé pour les requêtes d'incantation."""
        try:
            sender_id_str = str(sender_id)
            level = data.get("level")
            timestamp = data.get("timestamp", time.time())
            
            logger.info(f"[CoordinationManager] 📩 Requête: {sender_id_str}, level={level}, K={direction}")
            
            if self._should_respond_to_request(sender_id_str, level, direction, timestamp):
                self._send_protocol_response(sender_id_str, data, direction, timestamp)
            else:
                logger.debug(f"[CoordinationManager] Requête ignorée de {sender_id_str}")
            
        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur handler requête: {e}")

    def _should_respond_to_request(self, sender_id: str, level: int, direction: int, timestamp: float) -> bool:
        """Détermine si on doit répondre - logique CORRIGÉE."""
        current_time = time.time()
        
        if sender_id == str(self.state.agent_id):
            return False
            
        if level == 1:
            return False
            
        if current_time - timestamp > CoordinationProtocol.BROADCAST_TIMEOUT:
            logger.debug(f"[CoordinationManager] Message expiré de {sender_id}")
            return False
        
        if self._is_response_too_frequent(sender_id, current_time):
            return False
        
        if (self.chosen_incanter_id and 
            self.chosen_incanter_id != sender_id and
            current_time < self.coordination_busy_until):
            logger.debug(f"[CoordinationManager] Occupé avec {self.chosen_incanter_id}")
            return False
        
        current_role = getattr(self.state, 'role', AgentRoles.SURVIVOR)
        if (current_role == AgentRoles.INCANTER and 
            self.pending_coordination_level is not None and
            self.pending_coordination_level != level):
            return False
            
        return True

    def _is_response_too_frequent(self, sender_id: str, current_time: float) -> bool:
        """Vérifie le cooldown de réponse - CORRIGÉ."""
        if sender_id not in self.response_history:
            self.response_history[sender_id] = []
        
        history = self.response_history[sender_id]
        
        history[:] = [t for t in history if current_time - t < 20.0]
        
        min_interval = CoordinationHelperSettings.RESPONSE_DELAY_MIN
        
        if history and current_time - history[-1] < min_interval:
            return True
            
        return False

    def _send_protocol_response(self, sender_id: str, payload: Dict[str, Any], direction: int, timestamp: float):
        """Envoie la réponse selon le protocole Zappy STRICT."""
        try:
            level = payload.get("level")
            current_time = time.time()
            
            self.received_requests[sender_id] = {
                "timestamp": timestamp,
                "direction": direction,
                "level": level
            }

            response = self._determine_zappy_response(sender_id, direction, level)
            if response:
                if sender_id not in self.response_history:
                    self.response_history[sender_id] = []
                self.response_history[sender_id].append(current_time)
                
                if len(self.response_history[sender_id]) > self.max_response_history:
                    self.response_history[sender_id].pop(0)
                
                self._send_response_message(sender_id, response, level)
                self.last_auto_response_time = current_time
                logger.info(f"[CoordinationManager] 📤 '{response}' → {sender_id} (K={direction})")

        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur envoi réponse: {e}")

    def _determine_zappy_response(self, sender_id: str, direction: int, level: int) -> Optional[str]:
        """Détermine la réponse selon le protocole Zappy STRICT - CORRIGÉ."""
        current_food = self.state.get_food_count()
        current_level = self.state.level
        current_role = getattr(self.state, 'role', AgentRoles.SURVIVOR)
        
        if not self._can_help_optimized(level, current_food, current_level):
            return CoordinationProtocol.RESPONSE_BUSY
        
        if current_role == AgentRoles.INCANTER:
            return CoordinationProtocol.RESPONSE_BUSY
        
        if (self.chosen_incanter_id and 
            self.chosen_incanter_id != sender_id):
            return CoordinationProtocol.RESPONSE_BUSY
        
        logger.info(f"[CoordinationManager] 🤝 Accepte aide {sender_id} (K={direction})")
        
        self.chosen_incanter_id = sender_id
        self.chosen_incanter_direction = direction
        self.pending_coordination_level = level
        self.coordination_busy_until = time.time() + SafetyLimits.MAX_HELPER_WAIT_TIME
        
        if hasattr(self.state, 'set_role'):
            self.state.set_role(AgentRoles.HELPER)
        
        return self._determine_here_vs_coming_zappy_protocol(direction)

    def _can_help_optimized(self, level: int, current_food: int, current_level: int) -> bool:
        """Vérifications OPTIMISÉES pour aider."""
        if current_level != level:
            return False
        
        if current_food < SafetyLimits.MIN_FOOD_FOR_COORDINATION_SAFETY:
            return False
            
        if current_level <= 1 or current_level >= 8:
            return False
        
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(current_level, {})
        inventory = self.state.get_inventory()
        
        missing_critical = 0
        for resource, needed in requirements.items():
            current_amount = inventory.get(resource, 0)
            if current_amount < needed:
                missing_critical += (needed - current_amount)
        
        if missing_critical > 3:
            return False
                
        return True

    def _determine_here_vs_coming_zappy_protocol(self, direction: int) -> str:
        """Détermine 'here' vs 'coming'"""
        if direction == BroadcastDirections.HERE:
            logger.info(f"[CoordinationManager] 📍 K={direction} → 'here'")
            return CoordinationProtocol.RESPONSE_HERE
        else:
            logger.info(f"[CoordinationManager] 🏃 K={direction} → 'coming'")
            return CoordinationProtocol.RESPONSE_COMING

    def _send_response_message(self, request_sender: str, response: str, level: int):
        """Envoie le message de réponse."""
        try:
            encoded_message = Message.create_incantation_response(
                sender_id=self.state.agent_id,
                team_id=self.state.team_id,
                request_sender=int(request_sender),
                response=response,
                level=level
            )
            
            self.cmd_mgr.broadcast(encoded_message)
            
            self.sent_responses[request_sender] = {
                'response': response,
                'timestamp': time.time(),
                'level': level
            }
            
            if response == CoordinationProtocol.RESPONSE_HERE:
                self.here_responses[request_sender] = {
                    'timestamp': time.time(),
                    'level': level
                }
            elif response == CoordinationProtocol.RESPONSE_COMING:
                self.coming_responses[request_sender] = {
                    'timestamp': time.time(),
                    'level': level
                }
            
        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur envoi message: {e}")

    def _handle_incantation_response_message(self, sender_id: int, data: Dict[str, Any], direction: int):
        """Handler CORRIGÉ pour les réponses d'incantation."""
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return

        try:
            sender_id_str = str(sender_id)
            request_sender = str(data.get("request_sender"))
            response = data.get("response")
            level = data.get("level")
            timestamp = data.get("timestamp", time.time())
            
            if request_sender != str(self.state.agent_id):
                return

            if time.time() - timestamp > CoordinationProtocol.BROADCAST_TIMEOUT:
                return

            logger.info(f"[CoordinationManager] 📨 Réponse {sender_id_str}: '{response}' (niveau {level})")

            if response == CoordinationProtocol.RESPONSE_HERE:
                self.here_responses[sender_id_str] = {
                    'timestamp': time.time(),
                    'level': level
                }
                if sender_id_str not in self.confirmed_helpers:
                    self.confirmed_helpers.append(sender_id_str)
                logger.info(f"[CoordinationManager] ✅ Helper {sender_id_str} HERE confirmé")
                    
            elif response == CoordinationProtocol.RESPONSE_COMING:
                self.coming_responses[sender_id_str] = {
                    'timestamp': time.time(),
                    'level': level
                }
                logger.info(f"[CoordinationManager] 🏃 Helper {sender_id_str} COMING")
                
            elif response == CoordinationProtocol.RESPONSE_BUSY:
                self._remove_helper(sender_id_str)
                logger.debug(f"[CoordinationManager] ❌ Helper {sender_id_str} BUSY")

        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur traitement réponse: {e}")

    def _remove_helper(self, helper_id: str):
        """Supprime un helper de toutes les listes."""
        if helper_id in self.confirmed_helpers:
            self.confirmed_helpers.remove(helper_id)
        if helper_id in self.here_responses:
            del self.here_responses[helper_id]
        if helper_id in self.coming_responses:
            del self.coming_responses[helper_id]

    def send_incantation_request(self):
        """Envoie une requête d'incantation."""
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return

        if self.state.level == 1:
            logger.error("[CoordinationManager] ❌ Niveau 1 ne doit jamais utiliser coordination")
            return

        current_time = time.time()
        
        if current_time - self._last_broadcast_time < CoordinationProtocol.BROADCAST_COOLDOWN:
            return

        current_food = self.state.get_food_count()
        if current_food < CoordinationProtocol.MIN_FOOD_TO_INITIATE:
            return

        level = self.state.level
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(level, 1)
        
        if required_players <= 1:
            logger.error(f"[CoordinationManager] ❌ Niveau {level} ne nécessite pas coordination")
            return
        
        if self.coordination_start_time is None:
            self.coordination_start_time = current_time
            
        self.pending_coordination_level = level
        
        try:
            encoded_message = Message.create_incantation_request(
                sender_id=self.state.agent_id,
                team_id=self.state.team_id,
                level=level,
                required_players=required_players
            )
            
            self.cmd_mgr.broadcast(encoded_message)
            self._last_broadcast_time = current_time
            
            logger.info(f"[CoordinationManager] 📢 Requête incantation niveau {level}")
            
        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur envoi requête: {e}")

    def get_helpers_here_count(self) -> int:
        """Retourne le nombre de helpers confirmés présents."""
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return 0

        self._cleanup_old_responses()
        
        current_time = time.time()
        valid_count = 0

        for helper_id, response_data in self.here_responses.items():
            if (current_time - response_data['timestamp'] <= CoordinationProtocol.BROADCAST_TIMEOUT and
                response_data['level'] == self.state.level):
                valid_count += 1

        logger.debug(f"[CoordinationManager] Helpers HERE valides: {valid_count}")
        return valid_count

    def get_helpers_coming_count(self) -> int:
        """Retourne le nombre de helpers en route."""
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return 0

        current_time = time.time()
        valid_count = 0

        for helper_id, response_data in self.coming_responses.items():
            if (current_time - response_data['timestamp'] <= CoordinationProtocol.BROADCAST_TIMEOUT and
                response_data['level'] == self.state.level):
                valid_count += 1

        logger.debug(f"[CoordinationManager] Helpers COMING valides: {valid_count}")
        return valid_count

    def has_enough_helpers(self) -> bool:
        """Vérifie si on a assez de helpers confirmés."""
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return False

        if self.state.level == 1:
            return True

        required = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        helpers_needed = required - 1
        
        here_count = self.get_helpers_here_count()
        
        vision = self.state.get_vision()
        players_on_tile = 1
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                players_on_tile = data.players
                break
        
        has_enough = here_count >= helpers_needed or players_on_tile >= required
        
        if has_enough:
            logger.info(f"[CoordinationManager] ✅ Assez helpers: HERE={here_count}, Physiques={players_on_tile}")
        
        return has_enough

    def get_chosen_incanter_direction(self) -> Optional[int]:
        """Retourne la direction vers l'incanteur choisi."""
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.HELPER):
            return None
        return self.chosen_incanter_direction

    def _cleanup_old_responses(self):
        """Nettoie les réponses anciennes."""
        current_time = time.time()
        
        if current_time - self.last_cleanup < 2.0:
            return
            
        self.last_cleanup = current_time

        expired_here = [
            helper_id for helper_id, data in self.here_responses.items()
            if current_time - data['timestamp'] > CoordinationProtocol.BROADCAST_TIMEOUT
        ]
        
        for helper_id in expired_here:
            self._remove_helper(helper_id)

        expired_coming = [
            helper_id for helper_id, data in self.coming_responses.items()
            if current_time - data['timestamp'] > CoordinationProtocol.BROADCAST_TIMEOUT
        ]
        
        for helper_id in expired_coming:
            del self.coming_responses[helper_id]

        for sender_id in list(self.response_history.keys()):
            self.response_history[sender_id] = [
                t for t in self.response_history[sender_id] 
                if current_time - t < 30.0
            ]
            if not self.response_history[sender_id]:
                del self.response_history[sender_id]

    def clear_coordination_data(self):
        """Nettoie toutes les données de coordination."""
        self.received_requests.clear()
        self.sent_responses.clear()
        self.confirmed_helpers.clear()
        self.here_responses.clear()
        self.coming_responses.clear()
        self.response_history.clear()
        self.coordination_start_time = None
        self.chosen_incanter_id = None
        self.chosen_incanter_direction = None
        self.pending_coordination_level = None
        self.coordination_busy_until = 0.0
        logger.debug("[CoordinationManager] Données coordination nettoyées")

    def reset_helper_choice(self):
        """Reset le choix d'incanteur pour un helper."""
        if hasattr(self.state, 'role') and self.state.role == AgentRoles.HELPER:
            self.chosen_incanter_id = None
            self.chosen_incanter_direction = None
            self.pending_coordination_level = None
            self.coordination_busy_until = 0.0

    def is_coordination_timeout(self) -> bool:
        """Vérifie si la coordination a expiré."""
        if self.coordination_start_time is None:
            return False
        return time.time() - self.coordination_start_time > CoordinationProtocol.COORDINATION_TIMEOUT