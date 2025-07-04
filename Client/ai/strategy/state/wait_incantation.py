##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## wait_incantation - État d'attente d'incantation
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from config import CommandType
from constant import AgentRoles, TimingConstants
from utils.logger import logger

class WaitIncantationState(State):
    """
    État d'attente d'incantation pour les helpers.
    
    Cet état est activé quand un helper a rejoint un incanteur
    et attend que l'incantation commence.
    """
    
    def __init__(self, planner):
        super().__init__(planner)
        self.wait_start_time = time.time()
        self.last_check_time = time.time()
        self.check_interval = 2.0
        self.max_wait_time = TimingConstants.COORDINATION_TIMEOUT
        
        # S'assurer qu'on a le bon rôle
        self.state.role = AgentRoles.HELPER
        
        logger.info("[WaitIncantationState] ⏳ Attente d'incantation activée")

    def execute(self) -> Optional[Any]:
        """
        Logique d'attente d'incantation.
        """
        current_time = time.time()
        
        # Timeout de l'attente
        if self._is_wait_timeout():
            logger.warning("[WaitIncantationState] Timeout d'attente, abandon")
            return None
        
        # Vérification périodique de l'inventaire
        if self._should_check_inventory(current_time):
            self.last_check_time = current_time
            return self.cmd_mgr.inventory()
        
        # Vérification de la vision si nécessaire
        if self._needs_vision_update():
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()
        
        # Vérifier si on a assez de nourriture pour continuer à attendre
        current_food = self.state.get_food_count()
        if current_food < 15:  # Seuil minimum pour continuer à aider
            logger.warning(f"[WaitIncantationState] Nourriture insuffisante ({current_food}), abandon attente")
            return None
        
        # Attendre tranquillement
        return None

    def _is_wait_timeout(self) -> bool:
        """Vérifie si l'attente a expiré."""
        return (time.time() - self.wait_start_time > self.max_wait_time)

    def _should_check_inventory(self, current_time: float) -> bool:
        """Détermine si on doit vérifier l'inventaire."""
        return (current_time - self.last_check_time >= self.check_interval)

    def _needs_vision_update(self) -> bool:
        """Détermine si une mise à jour de vision est nécessaire."""
        if self.context.get('needs_vision_update', False):
            return True
        
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return True
            
        if getattr(self.state, 'needs_look', False):
            return True
            
        return False

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes."""
        if command_type == CommandType.INVENTORY:
            logger.debug("[WaitIncantationState] ✅ Inventaire vérifié")
            
        elif command_type == CommandType.LOOK:
            logger.debug("[WaitIncantationState] ✅ Vision mise à jour")

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes."""
        if command_type == CommandType.INVENTORY:
            logger.warning("[WaitIncantationState] ❌ Échec vérification inventaire")
            
        elif command_type == CommandType.LOOK:
            logger.warning("[WaitIncantationState] ❌ Échec mise à jour vision")

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements pendant l'attente."""
        if event == Event.FOOD_EMERGENCY:
            logger.error("[WaitIncantationState] URGENCE ALIMENTAIRE! Abandon attente")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)
            
        elif event == Event.FOOD_LOW:
            current_food = self.state.get_food_count()
            if current_food < 20:
                logger.warning("[WaitIncantationState] Nourriture faible, abandon attente")
                from ai.strategy.state.collect_food import CollectFoodState
                return CollectFoodState(self.planner)
                
        elif event == Event.INCANT_SUCCESS:
            logger.info("[WaitIncantationState] 🎉 Incantation réussie!")
            from ai.strategy.state.explore import ExploreState
            return ExploreState(self.planner)
            
        elif event == Event.INCANT_FAILED:
            logger.warning("[WaitIncantationState] ❌ Incantation échouée")
            from ai.strategy.state.explore import ExploreState
            return ExploreState(self.planner)
        
        return None

    def should_transition_to_exploration(self) -> bool:
        """Détermine si on doit retourner en exploration."""
        current_food = self.state.get_food_count()
        
        # Si timeout ou nourriture faible
        if self._is_wait_timeout() or current_food < 15:
            return True
            
        return False

    def on_enter(self):
        """Actions à l'entrée de l'état."""
        super().on_enter()
        current_food = self.state.get_food_count()
        
        logger.info(f"[WaitIncantationState] ⏳ ENTRÉE attente incantation - "
                   f"Food: {current_food}, Niveau: {self.state.level}")
        
        self.wait_start_time = time.time()
        self.last_check_time = time.time()
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie de l'état."""
        super().on_exit()
        wait_duration = time.time() - self.wait_start_time
        
        logger.info(f"[WaitIncantationState] ✅ SORTIE attente incantation - "
                   f"Durée: {wait_duration:.1f}s")