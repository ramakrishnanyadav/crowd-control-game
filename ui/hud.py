"""
Advanced HUD with combo system, kill feed, and statistics
"""
import pygame
import math
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS

class ComboTracker:
    """Tracks combo hits"""
    def __init__(self):
        self.combo = 0
        self.combo_timer = 0
        self.combo_timeout = 3000
        self.max_combo = 0
        
    def add_hit(self):
        """Add hit to combo"""
        self.combo += 1
        self.combo_timer = self.combo_timeout
        self.max_combo = max(self.max_combo, self.combo)
        
    def update(self, dt):
        """Update combo timer"""
        if self.combo > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0
                
    def get_multiplier(self):
        """Get score multiplier based on combo"""
        if self.combo >= 5:
            return 3.0
        elif self.combo >= 3:
            return 2.0
        elif self.combo >= 2:
            return 1.5
        return 1.0

class KillFeed:
    """Kill/elimination feed display"""
    def __init__(self):
        self.events = []
        self.font = pygame.font.Font(None, 24)
        
    def add_kill(self, killer_id, victim_id, killer_color, victim_color):
        """Add kill event"""
        self.events.append({
            'killer': killer_id,
            'victim': victim_id,
            'killer_color': killer_color,
            'victim_color': victim_color,
            'time': 0,
            'lifetime': 5000
        })
        
    def add_elimination(self, player_id, player_color, reason='fell off'):
        """Add elimination event"""
        self.events.append({
            'victim': player_id,
            'victim_color': player_color,
            'reason': reason,
            'time': 0,
            'lifetime': 5000
        })
        
    def update(self, dt):
        """Update kill feed"""
        for event in self.events[:]:
            event['time'] += dt
            if event['time'] >= event['lifetime']:
                self.events.remove(event)
                
    def render(self, screen):
        """Render kill feed"""
        x = SCREEN_WIDTH - 250
        y = 100
        
        for i, event in enumerate(self.events[-5:]):  # Show last 5
            # Fade out
            alpha = int(255 * (1 - event['time'] / event['lifetime']))
            
            if 'killer' in event:
                # Kill event
                killer_text = self.font.render(f"P{event['killer'] + 1}", True, event['killer_color'])
                eliminated_text = self.font.render("eliminated", True, (200, 200, 200))
                victim_text = self.font.render(f"P{event['victim'] + 1}", True, event['victim_color'])
                
                # Create surface with alpha
                surf = pygame.Surface((230, 30), pygame.SRCALPHA)
                surf.fill((0, 0, 0, 150))
                
                surf.blit(killer_text, (5, 5))
                surf.blit(eliminated_text, (45, 5))
                surf.blit(victim_text, (140, 5))
                
                surf.set_alpha(alpha)
                screen.blit(surf, (x, y + i * 35))
            else:
                # Self-elimination
                victim_text = self.font.render(f"P{event['victim'] + 1}", True, event['victim_color'])
                reason_text = self.font.render(event['reason'], True, (200, 200, 200))
                
                surf = pygame.Surface((230, 30), pygame.SRCALPHA)
                surf.fill((0, 0, 0, 150))
                
                surf.blit(victim_text, (5, 5))
                surf.blit(reason_text, (45, 5))
                
                surf.set_alpha(alpha)
                screen.blit(surf, (x, y + i * 35))

