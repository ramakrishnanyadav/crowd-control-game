"""
Enhanced physics system with spatial partitioning and better collision resolution
"""
import pygame
import math
from config.settings import COLLISION_PUSH

class SpatialGrid:
    """Spatial partitioning grid for efficient collision detection"""
    def __init__(self, cell_size=100):
        self.cell_size = cell_size
        self.grid = {}
        
    def clear(self):
        """Clear the grid"""
        self.grid.clear()
        
    def _get_cell(self, x, y):
        """Get cell coordinates"""
        return (int(x // self.cell_size), int(y // self.cell_size))
        
    def insert(self, entity):
        """Insert entity into grid"""
        cell = self._get_cell(entity.pos.x, entity.pos.y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(entity)
        
    def get_nearby(self, entity):
        """Get entities in nearby cells"""
        cx, cy = self._get_cell(entity.pos.x, entity.pos.y)
        nearby = []
        
        # Check 3x3 grid around entity
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                cell = (cx + dx, cy + dy)
                if cell in self.grid:
                    nearby.extend(self.grid[cell])
                    
        return nearby

def check_collision(entity1, entity2):
    """Check if two circular entities are colliding"""
    dx = entity2.pos.x - entity1.pos.x
    dy = entity2.pos.y - entity1.pos.y
    distance_sq = dx * dx + dy * dy
    min_distance = entity1.radius + entity2.radius
    
    return distance_sq < min_distance * min_distance

def resolve_collision(entity1, entity2, dt_multiplier=1.0):
    """Enhanced collision resolution with better stability"""
    # Calculate collision vector
    dx = entity2.pos.x - entity1.pos.x
    dy = entity2.pos.y - entity1.pos.y
    distance = math.sqrt(dx * dx + dy * dy)
    
    # Handle perfect overlap
    if distance < 0.0001:
        import random
        angle = random.uniform(0, math.pi * 2)
        dx = math.cos(angle)
        dy = math.sin(angle)
        distance = 0.0001
    
    # Normalize collision vector
    nx = dx / distance
    ny = dy / distance
    
    # Calculate overlap
    min_distance = entity1.radius + entity2.radius
    overlap = min_distance - distance
    
    # Position correction with damping
    correction_factor = 0.6  # Soft correction to prevent jitter
    correction = overlap * correction_factor
    
    entity1.pos.x -= nx * correction
    entity1.pos.y -= ny * correction
    entity2.pos.x += nx * correction
    entity2.pos.y += ny * correction
    
    # Velocity resolution
    # Calculate relative velocity
    rel_vel_x = entity2.vel.x - entity1.vel.x
    rel_vel_y = entity2.vel.y - entity1.vel.y
    
    # Velocity along collision normal
    vel_along_normal = rel_vel_x * nx + rel_vel_y * ny
    
    # Don't resolve if objects are separating
    if vel_along_normal > 0:
        return
    
    # Calculate impulse (with restitution for bounce)
    restitution = 0.7
    impulse_strength = -(1 + restitution) * vel_along_normal
    impulse_strength /= 2  # Assume equal mass
    
    # Apply velocity impulse
    impulse_x = impulse_strength * nx
    impulse_y = impulse_strength * ny
    
    entity1.vel.x -= impulse_x
    entity1.vel.y -= impulse_y
    entity2.vel.x += impulse_x
    entity2.vel.y += impulse_y
    
    # Add gameplay push force
    push_force = COLLISION_PUSH * dt_multiplier
    entity1.vel.x -= nx * push_force
    entity1.vel.y -= ny * push_force
    entity2.vel.x += nx * push_force
    entity2.vel.y += ny * push_force
    
    # Add slight tangential force for more dynamic collisions
    tangent_x = -ny
    tangent_y = nx
    tangent_force = 50 * dt_multiplier
    
    entity1.vel.x += tangent_x * tangent_force
    entity1.vel.y += tangent_y * tangent_force
    entity2.vel.x -= tangent_x * tangent_force
    entity2.vel.y -= tangent_y * tangent_force

def circle_contains_point(circle_x, circle_y, radius, point_x, point_y):
    """Check if a point is inside a circle"""
    dx = point_x - circle_x
    dy = point_y - circle_y
    distance_sq = dx * dx + dy * dy
    return distance_sq <= radius * radius

def apply_drag(velocity, drag_coefficient=0.02):
    """Apply quadratic drag (more realistic than linear friction)"""
    speed = velocity.length()
    if speed > 0:
        drag_force = drag_coefficient * speed * speed
        drag_direction = velocity.normalize()
        velocity.x -= drag_direction.x * drag_force
        velocity.y -= drag_direction.y * drag_force
    return velocity

def clamp_velocity(velocity, max_speed=1000):
    """Clamp velocity to prevent physics explosions"""
    speed = velocity.length()
    if speed > max_speed:
        velocity.scale_to_length(max_speed)
    return velocity