##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## Agent mis à jour avec système de coordination
##

import time
import select
from protocol.connection import Connection
from protocol.commands import CommandManager
from protocol.message_manager import MessageManager
from teams.message_checker import MessageBus
from utils.timing import TimingManager
from utils.game_state import GameState
from utils.logger import logger
from config import CommandStatus
from ai.strategy.planner import Planner
from constant import FoodThresholds, GameplayConstants


class Agent:
    """Agent unique supportant coordination avec protocole simplifié"""

    _next_id = 0

    def __init__(self, connection: Connection, team_id: str, agent_thread, model: str):
        """
        Initialise un nouvel agent avec support de coordination
        
        Args:
            connection: Connexion au serveur
            team_id: Nom de l'équipe
            agent_thread: Gestionnaire des threads d'agents
            model: Type de modèle IA (basic, DQN, PPO)
        """
        self.conn = connection
        self.agent_thread = agent_thread
        self.dimension_map = self.conn.get_map_size()

        self.agent_id = Agent._next_id
        Agent._next_id += 1

        self.timing = TimingManager()
        self.state = GameState(team_id, self.dimension_map, self.agent_id)
        self.state.agent_thread = self.agent_thread
        self.commands = CommandManager(self.conn, self.timing, self.state)
        self.msg_bus = MessageBus(self.state.level, team_id)
        self.msg_manager = MessageManager(self.commands, self.msg_bus)

        self.planner = Planner(
            command_manager=self.commands,
            game_state=self.state,
            message_bus=self.msg_bus,
            model=model,
        )

        self._last_decision_time = time.time()
        self._last_command_time = time.time()

        self.initialized = False
        self.init_stage = 0

        self.decisions_count = 0
        self.successful_actions = 0
        self.failed_actions = 0

        logger.info(f"[Agent] Agent {self.agent_id} initialisé - Team: {team_id}")

    def run_loop(self):
        """Boucle principale de l'agent avec support de coordination"""
        while True:
            try:
                now = time.time()

                responses = self.read_non_blocking()
                completed = self.msg_manager.process_responses(responses)

                if self.msg_manager.is_dead:
                    self.planner.decide_next_action(responses=responses)
                    self._handle_agent_death()
                    return

                self._process_completed_commands(completed, now)

                if not self.initialized:
                    if self._handle_initialization():
                        continue

                self.timing.update_from_food_level(self.state.get_food_count())

                self._update_coordination_reference()

                self._make_ia_decision(now)

                self._adaptive_sleep()

            except Exception as e:
                logger.error(f"[Agent {self.agent_id}] Erreur critique: {e}")
                self._handle_critical_error(e)

    def _update_coordination_reference(self):
        """Met à jour la référence de coordination dans le MessageManager"""
        try:
            current_state = self.planner.fsm.state
            if hasattr(current_state, '__class__') and 'CoordinateIncantationState' in current_state.__class__.__name__:
                self.msg_manager.set_coordination_state(current_state)
            else:
                self.msg_manager.set_coordination_state(None)
        except Exception as e:
            logger.debug(f"[Agent {self.agent_id}] Erreur mise à jour coordination: {e}")

    def _handle_agent_death(self):
        """Gère la mort de l'agent"""
        self.agent_thread.agent_dead(self)
        survival = time.time() - getattr(self, '_start_time', time.time())
        logger.info(f"[Agent {self.agent_id}] MORT niveau {self.state.level} - "
                   f"Décisions: {self.decisions_count}, Survie: {survival:.1f}s")

    def _process_completed_commands(self, completed: list, now: float):
        """
        Traite les commandes terminées
        
        Args:
            completed: Liste des commandes terminées
            now: Temps actuel
        """
        if completed is None:
            return
            
        for cmd in completed:
            self.state.update(cmd)
            self._last_command_time = now

            if cmd.status.value == CommandStatus.SUCCESS.value:
                self.successful_actions += 1
                self.planner.on_command_success(cmd.type, cmd.response)
            elif cmd.status.value == CommandStatus.FAILED.value:
                self.failed_actions += 1
                self.planner.on_command_failed(cmd.type, cmd.response)

    def _handle_initialization(self) -> bool:
        """
        Initialisation en plusieurs étapes
        
        Returns:
            True si initialisation en cours, False si terminée
        """
        if self.init_stage == 0:
            if not self.commands.has_pending():
                self.commands.look()
                self.init_stage = 1
            return True
        elif self.init_stage == 1:
            if not self.commands.has_pending():
                self.commands.inventory()
                self.init_stage = 2
            return True
        elif self.init_stage == 2:
            self.initialized = True
            self._start_time = time.time()
            logger.info(f"[Agent {self.agent_id}] INITIALISATION complète - Position: {self.state.get_position()}")
            return False
        return False

    def _make_ia_decision(self, now: float):
        """
        Délégation de la décision au Planner avec support coordination
        
        Args:
            now: Temps actuel
        """
        if self.state.command_already_send or self.commands.get_pending_count() >= GameplayConstants.MAX_PENDING_COMMANDS:
            return
        if not self.timing.can_execute_action():
            return

        cmd = self.planner.decide_next_action(responses=None)
        if cmd:
            self.decisions_count += 1
            self._last_decision_time = now
            self._last_command_time = now
        else:
            if self.state.get_food_count() <= FoodThresholds.CRITICAL:
                self.commands.look()
                self._last_decision_time = now

    def _adaptive_sleep(self):
        """Sleep adaptatif selon l'urgence de la situation"""
        sleep_time = self.timing.get_sleep_time()

        current_food = self.state.get_food_count()
        if current_food <= FoodThresholds.CRITICAL:
            sleep_time = min(sleep_time, 0.005)
        elif current_food <= FoodThresholds.SUFFICIENT:
            sleep_time = min(sleep_time, 0.01)

        if sleep_time > 0:
            time.sleep(sleep_time)

    def _handle_critical_error(self, error: Exception):
        """
        Gère les erreurs critiques avec récupération
        
        Args:
            error: Exception capturée
        """
        logger.error(f"[Agent {self.agent_id}] 🚨 ERREUR CRITIQUE: {error}")

        try:
            self.state.force_unlock()
            time.sleep(0.1)
        except:
            pass

    def read_non_blocking(self) -> list:
        """
        Lecture réseau non-bloquante optimisée
        
        Returns:
            Liste des réponses reçues
        """
        sock = self.conn.get_socket()
        if not sock:
            return []

        try:
            ready = select.select([sock], [], [], 0)
            if ready[0]:
                data = self.conn.receive_raw()
                return self.conn.split_responses(data)
        except Exception as e:
            logger.warning(f"[Agent {self.agent_id}] Erreur lecture réseau: {e}")

        return []