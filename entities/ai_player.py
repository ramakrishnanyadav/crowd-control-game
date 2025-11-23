"""
AI Player with difficulty levels and strategic behavior
"""
import pygame
import random
import math
from entities.player import Player

class AIState:
    """AI behavior states"""
    AGGRESSIVE = 'aggressive'
    DEFENSIVE = 'defensive'
    OPPORTUNISTIC = 'opportunistic'
    SURVIVAL = 'survival'

class AIPlayer(Player):
    """AI-controlled player"""
    def __init__(self, x, y, color, player_id, controls, difficulty='medium'):
        super().__init__(x, y, color, player_id, controls)
        
        self.is_ai = True
        self.difficulty = difficulty
        self.state = AIState.OPPORTUNISTIC
        
        # AI parameters based on difficulty
        self.reaction_time = self._get_reaction_time()
        self.aim_accuracy = self._get_aim_accuracy()
        self.decision_delay = 0
        self.next_decision = 0
        
        # Tactical awareness
        self.target_player = None
        self.danger_threshold = 0.3
        self.last_position = pygame.math.Vector2(x, y)
        
    def _get_reaction_time(self):
        """Get reaction time based on difficulty"""
        times = {
            'easy': 500,
            'medium': 250,
            'hard': 100,
            'expert': 50
        }
        return times.get(self.difficulty, 250)
        
    def _get_aim_accuracy(self):
        """Get aim accuracy (0-1) based on difficulty"""
        accuracy = {
            'easy': 0.6,
            'medium': 0.8,
            'hard': 0.95,
            'expert': 0.99
        }
        return accuracy.get(self.difficulty, 0.8)
        
    def update(self, dt, players, platform):
        """Update AI logic"""
        if not self.alive:
            return
            
        # Update decision timer
        self.decision_delay += dt
        
        # Make decisions at intervals (reaction time)
        if self.decision_delay >= self.reaction_time:
            self.decision_delay = 0
            self._make_decision(players, platform)
            
        # Execute current decision
        self._execute_action(dt)
        
        # Update base player physics
        super().update(dt)
        
        self.last_position = self.pos.copy()
        
    def _make_decision(self, players, platform):
        """Main AI decision-making"""
        # Assess situation
        self._assess_state(players, platform)
        
        # Choose action based on state
        if self.state == AIState.SURVIVAL:
            self._plan_survival(platform)
        elif self.state == AIState.AGGRESSIVE:
            self._plan_attack(players)
        elif self.state == AIState.DEFENSIVE:
            self._plan_defense(players, platform)
        else:  # OPPORTUNISTIC
            self._plan_opportunistic(players, platform)
            
    def _assess_state(self, players, platform):
        """Assess current situation and choose state"""
        # Check distance to platform edge
        distance_to_edge = platform.radius - (self.pos - platform.center).length()
        health_ratio = distance_to_edge / platform.radius
        
        # Count nearby threats
        threats = 0
        for player in players:
            if player != self and player.alive:
                dist = (player.pos - self.pos).length()
                if dist < 150:
                    threats += 1
                    
        # Decide state
        if health_ratio < self.danger_threshold:
            self.state = AIState.SURVIVAL
        elif threats >= 2:
            self.state = AIState.DEFENSIVE
        elif threats == 1:
            self.state = AIState.AGGRESSIVE
        else:
            self.state = AIState.OPPORTUNISTIC
            
    def _plan_survival(self, platform):
        """Plan survival strategy - move to center"""
        # Target platform center
        to_center = platform.center - self.pos
        distance = to_center.length()
        
        if distance > 10:
            direction = to_center.normalize()
            
            # Add some randomness based on difficulty
            noise = (1 - self.aim_accuracy) * 50
            direction.x += random.uniform(-noise, noise)
            direction.y += random.uniform(-noise, noise)
            
            if distance > 0:
                direction = direction.normalize()
            
            self.target_direction = direction
            self.should_dash = distance > 100 and self.dash_charges > 0
        else:
            self.target_direction = pygame.math.Vector2(0, 0)
            self.should_dash = False
            
    def _plan_attack(self, players):
        """Plan aggressive strategy - chase nearest enemy"""
        # Find nearest enemy
        nearest = None
        min_dist = float('inf')
        
        for player in players:
            if player != self and player.alive:
                dist = (player.pos - self.pos).length()
                if dist < min_dist:
                    min_dist = dist
                    nearest = player
                    
        if nearest:
            self.target_player = nearest
            
            # Predict enemy position
            prediction = self._predict_position(nearest)
            
            # Move towards predicted position
            to_target = prediction - self.pos
            distance = to_target.length()
            
            if distance > 10:
                direction = to_target.normalize()
                
                # Add inaccuracy
                noise = (1 - self.aim_accuracy) * 30
                direction.x += random.uniform(-noise, noise)
                direction.y += random.uniform(-noise, noise)
                
                if distance > 0:
                    direction = direction.normalize()
                
                self.target_direction = direction
                
                # Dash to catch up
                self.should_dash = (distance > 80 and distance < 200 and 
                                  self.dash_charges > 0)
            else:
                self.target_direction = pygame.math.Vector2(0, 0)
                self.should_dash = False
                
    def _plan_defense(self, players, platform):
        """Plan defensive strategy - maintain distance"""
        # Find center of mass of threats
        threat_center = pygame.math.Vector2(0, 0)
        threat_count = 0
        
        for player in players:
            if player != self and player.alive:
                dist = (player.pos - self.pos).length()
                if dist < 200:
                    threat_center += player.pos
                    threat_count += 1
                    
        if threat_count > 0:
            threat_center /= threat_count
            
            # Move away from threats but stay on platform
            away_from_threats = self.pos - threat_center
            to_center = platform.center - self.pos
            
            # Balance between staying on platform and avoiding threats
            safe_direction = (away_from_threats * 0.6 + to_center.normalize() * 0.4)
            
            if safe_direction.length() > 0:
                safe_direction = safe_direction.normalize()
                
            self.target_direction = safe_direction
            self.should_dash = self.dash_charges > 1  # Keep one charge for escape
        else:
            self._plan_opportunistic(players, platform)
            
    def _plan_opportunistic(self, players, platform):
        """Plan opportunistic strategy - position strategically"""
        # Move to tactical position
        # Stay near center but watch for opportunities
        
        to_center = platform.center - self.pos
        distance_from_center = to_center.length()
        
        # Ideal position: 30% from center
        ideal_distance = platform.radius * 0.3
        
        if distance_from_center > ideal_distance + 20:
            # Move toward center
            direction = to_center.normalize()
            self.target_direction = direction
            self.should_dash = False
        elif distance_from_center < ideal_distance - 20:
            # Move away from center slightly
            direction = -to_center.normalize()
            self.target_direction = direction
            self.should_dash = False
        else:
            # Patrol/circle
            tangent = pygame.math.Vector2(-to_center.y, to_center.x).normalize()
            self.target_direction = tangent
            self.should_dash = False
            
    def _predict_position(self, player):
        """Predict future position of player"""
        if not hasattr(player, 'vel'):
            return player.pos
            
        # Predict 300ms ahead
        prediction_time = 0.3
        predicted = player.pos + player.vel * prediction_time
        
        return predicted
        
    def _execute_action(self, dt):
        """Execute planned action using fake keyboard input"""
        if not hasattr(self, 'target_direction'):
            return
            
        # Simulate key presses
        keys_state = {}
        
        # Movement
        if self.target_direction.length() > 0.1:
            if self.target_direction.x > 0.3:
                keys_state[self.controls['right']] = True
            elif self.target_direction.x < -0.3:
                keys_state[self.controls['left']] = True
                
            if self.target_direction.y > 0.3:
                keys_state[self.controls['down']] = True
            elif self.target_direction.y < -0.3:
                keys_state[self.controls['up']] = True
                
        # Dash
        if hasattr(self, 'should_dash') and self.should_dash:
            keys_state[self.controls['dash']] = True
            
        # Override pygame.key.get_pressed for this AI
        self._fake_keys = keys_state
        
    def get_keys(self):
        """Get simulated key state"""
        return getattr(self, '_fake_keys', {})

class AIManager:
    """Manages AI players"""
    def __init__(self):
        self.ai_players = []
        
    def add_ai(self, player):
        """Register an AI player"""
        if isinstance(player, AIPlayer):
            self.ai_players.append(player)
            
    def update(self, dt, all_players, platform):
        """Update all AI players"""
        for ai in self.ai_players:
            if ai.alive:
                # Override key reading
                original_get_pressed = pygame.key.get_pressed
                pygame.key.get_pressed = lambda: ai.get_keys()
                
                # Update AI logic
                ai.update(dt, all_players, platform)
                
                # Restore original function
                pygame.key.get_pressed = original_get_pressed