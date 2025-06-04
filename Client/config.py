##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## config
##

from enum import Enum
import time

class Constants(Enum):
    HOST = 'localhost'
    PORT_DEFAULT = 6666
    FREQ_DEFAULT = 100  # freq (100ms)
    MAX_PENDING = 10
    TIME_UNIT = 1.0  # seconds
    FOODS_LOSS_TIME = 126 # times units send inventory for look nb of food

    # Network settings
    SOCKET_TIMEOUT = 5.0
    RECONNECT_MAX_RETRIES = 3
    RECONNECT_BASE_DELAY = 1.0
    RESPONSE_TIMEOUT = 10.0

    # Command durations (multiplier of 1/f)
    DUR_FORWARD = 7
    DUR_TURN = 7
    DUR_LOOK = 7
    DUR_INVENTORY = 1
    DUR_BROADCAST = 7
    DUR_FORK = 42
    DUR_INCANTATION = 300

    FOOD = 'food'
    LINEMATE = 'linemate'
    DERAUMERE = 'deraumere'
    SIBUR = 'sibur'
    MENDIANE = 'mendiane'
    PHIRAS = 'phiras'
    THYSTAME = 'thystame'

    VISION_RANGE = 3
    MAX_LEVEL = 8

class CommandType(Enum):
    FORWARD = 'Forward'
    RIGHT = 'Right'
    LEFT = 'Left'
    LOOK = 'Look'
    INVENTORY = 'Inventory'
    BROADCAST = 'Broadcast'
    CONNECT_NBR = 'Connect_nbr'
    FORK = 'Fork'
    EJECT = 'Eject'
    TAKE = 'Take'
    SET = 'Set'
    INCANTATION = 'Incantation'

class CommandStatus(Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
    DEAD = 'dead'
    TIMEOUT = 'timeout'

class GameStates(Enum):
    EXPLORE = 'explore'
    COLLECT = 'collect'
    INCANT_PREP = 'incant_prep'
    INCANTING = 'incanting'
    FLEEING = 'fleeing'
    DEAD = 'dead'

class Orientation(int):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class ResponseType(Enum):
    OK = 'ok'
    KO = 'ko'
    DEAD = 'dead'
    CURRENT_LEVEL = 'current level:'
    ELEVATION_UNDERWAY = 'elevation underway'
    LOOK = '['
    INVENTORY = '['
    BROADCAST = 'message'
    EJECT = 'eject:'
