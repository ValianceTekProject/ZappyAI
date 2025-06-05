##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## client
##

import argparse
import sys
import time
from agent_threads import AgentThreads
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

        pool = AgentThreads(args.host, args.port, args.team, args.freq)
        pool.start_initial_agent()

        while True:
            with pool._lock:
                alive = len(pool._agents)
            if alive == 0:
                logger.info("Tous les agents sont morts, arrêt automatique du programme.")
                break
            time.sleep(0.1)

        pool.close_client()
        return 0

    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        return 84

if __name__ == '__main__':
    sys.exit(main())
