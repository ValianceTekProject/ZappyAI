##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## pathfinding
##

import heapq
import math
from typing import List, Tuple, Set, Optional, Dict
from utils.logger import logger

class ToroidalGrid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.obstacles = set()
