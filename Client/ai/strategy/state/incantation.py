##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## incantation - État d'incantation solo avec vérifications strictes
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
    """État d'incantation SOLO uniquement pour niveau 1"""

    def __init__(self, planner):
        super().__init__(planner)
        
        self.incantation_stage = 0
        self.incantation_start_time = time.time()
        self.last_verification_time = time.time()
        self.resource_preparation_completed = False
        self.final_verification_completed = False
        self.incantation_launched = False
        
        current_level = self.state.level
        logger.info(f"[IncantationState] 🔮 Incantation SOLO {current_level} → {current_level + 1} initiée")

    def execute(self) -> Optional[Any]:
        """Logique d'incantation solo avec vérifications strictes"""
        
        # Vérification critique : niveau 1 uniquement
        if not self._is_solo_incantation_allowed():
            logger.error("[IncantationState] ❌ Incantation solo non autorisée pour ce niveau")
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
        
        # Machine à états pour l'incantation
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
        """Vérifie si l'incantation solo est autorisée (niveau 1 uniquement)"""
        current_level = self.state.level
        
        # Règle stricte : solo uniquement pour niveau 1
        if current_level != 1:
            logger.error(f"[IncantationState] ❌ Niveau {current_level} nécessite coordination obligatoire")
            return False
            
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(current_level, 1)
        if required_players > 1:
            logger.error(f"[IncantationState] ❌ Niveau {current_level} nécessite {required_players} joueurs")
            return False
            
        logger.info("[IncantationState] ✅ Niveau 1: Solo autorisé")
        return True

    def _verify_food_safety(self) -> bool:
        """Vérifie que la nourriture est suffisante pour l'incantation"""
        current_food = self.state.get_food_count()
        min_food = StateTransitionThresholds.MIN_FOOD_FOR_LEVEL_1_INCANTATION
        
        return current_food >= min_food

    def _stage_preparation(self) -> Optional[Any]:
        """Phase 0: Préparation et vérifications initiales"""
        if not self._is_solo_incantation_allowed():
            return self._transition_to_coordination()
            
        logger.info(f"[IncantationState] 📋 Phase 0: Préparation SOLO niveau {self.state.level}")
        
        # Vérifier qu'on a toutes les ressources
        missing_resources = self._get_missing_resources()
        if missing_resources:
            logger.warning(f"[IncantationState] ❌ Ressources manquantes: {missing_resources}")
            return self._transition_to_resource_collection()
        
        self.incantation_stage = 1
        return self._stage_resource_deposit()

    def _stage_resource_deposit(self) -> Optional[Any]:
        """Phase 1: Dépôt des ressources nécessaires"""
        if not self._is_solo_incantation_allowed():
            return self._transition_to_coordination()
            
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        resources_to_deposit = []
        
        for resource, needed in requirements.items():
            current = self.state.get_inventory().get(resource, 0)
            if current >= needed:
                resources_to_deposit.extend([resource] * needed)
        
        logger.info(f"[IncantationState] 📦 Ressources à déposer: {resources_to_deposit}")
        
        if resources_to_deposit:
            resource_to_deposit = resources_to_deposit[0]
            remaining = len(resources_to_deposit) - 1
            logger.info(f"[IncantationState] 📦 Dépôt {resource_to_deposit} ({remaining} restants)")
            return self.cmd_mgr.set(resource_to_deposit)
        else:
            logger.info("[IncantationState] ✅ Ressources déposées, vérification")
            self.resource_preparation_completed = True
            self.incantation_stage = 2
            return self._stage_final_verification()

    def _stage_final_verification(self) -> Optional[Any]:
        """Phase 2: Vérification finale avant lancement"""
        if not self._is_solo_incantation_allowed():
            return self._transition_to_coordination()
            
        logger.info(f"[IncantationState] 🔍 Phase 2: Vérification finale SOLO")
        
        # Vérifier les conditions une dernière fois
        if not self._verify_incantation_conditions():
            logger.error("[IncantationState] ❌ Conditions finales non remplies")
            return self._handle_incantation_failure()
        
        logger.info("[IncantationState] ✅ Conditions vérifiées")
        self.final_verification_completed = True
        self.incantation_stage = 3
        return self._stage_launch_incantation()

    def _stage_launch_incantation(self) -> Optional[Any]:
        """Phase 3: Lancement de l'incantation"""
        if not self._is_solo_incantation_allowed():
            return self._transition_to_coordination()
            
        logger.info("[IncantationState] 🚀 Phase 3: Lancement SOLO")
        
        # Vérification finale des joueurs sur la tuile
        players_on_tile = self._get_players_on_current_tile()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        
        logger.info(f"[IncantationState] 🔮✨ LANCEMENT INCANTATION SOLO {self.state.level} → {self.state.level + 1}")
        logger.info(f"[IncantationState] 👥 Joueurs: {players_on_tile}/{required_players}")
        
        self.incantation_launched = True
        self.incantation_stage = 4
        return self.cmd_mgr.incantation()

    def _stage_wait_completion(self) -> Optional[Any]:
        """Phase 4: Attente de la completion"""
        # Attendre la réponse du serveur
        return None

    def _verify_incantation_conditions(self) -> bool:
        """Vérifie toutes les conditions pour l'incantation"""
        if not self._is_solo_incantation_allowed():
            return False
            
        # Vérifier les ressources sur le terrain via vision
        vision = self.state.get_vision()
        required_resources = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                for resource, needed in required_resources.items():
                    available = data.resources.get(resource, 0)
                    if available < needed:
                        logger.warning(f"[IncantationState] Ressource {resource}: {available}/{needed}")
                        return False
                break
        
        # Vérifier le nombre de joueurs
        players_on_tile = self._get_players_on_current_tile()
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        
        if players_on_tile < required_players:
            logger.warning(f"[IncantationState] Joueurs: {players_on_tile}/{required_players}")
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
        """Retourne les ressources manquantes pour l'incantation"""
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        inventory = self.state.get_inventory()
        missing = {}
        
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current
                
        return missing

    def _transition_to_coordination(self) -> Optional[Any]:
        """Transition vers la coordination pour les niveaux > 1"""
        logger.info(f"[IncantationState] → Coordination niveau {self.state.level}")
        from ai.strategy.state.coordination_incantation import CoordinateIncantationState
        new_state = CoordinateIncantationState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _transition_to_resource_collection(self) -> Optional[Any]:
        """Transition vers la collecte de ressources"""
        logger.info("[IncantationState] → Collecte ressources manquantes")
        from ai.strategy.state.collect_resources import CollectResourcesState
        new_state = CollectResourcesState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _handle_incantation_failure(self) -> Optional[Any]:
        """Gère l'échec de l'incantation"""
        current_food = self.state.get_food_count()
        
        logger.warning(f"[IncantationState] 🔄 Échec incantation - Food: {current_food}")
        
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
        """Gestion du succès des commandes"""
        if command_type == CommandType.SET:
            # Continuer le dépôt de ressources
            if self.incantation_stage == 1:
                return
                
        elif command_type == CommandType.INCANTATION:
            duration = time.time() - self.incantation_start_time
            old_level = self.state.level - 1  # Le niveau a déjà été mis à jour
            new_level = self.state.level
            
            logger.info(f"[IncantationState] 🎉✨ INCANTATION SOLO RÉUSSIE! Nouveau niveau: {new_level}")
            
            # Transition appropriée selon le nouveau niveau
            if self.state.should_reproduce():
                from ai.strategy.state.reproduction import ReproductionState
                new_state = ReproductionState(self.planner)
            elif self.state.has_missing_resources():
                from ai.strategy.state.collect_resources import CollectResourcesState
                new_state = CollectResourcesState(self.planner)
            else:
                from ai.strategy.state.explore import ExploreState
                new_state = ExploreState(self.planner)
            
            self.planner.fsm.transition_to(new_state)

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes"""
        if command_type == CommandType.SET:
            logger.warning(f"[IncantationState] ❌ Échec dépôt ressource: {response}")
            
        elif command_type == CommandType.INCANTATION:
            logger.error(f"[IncantationState] 💥 INCANTATION ÉCHOUÉE: {response}")

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements pendant l'incantation"""
        if event == Event.FOOD_EMERGENCY:
            logger.error("[IncantationState] URGENCE ALIMENTAIRE!")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)

        return None

    def on_enter(self):
        """Actions à l'entrée de l'état"""
        super().on_enter()
        current_food = self.state.get_food_count()
        required_resources = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        
        logger.info(f"[IncantationState] 🔮 ENTRÉE incantation SOLO")
        logger.info(f"[IncantationState] 📊 Niveau: {self.state.level}, Food: {current_food}")
        logger.info(f"[IncantationState] 📦 Ressources: {required_resources}")
        logger.info(f"[IncantationState] 👥 Joueurs: {required_players}")
        
        self.incantation_start_time = time.time()
        self.incantation_stage = 0
        self.resource_preparation_completed = False
        self.final_verification_completed = False
        self.incantation_launched = False

    def on_exit(self):
        """Actions à la sortie de l'état"""
        super().on_exit()
        duration = time.time() - self.incantation_start_time
        
        if self.incantation_launched and self.state.level > 1:
            resources_deposited = len(IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level - 1, {}))
            logger.info(f"[IncantationState] 🎉 SORTIE SUCCÈS SOLO - "
                       f"Niveau: {self.state.level}, Durée: {duration:.1f}s, "
                       f"Ressources: {resources_deposited}")
        else:
            logger.info(f"[IncantationState] ❌ SORTIE ÉCHEC SOLO - Durée: {duration:.1f}s")