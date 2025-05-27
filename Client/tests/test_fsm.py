##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## test_fsm
##

import pytest
from ai.fsm import FiniteStateMachine

def test_initial_state():
    fsm = FiniteStateMachine()
    assert fsm.state == 'EXPLORE'