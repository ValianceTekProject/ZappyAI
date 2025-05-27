##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## mcts
##

import random
import math
from typing import List, Dict, Any, Optional, Tuple
from config import Constants
from utils.logger import logger

class MCTSNode:
    def __init__(self, state: Dict[str, Any], parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_actions = []


class MCTSPlanner:
    def __init__(self):
        self.root = None
