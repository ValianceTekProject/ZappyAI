##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## incantation - État d'incantation SOLO NIVEAU 1 UNIQUEMENT
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from config import CommandType
from constant import (
    IncantationRequirements, FoodThresholds, 
    StateTransitionThresholds, TimingConstants
)
from utils.logger import logger


class IncantationState(State):
    """État d'incantation SOLO STRICTEMENT NIVEAU 1 UNIQUEMENT"""

    def __init__(self, planner):
        super().__init__(planner)
        
        # Vérification STRICTE du niveau
        current_level = self.state.level
        if current_level != 1:
            logger.error(f"[IncantationState] ❌ ERREUR CRITIQUE: Solo interdit pour niveau {current_level}")
            raise ValueError(f"Incantation solo interdite pour niveau {current_level}. Utiliser coordination.")
        
        self.incantation_stage = 0
        self.incantation_start_time = time.time()
        self.last_verification_time = time.time()
        self.resource_preparation_completed = False
        self.final_verification_completed = False
        self.incantation_launched = False
        
        logger.info(f"[IncantationState] 🔮 Incantation SOLO niveau 1 → 2 initiée")

    def execute(self) -> Optional[Any]:
        """Logique d'incantation solo NIVEAU 1 UNIQUEMENT"""
        
        # Vérification CRITIQUE à chaque exécution
        if not self._is_solo_incantation_allowed():
            logger.error("[IncantationState] ❌ Incantation solo non autorisée!")
            return self._transition_to_coordination()
        
        current_time = time.time()
        
        # Timeout de sécurité
        if current_time - self.incantation_start_time > TimingConstants.INCANTATION_TIMEOUT:
            logger.warning("[IncantationState] ⏰ Timeout incantation")
            return self._handle_incantation_failure()
        
        # Vérification continue de la nourriture
        if not self._verify_food_safety():
            logger.warning("[IncantationState] ⚠️ Nourriture insuffisante pour incantation")
            return self._handle_incantation_failure()
        
        # Machine à états pour l'incantation NIVEAU 1
        if self.incantation_stage == 0:
            return self._stage_preparation()
        elif self.incantation_stage == 1:
            return self._stage_resource_deposit()
        elif self.incantation_stage == 2:
            return self._stage_final_verification()
        elif self.incantation_stage == 3:
            return self._stage_launch_incantation()
        elif self.incantation_stage == 4:
            return self._stage_wait_completion()
        else:
            return self._handle_incantation_failure()

    def _is_solo_incantation_allowed(self) -> bool:
        """
        Vérifie STRICTEMENT que seul le niveau 1 peut faire du solo
        
        Returns:
            True seulement pour niveau 1
        """
        current_level = self.state.level
        
        # RÈGLE ABSOLUE : Solo UNIQUEMENT pour niveau 1
        if current_level != 1:
            logger.error(f"[IncantationState] ❌ INTERDIT: Niveau {current_level} nécessite coordination OBLIGATOIRE")
            return False
            
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(current_level, 1)
        if required_players != 1:
            logger.error(f"[IncantationState] ❌ INCOHÉRENCE: Niveau {current_level} nécessite {required_players} joueurs")
            return False
            
        logger.debug("[IncantationState] ✅ Niveau 1: Solo autorisé")
        return True

    def _verify_food_safety(self) -> bool:
        """Vérifie que la nourriture est suffisante pour l'incantation niveau 1"""
        current_food = self.state.get_food_count()
        min_food = StateTransitionThresholds.MIN_FOOD_FOR_LEVEL_1_INCANTATION
        
        return current_food >= min_food

    def _stage_preparation(self) -> Optional[Any]:
        """Phase 0: Préparation et vérifications NIVEAU 1"""
        if not self._is_solo_incantation_allowed():
            return self._transition_to_coordination()
            
        logger.info(f"[IncantationState] 📋 Phase 0: Préparation SOLO niveau 1")
        
        # Vérifier ressources pour niveau 1
        missing_resources = self._get_missing_resources()
        if missing_resources:
            logger.warning(f"[IncantationState] ❌ Ressources manquantes niveau 1: {missing_resources}")
            return self._transition_to_resource_collection()
        
        self.incantation_stage = 1
        return self._stage_resource_deposit()

    def _stage_resource_deposit(self) -> Optional[Any]:
        """Phase 1: Dépôt des ressources NIVEAU 1 (1 linemate)"""
        if not self._is_solo_incantation_allowed():
            return self._transition_to_coordination()
            
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(1, {})
        resources_to_deposit = []
        
        for resource, needed in requirements.items():
            current = self.state.get_inventory().get(resource, 0)
            if current >= needed:
                resources_to_deposit.extend([resource] * needed)
        
        logger.info(f"[IncantationState] 📦 Ressources niveau 1 à déposer: {resources_to_deposit}")
        
        if resources_to_deposit:
            resource_to_deposit = resources_to_deposit[0]
            remaining = len(resources_to_deposit) - 1
            logger.info(f"[IncantationState] 📦 Dépôt {resource_to_deposit} ({remaining} restants)")
            return self.cmd_mgr.set(resource_to_deposit)
        else:
            logger.info("[IncantationState] ✅ Ressources niveau 1 déposées")
            self.resource_preparation_completed = True
            self.incantation_stage = 2
            return self._stage_final_verification()

    def _stage_final_verification(self) -> Optional[Any]:
        """Phase 2: Vérification finale NIVEAU 1"""
        if not self._is_solo_incantation_allowed():
            return self._transition_to_coordination()
            
        logger.info(f"[IncantationState] 🔍 Phase 2: Vérification finale NIVEAU 1")
        
        # Vérifier conditions niveau 1
        if not self._verify_incantation_conditions():
            logger.error("[IncantationState] ❌ Conditions niveau 1 non remplies")
            return self._handle_incantation_failure()
        
        logger.info("[IncantationState] ✅ Conditions niveau 1 vérifiées")
        self.final_verification_completed = True
        self.incantation_stage = 3
        return self._stage_launch_incantation()

    def _stage_launch_incantation(self) -> Optional[Any]:
        """Phase 3: Lancement incantation NIVEAU 1"""
        if not self._is_solo_incantation_allowed():
            return self._transition_to_coordination()
            
        logger.info("[IncantationState] 🚀 Phase 3: Lancement NIVEAU 1")
        
        # Vérification finale joueurs pour niveau 1
        players_on_tile = self._get_players_on_current_tile()
        required_players = 1  # Niveau 1 = 1 joueur
        
        if players_on_tile < required_players:
            logger.error(f"[IncantationState] ❌ Joueurs insuffisants: {players_on_tile}/{required_players}")
            return self._handle_incantation_failure()
        
        logger.info(f"[IncantationState] 🔮✨ LANCEMENT INCANTATION SOLO 1 → 2")
        logger.info(f"[IncantationState] 👥 Joueurs: {players_on_tile}/{required_players}")
        
        self.incantation_launched = True
        self.incantation_stage = 4
        return self.cmd_mgr.incantation()

    def _stage_wait_completion(self) -> Optional[Any]:
        """Phase 4: Attente de la completion"""
        return None

    def _verify_incantation_conditions(self) -> bool:
        """Vérifie toutes les conditions pour l'incantation NIVEAU 1"""
        if not self._is_solo_incantation_allowed():
            return False
            
        # Vérifier ressources niveau 1 sur le terrain
        vision = self.state.get_vision()
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(1, {})  # {linemate: 1}
        
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                for resource, needed in requirements.items():
                    available = data.resources.get(resource, 0)
                    if available < needed:
                        logger.warning(f"[IncantationState] Ressource niveau 1 {resource}: {available}/{needed}")
                        return False
                break
        
        # Vérifier nombre de joueurs (1 pour niveau 1)
        players_on_tile = self._get_players_on_current_tile()
        if players_on_tile < 1:
            logger.warning(f"[IncantationState] Joueurs niveau 1: {players_on_tile}/1")
            return False
        
        return True

    def _get_players_on_current_tile(self) -> int:
        """Compte le nombre de joueurs sur la tuile actuelle"""
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return data.players
        return 1

    def _get_missing_resources(self) -> dict:
        """Retourne les ressources manquantes pour l'incantation NIVEAU 1"""
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(1, {})  # {linemate: 1}
        inventory = self.state.get_inventory()
        missing = {}
        
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current
                
        return missing

    def _transition_to_coordination(self) -> Optional[Any]:
        """INTERDIT pour niveau 1 - Log erreur et redirection"""
        current_level = self.state.level
        if current_level == 1:
            logger.error("[IncantationState] ❌ ERREUR: Coordination appelée pour niveau 1")
            return self._handle_incantation_failure()
        
        logger.info(f"[IncantationState] → Coordination niveau {current_level}")
        from ai.strategy.state.coordination_incantation import CoordinateIncantationState
        new_state = CoordinateIncantationState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _transition_to_resource_collection(self) -> Optional[Any]:
        """Transition vers la collecte de ressources niveau 1"""
        logger.info("[IncantationState] → Collecte ressources niveau 1 (linemate)")
        from ai.strategy.state.collect_resources import CollectResourcesState
        new_state = CollectResourcesState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _handle_incantation_failure(self) -> Optional[Any]:
        """Gère l'échec de l'incantation niveau 1"""
        current_food = self.state.get_food_count()
        
        logger.warning(f"[IncantationState] 🔄 Échec incantation niveau 1 - Food: {current_food}")
        
        if current_food <= FoodThresholds.CRITICAL:
            from ai.strategy.state.emergency import EmergencyState
            new_state = EmergencyState(self.planner)
        elif current_food <= FoodThresholds.SUFFICIENT:
            from ai.strategy.state.collect_food import CollectFoodState
            new_state = CollectFoodState(self.planner)
        elif self.state.has_missing_resources():
            from ai.strategy.state.collect_resources import CollectResourcesState
            new_state = CollectResourcesState(self.planner)
        else:
            from ai.strategy.state.explore import ExploreState
            new_state = ExploreState(self.planner)
        
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes niveau 1"""
        if command_type == CommandType.SET:
            if self.incantation_stage == 1:
                return
                
        elif command_type == CommandType.INCANTATION:
            duration = time.time() - self.incantation_start_time
            new_level = self.state.level
            
            logger.info(f"[IncantationState] INCANTATION SOLO NIVEAU 1 RÉUSSIE! Nouveau niveau: {new_level}")
            
            current_food = self.state.get_food_count()
            if self.state.should_reproduce():
                logger.info("[IncantationState] → Reproduction niveau 2")
                from ai.strategy.state.reproduction import ReproductionState
                new_state = ReproductionState(self.planner)
            elif current_food <= FoodThresholds.SUFFICIENT:
                logger.info("[IncantationState] → Collecte nourriture")
                from ai.strategy.state.collect_food import CollectFoodState
                new_state = CollectFoodState(self.planner)
            elif self.state.has_missing_resources():
                logger.info("[IncantationState] → Collecte ressources niveau 2")
                from ai.strategy.state.collect_resources import CollectResourcesState
                new_state = CollectResourcesState(self.planner)
            else:
                logger.info("[IncantationState] → Exploration niveau 2")
                from ai.strategy.state.explore import ExploreState
                new_state = ExploreState(self.planner)
            
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes niveau 1"""
        if command_type == CommandType.SET:
            logger.warning(f"[IncantationState] ❌ Échec dépôt ressource niveau 1: {response}")
            
        elif command_type == CommandType.INCANTATION:
            logger.error(f"[IncantationState] 💥 INCANTATION NIVEAU 1 ÉCHOUÉE: {response}")

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements pendant l'incantation niveau 1"""
        if event == Event.FOOD_EMERGENCY:
            logger.error("[IncantationState] URGENCE ALIMENTAIRE niveau 1!")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)

        return None

    def on_enter(self):
        """Actions à l'entrée de l'état NIVEAU 1"""
        super().on_enter()
        current_food = self.state.get_food_count()
        current_level = self.state.level
        
        if current_level != 1:
            logger.error(f"[IncantationState] ❌ ERREUR CRITIQUE: Niveau {current_level} interdit en solo")
            self.incantation_stage = 99
            return
        
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(1, {})
        
        logger.info(f"[IncantationState] 🔮 ENTRÉE incantation SOLO NIVEAU 1")
        logger.info(f"[IncantationState] 📊 Food: {current_food}, Ressources: {requirements}")
        
        self.incantation_start_time = time.time()
        self.incantation_stage = 0
        self.resource_preparation_completed = False
        self.final_verification_completed = False
        self.incantation_launched = False

    def on_exit(self):
        """Actions à la sortie de l'état NIVEAU 1"""
        super().on_exit()
        duration = time.time() - self.incantation_start_time
        
        if self.incantation_launched and self.state.level > 1:
            logger.info(f"[IncantationState] 🎉 SORTIE SUCCÈS SOLO NIVEAU 1 - "
                       f"Nouveau niveau: {self.state.level}, Durée: {duration:.1f}s")
        else:
            logger.info(f"[IncantationState] ❌ SORTIE ÉCHEC SOLO NIVEAU 1 - Durée: {duration:.1f}s")