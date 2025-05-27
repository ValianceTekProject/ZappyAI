##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## planner
##

import time
from typing import Dict, List, Tuple, Optional, Any
from strategy.pathfinding import ToroidalGrid
from strategy.mcts import MCTSPlanner
from config import Constants, Priority
from utils.logger import logger

class Goal:
    def __init__(self, target: Tuple[int, int], goal_type: str, priority: Priority, resources_needed: Dict[str, int] = None):
        self.target = target
        self.type = goal_type
        self.priority = priority
        self.resources_needed = resources_needed or {}
        self.created_at = time.time()
        self.completed = False

class Planner:
    def __init__(self, grid: ToroidalGrid, mcts: MCTSPlanner = None):
        self.grid = grid
        self.mcts = mcts
        self.current_goals = []
        self.completed_goals = []
