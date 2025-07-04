##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## incantation - État d'incantation avec respect strict du protocole Zappy
##

import time
from typing import Optional, Any
from ai.strategy.fsm import State, Event
from config import CommandType
from constant import (
    IncantationRequirements, StateTransitionThresholds, 
    GameplayConstants, FoodThresholds
)
from utils.logger import logger


class IncantationState(State):
    """
    État d'incantation avec respect strict du protocole Zappy.
    
    RÈGLES CRITIQUES:
    - Niveau 1: Solo autorisé UNIQUEMENT
    - Niveau 2+: Coordination OBLIGATOIRE (cet état ne doit PAS être utilisé)
    """

    def __init__(self, planner):
        """
        Initialise l'état d'incantation.
        
        Args:
            planner: Planificateur FSM
        """
        super().__init__(planner)
        
        # VÉRIFICATION CRITIQUE: Application stricte du protocole
        self.protocol_violation = False
        if not self._verify_protocol_compliance():
            self.protocol_violation = True
            logger.error("[IncantationState] 🚫 VIOLATION PROTOCOLE DÉTECTÉE")
            return
        
        self.incant_stage = 0
        self.resources_to_drop = []
        self.incant_start_time = time.time()
        self.waiting_for_command = False
        self.last_command_time = time.time()
        self.resources_dropped = 0
        self.attempts = 0
        
        target_level = self.state.level + 1
        logger.info(f"[IncantationState] 🔮 Incantation {self.state.level} → {target_level} initiée")

    def _verify_protocol_compliance(self) -> bool:
        """
        Vérification stricte du respect du protocole Zappy.
        
        Returns:
            True si le protocole est respecté, False sinon
        """
        current_level = self.state.level
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(current_level, 1)
        
        # RÈGLE 1: Niveau 1 = Solo autorisé UNIQUEMENT
        if current_level == 1:
            if required_players == 1:
                logger.info("[IncantationState] ✅ Niveau 1: Solo autorisé")
                return True
            else:
                logger.error(f"[IncantationState] ❌ Config invalide niveau 1: {required_players} joueurs requis")
                return False
        
        # RÈGLE 2: Niveau 2+ = Coordination OBLIGATOIRE
        if current_level >= 2:
            logger.error(f"[IncantationState] ❌ PROTOCOLE VIOLATION: Niveau {current_level} "
                        f"nécessite coordination obligatoire ({required_players} joueurs)")
            logger.error("[IncantationState] 🚫 CET ÉTAT NE DOIT PAS ÊTRE UTILISÉ POUR NIVEAU 2+")
            return False
        
        return True

    def execute(self) -> Optional[Any]:
        """
        Logique d'incantation avec vérifications de sécurité strictes.
        
        Returns:
            Commande à exécuter ou None
        """
        # Vérification critique de violation de protocole
        if self.protocol_violation:
            logger.error("[IncantationState] 🚫 Arrêt dû à violation protocole")
            return self._handle_protocol_violation()

        # Vérification si incantation déjà terminée
        if hasattr(self, 'incantation_completed') and self.incantation_completed:
            return None

        current_time = time.time()

        # Vérifications de sécurité continues
        if not self._verify_continuous_safety():
            logger.error("[IncantationState] ❌ Conditions de sécurité perdues")
            return self._handle_safety_failure()

        # Vérification timeout global
        if current_time - self.incant_start_time > 60.0:
            logger.error("[IncantationState] ⏰ Timeout incantation")
            return self._handle_timeout()

        # Vérification timeout commande
        if self.waiting_for_command and (current_time - self.last_command_time > 5.0):
            logger.warning("[IncantationState] ⏰ Timeout commande")
            self.waiting_for_command = False
            return self.cmd_mgr.look()

        # Ne pas exécuter si on attend une réponse
        if self.waiting_for_command:
            return None

        # Mise à jour vision si nécessaire
        if not self.state.get_vision().last_vision_data or getattr(self.state, 'needs_look', False):
            return self.cmd_mgr.look()

        # Exécution selon la phase
        if self.incant_stage == 0:
            return self._prepare_incantation()
        elif self.incant_stage == 1:
            return self._drop_resources()
        elif self.incant_stage == 2:
            return self._verify_before_incant()
        elif self.incant_stage == 3:
            return self._launch_incantation()

        return None

    def _verify_continuous_safety(self) -> bool:
        """
        Vérifications de sécurité continues.
        
        Returns:
            True si conditions sûres
        """
        current_food = self.state.get_food_count()
        
        # Vérification nourriture selon le niveau
        if self.state.level == 1:
            min_food_required = StateTransitionThresholds.MIN_FOOD_FOR_LEVEL_1_INCANTATION
        else:
            min_food_required = StateTransitionThresholds.MIN_FOOD_FOR_COORDINATION
            
        if current_food < min_food_required:
            logger.warning(f"[IncantationState] Nourriture insuffisante: {current_food} < {min_food_required}")
            return False
        
        # Vérification STRICTE du protocole
        if not self._verify_protocol_compliance():
            return False
        
        return True

    def _prepare_incantation(self) -> Optional[Any]:
        """
        Phase 0: Préparation avec vérifications strictes.
        
        Returns:
            Commande de préparation ou None
        """
        logger.info("[IncantationState] 📋 Phase 0: Préparation")

        # Vérification STRICTE du protocole une dernière fois
        if not self._verify_protocol_compliance():
            logger.error("[IncantationState] 🚫 Échec vérification protocole final")
            return self._handle_protocol_violation()

        # Vérification des ressources
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        inventory = self.state.get_inventory()

        missing = {}
        for resource, needed in requirements.items():
            current = inventory.get(resource, 0)
            if current < needed:
                missing[resource] = needed - current

        if missing:
            logger.error(f"[IncantationState] ❌ Ressources manquantes: {missing}")
            return self._handle_missing_resources()

        # Calcul des ressources à déposer
        ground_resources = self._get_resources_at_current_position()
        self.resources_to_drop = []

        for resource, needed in requirements.items():
            on_ground = ground_resources.get(resource, 0)
            to_drop = max(0, needed - on_ground)
            if to_drop > 0:
                self.resources_to_drop.extend([resource] * to_drop)

        logger.info(f"[IncantationState] 📦 Ressources à déposer: {self.resources_to_drop}")

        if not self.resources_to_drop:
            logger.info("[IncantationState] ✅ Aucune ressource à déposer")
            self.incant_stage = 2
            return self.cmd_mgr.look()

        self.incant_stage = 1
        return self._drop_resources()

    def _drop_resources(self) -> Optional[Any]:
        """
        Phase 1: Dépôt des ressources.
        
        Returns:
            Commande de dépôt ou None
        """
        if self.resources_to_drop:
            resource = self.resources_to_drop.pop(0)
            logger.info(f"[IncantationState] 📦 Dépôt {resource} ({len(self.resources_to_drop)} restants)")
            self.resources_dropped += 1
            self._last_set_resource = resource
            self.waiting_for_command = True
            self.last_command_time = time.time()
            return self.cmd_mgr.set(resource)
        else:
            logger.info("[IncantationState] ✅ Ressources déposées, vérification")
            self.incant_stage = 2
            return self.cmd_mgr.look()

    def _verify_before_incant(self) -> Optional[Any]:
        """
        Phase 2: Vérification finale avant lancement.
        
        Returns:
            Commande de vérification ou None
        """
        logger.info("[IncantationState] 🔍 Phase 2: Vérification finale")

        if self._verify_incantation_conditions():
            logger.info("[IncantationState] ✅ Conditions vérifiées")
            self.incant_stage = 3
            return self._launch_incantation()
        else:
            logger.warning("[IncantationState] ❌ Conditions non remplies")
            self.attempts += 1

            if self.attempts >= 2:
                logger.error("[IncantationState] 🔄 Trop de tentatives échouées")
                return self._handle_max_attempts()

            logger.info("[IncantationState] 🔄 Nouvel essai")
            self.incant_stage = 0
            return self.cmd_mgr.look()

    def _launch_incantation(self) -> Optional[Any]:
        """
        Phase 3: Lancement avec vérifications finales STRICTES.
        
        Returns:
            Commande d'incantation
        """
        logger.info("[IncantationState] 🚀 Phase 3: Lancement")

        # Vérification FINALE et STRICTE du protocole
        if not self._verify_protocol_compliance():
            logger.error("[IncantationState] 🚫 Protocole perdu au lancement")
            return self._handle_protocol_violation()

        # Vérification finale des conditions
        if not self._verify_incantation_conditions():
            logger.error("[IncantationState] ❌ Conditions perdues au lancement")
            self.attempts += 1
            if self.attempts >= 2:
                return self._handle_max_attempts()
            self.incant_stage = 0
            return self.cmd_mgr.look()

        # Log détaillé du lancement
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        current_players = self._count_players_on_tile()
        
        logger.info(f"[IncantationState] 🔮✨ LANCEMENT INCANTATION {self.state.level} → {self.state.level + 1}")
        logger.info(f"[IncantationState] 👥 Joueurs: {current_players}/{required_players}")
        
        self.waiting_for_command = True
        self.last_command_time = time.time()
        return self.cmd_mgr.incantation()

    def _verify_incantation_conditions(self) -> bool:
        """
        Vérification complète des conditions d'incantation.
        
        Returns:
            True si toutes les conditions sont remplies
        """
        # Vérification protocole
        if not self._verify_protocol_compliance():
            return False
            
        # Vérification ressources au sol
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        ground_resources = self._get_resources_at_current_position()

        for resource, needed in requirements.items():
            on_ground = ground_resources.get(resource, 0)
            if on_ground < needed:
                logger.warning(f"[IncantationState] ❌ {resource} au sol: {on_ground} < {needed}")
                return False

        return True

    def _get_resources_at_current_position(self) -> dict:
        """
        Retourne les ressources sur la tuile actuelle.
        
        Returns:
            Dictionnaire des ressources au sol
        """
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return dict(data.resources)
        return {}

    def _count_players_on_tile(self) -> int:
        """
        Compte les joueurs sur la tuile actuelle.
        
        Returns:
            Nombre de joueurs sur la tuile
        """
        vision = self.state.get_vision()
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return data.players
        return 1

    def _handle_protocol_violation(self) -> Optional[Any]:
        """
        Gère une violation du protocole de coordination.
        
        Returns:
            Transition appropriée
        """
        logger.error("[IncantationState] 🚫 GESTION VIOLATION PROTOCOLE")
        
        # Pour niveau 2+, transition vers coordination OBLIGATOIRE
        if self.state.level >= 2:
            logger.info("[IncantationState] → Transition coordination OBLIGATOIRE")
            from ai.strategy.state.coordination_incantation import CoordinateIncantationState
            new_state = CoordinateIncantationState(self.planner)
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()
        
        # Fallback général
        return self._handle_generic_failure()

    def _handle_safety_failure(self) -> Optional[Any]:
        """
        Gère un échec des conditions de sécurité.
        
        Returns:
            Transition appropriée
        """
        current_food = self.state.get_food_count()
        
        if current_food < StateTransitionThresholds.MIN_FOOD_FOR_LEVEL_1_INCANTATION:
            logger.info("[IncantationState] → Collecte nourriture")
            from ai.strategy.state.collect_food import CollectFoodState
            new_state = CollectFoodState(self.planner)
            self.planner.fsm.transition_to(new_state)
            return new_state.execute()
        
        return self._handle_generic_failure()

    def _handle_missing_resources(self) -> Optional[Any]:
        """
        Gère le cas de ressources manquantes.
        
        Returns:
            Transition vers collecte ressources
        """
        logger.info("[IncantationState] → Collecte ressources manquantes")
        from ai.strategy.state.collect_resources import CollectResourcesState
        new_state = CollectResourcesState(self.planner)
        self.planner.fsm.transition_to(new_state)
        return new_state.execute()

    def _handle_timeout(self) -> Optional[Any]:
        """
        Gère le timeout d'incantation.
        
        Returns:
            Fallback générique
        """
        logger.error("[IncantationState] Timeout d'incantation")
        return self._handle_generic_failure()

    def _handle_max_attempts(self) -> Optional[Any]:
        """
        Gère le dépassement du nombre maximum de tentatives.
        
        Returns:
            Fallback générique
        """
        logger.error("[IncantationState] Nombre maximum de tentatives atteint")
        return self._handle_generic_failure()

    def _handle_generic_failure(self) -> Optional[Any]:
        """
        Gestion générique d'échec avec fallback intelligent.
        
        Returns:
            Transition appropriée
        """
        current_food = self.state.get_food_count()
        
        # Priorité 1: Urgence alimentaire
        if current_food <= StateTransitionThresholds.FOOD_EMERGENCY_THRESHOLD:
            from ai.strategy.state.emergency import EmergencyState
            new_state = EmergencyState(self.planner)
        # Priorité 2: Collecte nourriture
        elif current_food <= StateTransitionThresholds.FOOD_LOW_THRESHOLD:
            from ai.strategy.state.collect_food import CollectFoodState
            new_state = CollectFoodState(self.planner)
        # Priorité 3: Collecte ressources
        elif self.state.has_missing_resources():
            from ai.strategy.state.collect_resources import CollectResourcesState
            new_state = CollectResourcesState(self.planner)
        # Priorité 4: Exploration
        else:
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
        self.waiting_for_command = False

        if command_type == CommandType.SET:
            resource_name = getattr(self, '_last_set_resource', 'unknown')
            logger.debug(f"[IncantationState] ✅ {resource_name} déposé")
            vision = self.state.get_vision()
            if hasattr(self, '_last_set_resource'):
                vision.add_resource_at((0, 0), self._last_set_resource)

        elif command_type == CommandType.INCANTATION:
            logger.info(f"[IncantationState] 🎉✨ INCANTATION RÉUSSIE! Nouveau niveau: {self.state.level}")
            self.incantation_completed = True
            # Le level up déclenchera les actions appropriées dans FSMPlanner

    def on_command_failed(self, command_type, response=None):
        """
        Gestion des échecs de commandes.
        
        Args:
            command_type: Type de commande
            response: Réponse du serveur
        """
        self.waiting_for_command = False

        if command_type == CommandType.SET:
            logger.error(f"[IncantationState] ❌ Échec dépôt: {response}")
            self.context['needs_vision_update'] = True

        elif command_type == CommandType.INCANTATION:
            logger.error(f"[IncantationState] 💥 INCANTATION ÉCHOUÉE: {response}")
            self.attempts += 1
            self.context['needs_vision_update'] = True

            if self.attempts >= 2:
                logger.error("[IncantationState] 🔄 Abandon après échecs répétés")
            else:
                self.incant_stage = 0
                logger.info("[IncantationState] 🔄 Préparation nouvel essai")

    def on_event(self, event: Event) -> Optional[State]:
        """
        Gestion des événements pendant incantation.
        
        Args:
            event: Événement reçu
            
        Returns:
            Nouvel état ou None
        """
        if event == Event.FOOD_EMERGENCY:
            logger.error("[IncantationState] 🚨 URGENCE! Abandon incantation")
            from ai.strategy.state.emergency import EmergencyState
            return EmergencyState(self.planner)
        return None

    def on_enter(self):
        """Actions à l'entrée de l'état."""
        super().on_enter()
        
        if self.protocol_violation:
            logger.error("[IncantationState] 🚫 ENTRÉE avec violation protocole")
            return
            
        current_food = self.state.get_food_count()
        requirements = IncantationRequirements.REQUIRED_RESOURCES.get(self.state.level, {})
        required_players = IncantationRequirements.REQUIRED_PLAYERS.get(self.state.level, 1)
        current_players = self._count_players_on_tile()

        logger.info(f"[IncantationState] 🔮 ENTRÉE incantation")
        logger.info(f"[IncantationState] 📊 Niveau: {self.state.level}, Food: {current_food}")
        logger.info(f"[IncantationState] 📦 Ressources: {requirements}")
        logger.info(f"[IncantationState] 👥 Joueurs: {current_players}/{required_players}")

        # Reset des variables
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

        if hasattr(self, 'incantation_completed') and self.incantation_completed:
            logger.info(f"[IncantationState] 🎉 SORTIE SUCCÈS - Niveau: {self.state.level}, "
                        f"Durée: {duration:.1f}s, Ressources: {self.resources_dropped}")
        else:
            logger.info(f"[IncantationState] ❌ SORTIE ÉCHEC - Durée: {duration:.1f}s")

        # Nettoyage
        self.resources_to_drop.clear()
        self.waiting_for_command = False