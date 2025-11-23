"""
Main game class - coordinates all game systems
"""
import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE

class Game:
    """Main game coordinator"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        
    def run(self):
        """Main game loop"""
        while self.running:
            self.dt = self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.render()
            
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
    def update(self):
        """Update game state"""
        pass
        
    def render(self):
        """Render game"""
        self.screen.fill((20, 20, 30))
        pygame.display.flip()
        
    def quit(self):
        """Clean up and quit"""
        pygame.quit()