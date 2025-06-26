##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## help_incantation
##

import time
from typing import Any, Optional, List
from config import CommandType
from utils.logger import logger
from Client.ai.strategy.fsm import State, Event
from teams.message import Message

class HelpIncantationState(State):
    """État d'aide à une incantation - CORRIGÉ sans calculs de fréquence."""

    def __init__(self, planner):
        super().__init__(planner)
        self.movement_sequence = []
        self.movement_index = 0
        self.target_reached = False
        self.help_start_time = None
        self.help_movement_stage = 0
        self.last_here_broadcast = 0.0
        self.help_timeout = 120.0
        self.here_broadcast_interval = 5.0

    def on_enter(self):
        logger.info(f"[{self.role}] ⇒ HELP_INCANTATION enter")
        self.help_start_time = time.time()
        self.help_movement_stage = 0
        self.target_reached = False
        self._reset_movement()

    def on_event(self, event: Event) -> Optional[State]:
        from ai.strategy.state.emergency import EmergencyState
        from ai.strategy.state.collect_food import CollectFoodState
        from ai.strategy.state.explore import ExploreState

        if event == Event.FOOD_CRITICAL:
            self._stop_helping()
            return EmergencyState(self.planner)

        if event == Event.FOOD_LOW and not self._can_continue_helping():
            self._stop_helping()
            return CollectFoodState(self.planner)

        if event in [Event.INCANT_SUCCESS, Event.INCANT_FAILED]:
            self._stop_helping()
            return ExploreState(self.planner)

        return None

    def execute(self) -> Optional[Any]:
        now = time.time()

        if self.help_start_time and now - self.help_start_time > self.help_timeout:
            logger.warning(f"[Helper] Timeout aide incantation ({self.help_timeout}s)")
            self._stop_helping()
            return None

        if not self._can_continue_helping():
            logger.warning("[Helper] Plus assez de nourriture pour aider")
            self._stop_helping()
            return None

        if self.state.needs_look:
            logger.debug("[Helper] 👁️ LOOK requis")
            return self.cmd_mgr.look()

        if (self._is_resource_at_current_position("food") and 
            not self._is_food_limit_reached()):
            logger.info("[Helper] Ramassage nourriture disponible")
            self.state.on_take_command("food")
            return self.cmd_mgr.take("food")

        return self._handle_help_phases(now)

    def _handle_help_phases(self, now: float) -> Optional[Any]:
        """Gère les phases d'aide avec mouvements intelligents."""
        if self.help_movement_stage == 0:
            direction = self.coordination.get_chosen_incanter_direction()
            logger.debug(f"[Helper] Phase 0: Direction vers incanteur: {direction}")

            if direction is None:
                logger.warning("[Helper] Pas de direction vers incanteur")
                self._stop_helping()
                return None

            if direction == 0:
                logger.info("[Helper] Déjà sur place avec l'incanteur")
                self.help_movement_stage = 2
                self.target_reached = True
                return self._send_here_message()
            else:
                commands = self._commands_from_sound_dir(direction)
                if commands:
                    self.movement_sequence = commands
                    self.movement_index = 0
                    self.help_movement_stage = 1
                    logger.info(f"[Helper] Phase 0→1: Séquence {len(commands)} mouvements calculée vers direction {direction}")
                    return self._execute_movement_sequence()
                else:
                    logger.warning(f"[Helper] Direction invalide: {direction}")
                    self._stop_helping()
                    return None

        elif self.help_movement_stage == 1:
            if self.movement_sequence and self.movement_index < len(self.movement_sequence):
                return self._execute_movement_sequence()
            else:
                logger.info("[Helper] Phase 1→2: Séquence terminée - LOOK final pour vérifier position")
                self.help_movement_stage = 2
                self.target_reached = True
                return self.cmd_mgr.look()

        elif self.help_movement_stage == 2:
            direction = self.coordination.get_chosen_incanter_direction()

            if direction is not None and direction != 0:
                logger.warning(f"[Helper] Position changée (direction={direction}) - Recalcul")
                self.help_movement_stage = 0
                self._reset_movement()
                return None

            if now - self.last_here_broadcast >= self.here_broadcast_interval:
                return self._send_here_message()

            return None

        return None

    def _execute_movement_sequence(self) -> Optional[Any]:
        """Exécute la séquence de mouvements avec gestion LOOK."""
        if not self.movement_sequence or self.movement_index >= len(self.movement_sequence):
            logger.debug("[Helper] Séquence de mouvements terminée")
            return None

        cmd = self.movement_sequence[self.movement_index]
        self.movement_index += 1

        if cmd in [CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT]:
            self.state.on_movement_command()

        if (self.movement_index >= len(self.movement_sequence) or
            self.movement_index % 2 == 0):
            logger.debug(f"[Helper] Mouvement {self.movement_index}/{len(self.movement_sequence)}: {cmd} (LOOK requis après)")
        else:
            logger.debug(f"[Helper] Mouvement {self.movement_index}/{len(self.movement_sequence)}: {cmd}")

        return self._execute_movement_command(cmd)

    def _send_here_message(self) -> Optional[Any]:
        """Envoie le message 'here' à l'incanteur."""
        if not hasattr(self.coordination, 'chosen_incanter') or not self.coordination.chosen_incanter:
            logger.warning("[Helper] Pas d'incanteur choisi pour envoyer 'here'")
            return None

        try:
            token = Message.create_incantation_response(
                sender_id=self.state.agent_id,
                team_id=self.state.team_id,
                request_sender=self.coordination.chosen_incanter,
                response='here',
                level=self.state.level,
                eta=0
            )
            self.cmd_mgr.broadcast(token)
            self.last_here_broadcast = time.time()
            logger.info(f"[Helper] Envoyé 'here' à {self.coordination.chosen_incanter}")
        except Exception as e:
            logger.error(f"[Helper] Erreur envoi message 'here': {e}")

        return None

    def _stop_helping(self):
        """Arrête l'aide à l'incantation."""
        self.help_start_time = None
        self.help_movement_stage = 0
        self.target_reached = False
        self._reset_movement()
        if hasattr(self.coordination, 'reset_helper_choice'):
            self.coordination.reset_helper_choice()
        logger.info("[Helper] Arrêt de l'aide incantation")

    def _reset_movement(self):
        """Reset l'état de mouvement."""
        self.movement_sequence = []
        self.movement_index = 0
        self.state.reset_target()

    def _can_continue_helping(self) -> bool:
        """Vérifie si le helper peut continuer à aider avec seuils fixes."""
        current_food = self.state.get_food_count()
        if self.help_start_time:
            elapsed = time.time() - self.help_start_time
            remaining = max(15, self.help_timeout - elapsed)
        else:
            remaining = self.help_timeout
        estimated_food_consumption_interval = 25.0
        food_needed = int(remaining / estimated_food_consumption_interval) + 8
        return current_food >= food_needed

    def _is_resource_at_current_position(self, resource_type: str) -> bool:
        """Vérifie si une ressource est présente sur la tuile courante."""
        try:
            vision_data = self.state.get_vision().last_vision_data or []
            for td in vision_data:
                if td.rel_pos == (0, 0) and td.resources.get(resource_type, 0) > 0:
                    return True
            return False
        except Exception as e:
            logger.error(f"[Helper] Erreur check resource: {e}")
            return False

    def _is_food_limit_reached(self) -> bool:
        """Vérifie si la limite de nourriture (100) est atteinte."""
        return self.state.get_food_count() >= 100

    def _commands_from_sound_dir(self, direction: int) -> List[Any]:
        """Convertit une direction sonore en séquence de commandes."""
        direction_map = {
            1: [CommandType.FORWARD],
            2: [CommandType.RIGHT, CommandType.FORWARD],
            3: [CommandType.RIGHT],
            4: [CommandType.RIGHT, CommandType.RIGHT, CommandType.FORWARD],
            5: [CommandType.RIGHT, CommandType.RIGHT],
            6: [CommandType.LEFT, CommandType.LEFT, CommandType.FORWARD],
            7: [CommandType.LEFT],
            8: [CommandType.LEFT, CommandType.FORWARD]
        }
        commands = direction_map.get(direction, [])
        if not commands:
            logger.warning(f"[Helper] Direction sonore inconnue: {direction}")
        return commands

    def _execute_movement_command(self, cmd):
        """Exécute une commande de mouvement."""
        try:
            if cmd == CommandType.FORWARD:
                return self.cmd_mgr.forward()
            elif cmd == CommandType.LEFT:
                return self.cmd_mgr.left()
            elif cmd == CommandType.RIGHT:
                return self.cmd_mgr.right()
            else:
                logger.warning(f"[HelpIncantation] Commande inconnue: {cmd}")
                return None
        except Exception as e:
            logger.error(f"[HelpIncantation] Erreur execute movement: {e}")
            return None

    def on_command_failed(self):
        """Gère les échecs de commandes."""
        logger.debug("[HelpIncantation] Commande échouée")
        if hasattr(self, '_failed_commands'):
            self._failed_commands += 1
            if self._failed_commands >= 3:
                logger.warning("[Helper] Trop d'échecs, arrêt de l'aide")
                self._stop_helping()
        else:
            self._failed_commands = 1

    def on_successful_move(self):
        """Gère les déplacements réussis."""
        if hasattr(self, '_failed_commands'):
            self._failed_commands = 0
