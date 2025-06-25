##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## EmergencyState - Gestion des situations critiques de survie
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from ai.strategy.pathfinding import Pathfinder
from config import Constants, CommandType
from utils.logger import logger

class EmergencyState(State):
    """
    État d'urgence critique - Survie immédiate.
    
    Priorités absolues:
    1. Ramasser toute nourriture sur la tuile actuelle
    2. Foncer vers la nourriture la plus proche visible
    3. Explorer désespérément si aucune nourriture visible
    4. Optimiser chaque action pour éviter la mort
    """
    
    def __init__(self, planner):
        super().__init__(planner)
        self.pathfinder = Pathfinder()
        
        # État interne de l'urgence
        self.emergency_target = None
        self.emergency_commands = []
        self.desperate_mode = False
        self.last_emergency_action = time.time()
        
        # Compteurs pour éviter les boucles infinies
        self.failed_attempts = 0
        self.max_failed_attempts = 3
        
        logger.warning("[EmergencyState] 🚨 MODE URGENCE ACTIVÉ - SURVIE CRITIQUE")

    def execute(self) -> Optional[Any]:
        """
        Logique d'urgence optimisée pour la survie immédiate.
        Chaque action compte, pas de temps à perdre.
        """
        current_food = self.state.get_food_count()
        critical_threshold = self._get_critical_threshold()
        
        # Log d'urgence fréquent
        if time.time() - self.last_emergency_action > 2.0:
            logger.error(f"[EmergencyState] 💀 CRITIQUE! Food: {current_food}/{critical_threshold}")
            self.last_emergency_action = time.time()
        
        # 1. Vérification vision obligatoire si pas de données
        if not self.state.get_vision().last_vision_data or self.context['needs_vision_update']:
            logger.warning("[EmergencyState] Vision manquante, LOOK d'urgence")
            self.context['needs_vision_update'] = False
            return self.cmd_mgr.look()
        
        # 2. Ramasser nourriture sur tuile actuelle (priorité absolue)
        if self._food_on_current_tile():
            logger.error("[EmergencyState] 🍖 NOURRITURE ICI! Ramassage immédiat")
            return self.cmd_mgr.take(Constants.FOOD.value)
        
        # 3. Exécuter les commandes d'urgence en queue
        if self.emergency_commands:
            next_cmd = self.emergency_commands.pop(0)
            logger.warning(f"[EmergencyState] Exécution commande urgence: {next_cmd}")
            return self._execute_emergency_command(next_cmd)
        
        # 4. Cibler nourriture visible la plus proche
        food_target = self._find_closest_food()
        if food_target:
            if food_target != self.emergency_target:
                self.emergency_target = food_target
                self.emergency_commands = self._plan_emergency_path(food_target)
                logger.error(f"[EmergencyState] 🎯 Nouvelle cible nourriture: {food_target.rel_position}")
            
            if self.emergency_commands:
                next_cmd = self.emergency_commands.pop(0)
                return self._execute_emergency_command(next_cmd)
        
        # 5. Mode désespéré - exploration rapide
        if not self.desperate_mode:
            logger.error("[EmergencyState] 😱 MODE DÉSESPÉRÉ - Aucune nourriture visible!")
            self.desperate_mode = True
        
        return self._desperate_exploration()

    def _get_critical_threshold(self) -> int:
        """Calcule le seuil critique selon le niveau."""
        base = 8
        if self.state.level >= 7:
            return int(base * 2.5)
        elif self.state.level >= 4:
            return int(base * 1.8)
        return base

    def _food_on_current_tile(self) -> bool:
        """Vérifie si de la nourriture est présente sur la tuile actuelle."""
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return Constants.FOOD.value in data.resources and data.resources[Constants.FOOD.value] > 0
        return False

    def _find_closest_food(self):
        """Trouve la nourriture la plus proche dans la vision."""
        vision = self.state.get_vision()
        return vision.find_closest_resource(Constants.FOOD.value)

    def _plan_emergency_path(self, target):
        """Planifie le chemin d'urgence le plus court vers la cible."""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return []
        
        # Utiliser pathfinder pour obtenir les commandes optimales
        commands = self.pathfinder.get_commands_to_target(
            target, 
            self.state.get_orientation(), 
            vision_data
        )
        
        # Limiter à 5 commandes max pour éviter les longs trajets en urgence
        return commands[:5] if commands else []

    def _execute_emergency_command(self, command_type: CommandType):
        """Exécute une commande d'urgence spécifique."""
        if command_type == CommandType.FORWARD:
            return self.cmd_mgr.forward()
        elif command_type == CommandType.LEFT:
            return self.cmd_mgr.left()
        elif command_type == CommandType.RIGHT:
            return self.cmd_mgr.right()
        else:
            logger.error(f"[EmergencyState] Commande inconnue: {command_type}")
            return None

    def _desperate_exploration(self):
        """Exploration désespérée quand aucune nourriture n'est visible."""
        vision_data = self.state.get_vision().last_vision_data
        
        if not vision_data:
            return self.cmd_mgr.look()
        
        # Choisir direction d'exploration rapide (toujours avancer)
        exploration_cmd = self.pathfinder.get_exploration_direction(
            self.state.get_orientation(), 
            vision_data
        )
        
        logger.warning(f"[EmergencyState] 🏃 Exploration désespérée: {exploration_cmd}")
        return self._execute_emergency_command(exploration_cmd)

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes en mode urgence."""
        self.failed_attempts = 0
        
        if command_type == CommandType.TAKE:
            if response and Constants.FOOD.value in str(response):
                new_food = self.state.get_food_count()
                logger.info(f"[EmergencyState] ✅ Nourriture récupérée! Nouveau total: {new_food}")
                
                # Mise à jour automatique de la vision (économie de commande)
                vision = self.state.get_vision()
                vision.remove_resource_at((0, 0), Constants.FOOD.value)
                
                # Vérifier si on peut sortir du mode urgence
                if new_food > self._get_critical_threshold():
                    logger.info("[EmergencyState] 🎉 Sortie du mode urgence possible")
        
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            # Après mouvement, forcer mise à jour vision
            self.context['needs_vision_update'] = True
            logger.debug("[EmergencyState] Mouvement réussi, vision update programmée")

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs en mode urgence."""
        self.failed_attempts += 1
        logger.error(f"[EmergencyState] ❌ Échec commande {command_type}, tentative {self.failed_attempts}")
        
        if command_type == CommandType.TAKE:
            # Si take échoue, la ressource n'est plus là
            logger.warning("[EmergencyState] Take échoué, ressource indisponible")
            self.emergency_target = None
            self.emergency_commands.clear()
            self.context['needs_vision_update'] = True
        
        elif command_type in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            # Mouvement bloqué, changer de stratégie
            if self.failed_attempts >= 2:
                logger.error("[EmergencyState] Mouvements bloqués, reset stratégie")
                self.emergency_target = None
                self.emergency_commands.clear()
                self.desperate_mode = True

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements en mode urgence."""
        if event == Event.FOOD_SUFFICIENT:
            logger.info("[EmergencyState] ✅ Nourriture suffisante, sortie du mode urgence")
            from ai.strategy.state.collect_food import CollectFoodState
            return CollectFoodState(self.planner)
        
        # En urgence, on ignore les autres événements sauf la nourriture
        return None

    def on_enter(self):
        """Actions à l'entrée du mode urgence."""
        super().on_enter()
        current_food = self.state.get_food_count()
        critical = self._get_critical_threshold()
        
        logger.error(f"[EmergencyState] 🚨 ENTRÉE MODE URGENCE - Food: {current_food}/{critical}")
        
        # Reset des états internes
        self.emergency_target = None
        self.emergency_commands.clear()
        self.desperate_mode = False
        self.failed_attempts = 0
        
        # Forcer une vision immédiate
        self.context['needs_vision_update'] = True

    def on_exit(self):
        """Actions à la sortie du mode urgence."""
        super().on_exit()
        logger.info("[EmergencyState] ✅ SORTIE MODE URGENCE - Situation stabilisée")
        
        # Nettoyage
        self.emergency_target = None
        self.emergency_commands.clear()
        self.desperate_mode = False