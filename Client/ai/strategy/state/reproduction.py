##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## reproduction - État de reproduction corrigé pour 1 fois par agent
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from config import CommandType
from constant import ReproductionRules, FoodThresholds
from utils.logger import logger


class ReproductionState(State):
    """État de reproduction avec règles strictes : 1 fois par agent au niveau 2 uniquement."""

    def __init__(self, planner):
        """
        Initialise l'état de reproduction.
        
        Args:
            planner: Planificateur FSM
        """
        super().__init__(planner)
        self.fork_stage = 0
        self.reproduction_start_time = time.time()
        self.fork_attempts = 0
        self.connect_nbr_received = False
        self.slots_available = 0
        self.last_action_time = time.time()
        
        logger.info(f"[ReproductionState] 👶 Reproduction activée - Food: {self.state.get_food_count()}")

    def execute(self) -> Optional[Any]:
        """
        Logique de reproduction avec vérifications strictes.
        
        Returns:
            Commande à exécuter ou None
        """
        current_time = time.time()

        # Vérification des conditions strictes
        if not self._can_reproduce():
            logger.warning("[ReproductionState] Conditions de reproduction perdues")
            return self._complete_reproduction_and_transition()

        # Timeout de sécurité
        if current_time - self.reproduction_start_time > ReproductionRules.TIMEOUT:
            logger.warning("[ReproductionState] Timeout reproduction")
            return self._complete_reproduction_and_transition()

        # Séquence de reproduction
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
        else:
            return self._complete_reproduction_and_transition()

    def _can_reproduce(self) -> bool:
        """
        Vérification stricte des conditions de reproduction.
        
        Returns:
            True si reproduction autorisée
        """
        # Vérification niveau exact
        if self.state.level != ReproductionRules.TRIGGER_LEVEL:
            logger.debug(f"[ReproductionState] Niveau incorrect: {self.state.level} != {ReproductionRules.TRIGGER_LEVEL}")
            return False

        # Vérification si déjà complétée
        if self.state.reproduction_completed:
            logger.debug("[ReproductionState] Reproduction déjà complétée")
            return False

        # Vérification flag de reproduction
        if not self.state.reproduction_triggered:
            logger.debug("[ReproductionState] Reproduction non déclenchée")
            return False

        # Vérification nourriture
        current_food = self.state.get_food_count()
        if current_food < ReproductionRules.MIN_FOOD_REQUIRED:
            logger.debug(f"[ReproductionState] Nourriture insuffisante: {current_food} < {ReproductionRules.MIN_FOOD_REQUIRED}")
            return False

        return True

    def _check_available_slots(self) -> Optional[Any]:
        """
        Phase 0: Vérification des slots disponibles.
        
        Returns:
            Commande connect_nbr
        """
        logger.info("[ReproductionState] Phase 0: Vérification slots disponibles")
        self.fork_stage = 1
        self.last_action_time = time.time()
        return self.cmd_mgr.connect_nbr()

    def _wait_connect_response(self) -> Optional[Any]:
        """
        Phase 1: Attente de la réponse connect_nbr.
        
        Returns:
            None (attente)
        """
        # Vérifier si on a reçu une réponse
        last_connect = self.cmd_mgr.get_last_success(CommandType.CONNECT_NBR)
        if last_connect and last_connect.timestamp > self.last_action_time:
            self.connect_nbr_received = True
            self.fork_stage = 2
            return self._analyze_connect_response()
        
        # Timeout pour la réponse connect_nbr
        if time.time() - self.last_action_time > 10.0:
            logger.warning("[ReproductionState] Timeout connect_nbr")
            self.fork_attempts += 1
            if self.fork_attempts >= ReproductionRules.MAX_ATTEMPTS:
                return self._complete_reproduction_and_transition()
            self.fork_stage = 0
            return self._check_available_slots()
        
        return None

    def _analyze_connect_response(self) -> Optional[Any]:
        """
        Phase 2: Analyse de la réponse connect_nbr.
        
        Returns:
            Commande fork ou transition
        """
        last_connect = self.cmd_mgr.get_last_success(CommandType.CONNECT_NBR)
        if not last_connect:
            logger.error("[ReproductionState] Pas de réponse connect_nbr")
            return self._complete_reproduction_and_transition()

        try:
            self.slots_available = int(last_connect.response)
            logger.info(f"[ReproductionState] Slots disponibles: {self.slots_available}")
            
            # Toujours faire un fork pour créer un oeuf selon les règles Zappy
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
        """
        Phase 3: Exécution du fork.
        
        Returns:
            Commande fork
        """
        logger.info("[ReproductionState] Phase 3: Exécution FORK")
        self.fork_stage = 4
        self.last_action_time = time.time()
        return self.cmd_mgr.fork()

    def _wait_fork_completion(self) -> Optional[Any]:
        """
        Phase 4: Attente de la completion du fork.
        
        Returns:
            None ou transition
        """
        # Cette phase sera complétée par on_command_success/failed
        # Timeout de sécurité
        if time.time() - self.last_action_time > ReproductionRules.TIMEOUT:
            logger.warning("[ReproductionState] Timeout fork")
            return self._complete_reproduction_and_transition()
        
        return None

    def _create_new_agent(self):
        """Crée un nouvel agent via agent_thread."""
        logger.info("[ReproductionState] 🎉 Création nouvel agent")
        
        agent_thread = getattr(self.state, 'agent_thread', None)
        if agent_thread is not None:
            try:
                agent_thread.create_new_agent()
                logger.info("[ReproductionState] ✅ Nouvel agent créé avec succès")
            except Exception as e:
                logger.error(f"[ReproductionState] ❌ Erreur création agent: {e}")
        else:
            logger.error("[ReproductionState] ❌ agent_thread non disponible")

    def _complete_reproduction_and_transition(self) -> Optional[Any]:
        """
        Complète la reproduction et transitionne vers l'état approprié.
        
        Returns:
            Transition vers nouvel état
        """
        duration = time.time() - self.reproduction_start_time
        
        # CRITIQUE: Marquer la reproduction comme terminée pour éviter les répétitions
        self.state.reproduction_completed = True
        
        if self.fork_stage >= 4:
            logger.info(f"[ReproductionState] ✅ Reproduction terminée avec succès ({duration:.1f}s)")
        else:
            logger.warning(f"[ReproductionState] ❌ Reproduction échouée ({duration:.1f}s)")
        
        # Après reproduction, transition selon les priorités
        return self._transition_after_reproduction()

    def _transition_after_reproduction(self) -> Optional[Any]:
        """
        Gère la transition après reproduction selon les règles strictes.
        
        Returns:
            Transition vers l'état approprié
        """
        current_food = self.state.get_food_count()
        
        logger.info(f"[ReproductionState] Planification post-reproduction - Food: {current_food}, Niveau: {self.state.level}")
        
        # Priorité 1: Urgence alimentaire
        if current_food <= FoodThresholds.CRITICAL:
            logger.info("[ReproductionState] → Urgence alimentaire")
            from ai.strategy.state.emergency import EmergencyState
            new_state = EmergencyState(self.planner)
        
        # Priorité 2: Collecte nourriture si insuffisante pour coordination
        elif current_food < FoodThresholds.COORDINATION_MIN:
            logger.info(f"[ReproductionState] → Collecte nourriture (food: {current_food})")
            from ai.strategy.state.collect_food import CollectFoodState
            new_state = CollectFoodState(self.planner)
        
        # Priorité 3: Collecte ressources pour incantation niveau 3
        elif self.state.has_missing_resources():
            logger.info("[ReproductionState] → Collecte ressources pour niveau 3")
            from ai.strategy.state.collect_resources import CollectResourcesState
            new_state = CollectResourcesState(self.planner)
        
        # Priorité 4: Coordination pour incantation niveau 3 (OBLIGATOIRE)
        elif current_food >= FoodThresholds.COORDINATION_MIN:
            logger.info("[ReproductionState] → Coordination niveau 3 (OBLIGATOIRE)")
            from ai.strategy.state.coordination_incantation import CoordinateIncantationState
            new_state = CoordinateIncantationState(self.planner)
        
        # Fallback: Exploration
        else:
            logger.info("[ReproductionState] → Exploration")
            from ai.strategy.state.explore import ExploreState
            new_state = ExploreState(self.planner)
        
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def on_command_success(self, command_type, response=None):
        """
        Gestion du succès des commandes.
        
        Args:
            command_type: Type de commande
            response: Réponse du serveur
        """
        if command_type == CommandType.CONNECT_NBR:
            logger.info(f"[ReproductionState] ✅ Connect_nbr réussi: {response}")
            self.connect_nbr_received = True

        elif command_type == CommandType.FORK:
            logger.info("[ReproductionState] ✅🎉 FORK RÉUSSI!")
            self._create_new_agent()
            self.fork_stage = 5
            # Ne pas transitionner immédiatement, attendre le prochain execute()

    def on_command_failed(self, command_type, response=None):
        """
        Gestion des échecs de commandes.
        
        Args:
            command_type: Type de commande
            response: Réponse du serveur
        """
        if command_type == CommandType.CONNECT_NBR:
            logger.warning(f"[ReproductionState] ❌ Connect_nbr échoué: {response}")
            self.fork_attempts += 1
            if self.fork_attempts >= ReproductionRules.MAX_ATTEMPTS:
                # Transition sera gérée au prochain execute()
                self.fork_stage = 99
            else:
                self.fork_stage = 0

        elif command_type == CommandType.FORK:
            logger.error(f"[ReproductionState] ❌ FORK ÉCHOUÉ: {response}")
            self.fork_attempts += 1
            if self.fork_attempts >= ReproductionRules.MAX_ATTEMPTS:
                self.fork_stage = 99
            else:
                self.fork_stage = 0

    def on_event(self, event: Event) -> Optional[State]:
        """
        Gestion des événements pendant reproduction.
        
        Args:
            event: Événement reçu
            
        Returns:
            Nouvel état ou None
        """
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
        """Actions à l'entrée de l'état."""
        super().on_enter()
        current_food = self.state.get_food_count()
        
        logger.info(f"[ReproductionState] 👶 ENTRÉE reproduction - "
                   f"Niveau: {self.state.level}, Food: {current_food}")
        
        # Vérifications d'entrée
        if not self._can_reproduce():
            logger.warning("[ReproductionState] Conditions non remplies à l'entrée")
            self.fork_stage = 99  # Force completion
            return
        
        # Reset des variables
        self.fork_stage = 0
        self.fork_attempts = 0
        self.connect_nbr_received = False
        self.slots_available = 0
        self.reproduction_start_time = time.time()
        self.last_action_time = time.time()

    def on_exit(self):
        """Actions à la sortie de l'état."""
        super().on_exit()
        duration = time.time() - self.reproduction_start_time
        
        logger.info(f"[ReproductionState] ✅ SORTIE reproduction - "
                   f"Durée: {duration:.1f}s, Succès: {self.state.reproduction_completed}")
        
        # S'assurer que la reproduction est marquée comme terminée
        if not self.state.reproduction_completed:
            self.state.reproduction_completed = True
            logger.info("[ReproductionState] Reproduction marquée comme terminée")