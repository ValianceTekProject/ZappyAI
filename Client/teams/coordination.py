##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination - Gestionnaire de coordination avec réponse automatique corrigé
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
    BroadcastDirections, FoodThresholds
)

class CoordinationManager:
    """Gestionnaire de coordination avec réponse automatique selon protocole Zappy corrigé."""
    
    def __init__(self, bus: MessageBus, cmd_mgr: CommandManager, game_state: GameState):
        """
        Initialise le gestionnaire de coordination avec réponse automatique.
        
        Args:
            bus: Bus de messages pour la communication
            cmd_mgr: Gestionnaire de commandes
            game_state: État du jeu de l'agent
        """
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
        
        self._register_message_handlers()
        
        logger.debug("[CoordinationManager] Initialisé avec réponse automatique corrigée")

    def _register_message_handlers(self):
        """Enregistre les handlers pour traiter les messages entrants automatiquement."""
        self.bus.subscribe(MessageType.INCANTATION_REQUEST, self._handle_incantation_request_message)
        self.bus.subscribe(MessageType.INCANTATION_RESPONSE, self._handle_incantation_response_message)

    def _handle_incantation_request_message(self, sender_id: int, data: Dict[str, Any], direction: int):
        """
        Handler automatique pour les requêtes d'incantation selon protocole Zappy CORRIGÉ.
        
        Args:
            sender_id: ID de l'expéditeur
            data: Données du message
            direction: Direction du broadcast (1-8, 0 si même tuile)
        """
        try:
            sender_id_str = str(sender_id)
            level = data.get("level")
            required_players = data.get("required_players") 
            timestamp = data.get("timestamp", time.time())
            
            logger.info(f"[CoordinationManager] Requête reçue: sender={sender_id_str}, level={level}, dir={direction}")
            
            if self._should_auto_respond_to_request(sender_id_str, level, timestamp):
                self._handle_incantation_request(sender_id_str, data, direction, timestamp)
            else:
                logger.debug(f"[CoordinationManager] Requête ignorée: conditions non remplies")
            
        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur handler requête: {e}")

    def _should_auto_respond_to_request(self, sender_id: str, level: int, timestamp: float) -> bool:
        """
        Détermine si on doit répondre automatiquement selon protocole Zappy CORRIGÉ.
        
        Args:
            sender_id: ID de l'expéditeur
            level: Niveau demandé
            timestamp: Timestamp du message
            
        Returns:
            True si réponse automatique requise
        """
        current_time = time.time()
        
        # Ne pas répondre à ses propres messages
        if sender_id == str(self.state.agent_id):
            logger.debug(f"[CoordinationManager] Ignore propre message de {sender_id}")
            return False
            
        # Niveau 1 ne nécessite pas de coordination
        if level == 1:
            logger.debug(f"[CoordinationManager] Niveau 1 - pas de coordination")
            return False
            
        # Vérifier l'âge du message
        if current_time - timestamp > CoordinationProtocol.BROADCAST_TIMEOUT:
            logger.debug(f"[CoordinationManager] Message trop ancien: {current_time - timestamp}s")
            return False
            
        # Éviter le spam de réponses
        if current_time - self.last_auto_response_time < CoordinationProtocol.BROADCAST_COOLDOWN:
            logger.debug(f"[CoordinationManager] Cooldown réponse: {current_time - self.last_auto_response_time}s")
            return False
        
        current_role = getattr(self.state, 'role', AgentRoles.SURVIVOR)
        if (current_role == AgentRoles.INCANTER and 
            self.pending_coordination_level is not None and
            self.pending_coordination_level != level):
            logger.debug(f"[CoordinationManager] Déjà incanteur pour niveau {self.pending_coordination_level}")
            return False
            
        logger.debug(f"[CoordinationManager] ✅ Doit répondre à {sender_id} (niveau demandé: {level})")
        return True

    def _handle_incantation_request(self, sender_id: str, payload: Dict[str, Any], direction: int, timestamp: float):
        """
        Traite les requêtes d'incantation avec réponse automatique CORRIGÉE.
        
        Args:
            sender_id: ID de l'expéditeur
            payload: Contenu du message
            direction: Direction du broadcast
            timestamp: Timestamp du message
        """
        try:
            level = payload.get("level")
            required_players = payload.get("required_players")
            
            self.received_requests[sender_id] = {
                "timestamp": timestamp,
                "direction": direction,
                "required_players": required_players,
                "level": level
            }

            logger.info(f"[CoordinationManager] 📩 Requête enregistrée: {sender_id} (dir={direction}, lvl={level})")

            response = self._determine_response_according_to_protocol(sender_id, direction, level)
            if response:
                self._send_automatic_response(sender_id, response, level)
                self.last_auto_response_time = time.time()
                logger.info(f"[CoordinationManager] 📤 Réponse '{response}' programmée pour {sender_id}")
            else:
                logger.warning(f"[CoordinationManager] ❌ Aucune réponse déterminée pour {sender_id}")

        except (ValueError, KeyError) as e:
            logger.error(f"[CoordinationManager] Erreur parsing requête: {payload}, {e}")

    def _determine_response_according_to_protocol(self, sender_id: str, direction: int, level: int) -> Optional[str]:
        """
        Détermine la réponse selon le protocole Zappy strict CORRIGÉ.
        
        Args:
            sender_id: ID de l'incanteur
            direction: Direction du broadcast
            level: Niveau requis
            
        Returns:
            Réponse selon protocole Zappy ou None
        """
        current_food = self.state.get_food_count()
        current_role = getattr(self.state, 'role', AgentRoles.SURVIVOR)
        current_time = time.time()
        
        logger.debug(f"[CoordinationManager] Analyse réponse: food={current_food}, role={current_role}, level={level}")
        
        if current_time < self.coordination_busy_until:
            logger.debug(f"[CoordinationManager] Temporairement occupé jusqu'à {self.coordination_busy_until - current_time:.1f}s")
            return CoordinationProtocol.RESPONSE_BUSY
        
        if not self._can_help_according_to_protocol(level):
            logger.debug(f"[CoordinationManager] Ne peut pas aider selon protocole")
            return CoordinationProtocol.RESPONSE_BUSY

        if current_role == AgentRoles.INCANTER:
            if self.pending_coordination_level is not None and self.pending_coordination_level != level:
                logger.debug(f"[CoordinationManager] Incanteur occupé niveau {self.pending_coordination_level}")
                return CoordinationProtocol.RESPONSE_BUSY
            elif self.pending_coordination_level == level:
                logger.debug(f"[CoordinationManager] Incanteur même niveau {level}")
            else:
                logger.debug(f"[CoordinationManager] Incanteur pas occupé")
                return CoordinationProtocol.RESPONSE_BUSY

        if (self.chosen_incanter_id and 
            self.chosen_incanter_id != sender_id and
            self.pending_coordination_level != level):
            logger.debug(f"[CoordinationManager] Déjà engagé avec {self.chosen_incanter_id} niveau {self.pending_coordination_level}")
            return CoordinationProtocol.RESPONSE_BUSY

        if self.state.level != level:
            logger.debug(f"[CoordinationManager] Niveau incompatible: {self.state.level} != {level}")
            return CoordinationProtocol.RESPONSE_BUSY

        logger.info(f"[CoordinationManager] 🤝 Accepter aide pour {sender_id} (direction={direction}, niveau={level})")
        
        self.chosen_incanter_id = sender_id
        self.chosen_incanter_direction = direction
        self.pending_coordination_level = level
        
        if hasattr(self.state, 'set_role'):
            self.state.set_role(AgentRoles.HELPER)
        
        if direction == BroadcastDirections.HERE:
            return CoordinationProtocol.RESPONSE_HERE
        else:
            return CoordinationProtocol.RESPONSE_COMING

    def _can_help_according_to_protocol(self, requested_level: int) -> bool:
        """
        Vérifie si l'agent peut aider selon le protocole Zappy strict CORRIGÉ.
        
        Args:
            requested_level: Niveau demandé pour l'incantation
            
        Returns:
            True si peut aider selon protocole
        """
        current_food = self.state.get_food_count()
        current_level = self.state.level
        
        if current_level != requested_level:
            logger.debug(f"[CoordinationManager] Niveau incorrect: {current_level} != {requested_level}")
            return False
        
        if current_food < FoodThresholds.COORDINATION_MIN:
            logger.debug(f"[CoordinationManager] Nourriture insuffisante: {current_food} < {FoodThresholds.COORDINATION_MIN}")
            return False
            
        if current_level <= 1:
            logger.debug(f"[CoordinationManager] Niveau trop bas: {current_level}")
            return False
            
        if current_level >= 8:
            logger.debug(f"[CoordinationManager] Niveau maximum atteint: {current_level}")
            return False
        
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(current_level, {})
        inventory = self.state.get_inventory()
        has_resources = True
        for resource, needed in requirements.items():
            if inventory.get(resource, 0) < needed:
                has_resources = False
                break
                
        if not has_resources:
            logger.debug(f"[CoordinationManager] Ressources manquantes pour niveau {current_level}")
            return False
            
        logger.debug(f"[CoordinationManager] ✅ Peut aider: level={current_level}, food={current_food}, ressources=OK")
        return True

    def _send_automatic_response(self, request_sender: str, response: str, level: int):
        """
        Envoie automatiquement une réponse d'incantation via Message.py.
        
        Args:
            request_sender: ID de l'incanteur demandeur
            response: Réponse à envoyer (here/coming/busy)
            level: Niveau de l'incantation
        """
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
            
            if response in [CoordinationProtocol.RESPONSE_HERE, CoordinationProtocol.RESPONSE_COMING]:
                self.coordination_busy_until = time.time() + 15.0  # Occupé pour 15 secondes
                logger.debug(f"[CoordinationManager] Marqué occupé pour {response}")
            
            logger.info(f"[CoordinationManager] 📤 Réponse AUTO '{response}' envoyée à {request_sender}")
            
        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur envoi réponse auto: {e}")

    def _handle_incantation_response_message(self, sender_id: int, data: Dict[str, Any], direction: int):
        """
        Handler pour les réponses d'incantation avec validation protocole strict.
        
        Args:
            sender_id: ID de l'expéditeur de la réponse
            data: Données de la réponse
            direction: Direction du broadcast
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return

        try:
            sender_id_str = str(sender_id)
            request_sender = str(data.get("request_sender"))
            response = data.get("response")
            timestamp = data.get("timestamp", time.time())
            
            if request_sender != str(self.state.agent_id):
                return

            current_time = time.time()
            if current_time - timestamp > CoordinationProtocol.BROADCAST_TIMEOUT:
                return

            logger.info(f"[CoordinationManager] 📨 Réponse reçue de {sender_id_str}: '{response}'")

            if response == CoordinationProtocol.RESPONSE_HERE:
                if sender_id_str not in self.confirmed_helpers:
                    self.confirmed_helpers.append(sender_id_str)
                    logger.info(f"[CoordinationManager] ✅ Helper {sender_id_str} confirmé (HERE)")
                    
            elif response == CoordinationProtocol.RESPONSE_COMING:
                logger.info(f"[CoordinationManager] 🏃 Helper {sender_id_str} en route (COMING)")
                
            elif response == CoordinationProtocol.RESPONSE_BUSY:
                logger.debug(f"[CoordinationManager] ❌ Helper {sender_id_str} occupé (BUSY)")

        except (ValueError, KeyError) as e:
            logger.error(f"[CoordinationManager] Erreur parsing réponse:{e}")

    def send_incantation_request(self):
        """
        Envoie une requête d'incantation avec vérifications protocole strict.
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            logger.warning("[CoordinationManager] Seuls les incanteurs peuvent envoyer des requêtes")
            return

        if self.state.level == 1:
            logger.error("[CoordinationManager] ❌ Niveau 1 ne doit JAMAIS utiliser coordination")
            return

        current_time = time.time()
        
        # Respect du cooldown
        if current_time - self._last_broadcast_time < CoordinationProtocol.BROADCAST_COOLDOWN:
            return

        # Vérification nourriture minimale
        current_food = self.state.get_food_count()
        if current_food < CoordinationProtocol.MIN_FOOD_TO_INITIATE:
            logger.warning(f"[CoordinationManager] Nourriture insuffisante pour initier: {current_food}")
            return

        level = self.state.level
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(level, 1)
        
        if required_players <= 1:
            logger.error(f"[CoordinationManager] ❌ Niveau {level} ne nécessite pas de coordination")
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
            
            logger.info(f"[CoordinationManager] 📢 Requête incantation envoyée pour niveau {level} ({required_players} joueurs)")
            
        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur envoi requête: {e}")

    def get_helpers_here_count(self) -> int:
        """
        Retourne le nombre de helpers confirmés présents.
        
        Returns:
            Nombre de helpers confirmés ici
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return 0

        current_time = time.time()
        valid_helpers = 0

        for helper_id in self.confirmed_helpers:
            if helper_id in self.sent_responses:
                response_data = self.sent_responses[helper_id]
                if (response_data['response'] == CoordinationProtocol.RESPONSE_HERE and
                    current_time - response_data['timestamp'] <= CoordinationProtocol.BROADCAST_TIMEOUT):
                    valid_helpers += 1

        logger.debug(f"[CoordinationManager] Helpers valides ici: {valid_helpers}")
        return valid_helpers

    def has_enough_helpers(self) -> bool:
        """
        Vérifie si on a assez de helpers confirmés pour l'incantation.
        
        Returns:
            True si assez de helpers selon protocole Zappy
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return False

        if self.state.level == 1:
            return True

        required = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        
        vision = self.state.get_vision()
        players_on_tile = 1
        
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                players_on_tile = data.players
                break
        
        confirmed_helpers = self.get_helpers_here_count()
        total_players = max(players_on_tile, confirmed_helpers + 1)

        result = total_players >= required
        logger.info(f"[CoordinationManager] 👥 Joueurs: physiques={players_on_tile}, confirmés={confirmed_helpers}, total={total_players}/{required}")

        return result

    def get_chosen_incanter_direction(self) -> Optional[int]:
        """
        Retourne la direction vers l'incanteur choisi pour un helper.
        
        Returns:
            Direction vers incanteur ou None
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.HELPER):
            return None

        return self.chosen_incanter_direction

    def reset_helper_choice(self):
        """Reset le choix d'incanteur pour un helper."""
        if hasattr(self.state, 'role') and self.state.role == AgentRoles.HELPER:
            self.chosen_incanter_id = None
            self.chosen_incanter_direction = None
            self.pending_coordination_level = None
            self.coordination_busy_until = 0.0
            logger.info("[CoordinationManager] Reset choix incanteur")

    def cleanup_old_data(self, max_age: Optional[float] = None):
        """
        Nettoie les données trop anciennes.
        
        Args:
            max_age: Âge maximum des données en secondes
        """
        if max_age is None:
            max_age = CoordinationProtocol.BROADCAST_TIMEOUT

        current_time = time.time()

        # Nettoyer les requêtes anciennes
        to_remove = []
        for sender_id, data in self.received_requests.items():
            if current_time - data.get('timestamp', 0) > max_age:
                to_remove.append(sender_id)
        for sender_id in to_remove:
            del self.received_requests[sender_id]

        # Nettoyer les réponses anciennes
        to_remove = []
        for sender_id, data in self.sent_responses.items():
            if current_time - data.get('timestamp', 0) > max_age:
                to_remove.append(sender_id)
        for sender_id in to_remove:
            del self.sent_responses[sender_id]

        # Nettoyer les helpers confirmés
        self.confirmed_helpers = [
            helper_id for helper_id in self.confirmed_helpers
            if helper_id in self.sent_responses
        ]

    def clear_coordination_data(self):
        """Nettoie toutes les données de coordination."""
        self.received_requests.clear()
        self.sent_responses.clear()
        self.confirmed_helpers.clear()
        self.coordination_start_time = None
        self.chosen_incanter_id = None
        self.chosen_incanter_direction = None
        self.pending_coordination_level = None
        self.coordination_busy_until = 0.0
        logger.debug("[CoordinationManager] Données de coordination nettoyées")

    def is_coordination_timeout(self) -> bool:
        """
        Vérifie si la coordination a expiré.
        
        Returns:
            True si timeout dépassé
        """
        if self.coordination_start_time is None:
            return False
        return time.time() - self.coordination_start_time > CoordinationProtocol.COORDINATION_TIMEOUT

    def get_coordination_status(self) -> Dict[str, Any]:
        """
        Retourne le statut de la coordination pour debug.
        
        Returns:
            Statut complet de la coordination
        """
        current_time = time.time()
        
        return {
            'role': getattr(self.state, 'role', 'unknown'),
            'level': self.state.level,
            'food': self.state.get_food_count(),
            'chosen_incanter': self.chosen_incanter_id,
            'chosen_direction': self.chosen_incanter_direction,
            'helpers_confirmed': len(self.confirmed_helpers),
            'required_players': IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1),
            'has_enough_helpers': self.has_enough_helpers(),
            'coordination_timeout': self.is_coordination_timeout(),
            'received_requests': len(self.received_requests),
            'sent_responses': len(self.sent_responses),
            'can_help': self._can_help_according_to_protocol(self.state.level),
            'auto_response_enabled': self.auto_response_enabled,
            'pending_coordination_level': self.pending_coordination_level,
            'busy_until': max(0, self.coordination_busy_until - current_time),
            'time_since_start': (current_time - self.coordination_start_time 
                               if self.coordination_start_time else 0)
        }