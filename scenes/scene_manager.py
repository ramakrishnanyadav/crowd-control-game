"""
Scene management system - handles switching between game states
"""
import pygame
from ui.transitions import FadeTransition

class Scene:
    """Base scene class"""
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.next_scene = None
        
    def handle_event(self, event):
        """Handle pygame events"""
        pass
        
    def update(self, dt):
        """Update scene logic"""
        pass
        
    def render(self, screen):
        """Render scene"""
        pass
        
    def on_enter(self):
        """Called when scene becomes active"""
        pass
        
    def on_exit(self):
        """Called when scene is left"""
        pass

class SceneManager:
    """Manages scene transitions and state"""
    def __init__(self):
        self.scenes = {}
        self.current_scene = None
        self.transition = None
        self.next_scene_name = None
        
    def add_scene(self, name, scene):
        """Register a scene"""
        self.scenes[name] = scene
        
    def change_scene(self, name, transition=None):
        """Change to a different scene"""
        if name not in self.scenes:
            raise ValueError(f"Scene '{name}' not found")
            
        if transition:
            self.transition = transition
            self.next_scene_name = name
            self.transition.start(callback=self._complete_transition)
        else:
            self._switch_scene(name)
            
    def _switch_scene(self, name):
        """Internal scene switching"""
        if self.current_scene:
            self.current_scene.on_exit()
            
        self.current_scene = self.scenes[name]
        self.current_scene.on_enter()
        
    def _complete_transition(self):
        """Called when transition completes"""
        if self.next_scene_name:
            self._switch_scene(self.next_scene_name)
            self.next_scene_name = None
            
    def handle_event(self, event):
        """Forward events to current scene"""
        if self.current_scene and not (self.transition and self.transition.active):
            self.current_scene.handle_event(event)
            
    def update(self, dt):
        """Update current scene and transitions"""
        if self.transition and self.transition.active:
            self.transition.update(dt)
        elif self.current_scene:
            self.current_scene.update(dt)
            
    def render(self, screen):
        """Render current scene and transitions"""
        if self.current_scene:
            self.current_scene.render(screen)
            
        if self.transition and self.transition.active:
            self.transition.render(screen)