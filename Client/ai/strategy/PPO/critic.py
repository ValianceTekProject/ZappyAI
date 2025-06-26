##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## critic
##

import tensorflow as tf
from tensorflow.keras import layers, models

class critic(tf.keras.Model):
  def __init__(self):
    super().__init__()
    self.model = models.Sequential([
      layers.Dense(64, activation='relu'),
      layers.Dropout(0.2),
      layers.Dense(32, activation='relu'),
      layers.Dense(1)
    ])

  def call(self, input_data):
    return self.model(input_data)
