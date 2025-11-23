"""
Enhanced screen shake with multiple simultaneous effects and trauma system
"""
import random
import math

class ScreenShake:
    """Advanced screen shake with trauma-based system"""
    def __init__(self):
        self.trauma = 0.0  # 0.0 to 1.0
        self.trauma_decay = 1.5  # How fast trauma fades
        self.max_offset = 20  # Maximum pixel offset
        self.max_angle = 2.0  # Maximum rotation in degrees
        self.shake_frequency = 15  # Oscillation speed
        self.time = 0
        
        # Hit-stop effect
        self.hitstop_duration = 0
        self.hitstop_elapsed = 0
        
    def add_trauma(self, amount):
        """Add trauma (0.0 to 1.0)"""
        self.trauma = min(1.0, self.trauma + amount)
        
    def shake(self, intensity=0.5, duration=None):
        """Trigger screen shake"""
        self.add_trauma(intensity)
        
    def hitstop(self, duration=50):
        """Freeze frame effect on impact"""
        self.hitstop_duration = duration
        self.hitstop_elapsed = 0
        
    def update(self, dt):
        """Update shake effect"""
        # Update hitstop
        if self.hitstop_elapsed < self.hitstop_duration:
            self.hitstop_elapsed += dt
            return dt * 0.1  # Return slowed time
            
        # Decay trauma
        self.trauma = max(0, self.trauma - self.trauma_decay * dt / 1000.0)
        self.time += dt
        
        return dt
        
    def get_offset(self):
        """Get current shake offset using Perlin-like noise"""
        if self.trauma <= 0:
            return 0, 0
            
        # Shake amount based on trauma squared (for smoother falloff)
        shake = self.trauma * self.trauma
        
        # Use sine waves for smooth oscillation
        time_factor = self.time * self.shake_frequency / 1000.0
        
        offset_x = (math.sin(time_factor * 2.1) + 
                   math.sin(time_factor * 3.7)) * self.max_offset * shake
        offset_y = (math.cos(time_factor * 1.9) + 
                   math.cos(time_factor * 4.3)) * self.max_offset * shake
        
        # Add some randomness for chaos
        offset_x += random.uniform(-1, 1) * self.max_offset * shake * 0.3
        offset_y += random.uniform(-1, 1) * self.max_offset * shake * 0.3
        
        return offset_x, offset_y
        
    def get_rotation(self):
        """Get camera rotation for shake"""
        if self.trauma <= 0:
            return 0
            
        shake = self.trauma * self.trauma
        time_factor = self.time * self.shake_frequency / 1000.0
        
        angle = math.sin(time_factor * 5.3) * self.max_angle * shake
        return angle
        
    def reset(self):
        """Reset shake"""
        self.trauma = 0
        self.hitstop_duration = 0
        self.hitstop_elapsed = 0
        self.time = 0
        
    def is_active(self):
        """Check if shake is active"""
        return self.trauma > 0.01

class CameraController:
    """Camera controller with zoom and follow"""
    def __init__(self, screen_width, screen_height):
        self.pos = pygame.math.Vector2(screen_width // 2, screen_height // 2)
        self.target = pygame.math.Vector2(screen_width // 2, screen_height // 2)
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.smoothness = 0.1
        
    def follow(self, target_x, target_y, dt):
        """Smoothly follow a target"""
        self.target.x = target_x
        self.target.y = target_y
        
        # Smooth lerp
        self.pos.x += (self.target.x - self.pos.x) * self.smoothness * dt / 16.67
        self.pos.y += (self.target.y - self.pos.y) * self.smoothness * dt / 16.67
        
    def set_zoom(self, zoom):
        """Set target zoom level"""
        self.target_zoom = zoom
        
    def update(self, dt):
        """Update camera"""
        # Smooth zoom
        self.zoom += (self.target_zoom - self.zoom) * 0.1 * dt / 16.67
        
    def get_transform(self):
        """Get camera transform"""
        return self.pos.x, self.pos.y, self.zoom

import pygame  # Import needed for CameraController