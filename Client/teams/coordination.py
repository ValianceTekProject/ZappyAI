##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination - Gestionnaire de coordination simplifié et corrigé
##

import time
from typing import Dict, Any, Optional
from protocol.commands import CommandManager
from utils.logger import logger
from utils.game_state import GameState
from teams.message_checker import MessageBus
from teams.message import Message, MessageType
from constant import (
    CoordinationProtocol, IncantationRequirements, AgentRoles,
    BroadcastDirections, SafetyLimits
)

class CoordinationManager:
    """Gestionnaire de coordination avec protocole simplifié et optimisé"""
    
    def __init__(self, bus: MessageBus, cmd_mgr: CommandManager, game_state: GameState):
        """
        Initialise le gestionnaire de coordination
        
        Args:
            bus: Bus de messages pour la communication
            cmd_mgr: Gestionnaire de commandes
            game_state: État du jeu
        """
        self.bus = bus
        self.cmd_mgr = cmd_mgr
        self.state = game_state
        
        self._last_broadcast_time = 0.0
        self.here_responses: Dict[str, float] = {}
        self.coordination_start_time: Optional[float] = None
        self.last_cleanup = time.time()
        
        self._register_message_handlers()
        
        logger.debug("[CoordinationManager] Initialisé avec protocole simplifié")

    def _register_message_handlers(self):
        """Enregistre les handlers pour les messages de coordination"""
        self.bus.subscribe(MessageType.INCANTATION_REQUEST, self._handle_incantation_request_message)
        self.bus.subscribe(MessageType.INCANTATION_RESPONSE, self._handle_incantation_response_message)

    def _handle_incantation_request_message(self, sender_id: int, data: Dict[str, Any], direction: int):
        """
        Traite les requêtes d'incantation reçues par les helpers
        
        Args:
            sender_id: ID de l'expéditeur
            data: Données du message
            direction: Direction du broadcast
        """
        try:
            sender_id_str = str(sender_id)
            level = data.get("level")
            timestamp = data.get("timestamp", time.time())
            
            if not self._should_respond_to_request(sender_id_str, level, direction, timestamp):
                return
            
            # Seule réponse autorisée : "here" si K=0 (même case)
            if direction == BroadcastDirections.HERE:
                self._send_here_response(sender_id_str, level)
                logger.info(f"[CoordinationManager] 📍 HERE envoyé à {sender_id_str}")
            
        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur handler requête: {e}")

    def _should_respond_to_request(self, sender_id: str, level: int, direction: int, timestamp: float) -> bool:
        """
        Détermine si on doit répondre à une requête d'incantation
        
        Args:
            sender_id: ID de l'expéditeur
            level: Niveau d'incantation
            direction: Direction du broadcast
            timestamp: Timestamp du message
            
        Returns:
            True si on doit répondre
        """
        current_time = time.time()
        
        # Ne pas répondre à ses propres messages
        if sender_id == str(self.state.agent_id):
            return False
            
        # Pas de coordination pour niveau 1
        if level == 1:
            return False
            
        # Vérification timeout du message
        if current_time - timestamp > CoordinationProtocol.COORDINATION_TIMEOUT:
            return False
        
        # Répondre seulement si on est sur la même case (K=0)
        if direction != BroadcastDirections.HERE:
            return False
        
        # Vérification de la nourriture
        current_food = self.state.get_food_count()
        if current_food < SafetyLimits.MIN_FOOD_FOR_COORDINATION_SAFETY:
            return False
        
        # Vérification du niveau
        if self.state.level != level:
            return False
            
        return True

    def _send_here_response(self, request_sender: str, level: int):
        """
        Envoie une réponse 'here' confirmant la présence sur la case
        
        Args:
            request_sender: ID de l'expéditeur de la requête
            level: Niveau d'incantation
        """
        try:
            encoded_message = Message.create_incantation_response(
                sender_id=self.state.agent_id,
                team_id=self.state.team_id,
                request_sender=int(request_sender),
                response=CoordinationProtocol.RESPONSE_HERE,
                level=level
            )
            
            self.cmd_mgr.broadcast(encoded_message)
            self.here_responses[request_sender] = time.time()
            logger.debug(f"[CoordinationManager] HERE envoyé à {request_sender}")
            
        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur envoi HERE: {e}")

    def _handle_incantation_response_message(self, sender_id: int, data: Dict[str, Any], direction: int):
        """
        Traite les réponses d'incantation pour l'incantateur
        
        Args:
            sender_id: ID de l'expéditeur
            data: Données du message
            direction: Direction du broadcast
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return

        try:
            sender_id_str = str(sender_id)
            request_sender = str(data.get("request_sender"))
            response = data.get("response")
            timestamp = data.get("timestamp", time.time())
            
            # Vérifier que c'est une réponse à notre requête
            if request_sender != str(self.state.agent_id):
                return

            # Vérifier timeout
            if time.time() - timestamp > CoordinationProtocol.COORDINATION_TIMEOUT:
                return

            # Traiter uniquement les réponses "here"
            if response == CoordinationProtocol.RESPONSE_HERE:
                self.here_responses[sender_id_str] = time.time()
                logger.info(f"[CoordinationManager] ✅ HERE reçu de {sender_id_str}")

        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur traitement réponse: {e}")

    def send_incantation_request(self):
        """
        Envoie une requête d'incantation (incantateur uniquement)
        Spam continu selon les spécifications
        """
        if not hasattr(self.state, 'role'):
            logger.error("[CoordinationManager] ERREUR: Attribut 'role' manquant dans GameState")
            return
            
        current_role = getattr(self.state, 'role', 'unknown')
        
        if current_role != AgentRoles.INCANTER:
            return

        if self.state.level == 1:
            return

        current_time = time.time()
        
        # Vérification du cooldown réduit pour spam continu
        if current_time - self._last_broadcast_time < CoordinationProtocol.INCANTER_BROADCAST_COOLDOWN:
            return

        current_food = self.state.get_food_count()
        if current_food < CoordinationProtocol.MIN_FOOD_TO_COORDINATE:
            return

        level = self.state.level
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(level, 1)
        
        if required_players <= 1:
            return
        
        # if self.coordination_start_time is None:
        #     self.coordination_start_time = current_time
        #     logger.info(f"[CoordinationManager] 🚀 Début coordination niveau {level}")
            
        try:
            encoded_message = Message.create_incantation_request(
                sender_id=self.state.agent_id,
                team_id=self.state.team_id,
                level=level,
                required_players=required_players
            )
            
            if not encoded_message:
                logger.error("[CoordinationManager] ERREUR: Message encodé vide!")
                return
            
            self.cmd_mgr.broadcast(encoded_message)
            self._last_broadcast_time = current_time
            
            logger.info(f"[CoordinationManager] 📢 Broadcast envoyé - Niveau: {level}")
            
        except Exception as e:
            logger.error(f"[CoordinationManager] Erreur envoi requête: {e}")

    def get_helpers_here_count(self) -> int:
        """
        Retourne le nombre de helpers confirmés présents sur la case
        
        Returns:
            Nombre de helpers qui ont confirmé leur présence
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return 0

        self._cleanup_old_responses()
        
        current_time = time.time()
        valid_count = 0

        for helper_id, response_time in self.here_responses.items():
            if current_time - response_time <= CoordinationProtocol.COORDINATION_TIMEOUT:
                valid_count += 1

        return valid_count

    def has_enough_helpers(self) -> bool:
        """
        Vérifie si on a assez de helpers confirmés présents
        
        Returns:
            True si assez de helpers sont présents
        """
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return False

        if self.state.level == 1:
            return True

        required = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        helpers_needed = required - 1
        
        here_count = self.get_helpers_here_count()
        
        # Vérification additionnelle avec la vision physique
        vision = self.state.get_vision()
        players_on_tile = 1
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                players_on_tile = data.players
                break
        
        has_enough = here_count >= helpers_needed or players_on_tile >= required
        
        return has_enough

    def _cleanup_old_responses(self):
        """Nettoie les anciennes réponses expirées"""
        current_time = time.time()
        
        if current_time - self.last_cleanup < 2.0:
            return
            
        self.last_cleanup = current_time

        expired_here = [
            helper_id for helper_id, response_time in self.here_responses.items()
            if current_time - response_time > CoordinationProtocol.COORDINATION_TIMEOUT
        ]
        
        for helper_id in expired_here:
            del self.here_responses[helper_id]
            logger.debug(f"[CoordinationManager] Nettoyage réponse expirée de {helper_id}")

    def clear_coordination_data(self):
        """Nettoie toutes les données de coordination"""
        self.here_responses.clear()
        self.coordination_start_time = None
        self._last_broadcast_time = 0.0
        logger.debug("[CoordinationManager] Données coordination nettoyées")

    def is_coordination_timeout(self) -> bool:
        """
        Vérifie si la coordination a expiré
        
        Returns:
            True si la coordination a timeout
        """
        if self.coordination_start_time is None:
            return False
        return time.time() - self.coordination_start_time > CoordinationProtocol.COORDINATION_TIMEOUT

    def get_coordination_status(self) -> Dict[str, Any]:
        """
        Retourne le statut de coordination pour debug
        
        Returns:
            Dictionnaire du statut de coordination
        """
        current_time = time.time()
        
        return {
            'role': getattr(self.state, 'role', 'unknown'),
            'level': self.state.level,
            'here_responses_count': len(self.here_responses),
            'here_responses': dict(self.here_responses),
            'coordination_duration': (
                current_time - self.coordination_start_time 
                if self.coordination_start_time else 0
            ),
            'last_broadcast': current_time - self._last_broadcast_time,
            'has_enough_helpers': self.has_enough_helpers(),
            'is_timeout': self.is_coordination_timeout()
        }