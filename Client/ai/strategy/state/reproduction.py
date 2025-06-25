##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## Reproduction State - CORRIGÉ sans dépendance fréquence
##

import time
from typing import Any, Optional
from config import CommandType
from utils.logger import logger
from Client.ai.strategy.state.fsm import State, Event

class ReproductionState(State):
    """État de reproduction - CORRIGÉ sans calculs de fréquence."""
    
    def __init__(self, planner):
        super().__init__(planner)
        
        # ✅ SEUILS FIXES LOGIQUES (pas de calculs de fréquence)
        self.min_food_for_fork = 20      # Minimum pour fork
        self.safe_food_threshold = 30    # Seuil de sécurité
        
        # État de reproduction
        self.fork_stage = 0  # 0: check_slots, 1: analyze_response, 2: fork_action, 3: wait_completion
        self.reproduction_attempts = 0
        self.max_attempts = 8
        
        # ✅ TIMEOUTS FIXES EN SECONDES RÉELLES
        self.command_timeout = 15.0      # 15 secondes par commande
        self.fork_timeout = 45.0         # 45 secondes pour fork
        
        # Tracking
        self.stage_start_time = time.time()
        
    def on_enter(self):
        current_food = self._get_real_food_count()
        logger.info(f"[{self.role}] ⇒ REPRODUCTION enter - Food: {current_food}")
        
        # ✅ Vérifications initiales strictes
        if not self._can_start_reproduction():
            logger.warning("[Reproduction] Conditions non remplies pour reproduction")
            return
        
        # Reset état
        self.fork_stage = 0
        self.reproduction_attempts = 0
        self.stage_start_time = time.time()
        
    def on_event(self, event: Event) -> Optional[State]:
        from ai.strategy.state.emergency import EmergencyState
        from ai.strategy.state.explore import ExploreState
        
        # ✅ Urgence alimentaire prioritaire avec seuil fixe
        current_food = self._get_real_food_count()
        if event == Event.FOOD_CRITICAL or current_food <= 5:
            logger.warning(f"[Reproduction] Urgence alimentaire - abandon reproduction (Food: {current_food})")
            self._reset_reproduction()
            return EmergencyState(self.planner)
            
        # ✅ Sortie si plus besoin de reproduction
        if not self.state.needs_repro:
            logger.info("[Reproduction] Plus besoin de reproduction")
            return ExploreState(self.planner)
            
        return None
        
    def execute(self) -> Optional[Any]:
        self.reproduction_attempts += 1
        current_time = time.time()
        current_food = self._get_real_food_count()
        
        # ✅ Timeout global pour éviter boucles infinies
        if self.reproduction_attempts > self.max_attempts:
            logger.warning(f"[Reproduction] Timeout après {self.reproduction_attempts} tentatives")
            self._reset_reproduction()
            return None
        
        # ✅ Timeout par stage avec temps fixes
        stage_duration = current_time - self.stage_start_time
        if stage_duration > self.command_timeout:
            logger.warning(f"[Reproduction] Timeout stage {self.fork_stage} après {stage_duration:.1f}s")
            if self.fork_stage < 2:  # Réessayer si pas encore en fork
                self.fork_stage = 0
                self.stage_start_time = current_time
            else:
                self._reset_reproduction()
                return None

        logger.debug(f"[Reproduction] Tentative {self.reproduction_attempts}/{self.max_attempts}, Stage: {self.fork_stage}, Food: {current_food}")
        
        # ✅ Vérifications de base prioritaires
        if self.state.needs_look:
            logger.debug("[Reproduction] 👁️ LOOK requis")
            return self.cmd_mgr.look()
            
        # ✅ Gestion par stages avec logique robuste
        return self._handle_reproduction_stages(current_time, current_food)

    def _handle_reproduction_stages(self, current_time: float, current_food: int) -> Optional[Any]:
        """✅ Gère les stages de reproduction avec logique complète."""
        
        # ✅ Stage 0: Vérifier les slots disponibles
        if self.fork_stage == 0:
            logger.info("[Reproduction] Stage 0: Vérification des slots disponibles")
            self.fork_stage = 1
            self.stage_start_time = current_time
            return self.cmd_mgr.connect_nbr()
            
        # ✅ Stage 1: Analyser la réponse connect_nbr et décider
        elif self.fork_stage == 1:
            last_connect = self.cmd_mgr.get_last_success(CommandType.CONNECT_NBR)
            if not last_connect:
                # Attendre la réponse
                logger.debug("[Reproduction] Stage 1: Attente réponse connect_nbr")
                return None
                
            try:
                slots = int(last_connect.response.strip())
                logger.info(f"[Reproduction] Stage 1: Slots disponibles: {slots}")
                
                # ✅ Logique de décision améliorée
                if slots == 0:
                    # Pas de slot libre - vérifier si on peut/doit faire fork
                    if self._should_do_fork(current_food):
                        logger.info("[Reproduction] Stage 1→2: Pas de slot libre, création via fork")
                        self.fork_stage = 2
                        self.stage_start_time = current_time
                        return self.cmd_mgr.fork()
                    else:
                        logger.info("[Reproduction] Pas assez de ressources pour fork - création thread simple")
                        self._create_new_thread()
                        self._reset_reproduction()
                        return None
                else:
                    # Il y a des slots libres - création thread simple
                    logger.info(f"[Reproduction] Stage 1: {slots} slots libres - création thread simple")
                    self._create_new_thread()
                    self._reset_reproduction()
                    return None
                    
            except (ValueError, AttributeError) as e:
                logger.error(f"[Reproduction] Erreur parsing connect_nbr '{last_connect.response}': {e}")
                # Réessayer ou abandon selon tentatives
                if self.reproduction_attempts < 3:
                    self.fork_stage = 0
                    self.stage_start_time = current_time
                else:
                    self._reset_reproduction()
                return None
                
        # ✅ Stage 2: Fork lancé, attendre la completion avec timeout fixe
        elif self.fork_stage == 2:
            # Vérifier si fork completé avec succès
            last_fork = self.cmd_mgr.get_last_success(CommandType.FORK)
            if last_fork:
                logger.info("[Reproduction] Stage 2: Fork completé avec succès")
                # ✅ Après fork réussi, AUSSI créer un thread
                self._create_new_thread()
                self._reset_reproduction()
                return None
            
            # Vérifier échec de fork
            last_failed = self.cmd_mgr.get_last_failed(CommandType.FORK)
            if last_failed:
                logger.warning("[Reproduction] Stage 2: Fork échoué")
                # Fallback: créer un thread quand même
                self._create_new_thread()
                self._reset_reproduction()
                return None
                
            # ✅ Timeout spécifique pour fork (fixe)
            fork_duration = current_time - self.stage_start_time
            if fork_duration > self.fork_timeout:
                logger.warning(f"[Reproduction] Timeout fork après {fork_duration:.1f}s")
                # Fallback: créer un thread
                self._create_new_thread()
                self._reset_reproduction()
                return None
            
            # Encore en cours
            logger.debug(f"[Reproduction] Stage 2: Fork en cours ({fork_duration:.1f}s/{self.fork_timeout}s)")
            return None
            
        return None

    def _can_start_reproduction(self) -> bool:
        """✅ Vérifie si on peut commencer une reproduction."""
        current_food = self._get_real_food_count()
        
        # Vérifier niveau minimum
        if self.state.level < 2:
            logger.debug("[Reproduction] Niveau trop bas pour reproduction")
            return False
        
        # Vérifier nourriture minimale pour survie (seuil fixe)
        if current_food < self.safe_food_threshold:
            logger.warning(f"[Reproduction] Nourriture insuffisante: {current_food} < {self.safe_food_threshold}")
            return False
        
        # Vérifier qu'on n'est pas au niveau max
        if self.state.level >= 8:
            logger.debug("[Reproduction] Niveau maximum atteint")
            return False
        
        return True

    def _should_do_fork(self, current_food: int) -> bool:
        """✅ Détermine si on doit faire un fork selon les ressources."""
        
        # Vérifier nourriture suffisante pour fork (seuil fixe)
        if current_food < self.min_food_for_fork:
            logger.info(f"[Reproduction] Pas assez de nourriture pour fork: {current_food} < {self.min_food_for_fork}")
            return False
        
        # ✅ Vérifier qu'on a au moins les ressources de base selon le niveau
        if self.state.level >= 2:
            # Pour niveau 2+, vérifier qu'on a quelques ressources de base
            basic_resources = ['linemate', 'deraumere', 'sibur']
            total_resources = sum(self.state.inventory.get(res, 0) for res in basic_resources)
            
            if total_resources < 2:  # Au moins 2 ressources de base
                logger.info(f"[Reproduction] Pas assez de ressources de base pour fork: {total_resources}")
                return False
        
        logger.info(f"[Reproduction] Conditions OK pour fork: Food={current_food}, Niveau={self.state.level}")
        return True

    def _create_new_thread(self):
        """✅ Crée un nouveau thread d'agent."""
        # ✅ Set new_agent flag pour créer un thread
        self.planner.set_new_agent_flag(True)
        logger.info("[Reproduction] Nouveau thread d'agent planifié")

    def _get_real_food_count(self) -> int:
        """Obtient le vrai compte de nourriture."""
        try:
            if hasattr(self.state, 'inventory') and 'food' in self.state.inventory:
                return self.state.inventory['food']
            elif hasattr(self.state, 'get_food_count'):
                return self.state.get_food_count()
            else:
                return 0
        except Exception as e:
            logger.error(f"[Reproduction] Erreur food count: {e}")
            return 0
            
    def _reset_reproduction(self):
        """✅ Reset l'état de reproduction."""
        self.state.needs_repro = False
        self.fork_stage = 0
        self.reproduction_attempts = 0
        logger.debug("[Reproduction] État reproduction reset")