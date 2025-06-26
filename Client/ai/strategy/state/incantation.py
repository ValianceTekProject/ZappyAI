##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## IncantationState - Gestion de l'incantation pour progression - CORRIGÉ
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from config import Constants, CommandType
from utils.logger import logger

class IncantationState(State):
    """
    État d'incantation pour la progression de niveau - VERSION CORRIGÉE.
    
    Objectifs:
    1. Déposer les ressources nécessaires au sol
    2. Lancer l'incantation en sécurité
    3. Gérer les cas d'échec avec LOOK automatique
    4. Transition vers reproduction après succès
    """
    
    def __init__(self, planner):
        super().__init__(planner)
        
        # Phases de l'incantation
        self.incant_stage = 0  # 0=préparation, 1=dépôt, 2=vérification, 3=lancement
        self.resources_to_drop = []
        
        # Timing et sécurité
        self.incant_start_time = time.time()
        self.incant_timeout = 60.0  # 1 minute max pour incantation
        self.min_food_for_incant = self._calculate_min_food()
        
        # Flags de contrôle pour éviter les boucles
        self.waiting_for_command = False
        self.last_command_time = time.time()
        self.command_timeout = 5.0  # 5 secondes max d'attente
        
        # Statistiques
        self.resources_dropped = 0
        self.attempts = 0
        self.max_attempts = 2
        
        logger.info(f"[IncantationState] 🔮 Préparation incantation niveau {self.state.level} → {self.state.level + 1}")

    def execute(self) -> Optional[Any]:
        """
        Logique d'incantation - SOLUTION SIMPLE avec sortie automatique.
        """
        # 🔧 SOLUTION SIMPLE : Si incantation terminée, laisser le FSM faire la transition
        if hasattr(self, 'incantation_completed') and self.incantation_completed:
            logger.info("[IncantationState] Incantation terminée, sortie de l'état")
            return None  # Le FSMPlanner fera la transition automatiquement
        
        current_time = time.time()
        
        # 1. Vérification sécurité alimentaire critique
        current_food = self.state.get_food_count()
        if current_food < self.min_food_for_incant:
            logger.warning(f"[IncantationState] Nourriture insuffisante ({current_food} < {self.min_food_for_incant}), abandon")
            return None  # Retour à la survie
        
        # 2. Timeout de sécurité
        if current_time - self.incant_start_time > self.incant_timeout:
            logger.error("[IncantationState] Timeout incantation, abandon")
            return None
        
        # 3. Timeout sur commande en attente
        if self.waiting_for_command and (current_time - self.last_command_time > self.command_timeout):
            logger.warning("[IncantationState] Timeout commande, reset état")
            self.waiting_for_command = False
            return self.cmd_mgr.look()
        
        # 4. Ne pas envoyer de nouvelle commande si on attend déjà
        if self.waiting_for_command:
            return None
        
        # 5. Vérification vision si nécessaire
        if not self.state.get_vision().last_vision_data or getattr(self.state, 'needs_look', False):
            logger.debug("[IncantationState] Mise à jour vision nécessaire")
            return self.cmd_mgr.look()
        
        # 6. Phases d'incantation
        if self.incant_stage == 0:
            return self._prepare_incantation()
        elif self.incant_stage == 1:
            return self._drop_resources()
        elif self.incant_stage == 2:
            return self._verify_before_incant()
        elif self.incant_stage == 3:
            return self._launch_incantation()
        
        return None

    def _calculate_min_food(self) -> int:
        """Calcule la nourriture minimale RÉDUITE pour incantation."""
        if self.state.level == 1:
            return 20  # Très accessible pour première incantation
        elif self.state.level <= 3:
            return 25  # Toujours plus accessible
        else:
            return 35  # Seuil normal pour niveaux élevés

    def _prepare_incantation(self) -> Optional[Any]:
        """Phase 0: Préparation et vérification des prérequis - CORRIGÉE."""
        logger.info("[IncantationState] Phase 0: Préparation incantation")
        
        # Vérifier qu'on a toutes les ressources
        requirements = self.state.get_incantation_requirements()
        inventory = self.state.get_inventory()
        
        missing = {}
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current
        
        if missing:
            logger.error(f"[IncantationState] Ressources manquantes: {missing}, abandon incantation")
            return None  # Retour à la collecte
        
        # Préparer liste des ressources à déposer
        ground_resources = self._get_resources_at_current_position()
        self.resources_to_drop = []
        
        for resource, needed in requirements.items():
            on_ground = ground_resources.get(resource, 0)
            to_drop = max(0, needed - on_ground)
            if to_drop > 0:
                self.resources_to_drop.extend([resource] * to_drop)
        
        logger.info(f"[IncantationState] Ressources à déposer: {self.resources_to_drop}")
        
        # 🔧 CORRECTION : Passer à la phase suivante ET retourner une action
        self.incant_stage = 1
        
        # Si pas de ressources à déposer, passer directement à la vérification
        if not self.resources_to_drop:
            logger.info("[IncantationState] Aucune ressource à déposer, vérification directe")
            self.incant_stage = 2
            return self.cmd_mgr.look()  # Vérifier l'état actuel
        
        # Sinon, commencer le dépôt
        return self._drop_resources()

    def _drop_resources(self) -> Optional[Any]:
        """Phase 1: Dépôt des ressources au sol - CORRIGÉE."""
        if self.resources_to_drop:
            resource = self.resources_to_drop.pop(0)
            logger.info(f"[IncantationState] Dépôt {resource} ({len(self.resources_to_drop)} restants)")
            self.resources_dropped += 1
            
            # 🔧 NOUVEAU : Tracker la ressource qu'on va déposer
            self._last_set_resource = resource
            
            # 🔧 CORRECTION : Marquer qu'on attend une réponse
            self.waiting_for_command = True
            self.last_command_time = time.time()
            return self.cmd_mgr.set(resource)
        else:
            logger.info("[IncantationState] Toutes les ressources déposées, vérification")
            self.incant_stage = 2
            # 🔧 CORRECTION : Retourner une commande LOOK au lieu de None
            return self.cmd_mgr.look()

    def _verify_before_incant(self) -> Optional[Any]:
        """Phase 2: Vérification finale avant lancement - CORRIGÉE."""
        logger.info("[IncantationState] Phase 2: Vérification finale")
        
        # Vérifier que toutes les conditions sont remplies
        if self._verify_incantation_conditions():
            logger.info("[IncantationState] ✅ Conditions vérifiées, passage au lancement")
            self.incant_stage = 3
            # 🔧 CORRECTION : Lancer directement l'incantation
            return self._launch_incantation()
        else:
            logger.warning("[IncantationState] ❌ Conditions non remplies")
            self.attempts += 1
            
            if self.attempts >= self.max_attempts:
                logger.error("[IncantationState] Trop de tentatives, abandon")
                return None
            
            # Reset pour nouvel essai
            logger.info("[IncantationState] Reset pour nouvel essai")
            self.incant_stage = 0
            # 🔧 CORRECTION : Faire un LOOK pour réactualiser la situation
            return self.cmd_mgr.look()

    def _launch_incantation(self) -> Optional[Any]:
        """Phase 3: Lancement de l'incantation - CORRIGÉE."""
        logger.info("[IncantationState] Phase 3: Lancement incantation")
        
        # Vérifications finales une dernière fois
        if not self._verify_incantation_conditions():
            logger.error("[IncantationState] Conditions perdues au moment du lancement")
            self.attempts += 1
            
            if self.attempts >= self.max_attempts:
                logger.error("[IncantationState] Trop de tentatives, abandon")
                return None
            
            # Reset pour nouvel essai
            self.incant_stage = 0
            return self.cmd_mgr.look()
        
        # Lancement!
        logger.info(f"[IncantationState] 🚀 LANCEMENT INCANTATION niveau {self.state.level} → {self.state.level + 1}")
        
        # 🔧 CORRECTION : Marquer qu'on attend une réponse
        self.waiting_for_command = True
        self.last_command_time = time.time()
        return self.cmd_mgr.incantation()

    def _verify_incantation_conditions(self) -> bool:
        """Vérifie que toutes les conditions sont remplies."""
        # Vérifier ressources au sol
        requirements = self.state.get_incantation_requirements()
        ground_resources = self._get_resources_at_current_position()
        
        for resource, needed in requirements.items():
            on_ground = ground_resources.get(resource, 0)
            if on_ground < needed:
                logger.warning(f"[IncantationState] {resource} insuffisant au sol: {on_ground} < {needed}")
                return False
        
        # Vérifier nombre de joueurs (pour plus tard quand on aura la coordination)
        required_players = self.state.get_required_player_count()
        current_players = self._count_players_on_tile()
        
        if current_players < required_players:
            logger.warning(f"[IncantationState] Joueurs insuffisants: {current_players} < {required_players}")
            return False
        
        return True

    def _get_resources_at_current_position(self) -> dict:
        """Retourne les ressources sur la tuile actuelle."""
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return dict(data.resources)
        return {}

    def _count_players_on_tile(self) -> int:
        """Compte les joueurs sur la tuile actuelle."""
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return data.players
        return 1  # Au minimum nous-même

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes - SOLUTION SIMPLE."""
        # 🔧 CORRECTION : Reset du flag d'attente
        self.waiting_for_command = False

        if command_type == CommandType.SET:
            resource_name = getattr(self, '_last_set_resource', 'unknown')
            logger.debug(f"[IncantationState] ✅ Ressource {resource_name} déposée avec succès")

            # 🔧 NOUVEAU : Mise à jour automatique de la vision après SET
            vision = self.state.get_vision()
            if hasattr(self, '_last_set_resource'):
                vision.add_resource_at((0, 0), self._last_set_resource)

        elif command_type == CommandType.INCANTATION:
            logger.info(f"[IncantationState] ✅🎉 INCANTATION RÉUSSIE! Niveau {self.state.level}")

            # 🔧 SOLUTION SIMPLE : Marquer l'incantation comme terminée
            self.incantation_completed = True

        elif command_type == CommandType.LOOK:
            logger.debug("[IncantationState] Vision mise à jour")

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes - CORRIGÉE."""
        # 🔧 CORRECTION : Reset du flag d'attente
        self.waiting_for_command = False
        
        if command_type == CommandType.SET:
            logger.error(f"[IncantationState] ❌ Échec dépôt ressource: {response}")
            # 🔧 NOUVEAU : LOOK automatique après échec de SET
            self.context['needs_vision_update'] = True
            
        elif command_type == CommandType.INCANTATION:
            logger.error(f"[IncantationState] 💥 INCANTATION ÉCHOUÉE: {response}")
            self.attempts += 1
            
            # 🔧 NOUVEAU : LOOK automatique après échec d'incantation
            self.context['needs_vision_update'] = True
            
            if self.attempts >= self.max_attempts:
                logger.error("[IncantationState] Abandon après échecs répétés")
            else:
                # Reset pour nouvel essai
                self.incant_stage = 0
                logger.info("[IncantationState] Préparation nouvel essai")

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements pendant incantation."""
        if event == Event.FOOD_EMERGENCY:
            logger.error("[IncantationState] URGENCE ALIMENTAIRE! Abandon incantation")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)
        
        # Ignorer les autres événements pendant l'incantation
        return None

    def on_enter(self):
        """Actions à l'entrée de l'état."""
        super().on_enter()
        current_food = self.state.get_food_count()
        requirements = self.state.get_incantation_requirements()
        
        logger.info(f"[IncantationState] 🔮 ENTRÉE incantation - "
                   f"Niveau: {self.state.level}, Food: {current_food}, "
                   f"Ressources requises: {requirements}")
        
        # Reset état interne
        self.incant_stage = 0
        self.resources_to_drop = []
        self.resources_dropped = 0
        self.attempts = 0
        self.incant_start_time = time.time()
        
        # Reset des flags de contrôle
        self.waiting_for_command = False
        self.last_command_time = time.time()
        self.incantation_completed = False  # 🔧 NOUVEAU : Flag de fin d'incantation

    def on_exit(self):
        """Actions à la sortie de l'état."""
        super().on_exit()
        duration = time.time() - self.incant_start_time
        
        if self.state.level > self.state.level:  # Level up détecté
            logger.info(f"[IncantationState] ✅ SORTIE avec succès - Nouveau niveau: {self.state.level}, "
                       f"Durée: {duration:.1f}s, Ressources déposées: {self.resources_dropped}")
        else:
            logger.info(f"[IncantationState] ❌ SORTIE sans succès - Durée: {duration:.1f}s")
        
        # Nettoyage
        self.resources_to_drop.clear()
        self.waiting_for_command = False