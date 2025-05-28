##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## mcts
##

import random
import math
from typing import List, Dict, Any, Optional, Tuple
from config import Constants, GameStates
from utils.logger import logger

class clientState:
    def __init__(self, state: Dict[str, Any]) -> None:
        self.clientPos = {0, 0}
        self.inventory = None
        self.vision = None
        self.level = None
        self.objectif = GameStates
        pass

class MCTSNode:
    def __init__(self, state: Dict[str, Any], parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_actions = []
        for action in GameStates:
            self.untried_actions.append(action)

    def addAction(self, action):
        self.untried_actions.append(action)

class MCTSPlanner:
    def __init__(self):
        self.root = None
