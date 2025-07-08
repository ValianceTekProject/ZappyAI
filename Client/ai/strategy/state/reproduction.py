##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## reproduction - État de reproduction niveau 2 uniquement avec cooldown 1 minute
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from config import CommandType
from constant import ReproductionRules, FoodThresholds
from utils.logger import logger


class ReproductionState(State):
    """État de reproduction niveau 2 uniquement avec cooldown 1 minute"""

    def __init__(self, planner):
        super().__init__(planner)
        self.fork_stage = 0
        self.reproduction_start_time = time.time()
        self.fork_attempts = 0
        self.connect_nbr_received = False
        self.slots_available = 0
        self.last_action_time = time.time()
        self.succes_agent_create = False
        
        logger.info(f"[ReproductionState] Reproduction niveau 2 activée - Food: {self.state.get_food_count()}")

    def execute(self) -> Optional[Any]:
        """Logique de reproduction niveau 2 avec cooldown 1 minute"""
        current_time = time.time()

        if not self._can_reproduce():
            logger.warning("[ReproductionState] Conditions de reproduction perdues")
            return self._complete_reproduction_and_transition()

        if current_time - self.reproduction_start_time > ReproductionRules.TIMEOUT:
            logger.warning("[ReproductionState] Timeout reproduction")
            return self._complete_reproduction_and_transition()

        if self.fork_stage == 0:
            return self._check_available_slots()
        elif self.fork_stage == 1:
            return self._wait_connect_response()
        elif self.fork_stage == 2:
            return self._analyze_connect_response()
        elif self.fork_stage == 3:
            return self._execute_fork()
        elif self.fork_stage == 4:
            return self._wait_fork_completion()
        elif self.fork_stage >= 5:
            return self._complete_reproduction_and_transition()
        else:
            return self._complete_reproduction_and_transition()

    def _can_reproduce(self) -> bool:
        """Vérification stricte des conditions de reproduction niveau 2"""
        if self.state.level != ReproductionRules.TRIGGER_LEVEL:
            return False

        if not self.state.reproduction_triggered:
            return False

        current_food = self.state.get_food_count()
        if current_food < ReproductionRules.MIN_FOOD_REQUIRED:
            return False

        if hasattr(self.state, 'last_reproduction_time'):
            time_since_last_reproduction = time.time() - self.state.last_reproduction_time
            if time_since_last_reproduction < ReproductionRules.COOLDOWN_DURATION:
                return False

        return True

    def _check_available_slots(self) -> Optional[Any]:
        """Phase 0: Vérification des slots disponibles"""
        logger.info("[ReproductionState] Phase 0: Vérification slots disponibles")
        self.fork_stage = 1
        self.last_action_time = time.time()
        return self.cmd_mgr.connect_nbr()

    def _wait_connect_response(self) -> Optional[Any]:
        """Phase 1: Attente de la réponse connect_nbr"""
        last_connect = self.cmd_mgr.get_last_success(CommandType.CONNECT_NBR)
        if last_connect and last_connect.timestamp > self.last_action_time:
            self.connect_nbr_received = True
            self.fork_stage = 2
            return self._analyze_connect_response()
        
        if time.time() - self.last_action_time > 10.0:
            logger.warning("[ReproductionState] Timeout connect_nbr")
            self.fork_attempts += 1
            if self.fork_attempts >= ReproductionRules.MAX_ATTEMPTS:
                return self._complete_reproduction_and_transition()
            self.fork_stage = 0
            return self._check_available_slots()
        
        return None

    def _analyze_connect_response(self) -> Optional[Any]:
        """Phase 2: Analyse de la réponse connect_nbr"""
        last_connect = self.cmd_mgr.get_last_success(CommandType.CONNECT_NBR)
        if not last_connect:
            logger.error("[ReproductionState] Pas de réponse connect_nbr")
            return self._complete_reproduction_and_transition()

        try:
            self.slots_available = int(last_connect.response)
            logger.info(f"[ReproductionState] Slots disponibles: {self.slots_available}")
            if self.slots_available > 0:
                self.fork_stage = 4
                self.succes_agent_create = True
                return self._create_new_agent()

            logger.info("[ReproductionState] Création œuf via FORK")
            self.fork_stage = 3
            return self._execute_fork()
                
        except (ValueError, AttributeError) as e:
            logger.error(f"[ReproductionState] Réponse connect_nbr invalide: {last_connect.response}, erreur: {e}")
            self.fork_attempts += 1
            if self.fork_attempts >= ReproductionRules.MAX_ATTEMPTS:
                return self._complete_reproduction_and_transition()
            self.fork_stage = 0
            return self._check_available_slots()

    def _execute_fork(self) -> Optional[Any]:
        """Phase 3: Exécution du fork"""
        logger.info("[ReproductionState] Phase 3: Exécution FORK")
        self.fork_stage = 4
        self.last_action_time = time.time()
        return self.cmd_mgr.fork()

    def _wait_fork_completion(self) -> Optional[Any]:
        """Phase 4: Attente de la completion du fork"""
        if time.time() - self.last_action_time > ReproductionRules.TIMEOUT:
            logger.warning("[ReproductionState] Timeout fork")
            return self._complete_reproduction_and_transition()
        
        # Vérifier si le fork est terminé en regardant les commandes récentes
        last_fork = self.cmd_mgr.get_last_success(CommandType.FORK)
        if last_fork and last_fork.timestamp > self.last_action_time:
            logger.info("[ReproductionState] Fork terminé avec succès")
            self.fork_stage = 5
            return self._complete_reproduction_and_transition()
        
        if self.succes_agent_create:
            self._complete_reproduction_and_transition()
        return None

    def _create_new_agent(self):
        """Crée un nouvel agent via agent_thread"""
        logger.info("[ReproductionState] Création nouvel agent niveau 2")
        
        agent_thread = getattr(self.state, 'agent_thread', None)
        if agent_thread is not None:
            try:
                agent_thread.create_new_agent()
                logger.info("[ReproductionState] Nouvel agent créé avec succès")
            except Exception as e:
                logger.error(f"[ReproductionState] Erreur création agent: {e}")
        else:
            logger.error("[ReproductionState] agent_thread non disponible")

    def _complete_reproduction_and_transition(self) -> Optional[Any]:
        """Complète la reproduction avec enregistrement du cooldown"""
        duration = time.time() - self.reproduction_start_time
        
        if self.fork_stage >= 4:
            self.state.last_reproduction_time = time.time()
            logger.info(f"[ReproductionState] Reproduction niveau 2 terminée ({duration:.1f}s)")
            logger.info(f"[ReproductionState] Prochaine reproduction dans {ReproductionRules.COOLDOWN_DURATION}s")
        else:
            logger.warning(f"[ReproductionState] Reproduction niveau 2 échouée ({duration:.1f}s)")
        
        return self._transition_after_reproduction()

    def _transition_after_reproduction(self) -> Optional[Any]:
        """Gère la transition après reproduction niveau 2 - CollectFoodState par défaut"""
        current_food = self.state.get_food_count()
        
        logger.info(f"[ReproductionState] Transition post-reproduction - Food: {current_food}")
        
        # Toujours aller vers CollectFoodState par défaut après reproduction
        if current_food <= FoodThresholds.CRITICAL:
            logger.info("[ReproductionState] → Urgence alimentaire")
            from ai.strategy.state.emergency import EmergencyState
            new_state = EmergencyState(self.planner)
        else:
            logger.info("[ReproductionState] → Collecte nourriture (par défaut post-reproduction)")
            from ai.strategy.state.collect_food import CollectFoodState
            new_state = CollectFoodState(self.planner)
        
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes"""
        if command_type == CommandType.CONNECT_NBR:
            logger.info(f"[ReproductionState] Connect_nbr réussi: {response}")
            self.connect_nbr_received = True

        elif command_type == CommandType.FORK:
            logger.info("[ReproductionState] FORK niveau 2 RÉUSSI!")
            self._create_new_agent()
            self.fork_stage = 5
            return self._complete_reproduction_and_transition()

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes"""
        if command_type == CommandType.CONNECT_NBR:
            logger.warning(f"[ReproductionState] Connect_nbr échoué: {response}")
            self.fork_attempts += 1
            if self.fork_attempts >= ReproductionRules.MAX_ATTEMPTS:
                return self._complete_reproduction_and_transition()
            else:
                self.fork_stage = 0

        elif command_type == CommandType.FORK:
            logger.error(f"[ReproductionState] FORK niveau 2 ÉCHOUÉ: {response}")
            self.fork_attempts += 1
            if self.fork_attempts >= ReproductionRules.MAX_ATTEMPTS:
                return self._complete_reproduction_and_transition()
            else:
                self.fork_stage = 0

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements pendant reproduction"""
        if event == Event.FOOD_EMERGENCY:
            logger.error("[ReproductionState] URGENCE ALIMENTAIRE! Abandon reproduction")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)

        elif event == Event.FOOD_LOW:
            current_food = self.state.get_food_count()
            if current_food < FoodThresholds.SUFFICIENT:
                logger.warning("[ReproductionState] Nourriture faible, abandon reproduction")
                from ai.strategy.state.collect_food import CollectFoodState
                return CollectFoodState(self.planner)

        return None

    def on_enter(self):
        """Actions à l'entrée de l'état"""
        super().on_enter()
        current_food = self.state.get_food_count()
        
        logger.info(f"[ReproductionState] ENTRÉE reproduction niveau 2 - Food: {current_food}")
        
        if not self._can_reproduce():
            logger.warning("[ReproductionState] Conditions non remplies à l'entrée")
            self.fork_stage = 99
            return
        
        self.fork_stage = 0
        self.fork_attempts = 0
        self.connect_nbr_received = False
        self.succes_agent_create = False
        self.slots_available = 0
        self.reproduction_start_time = time.time()
        self.last_action_time = time.time()

    def on_exit(self):
        """Actions à la sortie de l'état"""
        super().on_exit()
        duration = time.time() - self.reproduction_start_time
        success = self.fork_stage >= 4
        
        logger.info(f"[ReproductionState] SORTIE reproduction niveau 2 - Durée: {duration:.1f}s, Succès: {success}")
        
        if success and hasattr(self.state, 'last_reproduction_time'):
            next_reproduction = self.state.last_reproduction_time + ReproductionRules.COOLDOWN_DURATION
            logger.info(f"[ReproductionState] Prochaine reproduction: {time.strftime('%H:%M:%S', time.localtime(next_reproduction))}")