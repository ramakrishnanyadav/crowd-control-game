"""
Advanced VFX system - Post-processing, distortion, chromatic aberration
FIXED VERSION - Corrected array handling
"""
import pygame
import numpy as np
import math

class VFXManager:
    """Advanced visual effects manager"""
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.effects = []
        
        # Post-processing surfaces
        self.game_surface = pygame.Surface((screen_width, screen_height))
        self.blur_surface = pygame.Surface((screen_width, screen_height))
        
        # Effects settings
        self.chromatic_aberration = 0
        self.motion_blur_alpha = 0
        self.vignette_intensity = 0.3
        self.bloom_intensity = 0
        self.distortion = 0
        self.time = 0
        
    def add_chromatic_aberration(self, intensity, duration=500):
        """Add chromatic aberration effect"""
        self.effects.append({
            'type': 'chromatic',
            'intensity': intensity,
            'duration': duration,
            'elapsed': 0
        })
        
    def add_bloom(self, intensity, duration=300):
        """Add bloom/glow effect"""
        self.effects.append({
            'type': 'bloom',
            'intensity': intensity,
            'duration': duration,
            'elapsed': 0
        })
        
    def add_distortion(self, intensity, duration=200):
        """Add screen distortion"""
        self.effects.append({
            'type': 'distortion',
            'intensity': intensity,
            'duration': duration,
            'elapsed': 0
        })
        
    def update(self, dt):
        """Update all effects"""
        self.time += dt
        
        # Update effect timers
        self.chromatic_aberration = 0
        self.bloom_intensity = 0
        self.distortion = 0
        
        for effect in self.effects[:]:
            effect['elapsed'] += dt
            progress = effect['elapsed'] / effect['duration']
            
            if progress >= 1.0:
                self.effects.remove(effect)
            else:
                # Exponential decay
                current_intensity = effect['intensity'] * (1 - progress) ** 2
                
                if effect['type'] == 'chromatic':
                    self.chromatic_aberration = max(self.chromatic_aberration, current_intensity)
                elif effect['type'] == 'bloom':
                    self.bloom_intensity = max(self.bloom_intensity, current_intensity)
                elif effect['type'] == 'distortion':
                    self.distortion = max(self.distortion, current_intensity)
                    
    def apply_chromatic_aberration(self, surface, intensity):
        """Apply RGB channel separation effect - FIXED VERSION"""
        if intensity <= 0:
            return surface
        
        try:
            # Calculate offset with safety bounds
            offset = int(intensity * 5)
            
            # Safety check: ensure offset is valid
            if offset <= 0:
                return surface
            
            width, height = surface.get_size()
            if offset >= width:
                offset = width - 1
            
            # Get pixel array (use pixels3d for direct access)
            arr = pygame.surfarray.pixels3d(surface)
            result = arr.copy()  # Create writable copy
            
            # Apply channel shifts with bounds checking
            if offset < width:
                # Shift red channel right
                result[offset:, :, 0] = arr[:-offset, :, 0]
                # Shift blue channel left
                result[:-offset, :, 2] = arr[offset:, :, 2]
            
            # Green channel stays in place (already copied)
            
            # Clean up the reference to original array
            del arr
            
            # Convert back to surface
            return pygame.surfarray.make_surface(result)
            
        except Exception as e:
            print(f"Chromatic aberration error: {e}")
            return surface  # Return original if any error
        
    def apply_bloom(self, surface, intensity):
        """Apply bloom/glow effect"""
        if intensity <= 0:
            return surface
        
        try:
            # Create brightened copy
            bright = surface.copy()
            bright.set_alpha(int(intensity * 100))
            
            # Upscale and downscale for blur effect
            w, h = surface.get_size()
            temp = pygame.transform.smoothscale(bright, (w // 4, h // 4))
            blurred = pygame.transform.smoothscale(temp, (w, h))
            
            # Blend with original
            result = surface.copy()
            result.blit(blurred, (0, 0), special_flags=pygame.BLEND_ADD)
            
            return result
        except Exception as e:
            print(f"Bloom error: {e}")
            return surface
        
    def apply_vignette(self, surface, intensity):
        """Apply vignette darkening at edges"""
        if intensity <= 0:
            return surface
        
        try:
            vignette = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Create radial gradient
            center_x, center_y = self.width // 2, self.height // 2
            max_dist = math.sqrt(center_x**2 + center_y**2)
            
            for y in range(0, self.height, 4):  # Step for performance
                for x in range(0, self.width, 4):
                    dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    alpha = int(255 * intensity * (dist / max_dist) ** 2)
                    alpha = min(255, alpha)
                    pygame.draw.rect(vignette, (0, 0, 0, alpha), (x, y, 4, 4))
            
            result = surface.copy()
            result.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            return result
        except Exception as e:
            print(f"Vignette error: {e}")
            return surface
        
    def apply_distortion(self, surface, intensity):
        """Apply wave distortion effect"""
        if intensity <= 0:
            return surface
        
        try:
            # Simple wave distortion
            result = surface.copy()
            
            for y in range(0, self.height, 2):
                offset = int(math.sin(y * 0.1 + self.time * 0.01) * intensity * 10)
                
                if abs(offset) > 0 and 0 <= y < self.height - 2:
                    # Shift row
                    strip = surface.subsurface((0, y, self.width, min(2, self.height - y)))
                    
                    # Calculate target x position with bounds
                    target_x = max(0, min(offset, self.width - 1))
                    result.blit(strip, (target_x, y))
            
            return result
        except Exception as e:
            print(f"Distortion error: {e}")
            return surface
        
    def render(self, screen, game_surface):
        """Apply all post-processing effects"""
        # Start with game surface
        result = game_surface.copy()
        
        # Apply effects in order
        if self.chromatic_aberration > 0:
            result = self.apply_chromatic_aberration(result, self.chromatic_aberration)
            
        if self.bloom_intensity > 0:
            result = self.apply_bloom(result, self.bloom_intensity)
            
        if self.distortion > 0:
            result = self.apply_distortion(result, self.distortion)
            
        # Always apply subtle vignette
        result = self.apply_vignette(result, self.vignette_intensity)
        
        # Blit to screen
        screen.blit(result, (0, 0))
        
        return screen


class TrailRenderer:
    """Motion trail renderer for fast-moving objects"""
    def __init__(self):
        self.trails = []
        
    def add_trail(self, x, y, color, radius, lifetime=200):
        """Add trail point"""
        self.trails.append({
            'pos': (x, y),
            'color': color,
            'radius': radius,
            'lifetime': lifetime,
            'age': 0
        })
        
    def update(self, dt):
        """Update trails"""
        for trail in self.trails[:]:
            trail['age'] += dt
            if trail['age'] >= trail['lifetime']:
                self.trails.remove(trail)
                
    def render(self, screen, offset_x=0, offset_y=0):
        """Render motion trails"""
        for trail in self.trails:
            alpha = int(255 * (1 - trail['age'] / trail['lifetime']))
            radius = int(trail['radius'] * (1 - trail['age'] / trail['lifetime'] * 0.5))
            
            if radius > 0 and alpha > 0:
                x = int(trail['pos'][0] + offset_x)
                y = int(trail['pos'][1] + offset_y)
                
                # Create surface with alpha
                surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*trail['color'], alpha), (radius, radius), radius)
                screen.blit(surf, (x - radius, y - radius))
                
    def clear(self):
        """Clear all trails"""
        self.trails.clear()


