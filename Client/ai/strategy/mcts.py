##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## mcts
##

import random
import copy
from typing import List, Dict, Any, Optional, Tuple
from config import Orientation, CommandType

class clientState:
    def __init__(self, state: Dict[str, Any], position: Tuple[int, int]) -> None:
        self.clientPos = position
        self.inventory = state.get("inventory", {})
        self.vision = state.get("vision", [])
        self.level = state.get("level", 1)
        self.objectif = state.get("objectif", None)
        self.orientation = list(Orientation)
        self.map_data = {}
        self.known_tiles = set()

    def simulate_action(self, action: CommandType) -> 'clientState':
        new_state = copy.deepcopy(self)

        return new_state

class MCTSNode:
    def __init__(self, state: clientState, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_actions = list(CommandType)

class MCTSPlanner:
    def __init__(self, root_state: clientState):
        self.root = MCTSNode(root_state)

    def simulate_action(self, state: clientState, action: CommandType) -> clientState:
        return state.simulate_action(action)
