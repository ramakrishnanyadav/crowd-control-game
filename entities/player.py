"""
Enhanced player entity with more abilities and visual effects
DEBUGGED VERSION - Added extensive debugging
"""
import pygame
import math
from config.settings import (
    PLAYER_RADIUS, PLAYER_SPEED, PLAYER_DASH_SPEED,
    PLAYER_DASH_DURATION, PLAYER_DASH_COOLDOWN, FRICTION,
    SCREEN_WIDTH, SCREEN_HEIGHT
)

class Player:
    """Enhanced player character with more abilities"""
    def __init__(self, x, y, color, player_id, controls):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.color = color
        self.player_id = player_id
        self.controls = controls
        self.radius = PLAYER_RADIUS
        self.alive = True
        
        # DEBUG: Print initialization
        print(f"🎮 Player {player_id} initialized:")
        print(f"   Position: ({x:.1f}, {y:.1f})")
        print(f"   Color: {color}")
        print(f"   Radius: {self.radius}")
        print(f"   Alive: {self.alive}")
        print(f"   Controls: {controls}")
        
        # Dash mechanics
        self.is_dashing = False
        self.dash_time = 0
        self.dash_cooldown = 0
        self.dash_direction = pygame.math.Vector2(0, 0)
        self.dash_charges = 1
        self.max_dash_charges = 2
        
        # Visual effects
        self.trail_points = []
        self.max_trail_length = 10
        self.glow_pulse = 0
        
        # Stats
        self.kills = 0
        self.deaths = 0
        
        # Input buffering
        self.buffered_dash = False
        self.buffer_time = 0
        
        # DEBUG: Frame counter for render debugging
        self.render_count = 0
        
    def update(self, dt):
        """Update player state"""
        if not self.alive:
            return
            
        dt_sec = dt / 1000.0
        
        # Update dash cooldown and recharge
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
            if self.dash_cooldown <= 0 and self.dash_charges < self.max_dash_charges:
                self.dash_charges += 1
                self.dash_cooldown = PLAYER_DASH_COOLDOWN
                
        # Update input buffer
        if self.buffer_time > 0:
            self.buffer_time -= dt
            if self.buffer_time <= 0:
                self.buffered_dash = False
                
        # Update glow pulse
        self.glow_pulse += dt * 0.005
        
        # Handle dashing
        if self.is_dashing:
            self.dash_time += dt
            if self.dash_time >= PLAYER_DASH_DURATION:
                self.is_dashing = False
                self.dash_time = 0
            else:
                # Apply dash velocity with slight control
                dash_vel = self.dash_direction * PLAYER_DASH_SPEED
                self.vel = self.vel * 0.1 + dash_vel * 0.9
        else:
            # Normal movement
            keys = pygame.key.get_pressed()
            move_x = 0
            move_y = 0
            
            if keys[self.controls['up']]:
                move_y -= 1
            if keys[self.controls['down']]:
                move_y += 1
            if keys[self.controls['left']]:
                move_x -= 1
            if keys[self.controls['right']]:
                move_x += 1
                
            # Normalize diagonal movement
            if move_x != 0 and move_y != 0:
                move_x *= 0.707
                move_y *= 0.707
                
            # Apply movement with acceleration
            target_vel_x = move_x * PLAYER_SPEED
            target_vel_y = move_y * PLAYER_SPEED
            
            accel = 15 * dt_sec
            self.vel.x += (target_vel_x - self.vel.x) * accel
            self.vel.y += (target_vel_y - self.vel.y) * accel
            
            # Check for dash input
            if keys[self.controls['dash']]:
                if self.dash_charges > 0 and not self.buffered_dash:
                    if move_x != 0 or move_y != 0:
                        self.start_dash(move_x, move_y)
                    else:
                        # Buffer dash for next movement
                        self.buffered_dash = True
                        self.buffer_time = 100
            
            # Execute buffered dash
            if self.buffered_dash and (move_x != 0 or move_y != 0):
                self.start_dash(move_x, move_y)
                self.buffered_dash = False
                
        # Apply friction
        self.vel *= FRICTION
        
        # Clamp velocity
        max_vel = 800
        if self.vel.length() > max_vel:
            self.vel.scale_to_length(max_vel)
        
        # Update position
        self.pos += self.vel * dt_sec
        
        # Keep in bounds (with buffer)
        buffer = 50
        self.pos.x = max(-buffer, min(SCREEN_WIDTH + buffer, self.pos.x))
        self.pos.y = max(-buffer, min(SCREEN_HEIGHT + buffer, self.pos.y))
        
        # Update trail
        self.trail_points.append(self.pos.copy())
        if len(self.trail_points) > self.max_trail_length:
            self.trail_points.pop(0)
        
    def start_dash(self, dir_x, dir_y):
        """Start a dash"""
        if self.dash_charges <= 0:
            return
            
        self.is_dashing = True
        self.dash_time = 0
        self.dash_charges -= 1
        
        if self.dash_charges == 0:
            self.dash_cooldown = PLAYER_DASH_COOLDOWN
            
        self.dash_direction = pygame.math.Vector2(dir_x, dir_y).normalize()
        
    def eliminate(self):
        """Eliminate this player"""
        print(f"💀 Player {self.player_id} eliminated at ({self.pos.x:.1f}, {self.pos.y:.1f})")
        self.alive = False
        self.deaths += 1
        
    def respawn(self, x, y):
        """Respawn player"""
        print(f"🔄 Player {self.player_id} respawning at ({x:.1f}, {y:.1f})")
        self.pos.x = x
        self.pos.y = y
        self.vel.x = 0
        self.vel.y = 0
        self.alive = True
        self.dash_charges = self.max_dash_charges
        self.dash_cooldown = 0
        self.trail_points.clear()
        
    def render(self, screen, offset_x=0, offset_y=0):
        """Draw player with enhanced visuals"""
        # DEBUG: Print render call info every 60 frames
        self.render_count += 1
        if self.render_count % 60 == 0:
            print(f"🎨 Rendering Player {self.player_id}:")
            print(f"   Alive: {self.alive}")
            print(f"   Position: ({self.pos.x:.1f}, {self.pos.y:.1f})")
            print(f"   Screen pos: ({int(self.pos.x + offset_x)}, {int(self.pos.y + offset_y)})")
            print(f"   Offset: ({offset_x:.1f}, {offset_y:.1f})")
            print(f"   Radius: {self.radius}")
            print(f"   Color: {self.color}")
        
        if not self.alive:
            if self.render_count % 60 == 0:
                print(f"   ⚠️ Skipping render - player is dead")
            return
        
        # Calculate screen position
        x = int(self.pos.x + offset_x)
        y = int(self.pos.y + offset_y)
        
        # DEBUG: Check if position is on screen
        screen_rect = screen.get_rect()
        if self.render_count % 60 == 0:
            on_screen = screen_rect.collidepoint(x, y)
            print(f"   On screen: {on_screen} (Screen size: {screen.get_width()}x{screen.get_height()})")
        
        # Draw trail
        if len(self.trail_points) > 1 and self.is_dashing:
            for i, point in enumerate(self.trail_points):
                alpha = int(255 * (i / len(self.trail_points)))
                trail_radius = int(self.radius * (i / len(self.trail_points)))
                if trail_radius > 0:
                    try:
                        trail_surf = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(trail_surf, (*self.color, alpha // 2), 
                                         (trail_radius, trail_radius), trail_radius)
                        screen.blit(trail_surf, 
                                  (int(point.x + offset_x - trail_radius), 
                                   int(point.y + offset_y - trail_radius)))
                    except Exception as e:
                        print(f"⚠️ Trail render error: {e}")
        
        # Draw glow when dashing
        if self.is_dashing:
            try:
                glow_radius = self.radius + 8
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pulse = abs(math.sin(self.glow_pulse))
                glow_alpha = int(100 + pulse * 100)
                pygame.draw.circle(glow_surf, (*self.color, glow_alpha), 
                                 (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surf, (x - glow_radius, y - glow_radius))
            except Exception as e:
                print(f"⚠️ Glow render error: {e}")
        
        # Draw player circle with border (MAIN PLAYER RENDER)
        try:
            # White border
            pygame.draw.circle(screen, (255, 255, 255), (x, y), self.radius + 2)
            # Main colored circle
            pygame.draw.circle(screen, self.color, (x, y), self.radius)
            
            if self.render_count % 60 == 0:
                print(f"   ✅ Main circles drawn successfully")
                
        except Exception as e:
            print(f"❌ ERROR drawing main player circle: {e}")
            print(f"   Screen: {screen}")
            print(f"   Position: ({x}, {y})")
            print(f"   Radius: {self.radius}")
            print(f"   Color: {self.color}")
        
        # Draw direction indicator
        if self.vel.length() > 50:
            try:
                angle = math.atan2(self.vel.y, self.vel.x)
                end_x = x + int(math.cos(angle) * (self.radius + 5))
                end_y = y + int(math.sin(angle) * (self.radius + 5))
                pygame.draw.line(screen, (255, 255, 255), (x, y), (end_x, end_y), 3)
            except Exception as e:
                print(f"⚠️ Direction indicator error: {e}")
        
        # Draw dash charges
        try:
            charge_radius = 3
            charge_spacing = 8
            start_x = x - (self.max_dash_charges - 1) * charge_spacing // 2
            for i in range(self.max_dash_charges):
                charge_x = start_x + i * charge_spacing
                charge_y = y + self.radius + 8
                
                if i < self.dash_charges:
                    color = (100, 255, 100)
                else:
                    # Show cooldown progress
                    if i == self.dash_charges and self.dash_cooldown > 0:
                        progress = 1 - (self.dash_cooldown / PLAYER_DASH_COOLDOWN)
                        color = (50 + int(155 * progress), 100, 100)
                    else:
                        color = (50, 50, 50)
                        
                pygame.draw.circle(screen, color, (charge_x, charge_y), charge_radius)
        except Exception as e:
            print(f"⚠️ Dash charges render error: {e}")
        
        # Draw player number
        try:
            font = pygame.font.Font(None, 16)
            num_text = font.render(str(self.player_id + 1), True, (255, 255, 255))
            num_rect = num_text.get_rect(center=(x, y))
            screen.blit(num_text, num_rect)
        except Exception as e:
            print(f"⚠️ Player number render error: {e}")