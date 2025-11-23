"""
Enhanced particle system with object pooling and advanced effects
"""
import pygame
import random
import math
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Particle:
    """Individual particle with enhanced properties"""
    def __init__(self):
        self.reset()
        
    def reset(self):
        """Reset particle to default state"""
        self.pos = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.color = (255, 255, 255)
        self.lifetime = 1000
        self.age = 0
        self.radius = 3
        self.gravity = 0
        self.fade_speed = 1.0
        self.scale_speed = 1.0
        self.rotation = 0
        self.rotation_speed = 0
        self.active = False
        
    def init(self, x, y, color, velocity, lifetime=1000, radius=3, 
             gravity=0, rotation_speed=0):
        """Initialize particle with values"""
        self.pos.x = x
        self.pos.y = y
        self.velocity = velocity
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.radius = radius
        self.gravity = gravity
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = rotation_speed
        self.active = True
        
    def update(self, dt):
        """Update particle"""
        if not self.active:
            return False
            
        self.age += dt
        
        # Update position
        dt_sec = dt / 1000.0
        self.pos += self.velocity * dt_sec
        
        # Apply gravity
        self.velocity.y += self.gravity * dt_sec
        
        # Apply air resistance
        self.velocity *= 0.98
        
        # Update rotation
        self.rotation += self.rotation_speed * dt_sec
        
        # Check if particle should die
        if self.age >= self.lifetime:
            self.active = False
            return False
            
        # Cull off-screen particles
        if (self.pos.x < -50 or self.pos.x > SCREEN_WIDTH + 50 or
            self.pos.y < -50 or self.pos.y > SCREEN_HEIGHT + 50):
            self.active = False
            return False
            
        return True
        
    def render(self, screen, offset_x=0, offset_y=0):
        """Draw particle with fade"""
        if not self.active:
            return
            
        # Calculate alpha based on age
        alpha = int(255 * (1 - self.age / self.lifetime))
        alpha = max(0, min(255, alpha))
        
        # Calculate current radius (can shrink over time)
        current_radius = int(self.radius * (1 - (self.age / self.lifetime) * 0.5))
        current_radius = max(1, current_radius)
        
        x = int(self.pos.x + offset_x)
        y = int(self.pos.y + offset_y)
        
        # Create surface with alpha
        if alpha > 0:
            # Draw glow effect
            glow_radius = current_radius + 2
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, alpha // 3), 
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (x - glow_radius, y - glow_radius))
            
            # Draw main particle
            pygame.draw.circle(screen, (*self.color, alpha), (x, y), current_radius)

class ParticleEmitter:
    """Particle emitter with specific behavior"""
    def __init__(self, x, y, particle_system):
        self.pos = pygame.math.Vector2(x, y)
        self.particle_system = particle_system
        self.active = True
        self.emit_rate = 10  # particles per second
        self.accumulator = 0
        
    def update(self, dt):
        """Update emitter"""
        if not self.active:
            return
            
        self.accumulator += dt
        particles_to_emit = int(self.accumulator * self.emit_rate / 1000)
        
        if particles_to_emit > 0:
            self.particle_system.emit(
                self.pos.x, self.pos.y,
                (255, 200, 100),
                count=particles_to_emit,
                speed=50
            )
            self.accumulator = 0

class ParticleSystem:
    """Enhanced particle system with object pooling"""
    def __init__(self, pool_size=500):
        self.particles = [Particle() for _ in range(pool_size)]
        self.active_count = 0
        
    def emit(self, x, y, color, count=10, speed=100, lifetime=1000, 
             gravity=0, spread=360, direction=None):
        """Emit particles with various parameters"""
        for _ in range(count):
            # Find inactive particle
            particle = self._get_inactive_particle()
            if not particle:
                break
                
            # Calculate velocity
            if direction is not None:
                angle = direction + random.uniform(-spread/2, spread/2)
            else:
                angle = random.uniform(0, 360)
                
            vel_magnitude = random.uniform(speed * 0.5, speed * 1.5)
            vel_x = math.cos(math.radians(angle)) * vel_magnitude
            vel_y = math.sin(math.radians(angle)) * vel_magnitude
            velocity = pygame.math.Vector2(vel_x, vel_y)
            
            # Initialize particle
            radius = random.randint(2, 5)
            rotation_speed = random.uniform(-360, 360)
            particle.init(x, y, color, velocity, lifetime, radius, 
                         gravity, rotation_speed)
            
    def emit_explosion(self, x, y, color, intensity=30):
        """Emit explosion-style particles"""
        self.emit(x, y, color, count=intensity, speed=200, lifetime=800, gravity=100)
        
    def emit_trail(self, x, y, color, velocity_x, velocity_y):
        """Emit trail particles behind moving objects"""
        # Emit in opposite direction of movement
        angle = math.degrees(math.atan2(-velocity_y, -velocity_x))
        self.emit(x, y, color, count=2, speed=50, lifetime=500, 
                 spread=30, direction=angle)
        
    def emit_sparkle(self, x, y, color):
        """Emit sparkle effect"""
        self.emit(x, y, color, count=5, speed=150, lifetime=600, gravity=-50)
        
    def _get_inactive_particle(self):
        """Get an inactive particle from pool"""
        for particle in self.particles:
            if not particle.active:
                return particle
        return None
        
    def update(self, dt):
        """Update all active particles"""
        self.active_count = 0
        for particle in self.particles:
            if particle.active:
                particle.update(dt)
                if particle.active:
                    self.active_count += 1
        
    def render(self, screen, offset_x=0, offset_y=0):
        """Draw all active particles"""
        for particle in self.particles:
            if particle.active:
                particle.render(screen, offset_x, offset_y)
            
    def clear(self):
        """Clear all particles"""
        for particle in self.particles:
            particle.active = False
        self.active_count = 0
        
    def get_active_count(self):
        """Get number of active particles"""
        return self.active_count