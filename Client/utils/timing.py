##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## timing - VERSION DÉFINITIVE sans dépendance fréquence
##

import time
from utils.logger import logger
from config import CommandType

class TimingManager:
    def __init__(self):
        self.last_action_time = 0.0
        self.last_food_observation = time.time()
        self.food_consumption_observed = False
        
        # ✅ TIMING PLUS RÉACTIF pour la survie
        self.min_command_interval = 0.05  # 50ms au lieu de 100ms
        
        # ✅ Mode urgence avec timing encore plus rapide
        self.emergency_mode = False
        self.emergency_interval = 0.02  # 20ms en urgence
        
        self.food_observation_history = []
        self.last_food_level = 0
        
        logger.debug(f"[TimingManager] Timing réactif: normal={self.min_command_interval}s, urgence={self.emergency_interval}s")


    def can_execute_action(self) -> bool:
        """
        Vérifie si on peut envoyer une action.
        Basé sur un interval minimum fixe.
        """
        return time.time() >= self.last_action_time + self.min_command_interval

    def register_action(self, cmd_type: CommandType) -> None:
        """
        Enregistre une action envoyée.
        """
        self.last_action_time = time.time()

    def set_emergency_mode(self, is_emergency: bool):
        """Active/désactive le mode urgence."""
        if is_emergency != self.emergency_mode:
            self.emergency_mode = is_emergency
            interval = self.emergency_interval if is_emergency else self.min_command_interval
            logger.info(f"[TimingManager] Mode urgence: {is_emergency}, interval: {interval}s")

    def can_execute_action(self) -> bool:
        """Vérifie si on peut envoyer une action avec timing adaptatif."""
        interval = self.emergency_interval if self.emergency_mode else self.min_command_interval
        return time.time() >= self.last_action_time + interval

    def get_sleep_time(self) -> float:
        """Retourne le temps d'attente avec timing adaptatif."""
        interval = self.emergency_interval if self.emergency_mode else self.min_command_interval
        next_available = self.last_action_time + interval
        return max(0.0, next_available - time.time())

    def observe_food_change(self, old_food: int, new_food: int) -> None:
        """
        Observe un changement de nourriture et met à jour les statistiques.
        """
        now = time.time()
        
        if new_food != old_food:
            self.food_observation_history.append({
                'time': now,
                'old': old_food,
                'new': new_food,
                'change': new_food - old_food
            })
            
            # Garder seulement les 10 dernières observations
            if len(self.food_observation_history) > 10:
                self.food_observation_history.pop(0)
            
            if new_food < old_food:
                self.food_consumption_observed = True
                self.last_food_observation = now
                consumed = old_food - new_food
                logger.debug(f"[TimingManager] Consommation observée: -{consumed} nourriture")
            elif new_food > old_food:
                gained = new_food - old_food
                logger.debug(f"[TimingManager] Gain observé: +{gained} nourriture")
        
        self.last_food_level = new_food

    def should_check_inventory(self) -> bool:
        """
        Détermine si on devrait faire un inventory pour vérifier la nourriture.
        Basé sur le temps écoulé et les observations.
        """
        time_since_last = time.time() - self.last_food_observation
        
        # Fréquence adaptative selon les observations récentes
        if self.food_consumption_observed and time_since_last < 60:
            return time_since_last > 8.0  # Vérifier plus souvent si consommation récente
        elif time_since_last < 120:
            return time_since_last > 20.0  # Fréquence normale
        else:
            return time_since_last > 40.0  # Moins fréquent si pas de changements

    def get_estimated_consumption_rate(self) -> float:
        """
        Estime le taux de consommation basé sur les observations.
        Retourne le nombre de secondes entre les consommations de nourriture.
        """
        if len(self.food_observation_history) < 2:
            return 120.0  # Estimation par défaut si pas assez de données
        
        # Calculer les intervalles entre consommations
        consumption_intervals = []
        for i in range(1, len(self.food_observation_history)):
            prev = self.food_observation_history[i-1]
            curr = self.food_observation_history[i]
            
            # Si c'est une consommation (diminution)
            if curr['change'] < 0 and prev['change'] < 0:
                interval = curr['time'] - prev['time']
                if 10 < interval < 300:  # Ignorer les valeurs aberrantes
                    consumption_intervals.append(interval)
        
        if consumption_intervals:
            avg_interval = sum(consumption_intervals) / len(consumption_intervals)
            logger.debug(f"[TimingManager] Taux consommation estimé: {avg_interval:.1f}s")
            return avg_interval
        
        return 120.0  # Fallback

    def estimate_food_needed_for_duration(self, duration_seconds: float) -> int:
        """
        Estime la nourriture nécessaire pour une durée donnée.
        Basé sur les observations réelles, pas sur des calculs théoriques.
        """
        consumption_rate = self.get_estimated_consumption_rate()
        estimated_consumption = max(1, int(duration_seconds / consumption_rate))
        
        # Ajouter une marge de sécurité
        safety_margin = max(2, estimated_consumption // 4)
        total_needed = estimated_consumption + safety_margin
        
        logger.debug(f"[TimingManager] Nourriture estimée pour {duration_seconds}s: {total_needed}")
        return total_needed

    def reset_food_timer(self) -> None:
        """Reset le timer de nourriture."""
        self.last_food_observation = time.time()
        self.food_consumption_observed = False
        logger.debug("[TimingManager] Timer nourriture reset")

    def has_lost_food(self) -> bool:
        """
        Vérifie si on a perdu de la nourriture récemment.
        """
        return (self.food_consumption_observed and 
                time.time() - self.last_food_observation < 5.0)

    def get_food_status_info(self) -> dict:
        """Retourne des informations sur le statut de la nourriture."""
        current_time = time.time()
        time_since_observation = current_time - self.last_food_observation
        
        return {
            'time_since_last_observation': time_since_observation,
            'food_consumption_observed': self.food_consumption_observed,
            'should_check_inventory': self.should_check_inventory(),
            'estimated_consumption_rate': self.get_estimated_consumption_rate(),
            'recent_observations': len(self.food_observation_history),
            'has_lost_food_recently': self.has_lost_food()
        }