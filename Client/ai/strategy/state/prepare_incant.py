##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## Prepare Incant State - VERSION CORRIGÉE anti-boucle infinie et vérifications strictes
##

import time
from typing import Any, Dict, Optional
from config import Constants
from utils.logger import logger
from Client.ai.strategy.state.fsm import State, Event

class PrepareIncantState(State):
    """État de préparation et gestion d'incantation - VERSION CORRIGÉE avec vérifications strictes."""
    
    def __init__(self, planner):
        super().__init__(planner)
        
        # ✅ Stages de l'incantation avec vérifications strictes
        self.incant_stage = 0  # 0: verify, 1: prepare_resources, 2: final_check, 3: launch
        self.last_broadcast_time = 0.0
        self.incantation_start_time = None
        
        # ✅ TIMEOUTS STRICTS ET COURTS
        self.broadcast_interval = 3.0
        self.max_stage_duration = 15.0    # 15 secondes par stage
        self.max_total_duration = 45.0    # 45 secondes total max
        self.max_attempts = 3             # 3 tentatives max
        
        # ✅ Anti-boucle infinie STRICT
        self.stage_start_time = time.time()
        self.total_attempts = 0
        self.verification_failures = 0
        self.max_verification_failures = 2
        self.last_verification_time = 0.0
        
        # ✅ Conditions strictes
        self.conditions_verified = False
        self.resources_prepared = False

    def on_enter(self):
        logger.info(f"[{self.role}] ⇒ PREPARE_INCANT enter - Niveau {self.state.level}")
        
        # ✅ Vérifications initiales STRICTES avec logs détaillés
        current_food = self._get_real_food_count()
        
        if not self._strict_initial_verification():
            logger.error("[PrepareIncant] ❌ ÉCHEC vérifications initiales STRICTES")
            self._abort_incantation("Initial verification failed")
            return
        
        # Reset état avec compteurs stricts
        self.incant_stage = 0
        self.last_broadcast_time = 0.0
        self.incantation_start_time = time.time()
        self.stage_start_time = time.time()
        self.total_attempts = 0
        self.verification_failures = 0
        self.conditions_verified = False
        self.resources_prepared = False
        
        # ✅ Marquer incantation démarrée dans le state
        self.state.start_incantation()
        
        logger.info(f"[PrepareIncant] ✅ Initialisation STRICTE réussie - Food: {current_food}, Niveau: {self.state.level}")

    def on_event(self, event: Event) -> Optional[State]:
        from ai.strategy.state.emergency import EmergencyState
        from ai.strategy.state.collect_food import CollectFoodState
        from ai.strategy.state.explore import ExploreState
        
        current_food = self._get_real_food_count()
        
        # ✅ Urgences STRICTES - arrêt immédiat
        if event == Event.FOOD_CRITICAL or current_food <= 3:
            logger.error(f"[PrepareIncant] 🆘 URGENCE CRITIQUE - ARRÊT INCANTATION - Food: {current_food}")
            self._abort_incantation("Food critical")
            return EmergencyState(self.planner)
        
        # ✅ Échec ou timeout - abandon immédiat
        if (event in [Event.INCANT_FAILED, Event.NO_RESOURCES_FOUND] or
            self.verification_failures >= self.max_verification_failures or
            self.total_attempts >= self.max_attempts):
            
            reason = f"failures={self.verification_failures}, attempts={self.total_attempts}"
            logger.warning(f"[PrepareIncant] ❌ ABANDON incantation - {reason}")
            self._abort_incantation(reason)
            return ExploreState(self.planner)
            
        return None

    def execute(self) -> Optional[Any]:
        now = time.time()
        current_food = self._get_real_food_count()
        
        # ✅ Timeouts STRICTS avec abandon immédiat
        stage_duration = now - self.stage_start_time
        total_duration = now - self.incantation_start_time if self.incantation_start_time else 0
        
        if total_duration > self.max_total_duration:
            logger.error(f"[PrepareIncant] ⏰ TIMEOUT TOTAL après {total_duration:.1f}s")
            self._abort_incantation(f"Total timeout: {total_duration:.1f}s")
            return None
            
        if stage_duration > self.max_stage_duration:
            logger.warning(f"[PrepareIncant] ⏰ TIMEOUT STAGE {self.incant_stage} après {stage_duration:.1f}s")
            self.verification_failures += 1
            if self.verification_failures >= self.max_verification_failures:
                self._abort_incantation(f"Stage timeout: {stage_duration:.1f}s")
                return None
            # Réessayer le stage
            self._next_stage(force_retry=True)

        self.total_attempts += 1
        
        # ✅ Log de progression avec détails
        if self.total_attempts % 5 == 0:
            logger.info(f"[PrepareIncant] 📊 Progression: Stage={self.incant_stage}, "
                       f"Tentatives={self.total_attempts}/{self.max_attempts}, "
                       f"Échecs={self.verification_failures}/{self.max_verification_failures}, "
                       f"Food={current_food}, Durée={total_duration:.1f}s")

        # ✅ PRIORITÉ: LOOK si nécessaire
        if self.state.needs_look:
            logger.debug("[PrepareIncant] 👁️ LOOK requis")
            return self.cmd_mgr.look()

        # ✅ PRIORITÉ: Inventory si pas synchronisé
        if not getattr(self.state, '_inventory_synchronized', False):
            logger.debug("[PrepareIncant] 🔄 Inventory requis pour synchronisation")
            return self.cmd_mgr.inventory()

        # ✅ Gestion par niveau avec vérifications STRICTES
        if self.state.level == 1:
            return self._handle_level1_incantation_strict()
        else:
            return self._handle_coordinated_incantation_strict(now)

    def _handle_level1_incantation_strict(self):
        """✅ Incantation niveau 1 avec vérifications STRICTES."""
        
        if self.incant_stage == 0:
            # ✅ Vérification STRICTE des conditions
            if self._verify_incantation_conditions_strict():
                logger.info("[PrepareIncant] ✅ Stage 0: Conditions vérifiées niveau 1")
                self.conditions_verified = True
                self.incant_stage = 1
                self._next_stage()
            else:
                self.verification_failures += 1
                if self.verification_failures >= self.max_verification_failures:
                    self._abort_incantation("Conditions verification failed level 1")
                    return None
                else:
                    # Essayer de préparer les ressources
                    self.incant_stage = 1
                    self._next_stage()
        
        elif self.incant_stage == 1:
            # ✅ Préparation ressources si nécessaire
            if not self.resources_prepared:
                requirements = self.state.get_incantation_requirements()
                cmd = self._prepare_resources_strict(requirements)
                if cmd:
                    logger.info("[PrepareIncant] Stage 1: Préparation ressource niveau 1")
                    return cmd
                else:
                    self.resources_prepared = True
                    
            # Passer au stage suivant
            self.incant_stage = 2
            self._next_stage()
            return self.cmd_mgr.look()  # LOOK obligatoire après préparation
        
        elif self.incant_stage == 2:
            # ✅ Vérification finale STRICTE
            if self.state.needs_look:
                return self.cmd_mgr.look()
                
            if self._verify_incantation_conditions_strict():
                logger.info("[PrepareIncant] ✅ Stage 2: Vérification finale OK niveau 1")
                self.incant_stage = 3
                self._next_stage()
            else:
                logger.warning("[PrepareIncant] ❌ Stage 2: Vérification finale ÉCHOUÉE niveau 1")
                self.verification_failures += 1
                if self.verification_failures >= self.max_verification_failures:
                    self._abort_incantation("Final verification failed level 1")
                    return None
                else:
                    # Réessayer préparation
                    self.incant_stage = 1
                    self.resources_prepared = False
                    self._next_stage()
        
        elif self.incant_stage == 3:
            # ✅ LANCEMENT avec dernière vérification
            if self._verify_incantation_conditions_strict():
                logger.info("[PrepareIncant] 🚀 LANCEMENT INCANTATION niveau 1")
                self._cleanup_state()
                return self.cmd_mgr.incantation()
            else:
                logger.error("[PrepareIncant] ❌ LANCEMENT IMPOSSIBLE - conditions non remplies niveau 1")
                self._abort_incantation("Launch verification failed level 1")
                return None

        return None

    def _handle_coordinated_incantation_strict(self, now: float):
        """✅ Incantation coordonnée avec vérifications STRICTES."""
        
        if self.incant_stage == 0:
            # Vérifications initiales
            if not self._verify_incantation_conditions_strict():
                self.verification_failures += 1
                if self.verification_failures >= self.max_verification_failures:
                    self._abort_incantation("Initial conditions failed coordinated")
                    return None
            
            # Envoyer requête aide
            self.coordination.send_incant_request()
            self.last_broadcast_time = now
            self.incant_stage = 1
            self._next_stage()
            logger.info(f"[PrepareIncant] Stage 0→1: Requête aide envoyée niveau {self.state.level}")
            return None
        
        elif self.incant_stage == 1:
            # Attendre helpers (temps TRÈS réduit)
            wait_time = now - self.incantation_start_time if self.incantation_start_time else 0
            
            # Broadcasts périodiques
            if now - self.last_broadcast_time >= self.broadcast_interval:
                self.coordination.send_incant_request()
                self.last_broadcast_time = now
                logger.debug(f"[PrepareIncant] Broadcast aide niveau {self.state.level}")
            
            # Continuer après timeout court OU si assez de helpers
            if (wait_time >= 8.0 or  # ✅ Timeout très court
                self.coordination.has_enough_helpers()):
                
                helpers_count = len(self.coordination.get_helpers_here())
                required_count = self.state.get_required_player_count()
                
                logger.info(f"[PrepareIncant] Stage 1→2: Helpers: {helpers_count}/{required_count}, "
                           f"Attente: {wait_time:.1f}s")
                
                self.incant_stage = 2
                self._next_stage()
        
        elif self.incant_stage == 2:
            # Préparation ressources
            if not self.resources_prepared:
                requirements = self.state.get_incantation_requirements()
                cmd = self._prepare_resources_strict(requirements)
                if cmd:
                    logger.info(f"[PrepareIncant] Stage 2: Préparation ressource niveau {self.state.level}")
                    return cmd
                else:
                    self.resources_prepared = True
                    
            # LOOK obligatoire après préparation
            self.incant_stage = 3
            self._next_stage()
            return self.cmd_mgr.look()
        
        elif self.incant_stage == 3:
            # Vérification finale et lancement
            if self.state.needs_look:
                return self.cmd_mgr.look()
            
            if self._verify_incantation_conditions_strict():
                logger.info(f"[PrepareIncant] 🚀 LANCEMENT INCANTATION niveau {self.state.level}")
                self._cleanup_state()
                return self.cmd_mgr.incantation()
            else:
                logger.error(f"[PrepareIncant] ❌ LANCEMENT IMPOSSIBLE niveau {self.state.level}")
                self._abort_incantation("Final verification failed coordinated")
                return None

        return None

    def _prepare_resources_strict(self, requirements: Dict[str, int]) -> Optional[Any]:
        """✅ Préparation ressources avec vérifications STRICTES."""
        try:
            ground_resources = self.state._get_resources_at_current_position()
            
            for resource, needed_qty in requirements.items():
                current_ground = ground_resources.get(resource, 0)
                current_inventory = self.state.inventory.get(resource, 0)
                
                # Besoin de déposer cette ressource
                if current_ground < needed_qty and current_inventory > 0:
                    to_set = min(current_inventory, needed_qty - current_ground)
                    
                    logger.info(f"[PrepareIncant] 📤 SET {resource} x{to_set} - "
                               f"Sol:{current_ground}/{needed_qty}, Inv:{current_inventory}")
                    
                    self.state.on_set_command(resource)
                    return self.cmd_mgr.set(resource)
            
            return None
            
        except Exception as e:
            logger.error(f"[PrepareIncant] Erreur prepare resources: {e}")
            return None

    def _verify_incantation_conditions_strict(self) -> bool:
        """✅ Vérification TRÈS STRICTE des conditions d'incantation."""
        try:
            current_food = self._get_real_food_count()
            level = self.state.level
            required_players = self.state.get_required_player_count()
            requirements = self.state.get_incantation_requirements()
            
            # ✅ Log détaillé des vérifications
            logger.debug(f"[PrepareIncant] 🔍 Vérification conditions niveau {level}:")
            
            # ✅ Vérification nourriture STRICTE
            min_food = self.state.food_thresholds['incant_min']
            if current_food < min_food:
                logger.warning(f"  ❌ Nourriture: {current_food} < {min_food}")
                return False
            else:
                logger.debug(f"  ✅ Nourriture: {current_food} >= {min_food}")
            
            # ✅ Vérification joueurs STRICTE
            players_here = self.state._players_on_current_tile()
            if level > 1 and players_here < required_players:
                logger.warning(f"  ❌ Joueurs: {players_here} < {required_players}")
                return False
            else:
                logger.debug(f"  ✅ Joueurs: {players_here} >= {required_players}")
            
            # ✅ Vérification ressources STRICTE
            ground_resources = self.state._get_resources_at_current_position()
            missing_resources = []
            
            for resource, needed in requirements.items():
                ground_count = ground_resources.get(resource, 0)
                if ground_count < needed:
                    missing_resources.append(f"{resource}:{ground_count}/{needed}")
            
            if missing_resources:
                logger.warning(f"  ❌ Ressources manquantes: {', '.join(missing_resources)}")
                return False
            else:
                logger.debug(f"  ✅ Ressources: toutes présentes")
            
            logger.info(f"[PrepareIncant] ✅ TOUTES CONDITIONS VÉRIFIÉES niveau {level}")
            return True
            
        except Exception as e:
            logger.error(f"[PrepareIncant] Erreur verify conditions: {e}")
            return False

    def _strict_initial_verification(self) -> bool:
        """✅ Vérification initiale TRÈS STRICTE."""
        current_food = self._get_real_food_count()
        
        # Vérifications de base
        if self.state.level >= 8:
            logger.warning("[PrepareIncant] Niveau maximum déjà atteint")
            return False
        
        min_food = self.state.food_thresholds['incant_min']
        if current_food < min_food:
            logger.warning(f"[PrepareIncant] Nourriture insuffisante: {current_food} < {min_food}")
            return False
        
        # Vérifier que l'agent peut vraiment incanter
        if not self.state.can_incant():
            logger.warning("[PrepareIncant] state.can_incant() retourne False")
            return False
        
        # Vérifier l'inventaire synchronisé
        if not getattr(self.state, '_inventory_synchronized', False):
            logger.warning("[PrepareIncant] Inventaire pas synchronisé")
            return False
        
        logger.info(f"[PrepareIncant] ✅ Vérifications initiales STRICTES OK")
        return True

    def _next_stage(self, force_retry: bool = False):
        """✅ Passe au stage suivant avec reset timer."""
        if not force_retry:
            self.incant_stage = min(3, self.incant_stage)  # Limiter à 3
        
        self.stage_start_time = time.time()
        logger.debug(f"[PrepareIncant] Stage {self.incant_stage} démarré")

    def _abort_incantation(self, reason: str):
        """✅ Abandon incantation avec nettoyage complet."""
        duration = time.time() - self.incantation_start_time if self.incantation_start_time else 0
        
        logger.error(f"[PrepareIncant] 🛑 ABANDON INCANTATION - {reason} (durée: {duration:.1f}s)")
        
        # Nettoyer état
        self._cleanup_state()
        
        # Marquer incantation terminée (échec)
        self.state.complete_incantation(False)

    def _cleanup_state(self):
        """✅ Nettoyage complet de l'état."""
        self.incant_stage = 0
        self.incantation_start_time = None
        self.verification_failures = 0
        self.conditions_verified = False
        self.resources_prepared = False
        
        # Nettoyer helpers
        if hasattr(self.coordination, 'clear_helpers'):
            self.coordination.clear_helpers()
            
        logger.debug("[PrepareIncant] État nettoyé")

    def _get_real_food_count(self) -> int:
        """Obtient le compte réel de nourriture."""
        try:
            if hasattr(self.state, 'inventory') and 'food' in self.state.inventory:
                return self.state.inventory['food']
            elif hasattr(self.state, 'get_food_count'):
                return self.state.get_food_count()
            else:
                return 0
        except Exception as e:
            logger.error(f"[PrepareIncant] Erreur food count: {e}")
            return 0