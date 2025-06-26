##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## ppo
##

from ai.strategy.PPO.actor import actor
from ai.strategy.PPO.critic import critic
import tensorflow as tf
from tensorflow.keras.optimizers import Adam


class PPO:
    def __init__(self, state_dim, action_dim):
        self.actor = actor(action_dim)
        self.critic = critic()
        self.optimizer_actor = Adam(3e-4)
        self.optimizer_critic = Adam(3e-4)

        self.clip_ratio = 0.2
        self.epochs = 10

        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []

    def get_action(self, state):
        action_probs = self.actor(state)
        value = self.critic(state)

        result = tf.random.categorical(tf.math.log(action_probs), 1)

        action_index = result[0, 0].numpy()
        log_prob = tf.math.log(action_probs[0, action_index])

        return action_index, value[0, 0].numpy(), log_prob.numpy()

    def compute_gae(self, rewards, values, gamma=0.99, lam=0.95):
        advantages = []
        last_advantage = 0

        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[t + 1]
            delta = rewards[t] + gamma * next_value - values[t]
            last_advantage = delta + gamma * lam * last_advantage
            advantages.insert(0, last_advantage)

        advantages = tf.convert_to_tensor(advantages, dtype=tf.float32)

        return advantages + values, advantages

    @tf.function
    def _update_actor(self, states, actions, advantages, old_log_probs):
        with tf.GradientTape() as tape:
            action_probs = self.actor(states)

            indices = tf.stack([tf.range(len(actions)), actions], axis=1)
            new_log_probs = tf.nn.log_softmax(tf.math.log(action_probs + 1e-8))
            new_log_probs = tf.gather_nd(new_log_probs, indices)

            ratio = tf.exp(new_log_probs - old_log_probs)
            clipped_ratio = tf.clip_by_value(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)

            policy_loss = -tf.reduce_mean(
                tf.minimum(ratio * advantages, clipped_ratio * advantages)
            )

            entropy = -tf.reduce_mean(tf.reduce_sum(
                action_probs * tf.nn.log_softmax(tf.math.log(action_probs + 1e-8)),
                axis=1
            ))

            total_loss = policy_loss - 0.01 * entropy

        grads = tape.gradient(total_loss, self.actor.trainable_variables)
        self.optimizer_actor.apply_gradients(zip(grads, self.actor.trainable_variables))

    @tf.function
    def _update_critic(self, states, returns):
        with tf.GradientTape() as tape:
            values = tf.squeeze(self.critic(states))
            value_loss = tf.reduce_mean(tf.square(returns - values))

        grads = tape.gradient(value_loss, self.critic.trainable_variables)
        self.optimizer_critic.apply_gradients(zip(grads, self.critic.trainable_variables))

    def update(self):
        if len(self.states) == 0:
            return

        states = tf.convert_to_tensor(self.states, dtype=tf.float32)
        actions = tf.convert_to_tensor(self.actions, dtype=tf.int32)
        rewards = tf.convert_to_tensor(self.rewards, dtype=tf.float32)
        values = tf.convert_to_tensor(self.values, dtype=tf.float32)
        old_log_probs = tf.convert_to_tensor(self.log_probs, dtype=tf.float32)

        returns, advantages = self.compute_gae(rewards, values)

        advantages = (advantages - tf.reduce_mean(advantages)) / (tf.math.reduce_std(advantages) + 1e-8)

        for _ in range(self.epochs):
            self._update_actor(states, actions, advantages, old_log_probs)
            self._update_critic(states, returns)

        self.clear_buffer()

    def clear_buffer(self):
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.values.clear()
        self.log_probs.clear()