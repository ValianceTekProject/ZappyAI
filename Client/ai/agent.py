##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## Exemple d'intégration de la FSM dans l'agent existant
##

import time
import select
from typing import Tuple
from protocol.connection import Connection
from protocol.commands import CommandManager
from protocol.message_manager import MessageManager
from teams.message_checker import MessageBus
from utils.timing import TimingManager
from utils.game_state import GameState  # Version améliorée
from utils.logger import logger
from config import CommandType

# Import de la FSM
from ai.strategy.planner import Planner  # Version avec FSM intégrée

class Agent:
    """
    Agent amélioré avec FSM de survie intégrée.
    Version optimisée pour la survie pure avec gestion d'erreurs renforcée.
    """

    _next_id = 0

    def __init__(self, connection: Connection, team_id: str, agent_thread):
        self.conn = connection
        self.agent_thread = agent_thread
        self.dimension_map = self.conn.get_map_size()

        self.agent_id = Agent._next_id
        Agent._next_id += 1

        # Composants principaux
        self.timing = TimingManager()
        self.state = GameState(team_id, self.dimension_map, self.agent_id)
        self.commands = CommandManager(self.conn, self.timing, self.state)
        self.msg_bus = MessageBus(self.state.level, team_id)
        self.msg_manager = MessageManager(self.commands, self.msg_bus)

        # 🎯 NOUVEAU: Utilisation de la FSM de survie
        self.planner = Planner(
            command_manager=self.commands,
            game_state=self.state, 
            message_bus=self.msg_bus,
            use_fsm=True  # ✅ Activer la FSM
        )

        # Détection de blocage améliorée
        self._last_decision_time = time.time()
        self._last_command_time = time.time()
        self._last_food_check = time.time()
        self._block_detection_threshold = 3.0  # Plus réactif
        self._force_unlock_threshold = 6.0     # Plus rapide

        # État d'initialisation
        self.initialized = False
        self.init_stage = 0

        # Statistiques de performance
        self.decisions_count = 0
        self.successful_actions = 0
        self.failed_actions = 0

        logger.info(f"[Agent] Agent {self.agent_id} initialisé avec FSM de survie - Team: {team_id}")

    def run_loop(self):
        """
        Boucle principale optimisée avec FSM de survie.
        Gestion d'erreurs renforcée et détection de blocage avancée.
        """
        while True:
            try:
                current_time = time.time()
                
                # 1. Lecture des réponses réseau
                responses = self.read_non_blocking()
                completed = self.msg_manager.process_responses(responses)

                # 2. Vérification mort de l'agent
                if self.msg_manager.is_dead:
                    self._handle_agent_death()
                    return

                # 3. Détection de blocage critique
                if self.initialized:
                    self._check_for_deadlock(current_time)

                # 4. Traitement des commandes complétées
                self._process_completed_commands(completed, current_time)

                # 5. Gestion du mode urgence timing
                self._update_emergency_timing()

                # 6. Initialisation si nécessaire
                if not self.initialized:
                    if self._handle_initialization():
                        continue  # Continuer l'initialisation

                # 7. 🎯 DÉCISION FSM PRINCIPALE
                self._make_fsm_decision(current_time)

                # 8. Sleep adaptatif optimisé
                self._adaptive_sleep()

            except Exception as e:
                logger.error(f"[Agent {self.agent_id}] Erreur critique: {e}")
                self._handle_critical_error(e)

    def _handle_agent_death(self):
        """Gère la mort de l'agent."""
        self.agent_thread.agent_dead(self)
        final_food = self.state.get_food_count()
        survival_time = time.time() - (getattr(self, '_start_time', time.time()))
        
        logger.info(f"[Agent {self.agent_id}] 💀 MORT à niveau {self.state.level} "
                   f"(Food: {final_food}, Survie: {survival_time:.1f}s, "
                   f"Décisions: {self.decisions_count})")

    def _check_for_deadlock(self, current_time: float):
        """Détection de blocage avancée avec intervention automatique."""
        time_since_decision = current_time - self._last_decision_time
        time_since_command = current_time - self._last_command_time
        
        # Force unlock en cas de blocage prolongé
        if time_since_command > self._force_unlock_threshold:
            current_food = self.state.get_food_count()
            logger.error(f"[Agent {self.agent_id}] 🚨 DEADLOCK DÉTECTÉ! "
                        f"Aucune commande depuis {time_since_command:.1f}s "
                        f"(Food: {current_food})")
            
            self.state.force_unlock()
            self._last_command_time = current_time
            
            # Action d'urgence selon la situation
            if current_food <= 5:
                logger.error(f"[Agent {self.agent_id}] DEADLOCK + URGENCE ALIMENTAIRE!")
                self.commands.look()  # Chercher nourriture désespérément
            
        # Avertissement si pas de décision
        elif time_since_decision > self._block_detection_threshold:
            logger.warning(f"[Agent {self.agent_id}] ⚠️ Pas de décision depuis "
                          f"{time_since_decision:.1f}s")

    def _process_completed_commands(self, completed: list, current_time: float):
        """Traite les commandes complétées avec notifications à la FSM."""
        for cmd in completed:
            # Mise à jour de l'état
            self.state.update(cmd)
            self._last_command_time = current_time
            
            # 🎯 Notification à la FSM
            if cmd.status.value == 'success':
                self.successful_actions += 1
                self.planner.on_command_success(cmd.type, cmd.response)
                
                # Log spécial pour actions critiques
                if cmd.type == CommandType.TAKE and 'food' in str(cmd.response):
                    new_food = self.state.get_food_count()
                    logger.info(f"[Agent {self.agent_id}] 🍖 NOURRITURE RÉCUPÉRÉE! "
                               f"Total: {new_food}")
                
            elif cmd.status.value == 'failed':
                self.failed_actions += 1
                self.planner.on_command_failed(cmd.type, cmd.response)
                
                # Log d'échec avec contexte
                logger.warning(f"[Agent {self.agent_id}] ❌ {cmd.type} échoué: {cmd.response}")

    def _update_emergency_timing(self):
        """Met à jour le timing d'urgence selon la situation alimentaire."""
        current_food = self.state.get_food_count()
        is_emergency = current_food <= self.state.food_thresholds.get('critical', 10)
        self.timing.set_emergency_mode(is_emergency)

    def _handle_initialization(self) -> bool:
        """
        Gère l'initialisation de l'agent en étapes.
        Returns: True si initialisation en cours, False si terminée
        """
        if self.init_stage == 0:
            if not self.commands.has_pending():
                logger.debug(f"[Agent {self.agent_id}] Initialisation: LOOK")
                self.commands.look()
                self.init_stage = 1
            return True

        elif self.init_stage == 1:
            if not self.commands.has_pending():
                logger.debug(f"[Agent {self.agent_id}] Initialisation: INVENTORY")
                self.commands.inventory()
                self.init_stage = 2
            return True

        elif self.init_stage == 2:
            self.initialized = True
            self._start_time = time.time()
            initial_food = self.state.get_food_count()
            
            logger.info(f"[Agent {self.agent_id}] ✅ INITIALISATION COMPLÈTE! "
                       f"Food: {initial_food}, Position: {self.state.get_position()}")
            return False

        return False

    def _make_fsm_decision(self, current_time: float):
        """
        Prend une décision via la FSM avec conditions de sécurité.
        """
        # Vérifications de sécurité
        if not self._can_make_decision():
            return

        try:
            # 🎯 APPEL PRINCIPAL À LA FSM
            cmd = self.planner.decide_next_action()
            
            if cmd:
                self.decisions_count += 1
                self._last_decision_time = current_time
                self._last_command_time = current_time
                
                # Log périodique de statut
                if self.decisions_count % 25 == 0:
                    self._log_agent_status()
            
            else:
                # FSM ne peut pas décider - action de sécurité
                current_food = self.state.get_food_count()
                if current_food <= 8:  # Seuil critique
                    logger.error(f"[Agent {self.agent_id}] FSM bloquée en urgence! "
                                f"Force LOOK (Food: {current_food})")
                    self.commands.look()
                    self._last_decision_time = current_time

        except Exception as e:
            logger.error(f"[Agent {self.agent_id}] Erreur FSM: {e}")
            # Action de récupération
            self.commands.look()

    def _can_make_decision(self) -> bool:
        """Vérifie si l'agent peut prendre une décision."""
        if self.state.command_already_send:
            return False
            
        if self.commands.get_pending_count() >= 8:
            return False
            
        if not self.timing.can_execute_action():
            return False
            
        return True

    def _adaptive_sleep(self):
        """Sleep adaptatif selon l'urgence de la situation."""
        sleep_time = self.timing.get_sleep_time()
        
        # Réduire sleep en cas d'urgence alimentaire
        current_food = self.state.get_food_count()
        if current_food <= 5:
            sleep_time = min(sleep_time, 0.005)  # 5ms max en urgence critique
        elif current_food <= 10:
            sleep_time = min(sleep_time, 0.01)   # 10ms max en urgence
        
        if sleep_time > 0:
            time.sleep(sleep_time)

    def _handle_critical_error(self, error: Exception):
        """Gère les erreurs critiques avec récupération."""
        logger.error(f"[Agent {self.agent_id}] 🚨 ERREUR CRITIQUE: {error}")
        
        # Tentative de récupération
        try:
            self.state.force_unlock()
            time.sleep(0.1)  # Pause de récupération
        except:
            pass

    def _log_agent_status(self):
        """Log périodique du statut de l'agent."""
        current_food = self.state.get_food_count()
        success_rate = (self.successful_actions / max(1, self.successful_actions + self.failed_actions)) * 100
        
        # Obtenir infos de stratégie FSM
        strategy_info = self.planner.get_current_strategy_info()
        current_state = strategy_info.get('state', 'unknown')
        
        logger.info(f"[Agent {self.agent_id}] 📊 STATUS - "
                   f"État: {current_state}, Food: {current_food}, "
                   f"Niveau: {self.state.level}, Décisions: {self.decisions_count}, "
                   f"Succès: {success_rate:.1f}%")

    def read_non_blocking(self) -> list:
        """
        Lecture réseau non-bloquante optimisée.
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

    def get_agent_stats(self) -> dict:
        """Retourne les statistiques de l'agent pour monitoring."""
        uptime = time.time() - getattr(self, '_start_time', time.time())
        
        return {
            'agent_id': self.agent_id,
            'uptime': uptime,
            'decisions': self.decisions_count,
            'successful_actions': self.successful_actions,
            'failed_actions': self.failed_actions,
            'success_rate': (self.successful_actions / max(1, self.successful_actions + self.failed_actions)) * 100,
            'current_food': self.state.get_food_count(),
            'current_level': self.state.level,
            'fsm_strategy': self.planner.get_current_strategy_info(),
            'state_summary': self.state.get_state_summary()
        }