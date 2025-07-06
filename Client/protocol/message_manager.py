##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## message_manager - Gestionnaire de messages simplifié

import time
from typing import List, Any, Optional
from utils.logger import logger
from teams.message import Message, MessageType
from protocol.parser import Parser

class MessageManager:
    """Gestionnaire des messages et broadcasts avec coordination simplifiée"""
    
    def __init__(self, cmd_mgr, bus, state):
        self.cmd_mgr = cmd_mgr
        self.bus = bus
        self.state = state
        self.is_dead = False
        self.coordination_state = None

    def set_coordination_state(self, coordination_state):
        """Définit la référence vers l'état de coordination actuel"""
        self.coordination_state = coordination_state

    def process_responses(self, raw_responses: List[str]) -> Optional[List[str]]:
        """
        Traite les réponses du serveur et dispatche les broadcasts
        
        Args:
            raw_responses: Liste des réponses brutes du serveur
            
        Returns:
            Liste des réponses de commandes traitées ou None si mort
        """
        command_responses = []
        
        for response in raw_responses:
            response = response.strip()
            
            if Parser.is_dead_response(response):
                self.is_dead = True
                return None
                
            if Parser.is_broadcast(response):
                self._handle_broadcast_message(response)
            else:
                command_responses.append(response)
                
        return self.cmd_mgr.process_responses(command_responses)

    def _handle_broadcast_message(self, response: str):
        """
        Traite un message de broadcast reçu
        
        Args:
            response: Réponse de broadcast brute du serveur
        """
        try:
            logger.info(f"[MessageManager] 📢 Broadcast reçu: {response}")
            broadcast_data = Parser.parse_broadcast_response(response)
            if not broadcast_data:
                return
            
            direction = broadcast_data.get("direction")
            token = broadcast_data.get("message")
            
            if direction is None or not token:
                return
                
            decoded = Message.decode_msg(token)
            if not decoded:
                self.bus.publish_raw(direction, token)
                return
                
            msg_type, sender_id, payload = decoded
            
            if self._should_handle_coordination_message(msg_type):
                self._handle_coordination_broadcast(sender_id, payload, direction)
            
            self.bus.publish_raw(direction, token)
            
        except Exception as e:
            logger.error(f"[MessageManager] Erreur traitement broadcast: {e}")

    def _should_handle_coordination_message(self, msg_type: MessageType) -> bool:
        """
        Détermine si un message doit être traité par la coordination
        
        Args:
            msg_type: Type de message reçu
            
        Returns:
            True si le message doit être traité par la coordination
        """
        return (msg_type in [MessageType.INCANTATION_REQUEST, MessageType.INCANTATION_RESPONSE])

    def _handle_coordination_broadcast(self, sender_id: int, payload: dict, direction: int):
        try:
            logger.info(f"[MessageManager] 📢 Broadcast coordination reçu: {payload}")

            if hasattr(self.coordination_state, 'handle_broadcast_message'):
                logger.info(f"[MessageManager] 📢 Transmis à la coordination active")
                self.coordination_state.handle_broadcast_message(sender_id, payload, direction)
            else:
                logger.info(f"[MessageManager] 📢 Pas en coordination, flag coordination à True si besoin - level {self.state.level} : {payload.get('level')}")
                if payload.get('level') == self.state.level:
                    logger.info("[MessageManager] 📢 Flag coordination déjà à True")
                    self.join_incantation = True
                    self.direction_incant = direction

        except Exception as e:
            logger.error(f"[MessageManager] Erreur transmission coordination: {e}")


    def broadcast_message(self, msg_type: MessageType, sender_id: int, team_id: str, **kwargs: Any) -> None:
        """
        Envoie un message via broadcast
        
        Args:
            msg_type: Type de message à envoyer
            sender_id: ID de l'expéditeur
            team_id: ID de l'équipe
            **kwargs: Données additionnelles du message
        """
        try:
            token = Message.encode_msg(msg_type, sender_id, {
                'team_id': team_id,
                **kwargs,
                'timestamp': time.time()
            })
            
            if token:
                self.cmd_mgr.broadcast(token)
                
        except Exception as e:
            logger.error(f"[MessageManager] Erreur envoi broadcast: {e}")