import pickle
import tensorflow as tf
from glob import glob
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.strategy.PPO.ppo import PPO

def load_all_buffers():
    buffer_files = sorted(glob("./models/ppo_buffer_*.pkl"))
    
    if not buffer_files:
        print("No buffer found")
        return None, None, None, None, None
    
    all_states = []
    all_actions = []
    all_rewards = []
    all_values = []
    all_log_probs = []
    
    for file in buffer_files:
        print(f"Loading {file}")
        try:
            with open(file, 'rb') as f:
                data = pickle.load(f)
                all_states.extend(data['states'])
                all_actions.extend(data['actions'])
                all_rewards.extend(data['rewards'])
                all_values.extend(data['values'])
                all_log_probs.extend(data['log_probs'])
        except Exception as e:
            print(f"Error {file}: {e}")
    
    print(f"Total: {len(all_states)} transitions loaded")
    return all_states, all_actions, all_rewards, all_values, all_log_probs

def train_offline():
    states, actions, rewards, values, log_probs = load_all_buffers()
    
    if states is None or len(states) < 100:
        print("Not enought data to train")
        return False
    
    ppo = PPO(state_dim=10, action_dim=6)
    
    dummy_input = tf.zeros((1, 10))
    _ = ppo.actor(dummy_input)
    _ = ppo.critic(dummy_input)

    try:
        ppo.actor.load_weights("ppo_model_actor.weights.h5")
        ppo.critic.load_weights("ppo_model_critic.weights.h5")
        print("Model loaded")
    except:
        print("No model foundm creation of new model")

    print("Start training")
    
    episode_ends = []
    for i, reward in enumerate(rewards):
        if reward <= -50:
            episode_ends.append(i + 1)
    
    if len(states) not in episode_ends:
        episode_ends.append(len(states))
    
    print(f"{len(episode_ends)} Episodes detected")
    
    total_updates = 0
    
    for epoch in range(3):
        print(f"\nEpoch {epoch + 1}/3")
        
        start_idx = 0
        for end_idx in episode_ends:
            if end_idx - start_idx < 10:
                start_idx = end_idx
                continue
            
            ppo.states = states[start_idx:end_idx]
            ppo.actions = actions[start_idx:end_idx]
            ppo.rewards = rewards[start_idx:end_idx]
            ppo.values = values[start_idx:end_idx]
            ppo.log_probs = log_probs[start_idx:end_idx]
            
            if len(ppo.states) >= 32:
                try:
                    ppo.update()
                    total_updates += 1
                    
                    if total_updates % 10 == 0:
                        print(f"{total_updates} updates")
                except Exception as e:
                    print(f"Update Error: {e}")
            
            start_idx = end_idx

    try:
        ppo.actor.save_weights("ppo_model_actor.weights.h5")
        ppo.critic.save_weights("ppo_model_critic.weights.h5")

        os.makedirs("models", exist_ok=True)
        ppo.actor.save_weights("models/ppo_model_actor.weights.h5")
        ppo.critic.save_weights("models/ppo_model_critic.weights.h5")

        print("Model Saved")
        print("Files in", os.getcwd())
        print(f"\nStats")
        print(f"   - Transitions: {len(states)}")
        print(f"   - Episodes: {len(episode_ends)}")
        print(f"   - Updates: {total_updates}")
        
        return True
        
    except Exception as e:
        print(f"save Error: {e}")
        return False

if __name__ == "__main__":
    success = train_offline()
    if success:
        exit (0)
    else:
        exit (1)
