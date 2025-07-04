##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination - Gestionnaire de coordination amélioré avec fallbacks
##

import time
from typing import Dict, List, Any, Optional, Tuple
from protocol.commands import CommandManager
from utils.logger import logger
from utils.game_state import GameState
from teams.message import Message, MessageType
from teams.message_checker import MessageBus
from constant import (
    CoordinationMessages, IncantationRequirements, AgentRoles,
    StateTransitionThresholds, CoordinationStrategy
)


class CoordinationManager:
    """
    Gestion de coordination améliorée avec mécanismes de récupération.
    """
    
    def __init__(self, bus: MessageBus, cmd_mgr: CommandManager, game_state: GameState):
        self.bus = bus
        self.cmd_mgr = cmd_mgr
        self.state = game_state
        
        # Configuration des timeouts optimisés
        self._message_timeout = CoordinationMessages.MESSAGE_TIMEOUT
        self._cleanup_interval = CoordinationMessages.CLEANUP_INTERVAL
        self._broadcast_cooldown = CoordinationMessages.BROADCAST_COOLDOWN
        self._last_broadcast_time = 0.0
        
        # Données de coordination
        self.active_incanters: Dict[int, Dict[str, Dict[str, Any]]] = {}
        self.helpers_info: Dict[str, Dict[str, Any]] = {}
        
        # Pour les helpers avec gestion d'échec
        self.chosen_incanter: Optional[str] = None
        self.chosen_incanter_level: Optional[int] = None
        self.helper_attempts: Dict[str, int] = {}  # Compteur de tentatives par incanteur
        self.max_helper_attempts = CoordinationStrategy.MAX_COORDINATION_ATTEMPTS
        
        # Pour les incanteurs avec gestion de timeout
        self.incanter_start_time: Optional[float] = None
        self.max_wait_time = CoordinationStrategy.MAX_WAIT_FOR_HELPERS
        
        # Abonnements aux messages
        bus.subscribe(MessageType.INCANTATION_REQUEST, self._on_inc_req)
        bus.subscribe(MessageType.INCANTATION_RESPONSE, self._on_inc_resp)
        
        logger.debug("[CoordinationManager] Initialisé avec timeouts optimisés")

    def _on_inc_req(self, sender_id: str, data: Dict[str, Any], direction: int):
        """Traite les requêtes d'incantation avec vérifications renforcées."""
        team = data.get("team_id")
        lvl = data.get("level")
        timestamp = data.get("timestamp", time.time())

        # Vérifications de base
        if team != self.state.team_id or lvl != self.state.level:
            return

        # Ignorer les requêtes pour niveau 1 (solo autorisé)
        if lvl == 1:
            logger.debug("[CoordinationManager] Ignore requête niveau 1 (solo)")
            return

        # Vérifier que le message n'est pas trop ancien
        if time.time() - timestamp > self._message_timeout:
            logger.debug("[CoordinationManager] Message trop ancien, ignoré")
            return

        sender_id = str(sender_id)
        my_id = str(self.state.agent_id)

        # Ne pas traiter sa propre requête
        if sender_id == my_id:
            return

        # Enregistrer l'incanteur
        if lvl not in self.active_incanters:
            self.active_incanters[lvl] = {}

        self.active_incanters[lvl][sender_id] = {
            "timestamp": timestamp,
            "direction": direction,
            "required_players": data.get("required_players", 1)
        }

        logger.info(f"[CoordinationManager] Incanteur {sender_id} niveau {lvl} (dir={direction})")

        # Répondre si on est disponible pour aider
        if (hasattr(self.state, 'role') and self.state.role == AgentRoles.HELPER and
            self.state.level == lvl and my_id != sender_id):
            
            self._handle_incantation_request(sender_id, direction, lvl)

    def _handle_incantation_request(self, sender_id: str, direction: int, level: int):
        """Gère une requête d'incantation avec logique de sélection d'incanteur."""
        # Vérifier si on peut aider
        if not self._can_help_incantation():
            self._send_busy_response(sender_id, level)
            return

        # Si on n'a pas encore choisi d'incanteur ou si c'est un meilleur choix
        should_help = False
        
        if self.chosen_incanter is None:
            # Pas d'incanteur choisi, accepter
            should_help = True
        elif self.chosen_incanter == sender_id:
            # Même incanteur, continuer à l'aider
            should_help = True
        else:
            # Comparer avec l'incanteur actuel
            current_attempts = self.helper_attempts.get(self.chosen_incanter, 0)
            new_attempts = self.helper_attempts.get(sender_id, 0)
            
            # Changer si l'incanteur actuel a trop échoué
            if current_attempts >= self.max_helper_attempts and new_attempts < current_attempts:
                logger.info(f"[CoordinationManager] Changement d'incanteur: {self.chosen_incanter} → {sender_id}")
                should_help = True

        if should_help:
            self._respond_to_incantation_request(sender_id, direction, level)
        else:
            self._send_busy_response(sender_id, level)

    def _respond_to_incantation_request(self, sender_id: str, direction: int, level: int):
        """Répond positivement à une requête d'incantation."""
        self.chosen_incanter = sender_id
        self.chosen_incanter_level = level
        
        logger.info(f"[CoordinationManager] Aide incanteur {sender_id} niveau {level}")

        reply, eta = self._prepare_helper_response(direction)

        # Enregistrer notre réponse
        self.helpers_info[str(self.state.agent_id)] = {
            "helping_incanter": sender_id,
            "status": reply,
            "eta": eta,
            "direction": direction,
            "level": level,
            "timestamp": time.time()
        }

        # Envoyer la réponse
        token = Message.create_incantation_response(
            sender_id=self.state.agent_id,
            team_id=self.state.team_id,
            request_sender=sender_id,
            response=reply,
            level=level,
            eta=eta
        )
        self.cmd_mgr.broadcast(token)
        logger.info(f"[CoordinationManager] Réponse '{reply}' envoyée (eta={eta})")

    def _send_busy_response(self, sender_id: str, level: int):
        """Envoie une réponse 'busy' à une requête d'incantation."""
        token = Message.create_incantation_response(
            sender_id=self.state.agent_id,
            team_id=self.state.team_id,
            request_sender=sender_id,
            response=CoordinationMessages.RESPONSE_BUSY,
            level=level
        )
        self.cmd_mgr.broadcast(token)
        logger.debug(f"[CoordinationManager] Réponse 'busy' à {sender_id}")

    def _can_help_incantation(self) -> bool:
        """Vérification stricte pour l'aide à l'incantation."""
        current_food = self.state.get_food_count()
        required_food = CoordinationMessages.MIN_FOOD_TO_HELP
        
        # Vérification nourriture
        if current_food < required_food:
            logger.debug(f"[CoordinationManager] Pas assez de nourriture: {current_food} < {required_food}")
            return False
            
        # Vérification niveau
        if self.state.level >= 8:
            logger.debug("[CoordinationManager] Niveau max atteint")
            return False
            
        if self.state.level == 1:
            logger.debug("[CoordinationManager] Niveau 1 ne peut pas aider")
            return False
            
        return True

    def _prepare_helper_response(self, direction: int) -> Tuple[str, Optional[int]]:
        """Détermine la réponse du helper avec ETA optimisé."""
        if direction == 0:
            return CoordinationMessages.RESPONSE_HERE, 0

        # Estimation de distance selon la direction
        W, H = self.state.dimension_map

        if direction in [1, 3, 5, 7]:  # Directions adjacentes
            estimated_distance = min(W, H) // 10  # Plus optimiste
        elif direction in [2, 4, 6, 8]:  # Directions diagonales
            estimated_distance = min(W, H) // 8   # Plus optimiste
        else:
            estimated_distance = min(W, H) // 6   # Plus optimiste

        eta_seconds = max(1, estimated_distance)  # Minimum 1 seconde
        return CoordinationMessages.RESPONSE_COMING, int(eta_seconds)

    def _on_inc_resp(self, sender_id: str, data: Dict[str, Any], direction: int):
        """Traite les réponses d'incantation - pour incanteurs seulement."""
        sender_id = str(sender_id)
        my_id = str(self.state.agent_id)

        # Seulement si je suis incanteur
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return

        lvl = data.get("level")
        resp = data.get('response')
        request_sender = data.get('request_sender')
        timestamp = data.get('timestamp', time.time())

        # Vérifier que la réponse nous est destinée
        if (lvl != self.state.level or 
            request_sender and str(request_sender) != my_id):
            return

        # Vérifier que le message n'est pas trop ancien
        if time.time() - timestamp > self._message_timeout:
            return

        eta = data.get('eta')

        # Enregistrer le helper
        self.helpers_info[sender_id] = {
            'role': AgentRoles.HELPER,
            'status': resp,
            'eta': eta,
            'timestamp': timestamp,
            'direction': direction,
            'level': lvl
        }

        logger.info(f"[CoordinationManager] Helper {sender_id}: {resp} (eta={eta})")

    def send_incant_request(self):
        """Envoie une requête d'incantation avec vérifications optimisées."""
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            logger.warning("[CoordinationManager] Seuls les incanteurs peuvent envoyer des requêtes")
            return

        # Pas de requête pour niveau 1 (solo autorisé)
        if self.state.level == 1:
            logger.debug("[CoordinationManager] Pas de requête niveau 1 (solo)")
            return

        current_time = time.time()
        
        # Cooldown entre broadcasts
        if current_time - self._last_broadcast_time < self._broadcast_cooldown:
            return

        # Vérifications de sécurité
        current_food = self.state.get_food_count()
        min_food_required = CoordinationMessages.MIN_FOOD_TO_INITIATE
        if current_food < min_food_required:
            logger.warning(f"[CoordinationManager] Pas assez de nourriture: {current_food} < {min_food_required}")
            return

        lvl = self.state.level
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(lvl, 1)
        
        # Seulement pour niveaux multi-joueurs
        if required_players <= 1:
            logger.debug(f"[CoordinationManager] Niveau {lvl} ne nécessite pas de coordination")
            return
        
        # Enregistrer le début de l'incantation si c'est la première fois
        if self.incanter_start_time is None:
            self.incanter_start_time = current_time
        
        token = Message.create_incantation_request(
            sender_id=self.state.agent_id,
            team_id=self.state.team_id,
            level=lvl,
            required_players=required_players
        )
        self.cmd_mgr.broadcast(token)
        self._last_broadcast_time = current_time
        
        logger.info(f"[CoordinationManager] Requête niveau {lvl} envoyée ({required_players} joueurs)")

    def get_my_helpers(self) -> List[str]:
        """Retourne les helpers actifs qui m'aident."""
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return []

        current_time = time.time()
        helpers = []
        my_id = str(self.state.agent_id)

        for helper_id, info in self.helpers_info.items():
            if helper_id == my_id:
                continue
                
            status = info.get('status')
            timestamp = info.get('timestamp', 0)
            level = info.get('level')

            # Vérifier validité temporelle et niveau
            if (level == self.state.level and 
                current_time - timestamp <= self._message_timeout and
                status in (CoordinationMessages.RESPONSE_HERE, CoordinationMessages.RESPONSE_COMING)):
                helpers.append(helper_id)

        return helpers

    def get_helpers_here(self) -> List[str]:
        """Retourne les helpers présents 'here'."""
        helpers = self.get_my_helpers()
        here_helpers = []

        for helper_id in helpers:
            info = self.helpers_info.get(helper_id, {})
            if info.get('status') == CoordinationMessages.RESPONSE_HERE:
                here_helpers.append(helper_id)

        return here_helpers

    def has_enough_helpers(self) -> bool:
        """Vérifie si on a assez de helpers 'here' pour l'incantation."""
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER):
            return False

        # Niveau 1 = solo, pas besoin d'helpers
        if self.state.level == 1:
            return True

        required = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        here_helpers = self.get_helpers_here()

        # Compter l'incanteur lui-même
        total_players = len(here_helpers) + 1

        result = total_players >= required
        logger.debug(f"[CoordinationManager] Joueurs: {total_players}/{required} (helpers ici: {len(here_helpers)})")

        return result

    def get_coming_helpers(self) -> List[str]:
        """Retourne les helpers en route 'coming'."""
        helpers = self.get_my_helpers()
        coming_helpers = []

        for helper_id in helpers:
            info = self.helpers_info.get(helper_id, {})
            if info.get('status') == CoordinationMessages.RESPONSE_COMING:
                coming_helpers.append(helper_id)

        return coming_helpers

    def get_chosen_incanter_direction(self) -> Optional[int]:
        """Retourne la direction vers l'incanteur choisi (pour helper)."""
        if not (hasattr(self.state, 'role') and self.state.role == AgentRoles.HELPER):
            return None

        if not self.chosen_incanter or not self.chosen_incanter_level:
            return None

        incanters = self.active_incanters.get(self.chosen_incanter_level, {})
        incanter_info = incanters.get(self.chosen_incanter)

        if incanter_info:
            return incanter_info.get('direction')

        return None

    def reset_helper_choice(self):
        """Reset le choix d'incanteur pour un helper."""
        if hasattr(self.state, 'role') and self.state.role == AgentRoles.HELPER:
            if self.chosen_incanter:
                # Incrémenter le compteur d'échecs pour cet incanteur
                self.helper_attempts[self.chosen_incanter] = self.helper_attempts.get(self.chosen_incanter, 0) + 1
                logger.info(f"[CoordinationManager] Échec avec {self.chosen_incanter} (tentative {self.helper_attempts[self.chosen_incanter]})")
            
            self.chosen_incanter = None
            self.chosen_incanter_level = None
            logger.info("[CoordinationManager] Reset choix incanteur")

    def cleanup_old_data(self, max_age: Optional[float] = None):
        """Nettoie les données trop anciennes avec gestion d'échecs."""
        if max_age is None:
            max_age = self._cleanup_interval

        current_time = time.time()

        # Nettoyer les incanteurs
        for level in list(self.active_incanters.keys()):
            incanters = self.active_incanters[level]
            to_remove = []
            for incanter_id, info in incanters.items():
                if current_time - info.get('timestamp', 0) > max_age:
                    to_remove.append(incanter_id)
            for incanter_id in to_remove:
                del incanters[incanter_id]
            if not incanters:
                del self.active_incanters[level]

        # Nettoyer les helpers
        to_remove = []
        for helper_id, info in self.helpers_info.items():
            if current_time - info.get('timestamp', 0) > max_age:
                to_remove.append(helper_id)
        for helper_id in to_remove:
            del self.helpers_info[helper_id]

        # Nettoyer les tentatives trop anciennes
        for incanter_id in list(self.helper_attempts.keys()):
            if incanter_id not in [info.get('helping_incanter') for info in self.helpers_info.values()]:
                if self.helper_attempts[incanter_id] > self.max_helper_attempts:
                    del self.helper_attempts[incanter_id]

    def clear_helpers(self):
        """Nettoie les helpers (pour incanteur après incantation)."""
        if hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER:
            self.helpers_info.clear()
            self.incanter_start_time = None
            logger.debug("[CoordinationManager] Helpers cleared")

    def is_coordination_needed(self) -> bool:
        """Vérifie si la coordination est nécessaire pour le niveau actuel."""
        if self.state.level == 1:
            return False
        
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        return required_players > 1

    def can_initiate_coordination(self) -> bool:
        """Vérifie si l'agent peut initier une coordination."""
        if not self.is_coordination_needed():
            return False
            
        current_food = self.state.get_food_count()
        min_food_required = CoordinationMessages.MIN_FOOD_TO_INITIATE
        
        if current_food < min_food_required:
            return False

        # Vérifier qu'on a toutes les ressources
        if self.state.has_missing_resources():
            return False

        return True

    def is_coordination_timeout(self) -> bool:
        """Vérifie si la coordination a expiré (pour incanteur)."""
        if (hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER and
            self.incanter_start_time is not None):
            return time.time() - self.incanter_start_time > self.max_wait_time
        return False

    def get_coordination_status(self) -> Dict[str, Any]:
        """Retourne le statut de la coordination pour debug."""
        current_time = time.time()
        
        status = {
            'role': getattr(self.state, 'role', 'unknown'),
            'my_level': self.state.level,
            'coordination_needed': self.is_coordination_needed(),
            'can_initiate': self.can_initiate_coordination(),
            'active_incanters': dict(self.active_incanters),
            'chosen_incanter': self.chosen_incanter,
            'chosen_incanter_level': self.chosen_incanter_level,
            'helper_attempts': dict(self.helper_attempts),
            'required_players': IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        }
        
        if hasattr(self.state, 'role') and self.state.role == AgentRoles.INCANTER:
            status.update({
                'my_helpers_count': len(self.get_my_helpers()),
                'helpers_here': len(self.get_helpers_here()),
                'has_enough_helpers': self.has_enough_helpers(),
                'coordination_timeout': self.is_coordination_timeout(),
                'wait_time': current_time - self.incanter_start_time if self.incanter_start_time else 0
            })
        elif hasattr(self.state, 'role') and self.state.role == AgentRoles.HELPER:
            status.update({
                'can_help': self._can_help_incantation(),
                'chosen_direction': self.get_chosen_incanter_direction()
            })
            
        return status
