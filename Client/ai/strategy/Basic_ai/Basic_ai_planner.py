##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## Basic_ai_planner
##

import time
import math
from utils.game_state import GameState
from typing import Optional, List, Dict, Any
from config import CommandType, Constants, GameStates
from ai.strategy.pathfinding import Pathfinder, RelativeTarget
from teams.coordination import CoordinationManager
from protocol.message_manager import MessageManager
from protocol.commands import CommandManager
from teams.message import MessageType
from utils.logger import logger

class BASIC_AI_Planner:
    def __init__(self, command_manager: CommandManager, game_state: GameState, message_bus):
        self.cmd_manager = command_manager
        self.state = game_state
        self.pathfinder = Pathfinder()
        self.bus = message_bus
        self.msgm = MessageManager(self.cmd_manager, self.bus)
        self.coordo = CoordinationManager(self.bus, self.cmd_manager, self.state)

        self.command_queue: List[CommandType] = []
        self.helper_cmds: Optional[List[CommandType]] = None

        self.current_target: Optional[RelativeTarget] = None
        self.current_strategy: GameStates = GameStates.EXPLORE
        self.new_agent = False

        self.stuck_counter = 0
        self.max_stuck_attempts = 3
        self.last_position = None

        self.fork_stage = 0
        self._incant_stage = 0
        self._last_broadcast = 0.0
        self._broadcast_interval = 3.0
        self.incant_helping = False
        self.remaining_max_dist = None
        self.help_requester = None
        self.last_sound_dir = None
        self.help_start_time = None
        self._last_broadcast_time = 0.0

        self.action_counter = 0

        self.bus.subscribe(MessageType.INCANTATION_REQUEST, self._on_incant_request)
        self.bus.subscribe(MessageType.INCANTATION_RESPONSE, self._on_incant_response)

    def basic_ai_decision(self):
        self.action_counter += 1

        if self.state.command_already_send:
            return None

        if self.command_queue:
            next_cmd = self.command_queue.pop(0)
            return self._execute_movement_command(next_cmd)

        if self.incant_helping:
            return self._incant_helping()

        if self.state.needs_look:
            self.current_target = None
            self.state.needs_look = False
            return self.cmd_manager.look()

        if self.cmd_manager.timing.has_lost_food():
            return self.cmd_manager.inventory()

        if self.state.needs_repro:
            return self._handle_fork()

        return self._decide_strategy()

    def _decide_strategy(self):
        """Détermine la stratégie à adopter selon l'état actuel."""
        if self._is_food_critically_low():
            return self._handle_food_emergency()

        if self.state.get_food_count() < self.state._get_safe_food_threshold():
            return self._handle_food_collection()

        if self.state.can_incant():
            return self._handle_incantation_ready()

        if self.state.has_missing_resources():
            return self._handle_resource_collection()

        return self._handle_exploration()

    def _is_food_critically_low(self) -> bool:
        """Vérifie si le niveau de nourriture est critique."""
        return self.state.get_food_count() < self.state._get_critical_food_threshold()

    def _is_stuck(self) -> bool:
        """Détecte si l'agent est bloqué."""
        return self.stuck_counter >= self.max_stuck_attempts

    def _handle_food_emergency(self):
        """Gère les urgences alimentaires."""
        self.current_strategy = GameStates.COLLECT_RESOURCES

        if self._is_resource_at_current_position(Constants.FOOD.value):
            return self.cmd_manager.take(Constants.FOOD.value)

        if self.current_target and self.current_target.resource_type == Constants.FOOD.value:
            return self._move_toward_current_target()

        if not self._search_and_target_resource(Constants.FOOD.value):
            return self._handle_exploration()
        return None

    def _handle_food_collection(self):
        """Gère la collecte préventive de nourriture."""
        self.current_strategy = GameStates.COLLECT_RESOURCES

        if self._is_resource_at_current_position(Constants.FOOD.value):
            return self.cmd_manager.take(Constants.FOOD.value)

        if self.current_target and self.current_target.resource_type == Constants.FOOD.value:
            return self._move_toward_current_target()

        if not self._search_and_target_resource(Constants.FOOD.value):
            return self._handle_exploration()
        return None

    def _handle_incantation_ready(self) -> Optional[Any]:
        """Gère l'incantation en plusieurs phases."""
        reqs = self.state.get_incantation_requirements()
        needed = self.state.get_required_player_count()
        local = self.state._get_resources_at_current_position()
        now = time.time()

        if self._incant_stage == 0:
            self.coordo.send_incant_request()
            self._last_broadcast_time = now
            self._incant_stage = 1
            return None

        helpers_here = len([h for h in self.coordo.get_helpers() if h[1] == 'here'])
        if helpers_here < needed - 1:
            if now - self._last_broadcast_time >= self._broadcast_interval:
                self.coordo.send_incant_request()
                self._last_broadcast_time = now
            return None

        if self._incant_stage == 1:
            for res, qty in reqs.items():
                if local.get(res, 0) < qty and self.state.inventory.get(res, 0) > 0:
                    return self.cmd_manager.set(res)
            self._incant_stage = 2
            return None

        if self._incant_stage == 2:
            self._incant_stage = 3
            return self.cmd_manager.look()
        if self._incant_stage == 3:
            players_here = self.state._players_on_current_tile()
            ground = self.state._get_resources_at_current_position()
            reqs = self.state.get_incantation_requirements()
            needed = self.state.get_required_player_count()

            logger.debug(f"[Initiateur] Avant INCANTATION (niveau {self.state.level}): "
                         f"players_here={players_here}/{needed}, ground={ground}, reqs={reqs}")
            if players_here < needed or any(ground.get(r, 0) < q for r, q in reqs.items()):
                logger.warning(f"[Initiateur] Abandon incant: conditions non remplies au LOOK final "
                               f"(players_here={players_here}/{needed}, ground={ground})")
                self._incant_stage = 0
                self.coordo.clear_helpers()
                self.state.needs_look = True
                return None
            self._incant_stage = 0
            self.coordo.clear_helpers()
            logger.info("[Initiateur] Lancement INCANTATION après LOOK final, conditions OK")
            return self.cmd_manager.incantation()

        return None

    def _on_incant_response(self, sender_id, data, direction):
        self.coordo.helpers.add((sender_id, data['response']))

    def _on_incant_request(self, sender_id, data, direction):
        """Réponse helper à une requête d'incantation."""
        logger.debug(
            f"[Helper] _on_incant_request called: sender={sender_id}, level={data.get('level')}, direction={direction}")
        if not self.incant_helping and self.state.level == data["level"]:
            needed_food = self.state.estimate_food_needed_for_incant()
            logger.debug(
                f"[Helper] Received incant_req from {sender_id}, direction={direction}, food={self.state.get_food_count()}, needed={needed_food}")
            if self.state.get_food_count() >= needed_food:
                self.incant_helping = True
                self.help_requester = sender_id
                self.last_sound_dir = direction
                self.help_start_time = time.time()
        elif self.incant_helping:
            logger.debug(
                f"[Helper] ping reçu; sender_id={sender_id}, expected={self.help_requester}, direction={direction}")
            if sender_id == self.help_requester:
                self.last_sound_dir = direction

    def _incant_helping(self):
        """Phase helper : déplacement vers l'initiateur et envoi 'here'."""
        if self.help_start_time and time.time() - self.help_start_time > 30.0:
            self.incant_helping = False
            self.remaining_max_dist = None
            self.last_sound_dir = None
            self.help_requester = None
            return None

        rem = self.remaining_max_dist
        if rem is None:
            W, H = self.state.dimension_map
            rem = (W // 2) + (H // 2)
            self.remaining_max_dist = rem

        time_travel = (rem + 2) * 7
        time_incant = 300
        reste_food_needed = math.ceil((time_travel + time_incant) / 126) + 1
        have = self.state.get_food_count()
        if have < reste_food_needed:
            logger.warning(
                f"[Helper] Abandon incant help: food insuffisante (have={have} < needed={reste_food_needed})")
            self.incant_helping = False
            self.remaining_max_dist = None
            self.last_sound_dir = None
            self.help_requester = None
            return None

        if self.last_sound_dir is not None:
            logger.debug(
                f"[Helper] incant_helping step: have={have}, reste_food_needed={reste_food_needed}, remaining_max_dist={self.remaining_max_dist}, last_sound_dir={self.last_sound_dir}")
            K = self.last_sound_dir
            self.last_sound_dir = None

            if K == 0:
                logger.info(f"[Helper] Arrived on case initiateur ({self.help_requester}), envoi 'here'")
                self.coordo.send_incant_response(self.help_requester, 'here', eta=0)
                self.incant_helping = False
                self.remaining_max_dist = 0
                return None

            cmds = self._commands_from_sound_dir(K)
            if cmds:
                cmd0 = cmds[0]
                if cmd0 == CommandType.FORWARD:
                    self.remaining_max_dist = max(0, self.remaining_max_dist - 1)
                if len(cmds) > 1:
                    self.helper_cmds = cmds[1:]
                return self._execute_movement_command(cmd0)
            return None

        return None

    def _commands_from_sound_dir(self, k: int) -> List[CommandType]:
        """Convertit une direction sonore en liste de commandes de déplacement."""
        if k == 1:
            return [CommandType.FORWARD]
        if k in (2, 3):
            return [CommandType.RIGHT, CommandType.FORWARD]
        if k in (7, 8):
            return [CommandType.LEFT, CommandType.FORWARD]
        if k in (4, 5):
            return [CommandType.RIGHT, CommandType.RIGHT, CommandType.FORWARD]
        if k == 6:
            return [CommandType.LEFT, CommandType.LEFT, CommandType.FORWARD, CommandType.LEFT, CommandType.FORWARD]
        return []

    def _handle_fork(self):
        """Gère la séquence de fork pour créer un nouvel agent."""
        if self.fork_stage == 0:
            self.fork_stage = 1
            return self.cmd_manager.connect_nbr()

        if self.fork_stage == 1:
            last = self.cmd_manager.get_last_success(CommandType.CONNECT_NBR)
            if not last:
                return None

            slots = int(last.response)
            if slots == 0 and self._has_enough_for_fork():
                return self.cmd_manager.fork()
            else:
                self.new_agent = True
                self.state.needs_repro = False
                self.fork_stage = 0
                return None
        return None

    def _has_enough_for_fork(self) -> bool:
        """Détermine si on a les ressources minimales pour un fork stratégique."""
        inv = self.state.inventory
        return inv.get("food", 0) >= self.state.critical_food_threshold

    def _handle_eject_if_necessary(self) -> Optional[CommandType]:
        """Éjecte les ennemis présents sur la même tuile si nécessaire."""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return None

        for tile in vision_data:
            if tile.rel_pos == (0, 0) and tile.players > 1:
                return self.cmd_manager.eject()

        return None

    def _handle_resource_collection(self):
        """Gère la collecte des ressources nécessaires à l'incantation."""
        self.current_strategy = GameStates.COLLECT_RESOURCES
        requirements = self.state.get_incantation_requirements()
        pickup_cmd = self._pickup_needed_resources(requirements)
        if pickup_cmd:
            return pickup_cmd

        if self.current_target and self._is_target_still_needed(self.current_target, requirements):
            return self._move_toward_current_target()

        resource_priorities = self.pathfinder.get_resource_priority_list(requirements, self.state.inventory)
        for resource in resource_priorities:
            if self._search_and_target_resource(resource):
                return self._move_toward_current_target()

        return self._handle_exploration()

    def _handle_exploration(self):
        """Gère l'exploration du terrain."""
        self.current_strategy = GameStates.EXPLORE
        vision_data = self.state.get_vision().last_vision_data

        if not vision_data:
            return self.cmd_manager.look()

        exploration_cmd = self.pathfinder.get_exploration_direction(self.state.get_orientation(), vision_data)
        return self._execute_movement_command(exploration_cmd)

    def _search_and_target_resource(self, resource_type: str) -> bool:
        """Cherche et cible une ressource dans la vision."""
        vision_data = self.state.get_vision().last_vision_data
        if not vision_data:
            return False
        target = self.pathfinder.find_target_in_vision(vision_data, resource_type)
        if target:
            self.current_target = target
            return True
        return False

    def _move_toward_current_target(self):
        """Se déplace vers la cible actuelle."""
        if not self.current_target:
            return None

        if self.current_target.rel_position == (0, 0):
            resource_type = self.current_target.resource_type
            self.current_target = None
            return self.cmd_manager.take(resource_type)

        if not self.command_queue:
            vision_data = self.state.get_vision().last_vision_data
            if not vision_data:
                return self.cmd_manager.look()

            commands = self.pathfinder.get_commands_to_target(self.current_target, self.state.get_orientation(),
                                                              vision_data)
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
        """Exécute une commande de mouvement."""
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
        """Vérifie si une ressource est présente sur la tuile courante."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return False
        for td in vision.last_vision_data:
            if td.rel_pos == (0, 0):
                return resource_type in td.resources and td.resources[resource_type] > 0
        return False

    def _drop_missing_resources(self, requirements: Dict[str, int]):
        """Dépose une ressource nécessaire si présente dans l'inventaire."""
        local = self.state._get_resources_at_current_position()
        for resource, needed in requirements.items():
            inv = self.state.inventory.get(resource, 0)
            ground = local.get(resource, 0)
            to_drop = max(0, needed - ground)
            if to_drop > 0 and inv > 0:
                return self.cmd_manager.set(resource)
        return None

    def _pickup_needed_resources(self, requirements: Dict[str, int]):
        """Ramasse une ressource présente sur la case si nécessaire."""
        ground = self.state._get_resources_at_current_position()
        for resource, needed in requirements.items():
            inv = self.state.inventory.get(resource, 0)
            if inv < needed and ground.get(resource, 0) > 0:
                return self.cmd_manager.take(resource)
        return None

    def _is_target_still_needed(self, target: RelativeTarget, requirements: Dict[str, int]) -> bool:
        """Vérifie si la cible est toujours pertinente."""
        r = target.resource_type
        needed = requirements.get(r, 0)
        current = self.state.inventory.get(r, 0)
        return current < needed

    def on_command_failed(self):
        """Gère un échec de commande de déplacement."""
        self.stuck_counter += 1
        logger.warning(f"Échec de commande, stuck_counter={self.stuck_counter}")
        if self.stuck_counter >= 3 and self.current_target:
            self.current_target = None
            self.command_queue.clear()

    def on_successful_move(self):
        """Reset du compteur de blocage après un déplacement réussi."""
        self.stuck_counter = 0

    def get_current_strategy_info(self) -> Dict:
        """Retourne l’état interne pour debug/interface."""
        return {
            'strategy': self.current_strategy.value,
            'target': self.current_target.rel_position if self.current_target else None,
            'target_resource': self.current_target.resource_type if self.current_target else None,
            'stuck_counter': self.stuck_counter,
            'food_count': self.state.get_food_count(),
            'critical_food': self._is_food_critically_low()
        }