class AdvancedHUD:
    """Advanced HUD with more information"""
    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.combo_tracker = ComboTracker()
        self.kill_feed = KillFeed()
        
        # Animation
        self.time = 0
        
    def add_hit(self):
        """Add hit to combo"""
        self.combo_tracker.add_hit()
        
    def add_kill(self, killer_id, victim_id, killer_color, victim_color):
        """Add kill to feed"""
        self.kill_feed.add_kill(killer_id, victim_id, killer_color, victim_color)
        
    def add_elimination(self, player_id, player_color, reason='fell off'):
        """Add elimination to feed"""
        self.kill_feed.add_elimination(player_id, player_color, reason)
        
    def update(self, dt):
        """Update HUD"""
        self.time += dt
        self.combo_tracker.update(dt)
        self.kill_feed.update(dt)
        
    def render(self, screen, players, scores, time_left):
        """Render advanced HUD"""
        # Timer at top center
        minutes = int(time_left // 60000)
        seconds = int((time_left % 60000) // 1000)
        
        # Warning color when time is low
        if time_left < 10000:
            pulse = abs(math.sin(self.time * 0.01))
            timer_color = (255, int(100 + pulse * 155), 100)
        else:
            timer_color = COLORS['TEXT']
            
        timer_text = self.font_large.render(f"{minutes}:{seconds:02d}", True, timer_color)
        timer_rect = timer_text.get_rect(midtop=(SCREEN_WIDTH // 2, 20))
        
        # Timer background
        bg_rect = pygame.Rect(timer_rect.left - 10, timer_rect.top - 5,
                             timer_rect.width + 20, timer_rect.height + 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(screen, COLORS['TEXT'], bg_rect, 2)
        
        screen.blit(timer_text, timer_rect)
        
        # Player stats panel
        self._render_player_stats(screen, players, scores)
        
        # Combo display
        if self.combo_tracker.combo > 1:
            self._render_combo(screen)
            
        # Kill feed
        self.kill_feed.render(screen)
        
        # Performance stats
        self._render_performance(screen)
        
    def _render_player_stats(self, screen, players, scores):
        """Render player statistics panel"""
        panel_width = 200
        panel_height = 60 * len(players) + 20
        panel_x = 10
        panel_y = 100
        
        # Panel background
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        
        y_offset = 10
        for i, player in enumerate(players):
            if i >= len(scores):
                break
                
            # Player color indicator
            pygame.draw.circle(panel, player.color, (20, y_offset + 20), 12)
            
            # Player number
            num_text = self.font_small.render(f"P{player.player_id + 1}", True, COLORS['TEXT'])
            panel.blit(num_text, (40, y_offset + 5))
            
            # Score
            score_text = self.font_medium.render(str(scores[i]), True, player.color)
            panel.blit(score_text, (40, y_offset + 25))
            
            # Status
            if player.alive:
                status_text = self.font_tiny.render("ALIVE", True, COLORS['HIGHLIGHT'])
                
                # Dash charges
                charges_text = self.font_tiny.render(
                    f"Dash: {player.dash_charges}", True, (200, 200, 200))
                panel.blit(charges_text, (100, y_offset + 35))
            else:
                status_text = self.font_tiny.render("OUT", True, (100, 100, 100))
                
            panel.blit(status_text, (100, y_offset + 5))
            
            # K/D ratio
            if hasattr(player, 'kills') and hasattr(player, 'deaths'):
                kd_text = self.font_tiny.render(
                    f"K/D: {player.kills}/{player.deaths}", True, (180, 180, 180))
                panel.blit(kd_text, (100, y_offset + 20))
            
            y_offset += 60
            
        screen.blit(panel, (panel_x, panel_y))
        
    def _render_combo(self, screen):
        """Render combo counter"""
        combo = self.combo_tracker.combo
        multiplier = self.combo_tracker.get_multiplier()
        
        # Position at top center
        x = SCREEN_WIDTH // 2
        y = 100
        
        # Scale based on combo
        scale = 1.0 + (combo / 10.0)
        
        # Combo text
        combo_text = self.font_large.render(f"{combo} HIT COMBO!", True, (255, 200, 50))
        combo_scaled = pygame.transform.scale(combo_text, 
            (int(combo_text.get_width() * scale), int(combo_text.get_height() * scale)))
        combo_rect = combo_scaled.get_rect(center=(x, y))
        
        # Pulsing effect
        pulse = abs(math.sin(self.time * 0.01))
        glow_color = (255, int(150 + pulse * 105), 50)
        
        # Draw glow
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_text = self.font_large.render(f"{combo} HIT COMBO!", True, glow_color)
            glow_scaled = pygame.transform.scale(glow_text,
                (int(glow_text.get_width() * scale), int(glow_text.get_height() * scale)))
            screen.blit(glow_scaled, (combo_rect.x + offset[0], combo_rect.y + offset[1]))
            
        screen.blit(combo_scaled, combo_rect)
        
        # Multiplier
        mult_text = self.font_medium.render(f"x{multiplier:.1f}", True, (255, 255, 100))
        mult_rect = mult_text.get_rect(center=(x, y + 50))
        screen.blit(mult_text, mult_rect)
        
    def _render_performance(self, screen):
        """Render performance metrics"""
        fps = int(pygame.time.Clock().get_fps()) if hasattr(pygame.time.Clock(), 'get_fps') else 60
        
        perf_text = self.font_tiny.render(f"FPS: {fps}", True, (100, 100, 100))
        screen.blit(perf_text, (SCREEN_WIDTH - 80, SCREEN_HEIGHT - 25))