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
    def __init__(self, command_manager: CommandManager):
        self.cmd_mgr = command_manager
        self.is_dead = False

    def process_message(self, raw_responses: List[str]) -> List[Command]:
        """
        Sépare les messages serveur :
         - réponses de commande (redirigées vers CommandManager)
         - événements asynchrones (stockés dans une liste séparée)
        """
        command_responses = []
        async_messages = []

        for response in raw_responses:
            response = response.strip()

            if Parser.is_dead_response(response):
                command_responses.append(response)
                self.is_dead = True
                continue

                #  TODO : Parser les messages broadcast
            # if response.startswith("message "):
            #     async_messages.append(response)
            #     continue

            command_responses.append(response)

        completed = self.cmd_mgr.process_responses(command_responses)
        return completed
