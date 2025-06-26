##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## ppo_planner
##

from ai.strategy.PPO.ppo import PPO
from ai.strategy.PPO.ppo_state import ppo_state
from config import Item, CommandType, Constants
import numpy as np
import tensorflow as tf
import pickle
from datetime import datetime
import os
from utils.game_state import GameState


class ppo_planner():
    def __init__(self, command_manager):
        self.rotation = 0
        self.ppo = PPO(state_dim=11, action_dim=6)

        self.cmd_manager = command_manager

        self.last_ppo_state = None
        self.last_state_vector = None
        self.last_action = None
        self.last_value = None
        self.last_log_prob = None
        self.last_result = None

        self.actualize_vision = True
        self.survival_counter = 0

        self.load_model()

        self.actions = [
            CommandType.FORWARD,
            CommandType.RIGHT,
            CommandType.LEFT,
            CommandType.TAKE,
            CommandType.LOOK,
            CommandType.INVENTORY
        ]

        self.distance_closest_food = None
        self.angle_closest_food = None

    def transform_state_into_vector(self, state: ppo_state):
        """Transforme un ppo_state en vecteur numpy"""
        vector = []

        vector.append(state.food_inventory)
        vector.append(state.level)
        vector.append(state.linemate_inventory)
        vector.append(state.deraumere_inventory)
        vector.append(state.sibur_inventory)
        vector.append(state.mediane_inventory)
        vector.append(state.phiras_inventory)
        vector.append(state.thystame_inventory)
        vector.append(state.distance_closest_food)
        vector.append(state.angle_closest_food)
        vector.append(self.rotation / 4.0)


        return np.array(vector, dtype=np.float32)

    def decide_action(self, game_state: GameState, responses):
        if responses:
            self.last_result = responses[0]

        #print("Responses", self.last_result)
        if self.actualize_vision:
            self.actualize_vision = False
            self.rotation = 0
            state = ppo_state(game_state, actualize_vision=True)
            self.distance_closest_food = state.distance_closest_food
            self.angle_closest_food = state.angle_closest_food
        else:
            state = ppo_state(game_state, actualize_vision=False)
            state.distance_closest_food = self.distance_closest_food
            state.angle_closest_food = self.angle_closest_food

        #print("State:")
        #print("Food = ", state.food_inventory)
        #print("Level = ", state.level)
        #print("closest food = ", state.distance_closest_food)
        #print("angle = ", state.angle_closest_food)
        # Si on a une transition complète, la stocker
        if self.last_ppo_state is not None and self.last_state_vector is not None:
            reward = self.calculate_reward(
                self.last_result,
                self.last_ppo_state,
                state,
                self.last_action
            )

            # Stocker la transition
            self.store_transition(
                self.last_state_vector,
                self.last_action,
                reward,
                self.last_value,
                self.last_log_prob
            )

            if self.last_result == "dead":
                print(f"Episode terminé - {len(self.ppo.states)} transitions")
                if len(self.ppo.states) > 50:
                    self.save_experience_buffer()
                self.reset_episode()
                return None

        state_vector = self.transform_state_into_vector(state)
        state_tensor = tf.expand_dims(state_vector, 0)

        action, value, log_prob = self.ppo.get_action(state_tensor)

        self.last_ppo_state = state
        self.last_state_vector = state_vector
        self.last_action = action
        self.last_value = value
        self.last_log_prob = log_prob

        self.update(action)

        return self.send_command(self.get_action_from_index(action))

    def send_command(self, action):
        if action == CommandType.FORWARD:
            self.last_action_reward = 0
            return self.cmd_manager.forward()
        elif action == CommandType.LEFT:
            self.last_action_reward = 1
            return self.cmd_manager.left()
        elif action == CommandType.RIGHT:
            self.last_action_reward = 2
            return self.cmd_manager.right()
        elif action == CommandType.TAKE:
            self.last_action_reward = 3
            return self.cmd_manager.take(Constants.FOOD.value)
        elif action == CommandType.LOOK:
            print("Look")
            return self.cmd_manager.look()
        elif action == CommandType.INVENTORY:
            return self.cmd_manager.inventory()
        return None

    def reset_episode(self):
        self.last_ppo_state = None
        self.last_state_vector = None
        self.last_action = None
        self.actualize_vision = True
        self.rotation = 0

    def store_transition(self, state, action, reward, value, log_prob):
        self.ppo.states.append(state)
        self.ppo.actions.append(action)
        self.ppo.rewards.append(reward)
        self.ppo.values.append(value)
        self.ppo.log_probs.append(log_prob)

    def update_food_distance_after_forward(self):
        angle = self.angle_closest_food * 360

        if angle == 0 or angle == 45 or angle == 315:
            self.distance_closest_food -= (1 / 20.0)
        elif angle == 180 or angle == 135 or angle == 225:
            self.distance_closest_food += (1 / 20.0)

        self.distance_closest_food = max(0, min(1, self.distance_closest_food))

    def update_angle_after_left(self):
        if self.angle_closest_food == -1:
            return
        angle = self.angle_closest_food * 360

        if angle == 0:
            self.angle_closest_food = 90 / 360.0
        elif angle == 45:
            self.angle_closest_food = 135 / 360.0
        elif angle == 90:
            self.angle_closest_food = 180 / 360.0
        elif angle == 135:
            self.angle_closest_food = 225 / 360.0
        elif angle == 180:
            self.angle_closest_food = 270 / 360.0
        elif angle == 225:
            self.angle_closest_food = 315 / 360.0
        elif angle == 270:
            self.angle_closest_food = 0
        elif angle == 315:
            self.angle_closest_food = 45 / 360.0

    def update_angle_after_right(self):
        if self.angle_closest_food == -1:
            return
        angle = self.angle_closest_food * 360

        if angle == 0:
            self.angle_closest_food = 270 / 360.0
        elif angle == 45:
            self.angle_closest_food = 315 / 360.0
        elif angle == 90:
            self.angle_closest_food = 0
        elif angle == 135:
            self.angle_closest_food = 45 / 360.0
        elif angle == 180:
            self.angle_closest_food = 90 / 360.0
        elif angle == 225:
            self.angle_closest_food = 135 / 360.0
        elif angle == 270:
            self.angle_closest_food = 180 / 360.0
        elif angle == 315:
            self.angle_closest_food = 225 / 360.0

    def update(self, action_index):
        if self.actions[action_index] == CommandType.RIGHT:
            self.update_angle_after_right()
            #print("New angle next right = ", self.angle_closest_food * 360)
            #print("----------------------------------")
            self.rotation = (self.rotation + 1) % 4
        elif self.actions[action_index] == CommandType.LEFT:
            self.update_angle_after_left()
            #print("New angle next left = ", self.angle_closest_food * 360)
            #print("----------------------------------")
            self.rotation = (self.rotation - 1) % 4
        elif self.actions[action_index] == CommandType.FORWARD:
            self.update_food_distance_after_forward()
        elif self.actions[action_index] == CommandType.LOOK:
            #print("Forward distance = ", self.distance_closest_food * 20)
            #print("----------------------------------")
            self.actualize_vision = True

    def get_action_from_index(self, index):
        if index < 0:
            return self.actions[0]
        if index >= len(self.actions):
            return self.actions[-1]
        return self.actions[index]

    def calculate_reward(self, result, old_state, new_state, action):
        reward = 0.01

        self.survival_counter += 1

        if result == "dead":
            return -100

        if result == "ko":
            return -0.5

        if self.distance_closest_food >= 0 and self.angle_closest_food >= 0:
            if old_state.distance_closest_food > new_state.distance_closest_food:
                reward += 1.0

            if abs(self.angle_closest_food * 360) < 45:
                reward += 0.2

        if new_state.food_inventory > old_state.food_inventory:
            reward += 20
            self.survival_counter = 0

        if new_state.food_inventory < 0.1:
            reward -= 5
        elif new_state.food_inventory < 0.2:
            reward -= 2

        if self.survival_counter > 500:
            reward += 10
        if self.survival_counter > 1000:
            reward += 20
        if self.survival_counter > 1500:
            reward += 50

        return reward

    def save_experience_buffer(self):

        buffer_data = {
            'states': self.ppo.states,
            'actions': self.ppo.actions,
            'rewards': self.ppo.rewards,
            'values': self.ppo.values,
            'log_probs': self.ppo.log_probs
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"models/ppo_buffer_{timestamp}.pkl"

        with open(filename, 'wb') as f:
            pickle.dump(buffer_data, f)

        print(f"Buffer saved: {filename}")

    def save_model(self, path="ppo_model"):
        try:
            self.ppo.actor.save_weights(f"{path}_actor.h5")
            self.ppo.critic.save_weights(f"{path}_critic.h5")
            print("Model saved")
        except Exception as e:
            print(f"Save Error: {e}")

    def load_model(self, path="ppo_model"):

        actor_path = f"{path}_actor.weights.h5"
        critic_path = f"{path}_critic.weights.h5"

        if not os.path.exists(actor_path) or not os.path.exists(critic_path):
            print("No model founded")
            return False

        try:
            dummy_input = tf.zeros((1, 11))
            _ = self.ppo.actor(dummy_input)
            _ = self.ppo.critic(dummy_input)

            self.ppo.actor.load_weights(actor_path)
            self.ppo.critic.load_weights(critic_path)

            print(f"Model fully loaded")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False