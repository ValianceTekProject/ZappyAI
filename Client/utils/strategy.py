##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## strategy
##

from typing import Dict
from enum import Enum
from utils.logger import logger

class StrategyType(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    COOPERATIVE = "cooperative"
    OPPORTUNISTIC = "opportunistic"
    SURVIVAL = "survival"

class LevelRequirement:
    def __init__(self, level: int, players_needed: int, resources: Dict[str, int]):
        self.level = level
        self.players_needed = players_needed
        self.resources = resources

class Strategy:
    def __init__(self, strategy_type: StrategyType = StrategyType.OPPORTUNISTIC):
        self.type = strategy_type
        self.level_requirements = self._init_level_requirements()
        self.current_objectives = []
        self.risk_tolerance = 0.5  # 0.0 = very safe, 1.0 = very risky
