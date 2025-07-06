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
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-h', default=Constants.HOST.value)
        parser.add_argument('-p', type=int, required=True)
        parser.add_argument('-n', required=True)
        parser.add_argument('--model', type=str, default="basic")
        args = parser.parse_args()

        pool = AgentThreads(args.h, args.p, args.n, args.model)
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
