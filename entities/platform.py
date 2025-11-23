"""
Platform entity - the shrinking arena
"""
import pygame
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLATFORM_START_RADIUS,
    PLATFORM_MIN_RADIUS, SHRINK_RATE, COLORS
)
from core.physics import circle_contains_point

class Platform:
    """Shrinking circular platform"""
    def __init__(self):
        self.center = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.radius = PLATFORM_START_RADIUS
        self.min_radius = PLATFORM_MIN_RADIUS
        self.shrinking = False
        
    def update(self, dt):
        """Update platform (shrinking)"""
        if self.radius > self.min_radius:
            self.radius -= SHRINK_RATE * (dt / 1000.0)
            self.radius = max(self.radius, self.min_radius)
            
    def contains_point(self, point):
        """Check if a point is inside the platform"""
        return circle_contains_point(
            self.center.x, self.center.y, self.radius,
            point.x, point.y
        )
        
    def render(self, screen, offset_x=0, offset_y=0):
        """Draw platform"""
        x = int(self.center.x + offset_x)
        y = int(self.center.y + offset_y)
        
        # Draw platform
        pygame.draw.circle(screen, COLORS['PLATFORM'], (x, y), int(self.radius))
        
        # Draw danger zone (near edge)
        danger_thickness = 20
        if self.radius > danger_thickness:
            pygame.draw.circle(screen, COLORS['DANGER'], (x, y), 
                             int(self.radius), danger_thickness)
            
        # Draw center marker
        pygame.draw.circle(screen, (100, 100, 100), (x, y), 5)
        
        # Draw crosshair
        line_length = 20
        pygame.draw.line(screen, (100, 100, 100),
                        (x - line_length, y), (x + line_length, y), 2)
        pygame.draw.line(screen, (100, 100, 100),
                        (x, y - line_length), (x, y + line_length), 2)