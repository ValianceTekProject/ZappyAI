##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## planner
##

import random
from protocol.commands import CommandManager
from utils.game_state import GameState
from config import CommandType, Constants
from ai.strategy.DQN.dqn_planner import DQNPlanner

class Planner:
    def __init__(self, command_manager: CommandManager, game_state: GameState, use_dqn=False):
        self.cmd_manager = command_manager
        self.state = game_state

        self.use_dqn = use_dqn
        self.dqn_planner = DQNPlanner(game_state, command_manager)

        self.last_state = None
        self.last_action_index = None

    def decide_next_action(self):
        if self.use_dqn:
            return self.dqn_planner.dqn_decision()

        if self.state.command_already_send:
            return None

        pos = self.state.vision.find_closest_resource("food")
        if pos:
            print("Cosest ressource is at")
            print("POS X = {}".format(pos[0]))
            print("POS Y = {}".format(pos[1]))
        if self.state.needs_look:
            return self.cmd_manager.look()

        if self.cmd_manager.timing.has_lost_food():
            return self.cmd_manager.inventory()

        if self.should_seek_food():
            if self.is_food_here():
                return self.cmd_manager.take(Constants.FOOD.value)
            return self.seek_food()

        reqs = self.state.get_incantation_requirements()
        if self.state.can_incant():
            local_ground = self.resources_here()
            if all(local_ground.get(res, 0) >= qty for res, qty in reqs.items()):
                return self.cmd_manager.incantation()

            drop_item = self.drop_missing_resources_for_incantation(reqs)
            if drop_item:
                return drop_item

        if self.state.has_missing_resources():
            return self.seek_resource(reqs)

        return self.explore_randomly()

    def should_seek_food(self) -> bool:
        """Vérifie si la quantité de nourriture est critique (< 6)."""
        return self.state.get_food_count() < 6

    def seek_food(self):
        """Cherche activement de la nourriture dans le champ de vision."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return self.cmd_manager.look()

        food_positions = vision.get_visible_resources().get(Constants.FOOD.value, [])
        if food_positions:
            # TODO: Remplacer par un chemin A* vers la nourriture
            return self.explore_randomly()
        return self.explore_randomly()

    def is_food_here(self) -> bool:
        """Retourne True si de la nourriture est présente sous nos pieds (position 0,0)."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return False
        return (0, 0) in vision.get_visible_resources().get(Constants.FOOD.value, [])

    def seek_resource(self, requirements: dict):
        """Collecte les pierres nécessaires à l'incantation."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return self.cmd_manager.look()

        pickup_item = self.pickup_resource(requirements)
        if pickup_item:
            return pickup_item

        for res, qty in requirements.items():
            have_inv = self.state.inventory.get(res, 0)
            if have_inv < qty:
                positions = vision.get_visible_resources().get(res, [])
                if positions:
                    # TODO: remplacer par A* vers la ressource
                    return self.explore_randomly()

        return self.explore_randomly()

    def drop_missing_resources_for_incantation(self, requirements: dict):
        """Dépose au sol les ressources nécessaires pour incanter."""
        local_ground = self.resources_here()
        for res, qty in requirements.items():
            inv = self.state.inventory.get(res, 0)
            ground = local_ground.get(res, 0)
            need_to_drop = max(0, qty - ground)

            if need_to_drop > 0 and inv > 0:
                return self.cmd_manager.set(res)
        return None

    def pickup_resource(self, requirements: dict):
        """Ramasse au sol les ressources si elles sont nécessaires."""
        ground = self.resources_here()
        for res, qty in requirements.items():
            have_inv = self.state.inventory.get(res, 0)
            if have_inv < qty and ground.get(res, 0) > 0:
                return self.cmd_manager.take(res)
        return None

    def resources_here(self) -> dict:
        """Retourne un dictionnaire des ressources sous nos pieds (0,0)."""
        vision = self.state.get_vision()
        if not vision.last_vision_data:
            return {}
        for data in vision.last_vision_data:
            if data.rel_pos == (0, 0):
                return dict(data.resources)
        return {}

    def explore_randomly(self):
        """Stratégie d'exploration basique : avancer ou tourner aléatoirement."""
        choice = random.choice([CommandType.FORWARD, CommandType.LEFT, CommandType.RIGHT])
        if choice == CommandType.FORWARD:
            return self.cmd_manager.forward()
        elif choice == CommandType.LEFT:
            return self.cmd_manager.left()
        elif choice == CommandType.RIGHT:
            return self.cmd_manager.right()
        return None
