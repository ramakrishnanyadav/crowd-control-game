"""
Settings and configuration management system
"""
import pygame
import json
from pathlib import Path

class GameSettings:
    """Game settings manager"""
    def __init__(self):
        self.config_file = Path('config.json')
        
        # Default settings
        self.settings = {
            'video': {
                'resolution': [1280, 720],
                'fullscreen': False,
                'vsync': True,
                'show_fps': False
            },
            'audio': {
                'master_volume': 0.7,
                'sfx_volume': 0.8,
                'music_volume': 0.5,
                'muted': False
            },
            'gameplay': {
                'screen_shake': True,
                'particles': True,
                'vfx_quality': 'high',  # low, medium, high
                'show_trails': True
            },
            'controls': {
                'player1': {
                    'up': 'w',
                    'down': 's',
                    'left': 'a',
                    'right': 'd',
                    'dash': 'lshift'
                },
                'player2': {
                    'up': 'up',
                    'down': 'down',
                    'left': 'left',
                    'right': 'right',
                    'dash': 'rshift'
                }
            }
        }
        
        self.load_settings()
        
    def load_settings(self):
        """Load settings from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    self._merge_settings(loaded)
            except Exception as e:
                print(f"Failed to load settings: {e}")
                
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")
            
    def _merge_settings(self, loaded):
        """Merge loaded settings with defaults"""
        for category, values in loaded.items():
            if category in self.settings:
                if isinstance(values, dict):
                    self.settings[category].update(values)
                else:
                    self.settings[category] = values
                    
    def get(self, category, key=None):
        """Get setting value"""
        if key:
            return self.settings.get(category, {}).get(key)
        return self.settings.get(category)
        
    def set(self, category, key, value):
        """Set setting value"""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
        
    def apply_video_settings(self):
        """Apply video settings"""
        res = self.settings['video']['resolution']
        fullscreen_flag = pygame.FULLSCREEN if self.settings['video']['fullscreen'] else 0
        vsync_flag = pygame.SCALED if self.settings['video']['vsync'] else 0
        
        return pygame.display.set_mode(res, fullscreen_flag | vsync_flag)
        
    def get_key_code(self, key_name):
        """Convert key name to pygame constant"""
        key_map = {
            'w': pygame.K_w, 's': pygame.K_s, 'a': pygame.K_a, 'd': pygame.K_d,
            'up': pygame.K_UP, 'down': pygame.K_DOWN, 
            'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
            'lshift': pygame.K_LSHIFT, 'rshift': pygame.K_RSHIFT,
            'space': pygame.K_SPACE, 'enter': pygame.K_RETURN,
            'escape': pygame.K_ESCAPE
        }
        return key_map.get(key_name.lower(), pygame.K_SPACE)

class SettingsMenu:
    """Settings menu UI"""
    def __init__(self, settings):
        self.settings = settings
        self.font_title = pygame.font.Font(None, 60)
        self.font_item = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.categories = ['Video', 'Audio', 'Gameplay', 'Controls']
        self.current_category = 0
        self.selected_item = 0
        
        # Category items
        self.items = {
            'Video': [
                ('Resolution', 'resolution', ['1280x720', '1920x1080', '2560x1440']),
                ('Fullscreen', 'fullscreen', [True, False]),
                ('VSync', 'vsync', [True, False]),
                ('Show FPS', 'show_fps', [True, False])
            ],
            'Audio': [
                ('Master Volume', 'master_volume', 'slider'),
                ('SFX Volume', 'sfx_volume', 'slider'),
                ('Music Volume', 'music_volume', 'slider'),
                ('Muted', 'muted', [True, False])
            ],
            'Gameplay': [
                ('Screen Shake', 'screen_shake', [True, False]),
                ('Particles', 'particles', [True, False]),
                ('VFX Quality', 'vfx_quality', ['low', 'medium', 'high']),
                ('Show Trails', 'show_trails', [True, False])
            ],
            'Controls': [
                ('Remap Player 1', 'player1', 'button'),
                ('Remap Player 2', 'player2', 'button')
            ]
        }
        
    def handle_input(self, event):
        """Handle menu input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected_item = (self.selected_item - 1) % len(self.get_current_items())
                return 'move'
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_item = (self.selected_item + 1) % len(self.get_current_items())
                return 'move'
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.current_category = (self.current_category - 1) % len(self.categories)
                self.selected_item = 0
                return 'category'
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.current_category = (self.current_category + 1) % len(self.categories)
                self.selected_item = 0
                return 'category'
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._toggle_setting()
                return 'select'
        return None
        
    def _toggle_setting(self):
        """Toggle current setting"""
        category = self.categories[self.current_category].lower()
        items = self.get_current_items()
        
        if self.selected_item < len(items):
            name, key, options = items[self.selected_item]
            
            if isinstance(options, list):
                # Cycle through options
                current = self.settings.get(category, key)
                try:
                    idx = options.index(current)
                    next_idx = (idx + 1) % len(options)
                    self.settings.set(category, key, options[next_idx])
                except ValueError:
                    self.settings.set(category, key, options[0])
            elif options == 'slider':
                # Increment slider (can be improved with mouse)
                current = self.settings.get(category, key)
                new_value = min(1.0, current + 0.1)
                self.settings.set(category, key, new_value)
                
        self.settings.save_settings()
        
    def get_current_items(self):
        """Get items for current category"""
        category_name = self.categories[self.current_category]
        return self.items.get(category_name, [])
        
    def render(self, screen):
        """Render settings menu"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Background
        screen.fill((20, 20, 30))
        
        # Title
        title = self.font_title.render("SETTINGS", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen_width // 2, 50))
        screen.blit(title, title_rect)
        
        # Category tabs
        tab_y = 120
        tab_width = screen_width // len(self.categories)
        
        for i, category in enumerate(self.categories):
            x = i * tab_width
            color = (100, 200, 255) if i == self.current_category else (100, 100, 100)
            
            # Tab background
            tab_rect = pygame.Rect(x, tab_y, tab_width, 40)
            pygame.draw.rect(screen, color, tab_rect)
            pygame.draw.rect(screen, (255, 255, 255), tab_rect, 2)
            
            # Tab text
            tab_text = self.font_item.render(category, True, (255, 255, 255))
            text_rect = tab_text.get_rect(center=(x + tab_width // 2, tab_y + 20))
            screen.blit(tab_text, text_rect)
            
        # Settings items
        items_y = 200
        items = self.get_current_items()
        category = self.categories[self.current_category].lower()
        
        for i, (name, key, options) in enumerate(items):
            y = items_y + i * 60
            
            # Highlight selected
            if i == self.selected_item:
                highlight = pygame.Rect(50, y - 5, screen_width - 100, 50)
                pygame.draw.rect(screen, (50, 50, 80), highlight)
                pygame.draw.rect(screen, (100, 200, 255), highlight, 2)
                
            # Setting name
            name_text = self.font_item.render(name, True, (255, 255, 255))
            screen.blit(name_text, (100, y))
            
            # Setting value
            current_value = self.settings.get(category, key)
            
            if isinstance(options, list):
                value_text = str(current_value)
            elif options == 'slider':
                value_text = f"{int(current_value * 100)}%"
                # Draw slider
                slider_x = screen_width - 300
                slider_w = 200
                pygame.draw.rect(screen, (100, 100, 100), (slider_x, y + 10, slider_w, 10))
                fill_w = int(slider_w * current_value)
                pygame.draw.rect(screen, (100, 200, 255), (slider_x, y + 10, fill_w, 10))
            else:
                value_text = "Configure"
                
            value_surf = self.font_item.render(value_text, True, (100, 200, 255))
            screen.blit(value_surf, (screen_width - 400, y))
            
        # Instructions
        inst_text = "ARROW KEYS: Navigate | ENTER: Select | ESC: Back"
        inst_surf = self.font_small.render(inst_text, True, (180, 180, 180))
        inst_rect = inst_surf.get_rect(center=(screen_width // 2, screen_height - 40))
        screen.blit(inst_surf, inst_rect)