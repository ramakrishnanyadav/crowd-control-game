"""
Screen transitions and animations for scene changes
"""
import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Transition:
    """Base transition class"""
    def __init__(self, duration=500):
        self.duration = duration
        self.elapsed = 0
        self.active = False
        self.callback = None
        
    def start(self, callback=None):
        self.active = True
        self.elapsed = 0
        self.callback = callback
        
    def update(self, dt):
        if not self.active:
            return False
            
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False
            if self.callback:
                self.callback()
            return False
        return True
        
    def get_progress(self):
        """Returns 0.0 to 1.0"""
        return min(1.0, self.elapsed / self.duration)
        
    def render(self, screen):
        pass

class FadeTransition(Transition):
    """Fade to black transition"""
    def __init__(self, duration=500, fade_in=False):
        super().__init__(duration)
        self.fade_in = fade_in
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface.fill((0, 0, 0))
        
    def render(self, screen):
        if not self.active:
            return
            
        progress = self.get_progress()
        if self.fade_in:
            alpha = int(255 * (1 - progress))
        else:
            alpha = int(255 * progress)
            
        self.surface.set_alpha(alpha)
        screen.blit(self.surface, (0, 0))

class SlideTransition(Transition):
    """Slide screen in/out"""
    def __init__(self, duration=500, direction='left'):
        super().__init__(duration)
        self.direction = direction
        
    def render(self, screen):
        if not self.active:
            return
            
        progress = self.get_progress()
        progress = 1 - (1 - progress) ** 3
        
        offset = int(SCREEN_WIDTH * progress)
        
        if self.direction == 'left':
            screen.scroll(-offset, 0)
        elif self.direction == 'right':
            screen.scroll(offset, 0)

class CircleWipe(Transition):
    """Circular wipe transition"""
    def __init__(self, duration=800, expand=True):
        super().__init__(duration)
        self.expand = expand
        self.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.max_radius = int(((SCREEN_WIDTH/2)**2 + (SCREEN_HEIGHT/2)**2)**0.5)
        
    def render(self, screen):
        if not self.active:
            return
            
        progress = self.get_progress()
        progress = progress ** 2
        
        if self.expand:
            radius = int(self.max_radius * progress)
        else:
            radius = int(self.max_radius * (1 - progress))
            
        mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        mask.fill((0, 0, 0))
        pygame.draw.circle(mask, (255, 255, 255), self.center, radius)
        mask.set_colorkey((255, 255, 255))
        screen.blit(mask, (0, 0))

class TransitionManager:
    """Manages multiple transitions"""
    def __init__(self):
        self.transitions = []
        
    def add(self, transition):
        self.transitions.append(transition)
        
    def update(self, dt):
        self.transitions = [t for t in self.transitions if t.update(dt)]
        
    def render(self, screen):
        for transition in self.transitions:
            transition.render(screen)
            
    def is_active(self):
        return len(self.transitions) > 0