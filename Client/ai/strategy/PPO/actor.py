##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## actor
##

import tensorflow as tf
from tensorflow.keras import layers, models

class actor(tf.keras.Model):
  def __init__(self, action_dim):
    super().__init__()
    self.model = models.Sequential([
      layers.Dense(64, activation='relu'),
      layers.BatchNormalization(),
      layers.Dense(32, activation='relu'),
      layers.Dense(action_dim, activation='softmax')
    ])

  def call(self, input_data):
    return self.model(input_data)
