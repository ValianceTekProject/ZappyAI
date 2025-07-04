##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## fsm_event - Détecteur d'événements avec constantes centralisées
##

import time
from typing import List, Dict, Any
from ai.strategy.fsm import Event
from constant import (
    FoodThresholds, IncantationRequirements, StateTransitionThresholds, 
    GameplayConstants, ReproductionRules
)
from utils.logger import logger


class EventDetector:
    """Détecteur d'événements pour la FSM avec constantes centralisées."""

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

        logger.debug("[EventDetector] Détecteur avec constantes centralisées initialisé")

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
            self.last_level = self.state.level

        # Événements de nourriture avec seuils centralisés
        current_food = self.state.get_food_count()
        food_events = self._check_food_events(current_food)
        events.extend(food_events)

        # Événements de progression
        if current_time - self.last_incant_check >= 8.0:
            progression_events = self._check_progression_events(current_food)
            events.extend(progression_events)
            self.last_incant_check = current_time

        # Événements de reproduction
        if current_time - self.last_reproduction_check >= 12.0:
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

            if new_level == ReproductionRules.TRIGGER_LEVEL:
                events.append(Event.LEVEL_2_ACHIEVED)
                logger.info("[EventDetector] Niveau 2 atteint - reproduction activée")

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
        Vérifie les opportunités de reproduction selon les règles strictes.
        
        Args:
            current_food: Nourriture actuelle
            
        Returns:
            Liste des événements de reproduction
        """
        events = []

        if self.state.should_reproduce():
            events.append(Event.SHOULD_REPRODUCE)

            if (current_food >= ReproductionRules.MIN_FOOD_REQUIRED and 
                self.state.level == ReproductionRules.TRIGGER_LEVEL):
                events.append(Event.REPRODUCTION_READY)
                logger.debug(f"[EventDetector] Reproduction prête (niveau {self.state.level}, food: {current_food})")

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
            min_food_required = StateTransitionThresholds.MIN_FOOD_FOR_COORDINATION
            
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

    def _check_food_events(self, current_food: int) -> List[Event]:
        """
        Vérifie les événements liés à la nourriture avec seuils centralisés.
        
        Args:
            current_food: Nourriture actuelle
            
        Returns:
            Liste des événements de nourriture
        """
        events = []

        if current_food <= FoodThresholds.CRITICAL:
            events.append(Event.FOOD_EMERGENCY)
            if current_food != self.last_food_count:
                logger.warning(f"[EventDetector] 🚨 URGENCE ALIMENTAIRE: {current_food} <= {FoodThresholds.CRITICAL}")

        elif current_food <= FoodThresholds.SUFFICIENT:
            events.append(Event.FOOD_LOW)
            if current_food != self.last_food_count:
                logger.info(f"[EventDetector] ⚠️ Nourriture faible: {current_food} <= {FoodThresholds.SUFFICIENT}")

        elif current_food >= FoodThresholds.ABUNDANT:
            events.append(Event.FOOD_SUFFICIENT)
            if self.last_food_count < FoodThresholds.ABUNDANT:
                logger.info(f"[EventDetector] ✅ Nourriture suffisante: {current_food} >= {FoodThresholds.ABUNDANT}")

        # Détection de la consommation
        if current_food < self.last_food_count:
            lost = self.last_food_count - current_food
            logger.debug(f"[EventDetector] Consommation détectée: -{lost} (reste: {current_food})")

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

        food_ratio = self.state.get_food_count() / max(FoodThresholds.SUFFICIENT, 1)

        if food_ratio <= 0.5:
            interval = 5.0
        elif food_ratio <= 1.0:
            interval = 8.0
        else:
            interval = GameplayConstants.VISION_UPDATE_INTERVAL

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

        if current_food <= FoodThresholds.CRITICAL:
            interval = 5.0
        elif current_food <= FoodThresholds.SUFFICIENT:
            interval = 8.0
        else:
            interval = GameplayConstants.INVENTORY_CHECK_INTERVAL

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
                'critical': FoodThresholds.CRITICAL,
                'sufficient': FoodThresholds.SUFFICIENT,
                'abundant': FoodThresholds.ABUNDANT,
                'coordination_min': FoodThresholds.COORDINATION_MIN,
                'reproduction_min': FoodThresholds.REPRODUCTION_MIN
            },
            'last_checks': {
                'vision': current_time - self.last_vision_check,
                'inventory': current_time - self.last_inventory_check,
                'incant': current_time - self.last_incant_check,
                'reproduction': current_time - self.last_reproduction_check
            },
            'food_status': (
                'emergency' if current_food <= FoodThresholds.CRITICAL else
                'low' if current_food <= FoodThresholds.SUFFICIENT else
                'sufficient'
            ),
            'progression_status': {
                'can_incant': self._can_attempt_incantation(current_food),
                'has_all_resources': self._has_all_incant_resources(),
                'should_reproduce': self.state.should_reproduce(),
                'level_up_detected': self.level_up_detected
            },
            'required_players': IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1),
            'resources_visible': self._resources_found_in_vision()
        }