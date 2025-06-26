##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## incantation
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from config import Constants, CommandType
from utils.logger import logger

class IncantationState(State):
    """
    État d'incantation pour la progression de niveau.
    """

    def __init__(self, planner):
        super().__init__(planner)
        self.incant_stage = 0
        self.resources_to_drop = []
        self.incant_start_time = time.time()
        self.incant_timeout = 60.0
        self.min_food_for_incant = self._calculate_min_food()
        self.waiting_for_command = False

        self.last_command_time = time.time()
        self.command_timeout = 5.0
        self.resources_dropped = 0
        self.attempts = 0
        self.max_attempts = 2
        logger.info(f"[IncantationState] 🔮 Préparation incantation niveau {self.state.level} → {self.state.level + 1}")

    def execute(self) -> Optional[Any]:
        """
        Logique d'incantation.
        """
        if hasattr(self, 'incantation_completed') and self.incantation_completed:
            logger.info("[IncantationState] Incantation terminée, sortie de l'état")
            return None

        current_time = time.time()

        current_food = self.state.get_food_count()
        if current_food < self.min_food_for_incant:
            logger.warning(f"[IncantationState] Nourriture insuffisante ({current_food} < {self.min_food_for_incant}), abandon")
            return None

        if current_time - self.incant_start_time > self.incant_timeout:
            logger.error("[IncantationState] Timeout incantation, abandon")
            return None

        if self.waiting_for_command and (current_time - self.last_command_time > self.command_timeout):
            logger.warning("[IncantationState] Timeout commande, reset état")
            self.waiting_for_command = False
            return self.cmd_mgr.look()

        if self.waiting_for_command:
            return None

        if not self.state.get_vision().last_vision_data or getattr(self.state, 'needs_look', False):
            logger.debug("[IncantationState] Mise à jour vision nécessaire")
            return self.cmd_mgr.look()

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
        """Calcule la nourriture minimale pour incantation."""
        if self.state.level == 1:
            return 20
        elif self.state.level <= 3:
            return 25
        else:
            return 35

    def _prepare_incantation(self) -> Optional[Any]:
        """Phase 0: Préparation et vérification des prérequis."""
        logger.info("[IncantationState] Phase 0: Préparation incantation")

        requirements = self.state.get_incantation_requirements()
        inventory = self.state.get_inventory()

        missing = {}
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current

        if missing:
            logger.error(f"[IncantationState] Ressources manquantes: {missing}, abandon incantation")
            return None

        ground_resources = self._get_resources_at_current_position()
        self.resources_to_drop = []

        for resource, needed in requirements.items():
            on_ground = ground_resources.get(resource, 0)
            to_drop = max(0, needed - on_ground)
            if to_drop > 0:
                self.resources_to_drop.extend([resource] * to_drop)

        logger.info(f"[IncantationState] Ressources à déposer: {self.resources_to_drop}")

        self.incant_stage = 1

        if not self.resources_to_drop:
            logger.info("[IncantationState] Aucune ressource à déposer, vérification directe")
            self.incant_stage = 2
            return self.cmd_mgr.look()

        return self._drop_resources()

    def _drop_resources(self) -> Optional[Any]:
        """Phase 1: Dépôt des ressources au sol."""
        if self.resources_to_drop:
            resource = self.resources_to_drop.pop(0)
            logger.info(f"[IncantationState] Dépôt {resource} ({len(self.resources_to_drop)} restants)")
            self.resources_dropped += 1
            self._last_set_resource = resource
            self.waiting_for_command = True
            self.last_command_time = time.time()
            return self.cmd_mgr.set(resource)
        else:
            logger.info("[IncantationState] Toutes les ressources déposées, vérification")
            self.incant_stage = 2
            return self.cmd_mgr.look()

    def _verify_before_incant(self) -> Optional[Any]:
        """Phase 2: Vérification finale avant lancement."""
        logger.info("[IncantationState] Phase 2: Vérification finale")

        if self._verify_incantation_conditions():
            logger.info("[IncantationState] ✅ Conditions vérifiées, passage au lancement")
            self.incant_stage = 3
            return self._launch_incantation()
        else:
            logger.warning("[IncantationState] ❌ Conditions non remplies")
            self.attempts += 1

            if self.attempts >= self.max_attempts:
                logger.error("[IncantationState] Trop de tentatives, abandon")
                return None

            logger.info("[IncantationState] Reset pour nouvel essai")
            self.incant_stage = 0
            return self.cmd_mgr.look()

    def _launch_incantation(self) -> Optional[Any]:
        """Phase 3: Lancement de l'incantation."""
        logger.info("[IncantationState] Phase 3: Lancement incantation")

        if not self._verify_incantation_conditions():
            logger.error("[IncantationState] Conditions perdues au moment du lancement")
            self.attempts += 1

            if self.attempts >= self.max_attempts:
                logger.error("[IncantationState] Trop de tentatives, abandon")
                return None

            self.incant_stage = 0
            return self.cmd_mgr.look()

        logger.info(f"[IncantationState] 🚀 LANCEMENT INCANTATION niveau {self.state.level} → {self.state.level + 1}")
        self.waiting_for_command = True
        self.last_command_time = time.time()
        return self.cmd_mgr.incantation()

    def _verify_incantation_conditions(self) -> bool:
        """Vérifie que toutes les conditions sont remplies."""
        requirements = self.state.get_incantation_requirements()
        ground_resources = self._get_resources_at_current_position()

        for resource, needed in requirements.items():
            on_ground = ground_resources.get(resource, 0)
            if on_ground < needed:
                logger.warning(f"[IncantationState] {resource} insuffisant au sol: {on_ground} < {needed}")
                return False

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
        return 1

    def on_command_success(self, command_type, response=None):
        """Gestion du succès des commandes."""
        self.waiting_for_command = False

        if command_type == CommandType.SET:
            resource_name = getattr(self, '_last_set_resource', 'unknown')
            logger.debug(f"[IncantationState] ✅ Ressource {resource_name} déposée avec succès")
            vision = self.state.get_vision()
            if hasattr(self, '_last_set_resource'):
                vision.add_resource_at((0, 0), self._last_set_resource)

        elif command_type == CommandType.INCANTATION:
            logger.info(f"[IncantationState] ✅🎉 INCANTATION RÉUSSIE! Niveau {self.state.level}")
            self.incantation_completed = True

        elif command_type == CommandType.LOOK:
            logger.debug("[IncantationState] Vision mise à jour")

    def on_command_failed(self, command_type, response=None):
        """Gestion des échecs de commandes."""
        self.waiting_for_command = False

        if command_type == CommandType.SET:
            logger.error(f"[IncantationState] ❌ Échec dépôt ressource: {response}")
            self.context['needs_vision_update'] = True

        elif command_type == CommandType.INCANTATION:
            logger.error(f"[IncantationState] 💥 INCANTATION ÉCHOUÉE: {response}")
            self.attempts += 1
            self.context['needs_vision_update'] = True

            if self.attempts >= self.max_attempts:
                logger.error("[IncantationState] Abandon après échecs répétés")
            else:
                self.incant_stage = 0
                logger.info("[IncantationState] Préparation nouvel essai")

    def on_event(self, event: Event) -> Optional[State]:
        """Gestion des événements pendant incantation."""
        if event == Event.FOOD_EMERGENCY:
            logger.error("[IncantationState] URGENCE ALIMENTAIRE! Abandon incantation")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)
        return None

    def on_enter(self):
        """Actions à l'entrée de l'état."""
        super().on_enter()
        current_food = self.state.get_food_count()
        requirements = self.state.get_incantation_requirements()

        logger.info(f"[IncantationState] 🔮 ENTRÉE incantation - "
                    f"Niveau: {self.state.level}, Food: {current_food}, "
                    f"Ressources requises: {requirements}")

        self.incant_stage = 0
        self.resources_to_drop = []
        self.resources_dropped = 0
        self.attempts = 0
        self.incant_start_time = time.time()
        self.waiting_for_command = False
        self.last_command_time = time.time()
        self.incantation_completed = False

    def on_exit(self):
        """Actions à la sortie de l'état."""
        super().on_exit()
        duration = time.time() - self.incant_start_time

        if self.state.level > self.state.level:
            logger.info(f"[IncantationState] ✅ SORTIE avec succès - Nouveau niveau: {self.state.level}, "
                        f"Durée: {duration:.1f}s, Ressources déposées: {self.resources_dropped}")
        else:
            logger.info(f"[IncantationState] ❌ SORTIE sans succès - Durée: {duration:.1f}s")

        self.resources_to_drop.clear()
        self.waiting_for_command = False
