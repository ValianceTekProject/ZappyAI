##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination - Gestionnaire de coordination simplifié et nettoyé
##

import time
from typing import Dict, List, Any, Optional
from protocol.commands import CommandManager
from utils.logger import logger
from utils.game_state import GameState
from teams.message_checker import MessageBus
from constant import (
    CoordinationProtocol, IncantationRequirements, AgentRoles,
    BroadcastDirections, CoordinationMessages
)


class CoordinationManager:
    """Gestionnaire de coordination simplifié pour le protocole Zappy."""
    
    def __init__(self, bus: MessageBus, cmd_mgr: CommandManager, game_state: GameState):
        """
        Initialise le gestionnaire de coordination.
        
        Args:
            bus: Bus de messages pour la communication
            cmd_mgr: Gestionnaire de commandes
            game_state: État du jeu
        """
        self.bus = bus
        self.cmd_mgr = cmd_mgr
        self.state = game_state
        
        self._last_broadcast_time = 0.0
        
        # Données simplifiées de coordination
        self.received_requests: Dict[str, Dict[str, Any]] = {}
        self.sent_responses: Dict[str, Dict[str, Any]] = {}
        
        # Pour les helpers
        self.chosen_incanter_id: Optional[str] = None
        self.chosen_incanter_direction: Optional[int] = None
        
        # Pour les incanteurs
        self.coordination_start_time: Optional[float] = None
        self.confirmed_helpers: List[str] = []
        
        logger.debug("[CoordinationManager] Initialisé avec protocole Zappy simplifié")

    def handle_incoming_broadcast(self, sender_id: str, message: str, direction: int):
        """
        Traite les broadcasts entrants selon le protocole.
        
        Args:
            sender_id: ID de l'expéditeur
            message: Message reçu
            direction: Direction du broadcast (0-8)
        """
        current_time = time.time()
        sender_id = str(sender_id)
        my_id = str(self.state.agent_id)

        # Ne pas traiter ses propres messages
        if sender_id == my_id:
            return

        # Parser le message selon le format standardisé
        if message.startswith(CoordinationMessages.REQUEST_PREFIX):
            self._handle_incantation_request(sender_id, message, direction, current_time)
        elif message.startswith(CoordinationMessages.RESPONSE_PREFIX):
            self._handle_incantation_response(sender_id, message, direction, current_time)

    def _handle_incantation_request(self, sender_id: str, message: str, direction: int, timestamp: float):
        """
        Traite les requêtes d'incantation.
        
        Args:
            sender_id: ID de l'expéditeur
            message: Message de requête
            direction: Direction du broadcast
            timestamp: Timestamp du message
        """
        try:
            # Parse: "INCANT_REQ:level:required_players"
            parts = message.split(':')
            if len(parts) != 3:
                return
                
            level = int(parts[1])
            required_players = int(parts[2])
            
            # Vérifications de base
            if (level != self.state.level or 
                time.time() - timestamp > CoordinationProtocol.BROADCAST_TIMEOUT):
                return

            # Ignorer les requêtes pour niveau 1 (solo uniquement)
            if level == 1:
                logger.warning(f"[CoordinationManager] Requête niveau 1 ignorée de {sender_id}")
                return

            # Enregistrer la requête
            self.received_requests[sender_id] = {
                "timestamp": timestamp,
                "direction": direction,
                "required_players": required_players,
                "level": level
            }

            logger.info(f"[CoordinationManager] Requête incantation de {sender_id} (dir={direction}, lvl={level})")

            # Déterminer et envoyer la réponse
            response = self._determine_response(sender_id, direction, level)
            self._send_response(sender_id, response, level)

        except (ValueError, IndexError) as e:
            logger.error(f"[CoordinationManager] Erreur parsing requête: {message}, {e}")

    def _handle_incantation_response(self, sender_id: str, message: str, direction: int, timestamp: float):
        """
        Traite les réponses d'incantation pour les incanteurs.
        
        Args:
            sender_id: ID de l'expéditeur
            message: Message de réponse
            direction: Direction du broadcast
            timestamp: Timestamp du message
        """
        # Seulement si je suis incanteur
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return

        try:
            # Parse: "INCANT_RESP:request_id:response"
            parts = message.split(':')
            if len(parts) != 3:
                return
                
            request_id = parts[1]
            response = parts[2]
            
            # Vérifier que la réponse nous est destinée
            if request_id != str(self.state.agent_id):
                return

            # Vérifier que le message n'est pas trop ancien
            if time.time() - timestamp > CoordinationProtocol.BROADCAST_TIMEOUT:
                return

            # Traiter selon le type de réponse
            if response == CoordinationProtocol.RESPONSE_HERE:
                if sender_id not in self.confirmed_helpers:
                    self.confirmed_helpers.append(sender_id)
                    logger.info(f"[CoordinationManager] Helper {sender_id} confirmé (HERE)")
            elif response == CoordinationProtocol.RESPONSE_COMING:
                logger.info(f"[CoordinationManager] Helper {sender_id} en route (COMING)")
            elif response == CoordinationProtocol.RESPONSE_BUSY:
                logger.debug(f"[CoordinationManager] Helper {sender_id} occupé (BUSY)")

        except (ValueError, IndexError) as e:
            logger.error(f"[CoordinationManager] Erreur parsing réponse: {message}, {e}")

    def _determine_response(self, sender_id: str, direction: int, level: int) -> str:
        """
        Détermine la réponse selon le protocole Zappy.
        
        Args:
            sender_id: ID de l'incanteur
            direction: Direction du broadcast
            level: Niveau d'incantation
            
        Returns:
            Réponse du protocole ("here", "coming", "busy")
        """
        # Vérifications d'éligibilité
        if not self._can_help_incantation():
            return CoordinationProtocol.RESPONSE_BUSY

        # Si déjà engagé avec un autre incanteur
        if (self.chosen_incanter_id and 
            self.chosen_incanter_id != sender_id):
            return CoordinationProtocol.RESPONSE_BUSY

        # Déterminer la réponse selon la direction
        if direction == BroadcastDirections.HERE:
            # Déjà sur la même tuile
            self.chosen_incanter_id = sender_id
            self.chosen_incanter_direction = direction
            return CoordinationProtocol.RESPONSE_HERE
        else:
            # Doit se déplacer
            self.chosen_incanter_id = sender_id
            self.chosen_incanter_direction = direction
            return CoordinationProtocol.RESPONSE_COMING

    def _can_help_incantation(self) -> bool:
        """
        Vérifie si l'agent peut aider selon le protocole Zappy.
        
        Returns:
            True si l'agent peut aider
        """
        current_food = self.state.get_food_count()
        
        # Vérification nourriture
        if current_food < CoordinationProtocol.MIN_FOOD_TO_HELP:
            return False
            
        # Vérification niveau (niveau 1 ne peut pas aider)
        if self.state.level <= 1:
            return False
            
        # Vérification niveau maximum
        if self.state.level >= 8:
            return False
            
        return True

    def _send_response(self, request_sender: str, response: str, level: int):
        """
        Envoie une réponse d'incantation avec format standardisé.
        
        Args:
            request_sender: ID de l'incanteur qui a fait la requête
            response: Réponse du protocole
            level: Niveau d'incantation
        """
        message = CoordinationMessages.format_response(request_sender, response)
        self.cmd_mgr.broadcast(message)
        
        # Enregistrer la réponse envoyée
        self.sent_responses[request_sender] = {
            'response': response,
            'timestamp': time.time(),
            'level': level
        }
        
        logger.info(f"[CoordinationManager] Réponse '{response}' envoyée à {request_sender}")

    def send_incantation_request(self):
        """Envoie une requête d'incantation selon le protocole Zappy."""
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            logger.warning("[CoordinationManager] Seuls les incanteurs peuvent envoyer des requêtes")
            return

        # Pas de requête pour niveau 1 (solo autorisé)
        if self.state.level == 1:
            logger.warning("[CoordinationManager] Niveau 1 ne doit pas utiliser coordination")
            return

        current_time = time.time()
        
        # Cooldown entre broadcasts
        if current_time - self._last_broadcast_time < CoordinationProtocol.BROADCAST_COOLDOWN:
            return

        # Vérifications de sécurité
        current_food = self.state.get_food_count()
        if current_food < CoordinationProtocol.MIN_FOOD_TO_INITIATE:
            logger.warning(f"[CoordinationManager] Nourriture insuffisante: {current_food}")
            return

        level = self.state.level
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(level, 1)
        
        # Seulement pour niveaux multi-joueurs
        if required_players <= 1:
            return
        
        # Enregistrer le début si première fois
        if self.coordination_start_time is None:
            self.coordination_start_time = current_time
        
        message = CoordinationMessages.format_request(level, required_players)
        self.cmd_mgr.broadcast(message)
        self._last_broadcast_time = current_time
        
        logger.info(f"[CoordinationManager] Requête incantation envoyée: {message}")

    def get_helpers_here_count(self) -> int:
        """
        Retourne le nombre de helpers confirmés présents.
        
        Returns:
            Nombre de helpers confirmés sur la tuile
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

        return valid_helpers

    def has_enough_helpers(self) -> bool:
        """
        Vérifie si on a assez de helpers confirmés pour l'incantation.
        
        Returns:
            True si assez de helpers confirmés
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return False

        # Niveau 1 = solo
        if self.state.level == 1:
            return True

        required = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        helpers_here = self.get_helpers_here_count()
        
        # Compter l'incanteur lui-même
        total_players = helpers_here + 1

        result = total_players >= required
        logger.debug(f"[CoordinationManager] Joueurs confirmés: {total_players}/{required}")

        return result

    def get_chosen_incanter_direction(self) -> Optional[int]:
        """
        Retourne la direction vers l'incanteur choisi (pour helper).
        
        Returns:
            Direction vers l'incanteur ou None
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.HELPER):
            return None

        return self.chosen_incanter_direction

    def reset_helper_choice(self):
        """Reset le choix d'incanteur pour un helper."""
        if hasattr(self.state, 'role') and self.state.role == AgentRoles.HELPER:
            self.chosen_incanter_id = None
            self.chosen_incanter_direction = None
            logger.info("[CoordinationManager] Reset choix incanteur")

    def cleanup_old_data(self, max_age: Optional[float] = None):
        """
        Nettoie les données trop anciennes.
        
        Args:
            max_age: Age maximum des données (défaut: timeout broadcast)
        """
        if max_age is None:
            max_age = CoordinationProtocol.BROADCAST_TIMEOUT

        current_time = time.time()

        # Nettoyer les requêtes
        to_remove = []
        for sender_id, data in self.received_requests.items():
            if current_time - data.get('timestamp', 0) > max_age:
                to_remove.append(sender_id)
        for sender_id in to_remove:
            del self.received_requests[sender_id]

        # Nettoyer les réponses
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
            Dictionnaire du statut de coordination
        """
        current_time = time.time()
        
        return {
            'role': getattr(self.state, 'role', 'unknown'),
            'level': self.state.level,
            'chosen_incanter': self.chosen_incanter_id,
            'chosen_direction': self.chosen_incanter_direction,
            'helpers_confirmed': len(self.confirmed_helpers),
            'required_players': IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1),
            'has_enough_helpers': self.has_enough_helpers(),
            'coordination_timeout': self.is_coordination_timeout(),
            'received_requests': len(self.received_requests),
            'sent_responses': len(self.sent_responses),
            'time_since_start': (current_time - self.coordination_start_time 
                               if self.coordination_start_time else 0)
        }