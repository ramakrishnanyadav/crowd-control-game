"""
Main menu scene
"""
import pygame
import random
from scenes.scene_manager import Scene
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, PLAYER_COUNT,
    PLAYER_COLORS
)
from ui.transitions import FadeTransition
from systems.particles import ParticleSystem

class MenuScene(Scene):
    """Main menu with player selection"""
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.font_title = pygame.font.Font(None, 80)
        self.font_menu = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 24)
        
        self.menu_items = [
            "START GAME",
            "CONTROLS",
            "QUIT"
        ]
        self.selected_index = 0
        self.particles = ParticleSystem()
        self.time = 0
        
        self.player_count = 2
        self.mode = "menu"
        
    def on_enter(self):
        """Reset menu state"""
        self.selected_index = 0
        self.mode = "menu"
        self.time = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.mode == "menu":
                self._handle_menu_input(event)
            elif self.mode == "player_select":
                self._handle_player_select(event)
            elif self.mode == "controls":
                self._handle_controls_input(event)
                
    def _handle_menu_input(self, event):
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._select_menu_item()
            
    def _handle_player_select(self, event):
        if event.key == pygame.K_ESCAPE:
            self.mode = "menu"
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.player_count = max(2, self.player_count - 1)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.player_count = min(PLAYER_COUNT, self.player_count + 1)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.scene_manager.scenes['game'].player_count = self.player_count
            transition = FadeTransition(duration=500)
            self.scene_manager.change_scene('game', transition)
            
    def _handle_controls_input(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            self.mode = "menu"
            
    def _select_menu_item(self):
        item = self.menu_items[self.selected_index]
        if item == "START GAME":
            self.mode = "player_select"
        elif item == "CONTROLS":
            self.mode = "controls"
        elif item == "QUIT":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            
    def update(self, dt):
        self.time += dt
        
        if self.time % 100 < dt:
            self.particles.emit(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.choice(list(COLORS.values())),
                count=1,
                speed=20
            )
        self.particles.update(dt)
        
    def render(self, screen):
        screen.fill(COLORS['BG'])
        self.particles.render(screen)
        
        if self.mode == "menu":
            self._render_menu(screen)
        elif self.mode == "player_select":
            self._render_player_select(screen)
        elif self.mode == "controls":
            self._render_controls(screen)
            
    def _render_menu(self, screen):
        title = self.font_title.render("CROWD CONTROL", True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(title, title_rect)
        
        y = 300
        for i, item in enumerate(self.menu_items):
            color = COLORS['HIGHLIGHT'] if i == self.selected_index else COLORS['TEXT']
            text = self.font_menu.render(item, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, y))
            
            if i == self.selected_index:
                pulse = abs(pygame.math.Vector2(1, 0).rotate(self.time * 0.2).x)
                pygame.draw.circle(screen, color, (rect.left - 30, rect.centery), 5 + pulse * 3)
                
            screen.blit(text, rect)
            y += 60
            
    def _render_player_select(self, screen):
        title = self.font_title.render("SELECT PLAYERS", True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(title, title_rect)
        
        count_text = self.font_menu.render(f"{self.player_count} PLAYERS", True, COLORS['HIGHLIGHT'])
        count_rect = count_text.get_rect(center=(SCREEN_WIDTH//2, 300))
        screen.blit(count_text, count_rect)
        
        arrow_l = self.font_menu.render("<", True, COLORS['TEXT'])
        arrow_r = self.font_menu.render(">", True, COLORS['TEXT'])
        screen.blit(arrow_l, (count_rect.left - 60, count_rect.top))
        screen.blit(arrow_r, (count_rect.right + 30, count_rect.top))
        
        y = 380
        spacing = 60
        for i in range(self.player_count):
            color = PLAYER_COLORS[i]
            pygame.draw.circle(screen, color, 
                             (SCREEN_WIDTH//2 + (i - self.player_count/2 + 0.5) * spacing, y), 
                             20)
        
        inst = self.font_small.render("ARROW KEYS to change | ENTER to start | ESC to go back", 
                                     True, COLORS['TEXT'])
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 80))
        screen.blit(inst, inst_rect)
        
    def _render_controls(self, screen):
        title = self.font_title.render("CONTROLS", True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(title, title_rect)
        
        controls_text = [
            "Player 1: WASD",
            "Player 2: Arrow Keys",
            "Player 3: IJKL",
            "Player 4: Numpad 8456",
            "",
            "Push opponents off the platform!",
            "Last player standing wins the round.",
            "Platform shrinks over time - stay on!"
        ]
        
        y = 200
        for line in controls_text:
            text = self.font_small.render(line, True, COLORS['TEXT'])
            rect = text.get_rect(center=(SCREEN_WIDTH//2, y))
            screen.blit(text, rect)
            y += 40
            
        inst = self.font_small.render("Press any key to return", True, COLORS['HIGHLIGHT'])
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 80))
        screen.blit(inst, inst_rect)