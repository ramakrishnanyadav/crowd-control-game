"""
Round results and score display scene
"""
import pygame
from scenes.scene_manager import Scene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, PLAYER_COLORS
from ui.transitions import FadeTransition

class ResultsScene(Scene):
    """Display round results and scores"""
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.font_large = pygame.font.Font(None, 80)
        self.font_medium = pygame.font.Font(None, 50)
        self.font_small = pygame.font.Font(None, 30)
        
        self.winner_id = None
        self.scores = []
        self.time = 0
        
    def set_results(self, winner_id, scores):
        """Set the results to display"""
        self.winner_id = winner_id
        self.scores = scores[:]
        
    def on_enter(self):
        """Reset timer"""
        self.time = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                transition = FadeTransition(duration=500)
                self.scene_manager.change_scene('game', transition)
            elif event.key == pygame.K_ESCAPE:
                transition = FadeTransition(duration=500)
                self.scene_manager.change_scene('menu', transition)
                
    def update(self, dt):
        self.time += dt
        
    def render(self, screen):
        screen.fill(COLORS['BG'])
        
        if self.winner_id is not None:
            winner_text = self.font_large.render(
                f"PLAYER {self.winner_id + 1} WINS!",
                True,
                PLAYER_COLORS[self.winner_id]
            )
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH//2, 150))
            screen.blit(winner_text, winner_rect)
        else:
            draw_text = self.font_large.render("DRAW!", True, COLORS['TEXT'])
            draw_rect = draw_text.get_rect(center=(SCREEN_WIDTH//2, 150))
            screen.blit(draw_text, draw_rect)
            
        scoreboard_title = self.font_medium.render("SCORES", True, COLORS['TEXT'])
        title_rect = scoreboard_title.get_rect(center=(SCREEN_WIDTH//2, 280))
        screen.blit(scoreboard_title, title_rect)
        
        y = 350
        for i, score in enumerate(self.scores):
            if i >= len(PLAYER_COLORS):
                break
                
            player_text = self.font_small.render(
                f"Player {i + 1}:",
                True,
                PLAYER_COLORS[i]
            )
            score_text = self.font_medium.render(
                str(score),
                True,
                PLAYER_COLORS[i]
            )
            
            player_rect = player_text.get_rect(midright=(SCREEN_WIDTH//2 - 20, y))
            score_rect = score_text.get_rect(midleft=(SCREEN_WIDTH//2 + 20, y))
            
            screen.blit(player_text, player_rect)
            screen.blit(score_text, score_rect)
            
            y += 50
            
        alpha = int(200 + 55 * abs(pygame.math.Vector2(1, 0).rotate(self.time * 0.3).x))
        inst_text = self.font_small.render(
            "ENTER to continue | ESC for menu",
            True,
            COLORS['TEXT']
        )
        inst_surface = pygame.Surface(inst_text.get_size(), pygame.SRCALPHA)
        inst_surface.blit(inst_text, (0, 0))
        inst_surface.set_alpha(alpha)
        
        inst_rect = inst_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 80))
        screen.blit(inst_surface, inst_rect)