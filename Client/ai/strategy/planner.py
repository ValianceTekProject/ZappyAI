##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## planner
##

from ai.strategy.Basic_ai.fsm_planner import FSMPlanner
from ai.strategy.DQN.dqn_planner import DQNPlanner

class Planner:
    def __init__(self, command_manager, game_state, message_bus, use_dqn=False):
        self.use_dqn = use_dqn
        self.use_fsm = False

        self.state = game_state
        self.dqn_planner = DQNPlanner(game_state, command_manager)
        self.fsm_planner = FSMPlanner(command_manager, game_state, message_bus)

        self.new_agent = False

    def decide_next_action(self, responses=None):
        if self.use_dqn:
            return self.dqn_planner.dqn_decision(responses)
        else:
            self.use_fsm = True
            return self.fsm_planner.decide_next_action()

    def on_command_success(self, command_type, response=None):
        if self.use_fsm:
            self.fsm_planner.on_command_success(command_type, response)

    def on_command_failed(self, command_type, response=None):
        if self.use_fsm:
            self.fsm_planner.on_command_failed(command_type, response)

