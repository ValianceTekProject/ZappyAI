##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## message_manager
##

from typing import List, Tuple
from protocol.commands import Command, CommandManager
from utils.logger import logger
from protocol.parser import Parser

class MessageManager:
    def __init__(self, cmd_mgr, bus):
        self.cmd_mgr = cmd_mgr
        self.bus = bus
        self.is_dead = False

    def process_responses(self, raw_responses: List[str]):
        command_responses = []
        for response in raw_responses:
            response = response.strip()
            if Parser.is_dead_response(response):
                self.is_dead = True
                return
            if Parser.is_broadcast(response):
                dir_, token = Parser.parse_broadcast_response(response).values()
                self.bus.publish_raw(dir_, token)
            else:
                command_responses.append(response)
        # On ne renvoie plus les broadcasts au CmdMgr
        return self.cmd_mgr.process_responses(command_responses)