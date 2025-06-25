##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## Planner principal intégrant la FSM de survie
##

import time
from typing import Optional, Any, Dict
from utils.logger import logger
from config import CommandType
from ai.strategy.Basic_ai.fsm_planner import FSMPlanner

class Planner:
    """
    Planner principal intégrant la logique FSM de survie.
    Point d'entrée unique pour toutes les décisions de l'IA.
    """
    
    def __init__(self, command_manager, game_state, message_bus, use_fsm=True):
        """
        Initialise le planner avec option FSM.
        
        Args:
            command_manager: Gestionnaire de commandes
            game_state: État du jeu
            message_bus: Bus de messages pour communication
            use_fsm: Utiliser la FSM (True par défaut)
        """
        self.cmd_mgr = command_manager
        self.state = game_state
        self.bus = message_bus
        self.use_fsm = use_fsm
        
        # Initialisation du planificateur de survie FSM
        if self.use_fsm:
            self.fsm_planner = FSMPlanner(command_manager, game_state, message_bus)
            logger.info("[Planner] FSM de survie initialisée")
        else:
            self.fsm_planner = None
            logger.info("[Planner] Mode classique (sans FSM)")
        
        # Statistiques et debug
        self.total_decisions = 0
        self.last_log_time = time.time()
        self.log_interval = 30.0  # Log toutes les 30 secondes
        
        # État de l'agent pour coordination future
        self.agent_role = getattr(game_state, 'role', 'survivor')  # survivor par défaut
        
    def decide_next_action(self) -> Optional[Any]:
        """
        Point d'entrée principal pour toutes les décisions.
        Utilise la FSM de survie ou fallback selon configuration.
        """
        self.total_decisions += 1
        current_time = time.time()
        
        try:
            # Vérifications préliminaires communes
            if not self._can_make_decision():
                return None
            
            # Log périodique des statistiques
            if current_time - self.last_log_time >= self.log_interval:
                self._log_planner_status()
                self.last_log_time = current_time
            
            # Utiliser FSM de survie si activée
            if self.use_fsm and self.fsm_planner:
                return self._fsm_decision()
            else:
                return self._fallback_decision()
                
        except Exception as e:
            logger.error(f"[Planner] Erreur critique dans decide_next_action: {e}")
            # En cas d'erreur, action de sécurité
            return self._emergency_action()

    def _can_make_decision(self) -> bool:
        """Vérifications préliminaires avant toute décision."""
        # Éviter les décisions si commande déjà envoyée
        if self.state.command_already_send:
            return False
        
        # Limiter le nombre de commandes en attente
        if self.cmd_mgr.get_pending_count() >= 8:
            return False
        
        # Vérifier timing si disponible
        if hasattr(self.cmd_mgr, 'timing') and not self.cmd_mgr.timing.can_execute_action():
            return False
        
        return True

    def _fsm_decision(self) -> Optional[Any]:
        """Décision utilisant la FSM de survie."""
        try:
            action = self.fsm_planner.decide_next_action()
            
            if action is None:
                # FSM ne peut pas décider, utiliser fallback léger
                logger.debug("[Planner] FSM retourne None, fallback minimal")
                return self._minimal_fallback()
            
            return action
            
        except Exception as e:
            logger.error(f"[Planner] Erreur FSM: {e}, fallback d'urgence")
            return self._emergency_action()

    def _fallback_decision(self) -> Optional[Any]:
        """Décision fallback simple sans FSM."""
        # Version simplifiée de la logique de base
        
        # 1. Vision si nécessaire
        if self.state.needs_look or not self.state.get_vision().last_vision_data:
            return self.cmd_mgr.look()
        
        # 2. Inventaire si perte de nourriture suspectée
        if hasattr(self.cmd_mgr, 'timing') and self.cmd_mgr.timing.has_lost_food():
            return self.cmd_mgr.inventory()
        
        # 3. Survie alimentaire basique
        current_food = self.state.get_food_count()
        if current_food <= 10:  # Seuil critique simple
            food_pos = self._find_food_simple()
            if food_pos == (0, 0):
                return self.cmd_mgr.take('food')
            elif food_pos:
                return self._move_towards_simple(food_pos)
        
        # 4. Exploration basique
        return self.cmd_mgr.forward()

    def _minimal_fallback(self) -> Optional[Any]:
        """Fallback minimal quand FSM ne peut pas décider."""
        # Actions de base essentielles
        
        if self.state.needs_look:
            return self.cmd_mgr.look()
        
        current_food = self.state.get_food_count()
        if current_food <= 5:  # Très critique
            return self.cmd_mgr.look()  # Chercher nourriture désespérément
        
        return self.cmd_mgr.forward()  # Explorer basique

    def _emergency_action(self) -> Optional[Any]:
        """Action d'urgence en cas d'erreur critique."""
        logger.error("[Planner] 🚨 ACTION D'URGENCE - Erreur critique détectée")
        
        # Toujours privilégier LOOK en cas de problème
        return self.cmd_mgr.look()

    def _find_food_simple(self) -> Optional[tuple]:
        """Trouve nourriture de manière simple (fallback)."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return None
        
        for data in vision.last_vision_data:
            if 'food' in data.resources and data.resources['food'] > 0:
                return data.rel_pos
        
        return None

    def _move_towards_simple(self, target_pos: tuple) -> Optional[Any]:
        """Mouvement simple vers une position (fallback)."""
        x, y = target_pos
        
        if x > 0:
            return self.cmd_mgr.right()
        elif x < 0:
            return self.cmd_mgr.left()
        elif y < 0:
            return self.cmd_mgr.forward()
        else:
            return self.cmd_mgr.forward()

    def on_command_success(self, command_type, response=None):
        """Notification de succès de commande."""
        if self.use_fsm and self.fsm_planner:
            self.fsm_planner.on_command_success(command_type, response)

    def on_command_failed(self, command_type, response=None):
        """Notification d'échec de commande."""
        if self.use_fsm and self.fsm_planner:
            self.fsm_planner.on_command_failed(command_type, response)

    def on_successful_move(self):
        """Notification de mouvement réussi (compatibilité)."""
        self.on_command_success(CommandType.FORWARD)

    def _log_planner_status(self):
        """Log périodique du statut du planner."""
        current_food = self.state.get_food_count()
        level = self.state.level
        
        if self.use_fsm and self.fsm_planner:
            strategy_info = self.fsm_planner.get_current_strategy_info()
            logger.info(f"[Planner] FSM - État: {strategy_info.get('state', 'unknown')}, "
                       f"Food: {current_food}, Level: {level}, "
                       f"Décisions: {self.total_decisions}")
        else:
            logger.info(f"[Planner] Classique - Food: {current_food}, Level: {level}, "
                       f"Décisions: {self.total_decisions}")

    def get_current_strategy_info(self) -> Dict[str, Any]:
        """Retourne les informations de stratégie actuelles."""
        base_info = {
            'planner_type': 'FSM' if self.use_fsm else 'Classic',
            'total_decisions': self.total_decisions,
            'agent_role': self.agent_role,
            'current_food': self.state.get_food_count(),
            'current_level': self.state.level
        }
        
        if self.use_fsm and self.fsm_planner:
            fsm_info = self.fsm_planner.get_current_strategy_info()
            base_info.update(fsm_info)
        
        return base_info

    def set_agent_role(self, role: str):
        """Définit le rôle de l'agent (pour future coordination)."""
        self.agent_role = role
        if hasattr(self.state, 'role'):
            self.state.role = role
        logger.info(f"[Planner] Rôle agent défini: {role}")

    def switch_to_fsm(self):
        """Active la FSM si elle était désactivée."""
        if not self.use_fsm:
            self.use_fsm = True
            if not self.fsm_planner:
                self.fsm_planner = FSMPlanner(self.cmd_mgr, self.state, self.bus)
            logger.info("[Planner] FSM activée")

    def switch_to_classic(self):
        """Désactive la FSM."""
        if self.use_fsm:
            self.use_fsm = False
            logger.info("[Planner] FSM désactivée, mode classique")

    def get_debug_info(self) -> Dict[str, Any]:
        """Informations détaillées pour debug."""
        debug_info = {
            'planner_config': {
                'use_fsm': self.use_fsm,
                'agent_role': self.agent_role,
                'total_decisions': self.total_decisions
            },
            'state_info': {
                'food': self.state.get_food_count(),
                'level': self.state.level,
                'position': self.state.get_position(),
                'orientation': self.state.get_orientation(),
                'command_pending': self.state.command_already_send,
                'needs_look': getattr(self.state, 'needs_look', False)
            },
            'command_manager': {
                'pending_count': self.cmd_mgr.get_pending_count(),
                'can_send': self.cmd_mgr._can_send() if hasattr(self.cmd_mgr, '_can_send') else 'unknown'
            }
        }
        
        if self.use_fsm and self.fsm_planner:
            debug_info['fsm_info'] = self.fsm_planner.get_current_strategy_info()
        
        return debug_info