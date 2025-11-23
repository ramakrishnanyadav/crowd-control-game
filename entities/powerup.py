"""
Power-up and special abilities system
"""
import pygame
import random
import math

class PowerUpType:
    """Power-up types enumeration"""
    SPEED_BOOST = 'speed'
    SHIELD = 'shield'
    SIZE_UP = 'size_up'
    SIZE_DOWN = 'size_down'
    TRIPLE_DASH = 'triple_dash'
    TELEPORT = 'teleport'
    FREEZE = 'freeze'
    MAGNET = 'magnet'

class PowerUp:
    """Power-up pickup entity"""
    def __init__(self, x, y, powerup_type):
        self.pos = pygame.math.Vector2(x, y)
        self.type = powerup_type
        self.radius = 15
        self.active = True
        self.lifetime = 15000  # 15 seconds
        self.age = 0
        self.float_offset = 0
        self.rotation = 0
        
        # Visual properties
        self.colors = {
            PowerUpType.SPEED_BOOST: (255, 200, 0),
            PowerUpType.SHIELD: (100, 200, 255),
            PowerUpType.SIZE_UP: (255, 100, 100),
            PowerUpType.SIZE_DOWN: (100, 255, 100),
            PowerUpType.TRIPLE_DASH: (200, 100, 255),
            PowerUpType.TELEPORT: (255, 100, 255),
            PowerUpType.FREEZE: (100, 200, 200),
            PowerUpType.MAGNET: (255, 150, 50)
        }
        
        self.color = self.colors.get(powerup_type, (255, 255, 255))
        
    def update(self, dt):
        """Update power-up"""
        if not self.active:
            return False
            
        self.age += dt
        self.rotation += dt * 0.2
        self.float_offset = math.sin(self.age * 0.005) * 10
        
        # Despawn after lifetime
        if self.age >= self.lifetime:
            self.active = False
            return False
            
        return True
        
    def check_pickup(self, player):
        """Check if player picked up this power-up"""
        if not self.active:
            return False
            
        distance = (player.pos - self.pos).length()
        return distance < (self.radius + player.radius)
        
    def render(self, screen, offset_x=0, offset_y=0):
        """Render power-up"""
        if not self.active:
            return
            
        x = int(self.pos.x + offset_x)
        y = int(self.pos.y + offset_y + self.float_offset)
        
        # Pulsing warning when about to despawn
        alpha = 255
        if self.age > self.lifetime - 3000:
            pulse = abs(math.sin(self.age * 0.01))
            alpha = int(100 + pulse * 155)
            
        # Draw outer glow
        glow_radius = self.radius + 5
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, alpha // 3), 
                         (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (x - glow_radius, y - glow_radius))
        
        # Draw main circle with rotating symbol
        pygame.draw.circle(screen, (*self.color, alpha), (x, y), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (x, y), self.radius, 2)
        
        # Draw type indicator
        self._draw_symbol(screen, x, y, alpha)
        
    def _draw_symbol(self, screen, x, y, alpha):
        """Draw power-up type symbol"""
        symbol_color = (255, 255, 255, alpha)
        
        if self.type == PowerUpType.SPEED_BOOST:
            # Lightning bolt
            points = [(x, y-8), (x-3, y), (x+3, y), (x, y+8)]
            pygame.draw.lines(screen, symbol_color[:3], False, points, 2)
            
        elif self.type == PowerUpType.SHIELD:
            # Shield outline
            pygame.draw.circle(screen, symbol_color[:3], (x, y), 6, 2)
            
        elif self.type == PowerUpType.SIZE_UP:
            # Plus sign
            pygame.draw.line(screen, symbol_color[:3], (x-5, y), (x+5, y), 2)
            pygame.draw.line(screen, symbol_color[:3], (x, y-5), (x, y+5), 2)
            
        elif self.type == PowerUpType.SIZE_DOWN:
            # Minus sign
            pygame.draw.line(screen, symbol_color[:3], (x-5, y), (x+5, y), 2)
            
        elif self.type == PowerUpType.TRIPLE_DASH:
            # Three arrows
            for i in range(3):
                offset = (i - 1) * 4
                pygame.draw.line(screen, symbol_color[:3], 
                               (x-3+offset, y), (x+3+offset, y), 2)

class PowerUpEffect:
    """Active power-up effect on player"""
    def __init__(self, powerup_type, duration=5000):
        self.type = powerup_type
        self.duration = duration
        self.elapsed = 0
        self.active = True
        
        # Effect modifiers
        self.speed_multiplier = 1.0
        self.size_multiplier = 1.0
        self.has_shield = False
        self.dash_charges_bonus = 0
        
        # Apply effect
        self._apply_effect()
        
    def _apply_effect(self):
        """Apply power-up effect"""
        if self.type == PowerUpType.SPEED_BOOST:
            self.speed_multiplier = 1.5
        elif self.type == PowerUpType.SIZE_UP:
            self.size_multiplier = 1.5
        elif self.type == PowerUpType.SIZE_DOWN:
            self.size_multiplier = 0.6
        elif self.type == PowerUpType.SHIELD:
            self.has_shield = True
        elif self.type == PowerUpType.TRIPLE_DASH:
            self.dash_charges_bonus = 2
            
    def update(self, dt):
        """Update effect"""
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False
            return False
        return True
        
    def get_remaining_time(self):
        """Get remaining time in seconds"""
        return max(0, (self.duration - self.elapsed) / 1000)

class PowerUpManager:
    """Manages power-up spawning and collection"""
    def __init__(self):
        self.powerups = []
        self.spawn_timer = 0
        self.spawn_interval = 8000  # 8 seconds
        
    def spawn_random(self, platform):
        """Spawn random power-up on platform"""
        # Random position on platform
        angle = random.uniform(0, 360)
        distance = random.uniform(0, platform.radius * 0.7)
        x = platform.center.x + math.cos(math.radians(angle)) * distance
        y = platform.center.y + math.sin(math.radians(angle)) * distance
        
        # Random power-up type
        types = [
            PowerUpType.SPEED_BOOST,
            PowerUpType.SHIELD,
            PowerUpType.SIZE_UP,
            PowerUpType.SIZE_DOWN,
            PowerUpType.TRIPLE_DASH,
        ]
        powerup_type = random.choice(types)
        
        powerup = PowerUp(x, y, powerup_type)
        self.powerups.append(powerup)
        
    def update(self, dt, platform):
        """Update all power-ups and spawn new ones"""
        self.spawn_timer += dt
        
        # Spawn new power-up
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            if len(self.powerups) < 3:  # Max 3 at once
                self.spawn_random(platform)
                
        # Update existing power-ups
        self.powerups = [p for p in self.powerups if p.update(dt)]
        
    def check_pickups(self, player):
        """Check if player picked up any power-ups"""
        for powerup in self.powerups[:]:
            if powerup.check_pickup(player):
                self.powerups.remove(powerup)
                return powerup.type
        return None
        
    def render(self, screen, offset_x=0, offset_y=0):
        """Render all power-ups"""
        for powerup in self.powerups:
            powerup.render(screen, offset_x, offset_y)
            
    def clear(self):
        """Clear all power-ups"""
        self.powerups.clear()