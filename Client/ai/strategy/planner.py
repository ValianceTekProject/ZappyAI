##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## planner
##

import time
from typing import Optional, List, Dict, Any
from protocol.commands import CommandManager
from utils.game_state import GameState
from config import CommandType, Constants, GameStates
from ai.strategy.pathfinding import Pathfinder, RelativeTarget
from teams.coordination import CoordinationManager
from protocol.message_manager import MessageManager
from teams.message import MessageType
from utils.logger import logger

class Planner:
    def __init__(self, command_manager: CommandManager, game_state: GameState, message_bus):
        """Initialise le planificateur avec le gestionnaire de commandes et l'état du jeu."""
        self.cmd_manager = command_manager
        self.state = game_state
        self.pathfinder = Pathfinder()
        self.bus   = message_bus
        self.msgm  = MessageManager(self.cmd_manager, self.bus)
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

        self.critical_food_threshold = 10
        self.safe_food_threshold = 25
        self.action_counter = 0

        self.bus.subscribe(MessageType.INCANTATION_REQUEST,  self._on_incant_request)
        self.bus.subscribe(MessageType.INCANTATION_RESPONSE, self._on_incant_response)

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

        if self.helper_cmds:
            cmd = self.helper_cmds.pop(0)
            # if last step, send "coming"
            if not self.helper_cmds:
                logger.info("Helper: arrived, send 'coming'")
                self.coordo.send_incant_response(self.coordo.last_requester, 'coming', eta=0)
            return self._execute_movement_command(cmd)

        if self.state.needs_look:
            logger.debug("Look nécessaire")
            self.current_target = None
            self.state.needs_look = False
            return self.cmd_manager.look()

        if self.cmd_manager.timing.has_lost_food():
            logger.debug("Vérification inventaire nécessaire")
            return self.cmd_manager.inventory()

        if self.state.needs_repro:
            return self._handle_fork()

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

        if self.state.has_missing_resources():
            logger.info("Collecte de ressources manquantes")
            return self._handle_resource_collection()

        eject_cmd = self._handle_eject_if_necessary()
        if eject_cmd:
            return eject_cmd

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
            return self._handle_exploration()
        return None

    def _handle_incantation_ready(self) -> Optional[Any]:
        reqs = self.state.get_incantation_requirements()
        needed = self.state.get_required_player_count()
        local = self._get_resources_at_current_position()
        now = time.time()

        # Phase 0: deposit resources
        if self._incant_stage == 0:
            for res, qty in reqs.items():
                if local.get(res, 0) < qty and self.state.inventory.get(res, 0) > 0:
                    return self.cmd_manager.set(res)
            self._incant_stage = 1
            return None

        # Phase 1: initial broadcast
        if self._incant_stage == 1:
            logger.info("Initiateur: broadcast incant_req")
            self.coordo.send_incant_request()
            self._last_broadcast_time = now
            self._incant_stage = 2
            return None

        # Phase 2: collect 'here' responses
        helpers_here = len([h for h in self.coordo.get_helpers() if h['response'] == 'here'])
        logger.debug(f"Helpers here: {helpers_here}/{needed-1}")
        if helpers_here >= needed - 1:
            logger.info("Sufficient 'here' responses, launching incantation")
            self._incant_stage = 0
            return self.cmd_manager.incantation()

        # rebroadcast if no here and interval elapsed
        if now - self._last_broadcast_time >= self._broadcast_interval:
            logger.info("Rebroadcast incant_req")
            self.coordo.send_incant_request()
            self._last_broadcast_time = now
        return None

    def _handle_incantation_help(self):
        """
        Se déplace vers la tuile d’incantation puis envoie sa réponse.
        """
        # position cible de la première requête
        target_pos = self.incant_requests[0]
        cur_pos    = self.state.get_position()

        # si on ne voit pas encore la cible, on explore pour la découvrir
        vision_data = self.state.get_vision().last_vision_data
        seen_tiles = {tile.rel_pos for tile in vision_data} if vision_data else set()

        # si la cible est dans la vision
        rel_x = target_pos[0] - cur_pos[0]
        rel_y = target_pos[1] - cur_pos[1]
        rel_target = (rel_x, rel_y)

        if vision_data and rel_target in seen_tiles:
            # on construit un RelativeTarget pour BFS local
            rt = RelativeTarget(rel_position=rel_target, resource_type="", distance=0)
            commands = self.pathfinder.get_commands_to_target(rt,
                                self.state.get_orientation(),
                                vision_data)
            if commands:
                # on exécute la prochaine commande de navigation
                self.command_queue = commands[1:]
                return self._execute_movement_command(commands[0])
            # sinon, inatteignable → abandon
            self.incant_requests.pop(0)
            return None

        # une fois qu’on arrive EXACTEMENT sur la tuile
        # (ce cas sera géré implicitement, car rel_target == (0,0)):
        # on envoie la réponse « coming » via CoordinationManager
        if cur_pos == target_pos:
            self.coordo.request_incant_help()
            self.incant_requests.pop(0)
            # puis on attend l’incantation, on ne fait rien de plus
            return None

        # si on n’est pas en vue de la cible, on continue d’explorer vers elle
        # (tu peux remplacer par ta logique d’exploration préférée)
        return self._handle_exploration()

    def _on_incant_request(self, sender_id: str, data: Dict[str, Any], k: int):
        # helper logic
        can_help = (self.state.level == data['level'] and
                    self.state.get_food_count() > self.critical_food_threshold)
        # remember requester for response
        self.coordo.last_requester = sender_id
        if not can_help:
            # respond busy
            logger.info(f"Helper: busy reply to {sender_id}")
            self.coordo.send_incant_response(sender_id, 'busy', eta=None)
            return
        if k == 0:
            # same tile -> here
            logger.info(f"Helper: here reply to {sender_id}")
            self.coordo.send_incant_response(sender_id, 'here', eta=0)
        else:
            # plan movement then send 'coming'
            cmds = self._commands_from_sound_dir(k)
            if cmds:
                logger.info(f"Helper: plan movement {cmds} towards {sender_id}")
                self.helper_cmds = cmds

    def _on_incant_response(self, sender_id: str, data: Dict[str, Any], direction: int):
        # record all responses
        logger.info(f"Initiateur reçu incant_resp '{data['response']}' de {sender_id}")
        self.coordo.helpers_store.append({'id': sender_id, **data})

    def _commands_from_sound_dir(self, k: int) -> List[CommandType]:
        # 1=front,2=front-right,3=right,4=back-right,5=back,6=back-left,7=left,8=front-left
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
        """Fork en deux étapes : connect_nbr puis fork si slots dispo."""
        if self.fork_stage == 0:
            logger.info("Vérification place dispo avant FORK")
            self.fork_stage = 1
            return self.cmd_manager.connect_nbr()

        if self.fork_stage == 1:
            last = self.cmd_manager.get_last_success(CommandType.CONNECT_NBR)
            if not last:
                return None

            slots = int(last.response)
            if slots == 0 and self._has_enough_for_fork():
                logger.info(f"FORK autorisé ({slots} slots restants)")
                return self.cmd_manager.fork()
            else:
                self.new_agent = True
                self.state.needs_repro = False
                self.fork_stage = 0
                return None

    def _has_enough_for_fork(self) -> bool:
        """Détermine si on a les ressources min. pour un fork stratégique."""
        inv = self.state.inventory
        return inv.get("food", 0) >= self.critical_food_threshold

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