class ImpactEffect:
    """Impact/hit effect visualizer"""
    def __init__(self):
        self.impacts = []
        
    def add_impact(self, x, y, color, size=50, duration=300):
        """Add impact effect"""
        self.impacts.append({
            'pos': (x, y),
            'color': color,
            'size': size,
            'duration': duration,
            'elapsed': 0
        })
        
    def update(self, dt):
        """Update impacts"""
        for impact in self.impacts[:]:
            impact['elapsed'] += dt
            if impact['elapsed'] >= impact['duration']:
                self.impacts.remove(impact)
                
    def render(self, screen, offset_x=0, offset_y=0):
        """Render impact effects"""
        for impact in self.impacts:
            progress = impact['elapsed'] / impact['duration']
            
            # Expand and fade
            current_size = int(impact['size'] * (1 + progress * 2))
            alpha = int(255 * (1 - progress))
            
            x = int(impact['pos'][0] + offset_x)
            y = int(impact['pos'][1] + offset_y)
            
            # Draw expanding ring
            if alpha > 0:
                surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*impact['color'], alpha // 2), 
                                 (current_size, current_size), current_size)
                pygame.draw.circle(surf, (*impact['color'], alpha), 
                                 (current_size, current_size), current_size, 3)
                screen.blit(surf, (x - current_size, y - current_size))
                
    def clear(self):
        """Clear all impacts"""
        self.impacts.clear()