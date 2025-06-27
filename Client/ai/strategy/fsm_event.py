##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## Détecteur d'événements FSM ENHANCED - Surveillance intelligente + progression
##

import time
from typing import List, Dict, Any
from ai.strategy.fsm import Event
from config import Constants
from utils.logger import logger

class EventDetector:
    """
    Détecteur d'événements ENHANCED pour la FSM.
    Surveille l'état du jeu et génère des événements pour déclencher des transitions,
    incluant la détection d'opportunités de progression et reproduction.
    """

    def __init__(self, game_state):
        self.state = game_state

        self.last_food_count = self.state.get_food_count()
        self.last_level = self.state.level
        self.last_vision_check = time.time()
        self.last_inventory_check = time.time()

        self.last_incant_check = time.time()
        self.last_reproduction_check = time.time()
        self.level_up_detected = False

        self.vision_check_interval = 15.0
        self.inventory_check_interval = 10.0
        self.emergency_check_interval = 5.0
        self.incant_check_interval = 8.0
        self.reproduction_check_interval = 12.0

        self._update_thresholds()

        logger.debug("[EventDetector] Enhanced detector initialisé avec surveillance progression")

    def _update_thresholds(self):
        """Met à jour les seuils selon le niveau actuel."""
        level = self.state.level
        base_critical = 8
        base_safe = 20

        if level >= 7:
            multiplier = 2.5
        elif level >= 4:
            multiplier = 1.8
        else:
            multiplier = 1.0

        self.critical_threshold = int(base_critical * multiplier)
        self.safe_threshold = int(base_safe * multiplier)
        self.abundant_threshold = int(base_safe * multiplier * 1.5)

        self.incant_food_threshold = max(35, int(base_safe * multiplier * 1.8))
        self.reproduction_food_threshold = max(45, int(base_safe * multiplier * 2.2))

    def detect_events(self) -> List[Event]:
        """
        Détecte les événements basés sur l'état actuel du jeu - ENHANCED.
        Retourne une liste d'événements à traiter par la FSM.
        """
        events = []
        current_time = time.time()

        if self.last_level != self.state.level:
            self._handle_level_change(events)
            self._update_thresholds()
            self.last_level = self.state.level

        # 1. Vérification critique de la nourriture (priorité absolue)
        current_food = self.state.get_food_count()
        food_events = self._check_food_events(current_food)
        events.extend(food_events)

        # 2. Vérification opportunités de progression
        if current_time - self.last_incant_check >= self.incant_check_interval:
            progression_events = self._check_progression_events(current_food)
            events.extend(progression_events)
            self.last_incant_check = current_time

        # 3. Vérification opportunités de reproduction
        if current_time - self.last_reproduction_check >= self.reproduction_check_interval:
            reproduction_events = self._check_reproduction_events(current_food)
            events.extend(reproduction_events)
            self.last_reproduction_check = current_time

        # 4. Vérification besoin de vision
        if self._needs_vision_update(current_time):
            events.append(Event.NEED_VISION)
            self.last_vision_check = current_time

        # 5. Vérification besoin d'inventaire
        if self._needs_inventory_check(current_time):
            events.append(Event.NEED_INVENTORY)
            self.last_inventory_check = current_time

        # 6. Détection de ressources trouvées
        if self._resources_found_in_vision():
            events.append(Event.RESOURCES_FOUND)

        self.last_food_count = current_food

        return events

    def _handle_level_change(self, events: List[Event]):
        """Gère les événements de changement de niveau."""
        old_level = self.last_level
        new_level = self.state.level

        if new_level > old_level:
            logger.info(f"[EventDetector] 🆙 LEVEL UP détecté: {old_level} → {new_level}")
            events.append(Event.LEVEL_UP)
            self.level_up_detected = True

            if new_level == 2:
                events.append(Event.LEVEL_2_ACHIEVED)
                logger.info("[EventDetector] Niveau 2 atteint - reproduction possible")

            if new_level >= Constants.MAX_LEVEL.value:
                events.append(Event.MAX_LEVEL_REACHED)
                logger.info("[EventDetector] Niveau maximum atteint!")

    def _check_progression_events(self, current_food: int) -> List[Event]:
        """Vérifie les opportunités de progression (incantation)."""
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
        """Vérifie les opportunités de reproduction."""
        events = []

        if self._should_attempt_reproduction(current_food):
            events.append(Event.SHOULD_REPRODUCE)

            if current_food >= self.reproduction_food_threshold and self.state.level >= 2:
                events.append(Event.REPRODUCTION_READY)
                logger.debug(f"[EventDetector] Reproduction prête (niveau {self.state.level}, food: {current_food})")

        return events

    def _can_attempt_incantation(self, current_food: int) -> bool:
        """Vérifie si on peut tenter une incantation."""
        if current_food < self.incant_food_threshold:
            return False

        if self.state.level >= Constants.MAX_LEVEL.value:
            return False

        requirements = self.state.get_incantation_requirements()
        if not requirements:
            return False

        return True

    def _has_all_incant_resources(self) -> bool:
        """Vérifie qu'on a toutes les ressources pour l'incantation."""
        requirements = self.state.get_incantation_requirements()
        inventory = self.state.get_inventory()

        for resource, needed in requirements.items():
            if inventory.get(resource, 0) < needed:
                return False

        return True

    def _should_attempt_reproduction(self, current_food: int) -> bool:
        """Vérifie si on devrait tenter une reproduction."""
        if self.state.level < 2:
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
        """Vérifie les événements liés à la nourriture - ENHANCED."""
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
        """Détermine si une mise à jour de vision est nécessaire."""
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
        """Détermine si une vérification d'inventaire est nécessaire."""
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
        """Vérifie si des ressources sont visibles dans la vision actuelle."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return False

        for vision_data in vision.last_vision_data:
            if vision_data.rel_pos != (0, 0) and vision_data.resources:
                return True

        return False

    def get_detection_status(self) -> Dict[str, Any]:
        """Retourne le statut de détection pour debug"""
        current_time = time.time()
        current_food = self.state.get_food_count()

        return {
            'current_food': current_food,
            'current_level': self.state.level,
            'thresholds': {
                'critical': self.critical_threshold,
                'safe': self.safe_threshold,
                'abundant': self.abundant_threshold,
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
            'resources_visible': self._resources_found_in_vision()
        }
