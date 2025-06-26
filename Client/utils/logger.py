##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## logger
##

import logging
import sys

def setup_logger(name: str = 'zappy_ai', level: int = logging.INFO) -> logging.Logger:
    """Configure et retourne un logger optimisé pour Zappy."""
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(level)

    if logger_instance.handlers:
        return logger_instance

    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger_instance.addHandler(console_handler)

    return logger_instance

logger = setup_logger()