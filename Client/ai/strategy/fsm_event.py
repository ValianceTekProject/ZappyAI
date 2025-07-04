##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## fsm_event - Détecteur d'événements avec coordination
##

import time
from typing import List, Dict, Any
from ai.strategy.fsm import Event
from config import Constants
from constant import (
    FoodThresholds, IncantationRequirements, CoordinationMessages, 
    StateTransitionThresholds, GameplayConstants, ReproductionConstants
)
from utils.logger import logger


class EventDetector:
    """
    Détecteur d'événements pour la FSM avec support de coordination.
    """

    def __init__(self, game_state):
        """
        Initialise le détecteur d'événements.
        
        Args:
            game_state: État du jeu à surveiller
        """
        self.state = game_state

        self.last_food_count = self.state.get_food_count()
        self.last_level = self.state.level
        self.last_vision_check = time.time()
        self.last_inventory_check = time.time()

        self.last_incant_check = time.time()
        self.last_reproduction_check = time.time()
        self.level_up_detected = False

        self.vision_check_interval = GameplayConstants.VISION_UPDATE_INTERVAL
        self.inventory_check_interval = GameplayConstants.INVENTORY_CHECK_INTERVAL
        self.emergency_check_interval = 5.0
        self.incant_check_interval = 8.0
        self.reproduction_check_interval = 12.0

        self._update_thresholds()

        logger.debug("[EventDetector] Détecteur avec coordination initialisé")

    def _update_thresholds(self):
        """Met à jour les seuils selon le niveau actuel."""
        level = self.state.level
        
        if level >= 7:
            multiplier = FoodThresholds.MULTIPLIER_HIGH_LEVEL
        elif level >= 4:
            multiplier = FoodThresholds.MULTIPLIER_MID_LEVEL
        else:
            multiplier = FoodThresholds.MULTIPLIER_LOW_LEVEL

        self.critical_threshold = int(FoodThresholds.BASE_CRITICAL * multiplier)
        self.safe_threshold = int(FoodThresholds.BASE_SAFE * multiplier)
        self.abundant_threshold = int(FoodThresholds.BASE_ABUNDANT * multiplier)
        self.exploration_return_threshold = int(FoodThresholds.BASE_EXPLORATION_THRESHOLD * multiplier)

        self.incant_food_threshold = max(
            StateTransitionThresholds.MIN_FOOD_FOR_COORDINATION, 
            int(FoodThresholds.BASE_SAFE * multiplier * 1.8)
        )
        self.reproduction_food_threshold = max(
            StateTransitionThresholds.MIN_FOOD_FOR_REPRODUCTION, 
            int(FoodThresholds.BASE_SAFE * multiplier * 2.2)
        )

    def detect_events(self) -> List[Event]:
        """
        Détecte les événements basés sur l'état actuel du jeu.
        
        Returns:
            Liste d'événements détectés
        """
        events = []
        current_time = time.time()

        # Gestion des changements de niveau
        if self.last_level != self.state.level:
            self._handle_level_change(events)
            self._update_thresholds()
            self.last_level = self.state.level

        # Événements de nourriture
        current_food = self.state.get_food_count()
        food_events = self._check_food_events(current_food)
        events.extend(food_events)

        # Événements de progression
        if current_time - self.last_incant_check >= self.incant_check_interval:
            progression_events = self._check_progression_events(current_food)
            events.extend(progression_events)
            self.last_incant_check = current_time

        # Événements de reproduction
        if current_time - self.last_reproduction_check >= self.reproduction_check_interval:
            reproduction_events = self._check_reproduction_events(current_food)
            events.extend(reproduction_events)
            self.last_reproduction_check = current_time

        # Besoins de mise à jour
        if self._needs_vision_update(current_time):
            events.append(Event.NEED_VISION)
            self.last_vision_check = current_time

        if self._needs_inventory_check(current_time):
            events.append(Event.NEED_INVENTORY)
            self.last_inventory_check = current_time

        # Ressources trouvées
        if self._resources_found_in_vision():
            events.append(Event.RESOURCES_FOUND)

        # Événements de coordination
        coordination_events = self._check_coordination_events()
        events.extend(coordination_events)

        self.last_food_count = current_food

        return events

    def _handle_level_change(self, events: List[Event]):
        """
        Gère les événements de changement de niveau.
        
        Args:
            events: Liste des événements à enrichir
        """
        old_level = self.last_level
        new_level = self.state.level

        if new_level > old_level:
            logger.info(f"[EventDetector] 🆙 LEVEL UP détecté: {old_level} → {new_level}")
            events.append(Event.LEVEL_UP)
            self.level_up_detected = True

            if new_level == 2:
                events.append(Event.LEVEL_2_ACHIEVED)
                logger.info("[EventDetector] Niveau 2 atteint - reproduction possible")

            if new_level >= GameplayConstants.MAX_LEVEL:
                events.append(Event.MAX_LEVEL_REACHED)
                logger.info("[EventDetector] Niveau maximum atteint!")

    def _check_progression_events(self, current_food: int) -> List[Event]:
        """
        Vérifie les opportunités de progression (incantation).
        
        Args:
            current_food: Nourriture actuelle
            
        Returns:
            Liste des événements de progression
        """
        events = []

        if self._can_attempt_incantation(current_food):
            events.append(Event.CAN_INCANT)

            if self._has_all_incant_resources():
                events.append(Event.INCANT_READY)
                logger.debug(f"[EventDetector] Incantation prête pour niveau {self.state.level}")

        if self.state.has_missing_resources():
            events.append(Event.MISSING_RESOURCES)
        else:
            events.append(Event.RESOURCES_COMPLETE)

        return events

    def _check_reproduction_events(self, current_food: int) -> List[Event]:
        """
        Vérifie les opportunités de reproduction.
        
        Args:
            current_food: Nourriture actuelle
            
        Returns:
            Liste des événements de reproduction
        """
        events = []

        if self._should_attempt_reproduction(current_food):
            events.append(Event.SHOULD_REPRODUCE)

            if (current_food >= self.reproduction_food_threshold and 
                self.state.level >= ReproductionConstants.MIN_LEVEL_FOR_REPRODUCTION):
                events.append(Event.REPRODUCTION_READY)
                logger.debug(f"[EventDetector] Reproduction prête (niveau {self.state.level}, food: {current_food})")

        return events

    def _check_coordination_events(self) -> List[Event]:
        """
        Vérifie les événements liés à la coordination.
        
        Returns:
            Liste des événements de coordination
        """
        events = []

        if hasattr(self.state, 'role'):
            if self.state.role == 'helper':
                events.append(Event.HELPER_AVAILABLE)
            elif self.state.role == 'incanter':
                required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
                if required_players > 1:
                    events.append(Event.HELPER_NEEDED)

        return events

    def _can_attempt_incantation(self, current_food: int) -> bool:
        """
        Vérifie si on peut tenter une incantation.
        
        Args:
            current_food: Nourriture actuelle
            
        Returns:
            True si incantation possible
        """
        if self.state.level >= GameplayConstants.MAX_LEVEL:
            return False

        # Vérifier la nourriture selon le niveau
        if self.state.level == 1:
            min_food_required = StateTransitionThresholds.MIN_FOOD_FOR_LEVEL_1_INCANTATION
        else:
            min_food_required = self.incant_food_threshold
            
        if current_food < min_food_required:
            return False

        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        if not requirements:
            return False

        return True

    def _has_all_incant_resources(self) -> bool:
        """
        Vérifie qu'on a toutes les ressources pour l'incantation.
        
        Returns:
            True si toutes les ressources sont disponibles
        """
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        inventory = self.state.get_inventory()

        for resource, needed in requirements.items():
            if inventory.get(resource, 0) < needed:
                return False

        return True

    def _should_attempt_reproduction(self, current_food: int) -> bool:
        """
        Vérifie si on devrait tenter une reproduction.
        
        Args:
            current_food: Nourriture actuelle
            
        Returns:
            True si reproduction recommandée
        """
        if self.state.level < ReproductionConstants.MIN_LEVEL_FOR_REPRODUCTION:
            return False

        if current_food < self.reproduction_food_threshold:
            return False

        if getattr(self.state, 'needs_repro', False):
            return True

        if self.state.level == 2:
            logger.info(f"Reproduction obligatoire niveau 2")
            self.state.needs_repro = True
            return True

        return True

    def _check_food_events(self, current_food: int) -> List[Event]:
        """
        Vérifie les événements liés à la nourriture.
        
        Args:
            current_food: Nourriture actuelle
            
        Returns:
            Liste des événements de nourriture
        """
        events = []

        if current_food <= self.critical_threshold:
            events.append(Event.FOOD_EMERGENCY)
            if current_food != self.last_food_count:
                logger.warning(f"[EventDetector] 🚨 URGENCE ALIMENTAIRE: {current_food} <= {self.critical_threshold}")

        elif current_food <= self.safe_threshold:
            events.append(Event.FOOD_LOW)
            if current_food != self.last_food_count:
                logger.info(f"[EventDetector] ⚠️ Nourriture faible: {current_food} <= {self.safe_threshold}")

        elif current_food >= self.abundant_threshold:
            events.append(Event.FOOD_SUFFICIENT)
            if self.last_food_count < self.abundant_threshold:
                logger.info(f"[EventDetector] ✅ Nourriture suffisante: {current_food} >= {self.abundant_threshold}")

        if current_food < self.last_food_count:
            lost = self.last_food_count - current_food
            logger.debug(f"[EventDetector] Perte de nourriture détectée: -{lost} (reste: {current_food})")

        return events

    def _needs_vision_update(self, current_time: float) -> bool:
        """
        Détermine si une mise à jour de vision est nécessaire.
        
        Args:
            current_time: Temps actuel
            
        Returns:
            True si mise à jour nécessaire
        """
        if getattr(self.state, 'needs_look', False):
            logger.debug("[EventDetector] Vision update demandée par GameState")
            return True

        food_ratio = self.state.get_food_count() / max(self.safe_threshold, 1)

        if food_ratio <= 0.5:
            interval = 5.0
        elif food_ratio <= 1.0:
            interval = 10.0
        else:
            interval = self.vision_check_interval

        time_since_last = current_time - self.last_vision_check
        return time_since_last >= interval

    def _needs_inventory_check(self, current_time: float) -> bool:
        """
        Détermine si une vérification d'inventaire est nécessaire.
        
        Args:
            current_time: Temps actuel
            
        Returns:
            True si vérification nécessaire
        """
        current_food = self.state.get_food_count()

        if current_food <= self.critical_threshold:
            interval = 5.0
        elif current_food <= self.safe_threshold:
            interval = 8.0
        else:
            interval = self.inventory_check_interval

        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= interval

    def _resources_found_in_vision(self) -> bool:
        """
        Vérifie si des ressources sont visibles dans la vision actuelle.
        
        Returns:
            True si ressources trouvées
        """
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return False

        for vision_data in vision.last_vision_data:
            if vision_data.rel_pos != (0, 0) and vision_data.resources:
                return True

        return False

    def get_detection_status(self) -> Dict[str, Any]:
        """
        Retourne le statut de détection pour debug.
        
        Returns:
            Dictionnaire du statut de détection
        """
        current_time = time.time()
        current_food = self.state.get_food_count()

        return {
            'current_food': current_food,
            'current_level': self.state.level,
            'thresholds': {
                'critical': self.critical_threshold,
                'safe': self.safe_threshold,
                'abundant': self.abundant_threshold,
                'exploration_return': self.exploration_return_threshold,
                'incant_food': self.incant_food_threshold,
                'reproduction_food': self.reproduction_food_threshold
            },
            'last_checks': {
                'vision': current_time - self.last_vision_check,
                'inventory': current_time - self.last_inventory_check,
                'incant': current_time - self.last_incant_check,
                'reproduction': current_time - self.last_reproduction_check
            },
            'food_status': (
                'emergency' if current_food <= self.critical_threshold else
                'low' if current_food <= self.safe_threshold else
                'sufficient'
            ),
            'progression_status': {
                'can_incant': self._can_attempt_incantation(current_food),
                'has_all_resources': self._has_all_incant_resources(),
                'should_reproduce': self._should_attempt_reproduction(current_food),
                'level_up_detected': self.level_up_detected
            },
            'coordination_status': {
                'role': getattr(self.state, 'role', 'unknown'),
                'required_players': IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
            },
            'resources_visible': self._resources_found_in_vision()
        }