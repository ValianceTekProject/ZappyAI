##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## client
##

import argparse
import sys
from protocol.connection import Connection
from ai.agent import Agent
from config import Constants
from utils.logger import logger

def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--host', default=Constants.HOST.value)
        parser.add_argument('--port', type=int, required=True)
        parser.add_argument('--team', required=True)
        parser.add_argument('--freq', type=int, default=Constants.FREQ_DEFAULT.value)
        args = parser.parse_args()

        conn = Connection(args.host, args.port)
        conn.handshake(args.team)

        agent = Agent(conn, freq=args.freq)
        agent.run_loop()
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(84)

if __name__ == '__main__':
    main()
