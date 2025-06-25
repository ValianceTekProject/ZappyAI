##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## coordination - VERSION CORRIGÉE avec timeouts fixes
##

import time
from typing import Dict, List, Any, Optional, Tuple
from protocol.commands import CommandManager, Constants
from utils.logger import logger
from utils.game_state import GameState
from teams.message import Message, MessageType
from teams.message_checker import MessageBus

class CoordinationManager:
    """
    Gestion de l'incantation avec système de rôles - VERSION CORRIGÉE avec timeouts fixes.
    - Incanteurs: peuvent lancer des incantations mais pas en rejoindre d'autres
    - Helpers: aident les incanteurs en se déplaçant vers eux
    - Les helpers choisissent quel incanteur aider et s'y dirigent
    """
    def __init__(self, bus: MessageBus, cmd_mgr: CommandManager, game_state: GameState):
        self.bus = bus
        self.cmd_mgr = cmd_mgr
        self.state = game_state

        # ✅ TIMEOUTS FIXES (pas basés sur fréquence)
        self._message_timeout = 60.0       # 1 minute pour les messages
        self._cleanup_interval = 30.0      # 30 secondes pour le nettoyage
        self._broadcast_cooldown = 5.0     # 5 secondes entre broadcasts

        self._last_broadcast_time = 0.0

        # Incanteurs actifs par niveau: level -> {incanter_id: info}
        self.active_incanters: Dict[int, Dict[str, Dict[str, Any]]] = {}
        
        # Helpers actifs: helper_id -> infos détaillées
        self.helpers_info: Dict[str, Dict[str, Any]] = {}
        
        # Pour les helpers: incanteur choisi à aider
        self.chosen_incanter: Optional[str] = None
        self.chosen_incanter_level: Optional[int] = None
        
        bus.subscribe(MessageType.INCANTATION_REQUEST,  self._on_inc_req)
        bus.subscribe(MessageType.INCANTATION_RESPONSE, self._on_inc_resp)

    def _on_inc_req(self, sender_id: str, data: Dict[str, Any], direction: int):
        """Traite les requêtes d'incantation - CORRIGÉ pour activer le helper"""
        team = data.get("team_id")
        lvl = data.get("level")
        timestamp = data.get("timestamp", time.time())

        # Filter: only messages from MY team
        if team != self.state.team_id:
            return
        
        if lvl != self.state.level:
            return

        sender_id = str(sender_id)
        my_id = str(self.state.agent_id)
        
        # Enregistrer l'incanteur actif
        if lvl not in self.active_incanters:
            self.active_incanters[lvl] = {}
        
        self.active_incanters[lvl][sender_id] = {
            "timestamp": timestamp,
            "direction": direction,
            "required_players": data.get("required_players", 1)
        }
        
        logger.info(f"[Coordination] Incanteur {sender_id} niveau {lvl} enregistré (direction={direction})")

        # Si je suis un HELPER et au bon niveau, je peux aider
        if (hasattr(self.state, 'role') and self.state.role == "helper" and 
            self.state.level == lvl and my_id != sender_id):
            
            # Si je n'ai pas encore choisi d'incanteur OU si c'est le même niveau
            if (self.chosen_incanter is None or 
                self.chosen_incanter_level == lvl):
                
                # Vérification des prérequis avant de répondre
                if not self._can_help_incantation():
                    reply, eta = "busy", None
                    logger.info(f"[Helper] Cannot help incanteur {sender_id} - not enough resources")
                else:
                    # Choisir cet incanteur si pas encore choisi
                    if self.chosen_incanter is None:
                        self.chosen_incanter = sender_id
                        self.chosen_incanter_level = lvl
                        logger.info(f"[Helper] Choisi d'aider l'incanteur {sender_id} niveau {lvl}")
                    
                    # Répondre seulement si c'est MON incanteur choisi
                    if self.chosen_incanter == sender_id:
                        reply, eta = ("here", 0) if direction == 0 else self._prepare_helper_response(direction)
                        
                        # Enregistrer mes infos
                        self.helpers_info[my_id] = {
                            "helping_incanter": sender_id,
                            "status": reply,
                            "eta": eta,
                            "direction": direction,
                            "level": lvl,
                            "timestamp": time.time()
                        }

                        token = Message.create_incantation_response(
                            sender_id=self.state.agent_id,
                            team_id=self.state.team_id,
                            request_sender=sender_id,
                            response=reply,
                            level=self.state.level,
                            eta=eta
                        )
                        self.cmd_mgr.broadcast(token)
                        logger.info(f"[Helper] Envoyé réponse '{reply}' à {sender_id} (eta={eta})")
                    else:
                        # Ignorer car j'aide déjà quelqu'un d'autre
                        logger.debug(f"[Helper] Ignore incanteur {sender_id}, j'aide déjà {self.chosen_incanter}")

    def _can_help_incantation(self) -> bool:
        """Vérification renforcée pour l'aide à l'incantation avec seuils fixes."""
        # ✅ Seuil de sécurité FIXE
        safe_threshold = 25  # Seuil fixe au lieu de self.state._get_safe_food_threshold()
        help_overhead = 15   # Coût estimé de l'aide (réduit)
        required_food = safe_threshold + help_overhead
        
        current_food = self.state.get_food_count()

        if current_food < required_food:
            logger.debug(f"[Helper] Pas assez de nourriture pour aider: {current_food} < {required_food}")
            return False

        # Vérifier qu'on n'est pas déjà au niveau max
        if self.state.level >= 8:
            return False

        # Vérifier qu'on a les ressources de base si niveau 1
        if self.state.level == 1 and self.state.has_missing_resources():
            logger.debug("[Helper] Niveau 1 avec ressources manquantes, priorité à la collecte")
            return False

        return True

    def _prepare_helper_response(self, direction: int) -> Tuple[str, Optional[int]]:
        """Détermine réponse helper avec ETA fixe estimé."""
        if direction == 0:
            return 'here', 0
        
        # ✅ ETA estimé sans calculs de fréquence
        W, H = self.state.dimension_map
        
        # Estimation de distance selon direction (simple)
        if direction in [1, 3, 5, 7]:  # directions cardinales
            estimated_distance = min(W, H) // 8  # Distance estimée conservative
        elif direction in [2, 4, 6, 8]:  # directions diagonales
            estimated_distance = min(W, H) // 6  # Distance estimée conservative
        else:
            estimated_distance = min(W, H) // 4
        
        # ETA en secondes réelles (estimation fixe)
        eta_seconds = max(2, estimated_distance * 2)  # 2 secondes par case estimée
        
        return 'coming', int(eta_seconds)

    def _on_inc_resp(self, sender_id: str, data: Dict[str, Any], direction: int):
        """Traite les réponses d'incantation - uniquement si je suis incanteur"""
        sender_id = str(sender_id)
        my_id = str(self.state.agent_id)
        
        # Seuls les incanteurs traitent les réponses
        if not (hasattr(self.state, 'role') and self.state.role == "incanter"):
            return
        
        lvl = data.get("level")
        resp = data.get('response')
        request_sender = data.get('request_sender')
        timestamp = data.get('timestamp', time.time())
        
        logger.debug(f"[Incanteur] _on_inc_resp reçu de {sender_id}: response={resp}, level={lvl}, request_sender={request_sender}")
        
        if lvl is None or resp is None or lvl != self.state.level:
            return
            
        # Vérifier si la réponse m'est destinée
        if request_sender and str(request_sender) != my_id:
            return
        
        eta = data.get('eta')
        
        # Stocker/mettre à jour les infos du helper
        self.helpers_info[sender_id] = {
            'role': 'helper',
            'status': resp,
            'eta': eta,
            'timestamp': timestamp,
            'direction': direction,
            'level': lvl
        }
        
        logger.info(f"[Incanteur] Helper {sender_id} registered: status={resp}, eta={eta}")

    def send_incant_request(self):
        """Envoie requête avec cooldown fixe pour éviter le spam"""
        if not (hasattr(self.state, 'role') and self.state.role == "incanter"):
            logger.warning("[Coordination] Seuls les incanteurs peuvent envoyer des requêtes")
            return
        
        now = time.time()
        if now - self._last_broadcast_time < self._broadcast_cooldown:
            return  # Cooldown pas encore écoulé
        
        # ✅ Vérification de nourriture avec seuils fixes
        safe_threshold = 25  # Seuil fixe
        estimated_duration = 45.0  # Durée estimée d'incantation en secondes
        food_needed = int(estimated_duration / 20) + 8  # Estimation nourriture nécessaire + marge
        required_food = safe_threshold + food_needed
        
        current_food = self.state.get_food_count()
        
        if current_food < required_food:
            logger.warning(f"[Incanteur] Pas assez de nourriture pour incanter: {current_food} < {required_food}")
            return
            
        lvl = self.state.level
        token = Message.create_incantation_request(
            sender_id=self.state.agent_id,
            team_id=self.state.team_id,
            level=lvl,
            required_players=self.state.get_required_player_count()
        )
        self.cmd_mgr.broadcast(token)
        self._last_broadcast_time = now
        
        logger.debug(f"[Incanteur] Requête envoyée (niveau {lvl}, nourriture: {current_food})")

    def get_my_helpers(self) -> List[str]:
        """Retourne les helpers qui m'aident (pour incanteur) - Timeout fixe"""
        if not (hasattr(self.state, 'role') and self.state.role == "incanter"):
            return []
        
        now = time.time()
        helpers = []
        my_id = str(self.state.agent_id)
        
        for helper_id, info in self.helpers_info.items():
            if helper_id == my_id:
                continue
                
            status = info.get('status')
            timestamp = info.get('timestamp', 0)
            level = info.get('level')
            
            # Vérifier le niveau et la fraîcheur avec timeout fixe
            if level != self.state.level or now - timestamp > self._message_timeout:
                continue

            # Inclure si statut positif
            if status in ('here', 'coming'):
                helpers.append(helper_id)

        return helpers

    def get_helpers_here(self) -> List[str]:
        """Retourne les helpers présents 'here' (pour incanteur)"""
        helpers = self.get_my_helpers()
        here_helpers = []
        
        for helper_id in helpers:
            info = self.helpers_info.get(helper_id, {})
            if info.get('status') == 'here':
                here_helpers.append(helper_id)
        
        return here_helpers

    def has_enough_helpers(self) -> bool:
        """Vérifie si on a assez de helpers 'here' pour l'incantation"""
        if not (hasattr(self.state, 'role') and self.state.role == "incanter"):
            return False

        required = self.state.get_required_player_count()
        here_helpers = self.get_helpers_here()

        result = len(here_helpers) >= required
        return result

    def get_coming_helpers(self) -> List[str]:
        """Retourne les helpers en route 'coming' (pour incanteur)"""
        helpers = self.get_my_helpers()
        coming_helpers = []
        
        for helper_id in helpers:
            info = self.helpers_info.get(helper_id, {})
            if info.get('status') == 'coming':
                coming_helpers.append(helper_id)
        
        return coming_helpers

    def get_chosen_incanter_direction(self) -> Optional[int]:
        """Retourne la direction vers l'incanteur choisi (pour helper)"""
        if not (hasattr(self.state, 'role') and self.state.role == "helper"):
            return None
            
        if not self.chosen_incanter or not self.chosen_incanter_level:
            return None
            
        # Chercher dans les incanteurs actifs
        incanters = self.active_incanters.get(self.chosen_incanter_level, {})
        incanter_info = incanters.get(self.chosen_incanter)
        
        if incanter_info:
            return incanter_info.get('direction')
        
        return None

    def reset_helper_choice(self):
        """Reset le choix d'incanteur pour un helper"""
        if hasattr(self.state, 'role') and self.state.role == "helper":
            self.chosen_incanter = None
            self.chosen_incanter_level = None
            logger.info("[Helper] Reset du choix d'incanteur")

    def cleanup_old_data(self, max_age: Optional[float] = None):
        """Nettoie les données trop anciennes - Intervalle fixe"""
        if max_age is None:
            max_age = self._cleanup_interval
            
        now = time.time()
        
        # Nettoyer les incanteurs
        for level in list(self.active_incanters.keys()):
            incanters = self.active_incanters[level]
            to_remove = []
            for incanter_id, info in incanters.items():
                if now - info.get('timestamp', 0) > max_age:
                    to_remove.append(incanter_id)
            
            for incanter_id in to_remove:
                del incanters[incanter_id]
            
            if not incanters:
                del self.active_incanters[level]
        
        # Nettoyer les helpers
        to_remove = []
        for helper_id, info in self.helpers_info.items():
            if now - info.get('timestamp', 0) > max_age:
                to_remove.append(helper_id)
        
        for helper_id in to_remove:
            del self.helpers_info[helper_id]

    def clear_helpers(self):
        """Nettoie les helpers (pour incanteur après incantation)"""
        if hasattr(self.state, 'role') and self.state.role == "incanter":
            self.helpers_info.clear()
            logger.debug("[Incanteur] Helpers cleared")

    def get_coordination_status(self) -> Dict[str, Any]:
        """Retourne le statut de la coordination pour debug"""
        return {
            'role': getattr(self.state, 'role', 'unknown'),
            'my_level': self.state.level,
            'active_incanters': dict(self.active_incanters),
            'chosen_incanter': self.chosen_incanter,
            'chosen_incanter_level': self.chosen_incanter_level,
            'my_helpers_count': len(self.get_my_helpers()) if hasattr(self.state, 'role') and self.state.role == "incanter" else 0,
            'helpers_here': len(self.get_helpers_here()) if hasattr(self.state, 'role') and self.state.role == "incanter" else 0,
            'has_enough_helpers': self.has_enough_helpers(),
            'timeouts': {
                'message_timeout': self._message_timeout,
                'cleanup_interval': self._cleanup_interval,
                'broadcast_cooldown': self._broadcast_cooldown
            }
        }
