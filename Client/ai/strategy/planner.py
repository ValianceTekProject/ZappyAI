##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## planner - CORRIGÉ - Logique de planification restructurée
##

import random
from typing import Optional, List, Dict
from protocol.commands import CommandManager
from utils.game_state import GameState
from config import CommandType, Constants, GameStates
from ai.strategy.pathfinding import Pathfinder, RelativeTarget
from utils.logger import logger

class Planner:
    def __init__(self, command_manager: CommandManager, game_state: GameState):
        """Initialise le planificateur avec le gestionnaire de commandes et l'état du jeu."""
        self.cmd_manager = command_manager
        self.state = game_state
        self.pathfinder = Pathfinder()

        self.command_queue: List[CommandType] = []

        self.current_target: Optional[RelativeTarget] = None
        self.current_strategy: GameStates = GameStates.EXPLORE

        self.stuck_counter = 0
        self.max_stuck_attempts = 3
        self.last_position = None

        self.critical_food_threshold = 8
        self.safe_food_threshold = 15
        self.action_counter = 0

    def decide_next_action(self):
        """
        Pipeline de décision principal:
        1. Vérifier si une commande est en cours
        2. Gérer la queue de commandes
        3. Gérer les besoins essentiels (look, inventaire)
        4. Gérer les urgences et stratégies
        """
        self.action_counter += 1
        logger.info(f"[Tick {self.action_counter}] Niveau de food = {self.state.get_food_count()}, current_target = {self.current_target}")

        if self.state.command_already_send:
            logger.debug("Commande déjà en cours, attente...")
            return None

        if self.command_queue:
            next_cmd = self.command_queue.pop(0)
            logger.debug(f"Exécution commande de la queue: {next_cmd}")
            return self._execute_movement_command(next_cmd)

        if self.state.needs_look:
            logger.debug("Look nécessaire")
            self.current_target = None
            return self.cmd_manager.look()

        if self.cmd_manager.timing.has_lost_food():
            logger.debug("Vérification inventaire nécessaire")
            return self.cmd_manager.inventory()

        return self._decide_strategy()

    def _decide_strategy(self):
        """
        Détermine la stratégie à adopter selon l'état actuel.
        """
        if self._is_food_critically_low():
            logger.info("Urgence alimentaire critique")
            return self._handle_food_emergency()

        if self.state.get_food_count() < self.safe_food_threshold:
            logger.info("Collecte préventive de nourriture")
            return self._handle_food_collection()

        if self.state.can_incant():
            logger.info("Préparation incantation")
            return self._handle_incantation_ready()

        if (self.state.get_player_level() == 1 and 
            self.state.inventory.get("linemate", 0) >= 1 and
            random.random() < 0.8):
            logger.info("Fork stratégique niveau 1")
            return self._handle_fork()

        eject_cmd = self._handle_eject_if_necessary()
        if eject_cmd:
            return eject_cmd

        if self.state.has_missing_resources():
            logger.info("Collecte de ressources manquantes")
            return self._handle_resource_collection()

        logger.debug("Mode exploration")
        return self._handle_exploration()

    def _is_food_critically_low(self) -> bool:
        """Vérifie si le niveau de nourriture est critique."""
        return self.state.get_food_count() < self.critical_food_threshold

    def _is_stuck(self) -> bool:
        """Détecte si l'agent est bloqué."""
        return self.stuck_counter >= self.max_stuck_attempts

    def _handle_food_emergency(self):
        """Gère les urgences alimentaires."""
        self.current_strategy = GameStates.COLLECT_RESOURCES

        if self._is_resource_at_current_position(Constants.FOOD.value):
            logger.info("Ramassage nourriture d'urgence au sol")
            return self.cmd_manager.take(Constants.FOOD.value)

        if (self.current_target and 
            self.current_target.resource_type == Constants.FOOD.value):
            return self._move_toward_current_target()

        if not self._search_and_target_resource(Constants.FOOD.value):
            logger.debug("Aucune cible d'urgence trouvée, fallback → exploration")
            return self._handle_exploration()
        return None

    def _handle_food_collection(self):
        """Gère la collecte préventive de nourriture."""
        self.current_strategy = GameStates.COLLECT_RESOURCES

        if self._is_resource_at_current_position(Constants.FOOD.value):
            return self.cmd_manager.take(Constants.FOOD.value)

        if (self.current_target and 
            self.current_target.resource_type == Constants.FOOD.value):
            return self._move_toward_current_target()

        if not self._search_and_target_resource(Constants.FOOD.value):
            logger.debug("Aucune cible d'urgence trouvée, fallback → exploration")
            return self._handle_exploration()
        return None

    def _handle_incantation_ready(self):
        """
        Gère la préparation à l'incantation.
        """
        logger.info(f"Préparation incantation niveau {self.state.get_player_level()}")
        requirements = self.state.get_incantation_requirements()
        local_resources = self._get_resources_at_current_position()

        resources_ready = all(
            local_resources.get(resource, 0) >= quantity 
            for resource, quantity in requirements.items()
        )

        needed_players = self.state.get_required_player_count()
        current_players = self.state._players_on_current_tile()

        if resources_ready and current_players >= needed_players:
            logger.info("Lancement incantation immédiate")
            return self.cmd_manager.incantation()

        if resources_ready == False:
            drop_cmd = self._drop_missing_resources(requirements)
            if drop_cmd:
                return drop_cmd

        if resources_ready and current_players < needed_players:
            call_msg = f"incant_level_{self.state.get_player_level()}"
            logger.info(f"Appel coéquipiers: {call_msg}")
            return self.cmd_manager.broadcast(call_msg)

        return self._handle_resource_collection()

    def _handle_fork(self):
        """Gère la reproduction stratégique."""
        logger.info("Exécution FORK stratégique")
        return self.cmd_manager.fork()

    def _handle_eject_if_necessary(self) -> Optional[CommandType]:
        """
        Éjecte les ennemis si nécessaire.
        """
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return None

        for tile in vision_data:
            if tile.rel_pos == (0, 0) and tile.players > 1:
                logger.info("Éjection d'ennemis détectés")
                return self.cmd_manager.eject()

        return None

    def _handle_resource_collection(self):
        """
        Gère la collecte de ressources nécessaires.
        """
        self.current_strategy = GameStates.COLLECT_RESOURCES
        requirements = self.state.get_incantation_requirements()
        pickup_cmd = self._pickup_needed_resources(requirements)
        if pickup_cmd:
            return pickup_cmd

        if (self.current_target and 
            self._is_target_still_needed(self.current_target, requirements)):
            return self._move_toward_current_target()

        resource_priorities = self.pathfinder.get_resource_priority_list(
            requirements, self.state.inventory
        )
        for resource in resource_priorities:
            if self._search_and_target_resource(resource):
                return self._move_toward_current_target()

        return self._handle_exploration()

    def _handle_exploration(self):
        """
        Gère l'exploration du terrain.
        """
        self.current_strategy = GameStates.EXPLORE
        vision_data = self.state.get_vision().last_vision_data

        if not vision_data:
            return self.cmd_manager.look()

        exploration_cmd = self.pathfinder.get_exploration_direction(
            self.state.get_orientation(), vision_data
        )
        return self._execute_movement_command(exploration_cmd)

    def _search_and_target_resource(self, resource_type: str) -> bool:
        """
        Cherche et cible une ressource dans la vision.
        Return True si une cible a été trouvée.
        """
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return False
        target = self.pathfinder.find_target_in_vision(vision_data, resource_type)
        if target:
            logger.debug(f"Recherche dans vision de resource {resource_type}")
            self.current_target = target
            logger.info(f"Nouvelle cible {resource_type} à {target.rel_position}")
            return True
        logger.error(f"Aucune resource {resource_type} trouvée dans la vision → fallback exploration")
        return False

    def _move_toward_current_target(self):
        """
        Se déplace vers la cible actuelle.
        """
        if not self.current_target:
            return None

        if self.current_target.rel_position == (0, 0):
            logger.info("Cible atteinte, ramassage")
            resource_type = self.current_target.resource_type
            self.current_target = None
            return self.cmd_manager.take(resource_type)

        if not self.command_queue:
            vision_data = self.state.get_vision().last_vision_data
            if not vision_data:
                return self.cmd_manager.look()

            commands = self.pathfinder.get_commands_to_target(
                self.current_target,
                self.state.get_orientation(),
                vision_data
            )
            if not commands:
                logger.warning("Cible inatteignable, abandon")
                self.current_target = None
                return self._handle_exploration()
            self.command_queue = commands[:10]

        if self.command_queue:
            next_cmd = self.command_queue.pop(0)
            return self._execute_movement_command(next_cmd)
        return None

    def _execute_movement_command(self, command_type: CommandType):
        """
        Exécute une commande de mouvement et gère les erreurs.
        """
        if command_type == CommandType.FORWARD:
            return self.cmd_manager.forward()
        elif command_type == CommandType.LEFT:
            return self.cmd_manager.left()
        elif command_type == CommandType.RIGHT:
            return self.cmd_manager.right()
        else:
            logger.warning(f"Commande inconnue: {command_type}")
            return None

    def _is_resource_at_current_position(self, resource_type: str) -> bool:
        """Vérifie si resource_type est déposée sur la tuile (0,0)."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return False
        for td in vision.last_vision_data:
            if td.rel_pos == (0, 0):
                return (resource_type in td.resources and 
                        td.resources[resource_type] > 0)
        return False

    def _get_resources_at_current_position(self) -> Dict[str, int]:
        """Retourne les ressources présentes à (0,0)."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return {}
        for td in vision.last_vision_data:
            if td.rel_pos == (0, 0):
                return dict(td.resources)
        return {}

    def _drop_missing_resources(self, requirements: Dict[str, int]):
        """
        Si on peut déposer directement une ressource pour l'incantation,
        on retourne la commande SET correspondante.
        """
        local = self._get_resources_at_current_position()
        for resource, needed in requirements.items():
            inv = self.state.inventory.get(resource, 0)
            ground = local.get(resource, 0)
            to_drop = max(0, needed - ground)
            if to_drop > 0 and inv > 0:
                logger.info(f"Dépôt {resource} pour incantation")
                return self.cmd_manager.set(resource)
        return None

    def _pickup_needed_resources(self, requirements: Dict[str, int]):
        """
        Si on a besoin de ramasser une ressource présente à (0,0),
        on retourne la commande TAKE correspondante.
        """
        ground = self._get_resources_at_current_position()
        for resource, needed in requirements.items():
            inv = self.state.inventory.get(resource, 0)
            if inv < needed and ground.get(resource, 0) > 0:
                logger.info(f"Pickup {resource} au sol")
                return self.cmd_manager.take(resource)
        return None

    def _is_target_still_needed(self, target: RelativeTarget,
                                requirements: Dict[str, int]) -> bool:
        """Vérifie si la cible est toujours pertinente (quantités manquantes)."""
        r = target.resource_type
        needed = requirements.get(r, 0)
        current = self.state.inventory.get(r, 0)
        return current < needed

    def on_command_failed(self):
        """
        À appeler si une commande FORWARD/LEFT/RIGHT retourne “ko” ou “dead” :
        on incrémente stuck_counter, et si ≥3 on abandonne la target.
        """
        self.stuck_counter += 1
        logger.warning(f"Échec de commande, stuck_counter={self.stuck_counter}")
        if self.stuck_counter >= 3 and self.current_target:
            logger.info("Cible abandonnée après échecs répétés")
            self.current_target = None
            self.command_queue.clear()

    def on_successful_move(self):
        """À appeler après un FORWARD “ok” pour reset stuck_counter."""
        self.stuck_counter = 0

    def get_current_strategy_info(self) -> Dict:
        """Retourne l’état interne (utile pour du debug/interface)."""
        return {
            'strategy': self.current_strategy.value,
            'target': self.current_target.rel_position if self.current_target else None,
            'target_resource': self.current_target.resource_type if self.current_target else None,
            'stuck_counter': self.stuck_counter,
            'food_count': self.state.get_food_count(),
            'critical_food': self._is_food_critically_low()
        }
