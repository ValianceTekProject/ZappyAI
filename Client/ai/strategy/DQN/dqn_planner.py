##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## dqn_planner
##

import numpy as np

from ai.strategy.DQN.dqn_state import DQNState
from protocol.commands import CommandManager
from utils.game_state import GameState
from config import CommandType, Constants
from ai.strategy.DQN.dqn import DeepQNetwork
from config import Item

class DQNPlanner:
    def __init__(self, game_state: GameState, command_manager: CommandManager):
        self.dqn = DeepQNetwork()
        self.cmd_manager = command_manager
        self.state = game_state

        self.last_state = None
        self.last_state_vector = None
        self.last_action_index = None
        self.last_result = None
        self.save_counter = 0
        self.dqn.load_model("dqn_model.pth")

        self.actualize_inventory = False

    def dqn_decision(self, responses):
        if self.state.command_already_send:
            return None
        self.last_result = responses
        current_state = self.dqn.build_state(self.state, self.actualize_inventory)
        if self.actualize_inventory:
            self.actualize_inventory = False
        else:
            if self.last_state and self.last_state.vision:
                current_state.vision = self.last_state.vision
        self.last_state = current_state
        current_state_vector = self.transform_state_into_vector(current_state)

        if self.last_state_vector is not None and self.last_action_index is not None:
            # Calculer la récompense
            reward = self.dqn.calculate_reward(
                self.last_action_index,
                self.last_result,
                self.last_state_vector,
                current_state_vector
            )

            done = (self.last_result == "dead")

            self.dqn.save_experience(
                self.last_state_vector,
                self.last_action_index,
                reward,
                current_state_vector,
                done
            )

            if done:
                self.last_state = None
                self.last_state_vector = None
                self.last_action_index = None
                self.actualize_inventory = True

                print("DEAD ------------------------------------------------------------")
                if len(self.dqn.memory) > 50:  # Au moins quelques expériences
                    print(f"SAVE ON DEATH - {len(self.dqn.memory)} experiences")
                    self.dqn.save_model("dqn_model.pth")

                exit(0)

        # 3. Choisir la nouvelle action
        action_index = self.dqn.choose_action(current_state_vector)
        action = self.dqn.get_action_form_index(action_index)

        # 4. Exécuter l'action et récupérer le résultat
        result = self.execute_dqn_action(action, current_state_vector)

        # 5. Stocker pour la prochaine itération
        self.last_state = current_state
        self.last_state_vector = current_state_vector
        self.last_action_index = action_index
        self.last_result = result  # Supposant que execute_dqn_action retourne le status

        # 6. Entraîner périodiquement
        if len(self.dqn.memory) > 0 and len(self.dqn.memory) % 10 == 0:
            self.dqn.replay()

        # 7. Sauvegarder périodiquement
        self.save_counter += 1
        if self.save_counter % 400 == 0:
            self.dqn.save_model("dqn_model.pth")

        if len(self.dqn.memory) % 100 == 0:
            print(f"Epsilon: {self.dqn.epsilon:.3f}, Expériences: {len(self.dqn.memory)}")

        return result

    def transform_state_into_vector(self, state: DQNState):
        vector = []

        vector.append(state.food_inventory)
        vector.append(state.level)
        vector.append(state.linemate_inventory)
        vector.append(state.deraumere_inventory)
        vector.append(state.sibur_inventory)
        vector.append(state.mediane_inventory)
        vector.append(state.phiras_inventory)
        vector.append(state.thystame_inventory)

        for line in state.vision:
            for tile in line:
                vector.append(tile[Item.FOOD] / 100)
                vector.append(tile[Item.LINEMATE] / 100)
                vector.append(tile[Item.DERAUMERE] / 100)
                vector.append(tile[Item.SIBUR] / 100)
                vector.append(tile[Item.MEDIANE] / 100)
                vector.append(tile[Item.PHIRAS] / 100)
                vector.append(tile[Item.THYSTAME] / 100)
                vector.append(tile[Item.PLAYER] / 100)
        return np.array(vector)

    def handle_forward_action(self, action, current_state):
        return self.cmd_manager.forward()

    def execute_dqn_action(self, action, current_state):
        if action == CommandType.FORWARD:
            return self.handle_forward_action(action, current_state)
        elif action == CommandType.LEFT:
            return self.cmd_manager.left()
        elif action == CommandType.RIGHT:
            return self.cmd_manager.right()
        elif action == CommandType.TAKE:
            return self.cmd_manager.take(Constants.FOOD.value)
        elif action == CommandType.LOOK:
            self.actualize_inventory = True
            return self.cmd_manager.look()
        return None
