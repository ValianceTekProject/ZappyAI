##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## Détecteur d'événements FSM - Surveillance intelligente de l'état
##

import time
from typing import List, Dict, Any
from ai.strategy.fsm import Event
from config import Constants
from utils.logger import logger

class EventDetector:
    """
    Détecteur d'événements pour la FSM.
    Surveille l'état du jeu et génère des événements pour déclencher des transitions.
    """
    
    def __init__(self, game_state):
        self.state = game_state
        
        # Historique pour détecter les changements
        self.last_food_count = self.state.get_food_count()
        self.last_level = self.state.level
        self.last_vision_check = time.time()
        self.last_inventory_check = time.time()
        
        # Intervalles de vérification (en secondes)
        self.vision_check_interval = 15.0  # Vérifier la vision toutes les 15s
        self.inventory_check_interval = 10.0  # Vérifier l'inventaire toutes les 10s
        self.emergency_check_interval = 5.0   # Vérifier urgence toutes les 5s
        
        # Seuils adaptatifs
        self._update_thresholds()
        
        logger.debug("[EventDetector] Initialisé avec surveillance intelligente")

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

    def detect_events(self) -> List[Event]:
        """
        Détecte les événements basés sur l'état actuel du jeu.
        Retourne une liste d'événements à traiter par la FSM.
        """
        events = []
        current_time = time.time()
        
        # Mise à jour des seuils si changement de niveau
        if self.last_level != self.state.level:
            self._update_thresholds()
            self.last_level = self.state.level
            logger.info(f"[EventDetector] Niveau changé: {self.state.level}, nouveaux seuils: "
                       f"critical={self.critical_threshold}, safe={self.safe_threshold}")
        
        # 1. Vérification critique de la nourriture
        current_food = self.state.get_food_count()
        food_events = self._check_food_events(current_food)
        events.extend(food_events)
        
        # 2. Vérification besoin de vision
        if self._needs_vision_update(current_time):
            events.append(Event.NEED_VISION)
            self.last_vision_check = current_time
        
        # 3. Vérification besoin d'inventaire
        if self._needs_inventory_check(current_time):
            events.append(Event.NEED_INVENTORY)
            self.last_inventory_check = current_time
        
        # 4. Détection de ressources trouvées
        if self._resources_found_in_vision():
            events.append(Event.RESOURCES_FOUND)
        
        # Mise à jour de l'historique
        self.last_food_count = current_food
        
        return events

    def _check_food_events(self, current_food: int) -> List[Event]:
        """Vérifie les événements liés à la nourriture."""
        events = []
        
        # Détection des changements critiques de nourriture
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
        
        # Détection de perte de nourriture
        if current_food < self.last_food_count:
            lost = self.last_food_count - current_food
            logger.debug(f"[EventDetector] Perte de nourriture détectée: -{lost} (reste: {current_food})")
        
        return events

    def _needs_vision_update(self, current_time: float) -> bool:
        """Détermine si une mise à jour de vision est nécessaire."""
        # Vision obligatoire si demandée explicitement
        if getattr(self.state, 'needs_look', False):
            logger.debug("[EventDetector] Vision update demandée par GameState")
            return True
        
        # Vision périodique selon l'urgence
        food_ratio = self.state.get_food_count() / max(self.safe_threshold, 1)
        
        if food_ratio <= 0.5:  # Urgence
            interval = 5.0
        elif food_ratio <= 1.0:  # Faible
            interval = 10.0
        else:  # Normal
            interval = self.vision_check_interval
        
        time_since_last = current_time - self.last_vision_check
        return time_since_last >= interval

    def _needs_inventory_check(self, current_time: float) -> bool:
        """Détermine si une vérification d'inventaire est nécessaire."""
        # Vérification plus fréquente en cas de faible nourriture
        current_food = self.state.get_food_count()
        
        if current_food <= self.critical_threshold:
            interval = 5.0  # Très fréquent en urgence
        elif current_food <= self.safe_threshold:
            interval = 8.0  # Fréquent si faible
        else:
            interval = self.inventory_check_interval  # Normal
        
        time_since_last = current_time - self.last_inventory_check
        return time_since_last >= interval

    def _resources_found_in_vision(self) -> bool:
        """Vérifie si des ressources sont visibles dans la vision actuelle."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return False
        
        # Vérifier s'il y a des ressources visibles (hors tuile actuelle)
        for vision_data in vision.last_vision_data:
            if vision_data.rel_pos != (0, 0) and vision_data.resources:
                return True
        
        return False

    def _food_found_in_vision(self) -> bool:
        """Vérifie si de la nourriture est visible."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return False
        
        for vision_data in vision.last_vision_data:
            if Constants.FOOD.value in vision_data.resources:
                return True
        
        return False

    def get_detection_status(self) -> Dict[str, Any]:
        """Retourne le statut de détection pour debug."""
        current_time = time.time()
        current_food = self.state.get_food_count()
        
        return {
            'current_food': current_food,
            'thresholds': {
                'critical': self.critical_threshold,
                'safe': self.safe_threshold,
                'abundant': self.abundant_threshold
            },
            'last_checks': {
                'vision': current_time - self.last_vision_check,
                'inventory': current_time - self.last_inventory_check
            },
            'food_status': (
                'emergency' if current_food <= self.critical_threshold else
                'low' if current_food <= self.safe_threshold else
                'sufficient'
            ),
            'resources_visible': self._resources_found_in_vision(),
            'food_visible': self._food_found_in_vision()
        }