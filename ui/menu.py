"""
Menu system for UI
"""
import pygame
from config.settings import COLORS

class Menu:
    """Generic menu class"""
    def __init__(self, items, title="MENU"):
        self.items = items
        self.title = title
        self.selected_index = 0
        self.font_title = pygame.font.Font(None, 80)
        self.font_item = pygame.font.Font(None, 40)
        
    def handle_input(self, event):
        """Handle menu input"""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.items)
                return 'move'
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.items)
                return 'move'
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return 'select'
        return None
        
    def get_selected(self):
        """Get currently selected item"""
        return self.items[self.selected_index]
        
    def render(self, screen, center_x, start_y):
        """Render menu"""
        # Title
        title_surf = self.font_title.render(self.title, True, COLORS['TEXT'])
        title_rect = title_surf.get_rect(center=(center_x, start_y - 100))
        screen.blit(title_surf, title_rect)
        
        # Menu items
        y = start_y
        for i, item in enumerate(self.items):
            color = COLORS['HIGHLIGHT'] if i == self.selected_index else COLORS['TEXT']
            text_surf = self.font_item.render(item, True, color)
            text_rect = text_surf.get_rect(center=(center_x, y))
            
            # Selection indicator
            if i == self.selected_index:
                pygame.draw.circle(screen, color, (text_rect.left - 30, text_rect.centery), 5)
                
            screen.blit(text_surf, text_rect)
            y += 60