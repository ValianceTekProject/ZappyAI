##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## planner
##

from protocol.commands import CommandManager
from utils.game_state import GameState
from ai.strategy.DQN.dqn_planner import DQNPlanner
from ai.strategy.Basic_ai.Basic_ai_planner import BASIC_AI_Planner
from ai.strategy.PPO.ppo_planner import ppo_planner

class Planner:
    def __init__(self, command_manager: CommandManager, game_state: GameState, message_bus, model: str):
        self.cmd_manager = command_manager
        self.state = game_state

        self.basic_ai = BASIC_AI_Planner(self.cmd_manager, game_state, message_bus)

        self.ppo = ppo_planner(command_manager)
        self.dqn_planner = DQNPlanner(game_state, command_manager)

        self.last_state = None
        self.last_action_index = None

        self.new_agent = False

        self.model = model

    def decide_next_action(self, responses):
        if self.model == 'PPO':
            return self.ppo.decide_action(self.state, responses)
        elif self.model == 'DQN':
            return self.dqn_planner.dqn_decision(responses)
        else:
            result = self.basic_ai.basic_ai_decision()
            self.new_agent = self.basic_ai.new_agent
            return result
