##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## fsm
##

from typing import Dict, Any, Optional
from config import GameStates
from utils.logger import logger

class StateTransition:
    def __init__(self, from_state: GameStates, to_state: GameStates, condition: callable):
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition

class FiniteStateMachine:
    def __init__(self):
        self.current_state = GameStates.EXPLORE
        self.previous_state = None
        self.state_history = []
        self.transitions = []
        self.state_actions = {}
