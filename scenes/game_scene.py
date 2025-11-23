"""
CROWD CONTROL V3.0 - Master Integration
Enhanced game scene with ALL new features - FIXED RENDERING
"""
import pygame
import random
from scenes.scene_manager import Scene
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, PLAYER_COLORS,
    ROUND_TIME, SHRINK_START_TIME, PLAYER_COUNT
)
from config.controls import PLAYER_CONTROLS
from entities.player import Player
from entities.ai_player import AIPlayer, AIManager
from entities.platform import Platform
from entities.powerup import PowerUpManager, PowerUpEffect, PowerUpType
from systems.particles import ParticleSystem
from systems.screenshake import ScreenShake
from systems.sound import SoundManager
from systems.vfx import VFXManager, TrailRenderer, ImpactEffect
from systems.replay import ReplayRecorder
from ui.hud import AdvancedHUD
from ui.transitions import FadeTransition
from core.physics import check_collision, resolve_collision, SpatialGrid

class GameScene(Scene):
    """Enhanced gameplay scene with ALL V3.0 features"""
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.player_count = 2
        self.ai_count = 0  # Number of AI players
        self.players = []
        self.platform = None
        
        # Enhanced systems
        self.particles = ParticleSystem(pool_size=2000)  # More particles!
        self.screen_shake = ScreenShake()
        self.sound_manager = SoundManager()
        self.hud = AdvancedHUD()
        self.spatial_grid = SpatialGrid()
        
        # NEW V3.0 Systems
        self.vfx_manager = VFXManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.trail_renderer = TrailRenderer()
        self.impact_effects = ImpactEffect()
        self.powerup_manager = PowerUpManager()
        self.ai_manager = AIManager()
        self.replay_recorder = ReplayRecorder()
        
        # Game state
        self.round_time = 0
        self.game_over = False
        self.winner = None
        self.scores = [0] * PLAYER_COUNT
        self.countdown = 3
        self.countdown_time = 0
        self.game_started = False
        self.shrink_warned = False
        self.last_shrink_warning = 0
        
        # Recording
        self.is_recording = False
        
        # VFX toggle (set to False to disable VFX if causing issues)
        self.enable_vfx = False  # Changed to False for stability
        
    def on_enter(self):
        """Start new round"""
        self._setup_round()
        
    def _setup_round(self):
        """Initialize round"""
        self.round_time = 0
        self.game_over = False
        self.winner = None
        self.countdown = 3
        self.countdown_time = 0
        self.game_started = False
        self.shrink_warned = False
        
        # Create platform
        self.platform = Platform()
        
        # Create players (mix human and AI)
        self.players = []
        spawn_radius = 150
        angle_step = 360 / (self.player_count + self.ai_count)
        
        # Human players
        for i in range(self.player_count):
            angle = i * angle_step
            x = SCREEN_WIDTH // 2 + spawn_radius * pygame.math.Vector2(1, 0).rotate(angle).x
            y = SCREEN_HEIGHT // 2 + spawn_radius * pygame.math.Vector2(1, 0).rotate(angle).y
            
            player = Player(x, y, PLAYER_COLORS[i], i, PLAYER_CONTROLS[i])
            self.players.append(player)
            
        # AI players
        for i in range(self.ai_count):
            idx = self.player_count + i
            angle = idx * angle_step
            x = SCREEN_WIDTH // 2 + spawn_radius * pygame.math.Vector2(1, 0).rotate(angle).x
            y = SCREEN_HEIGHT // 2 + spawn_radius * pygame.math.Vector2(1, 0).rotate(angle).y
            
            ai_player = AIPlayer(x, y, PLAYER_COLORS[idx], idx, 
                               PLAYER_CONTROLS[idx % len(PLAYER_CONTROLS)], 
                               difficulty='medium')
            self.players.append(ai_player)
            self.ai_manager.add_ai(ai_player)
            
        # Reset systems
        self.particles.clear()
        self.screen_shake.reset()
        self.trail_renderer.clear()
        self.impact_effects.clear()
        self.powerup_manager.clear()
        
        # Start replay recording
        if self.is_recording:
            colors = [p.color for p in self.players]
            self.replay_recorder.start_recording(len(self.players), colors)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                transition = FadeTransition(duration=300)
                self.scene_manager.change_scene('menu', transition)
            elif event.key == pygame.K_r and self.game_over:
                self._setup_round()
            elif event.key == pygame.K_m:
                enabled = self.sound_manager.toggle()
                print(f"Sound: {'ON' if enabled else 'OFF'}")
            elif event.key == pygame.K_F1:
                # Toggle recording
                self.is_recording = not self.is_recording
                if not self.is_recording and len(self.replay_recorder.frames) > 0:
                    filename = f"replay_{int(pygame.time.get_ticks())}.json"
                    path = self.replay_recorder.save_replay(filename)
                    print(f"Replay saved: {path}")
            elif event.key == pygame.K_v:
                # Toggle VFX (V key)
                self.enable_vfx = not self.enable_vfx
                print(f"VFX: {'ON' if self.enable_vfx else 'OFF'}")
                
    def update(self, dt):
        # Countdown phase
        if not self.game_started:
            self.countdown_time += dt
            if self.countdown_time >= 1000:
                self.countdown_time = 0
                self.countdown -= 1
                self.sound_manager.play_countdown(self.countdown)
                
                if self.countdown <= 0:
                    self.game_started = True
                    self.sound_manager.play_menu_select()
            
            self.particles.update(dt)
            self.vfx_manager.update(dt)
            return
            
        if self.game_over:
            self.particles.update(dt)
            self.screen_shake.update(dt)
            self.vfx_manager.update(dt)
            self.trail_renderer.update(dt)
            self.impact_effects.update(dt)
            return
            
        self.round_time += dt
        
        # Platform shrink warnings
        if self.round_time > SHRINK_START_TIME - 3000 and not self.shrink_warned:
            self.shrink_warned = True
            self.sound_manager.play_platform_shrink()
            if self.enable_vfx:
                self.vfx_manager.add_distortion(0.5, 1000)
            
        if self.round_time > SHRINK_START_TIME:
            if self.round_time - self.last_shrink_warning > 5000:
                self.last_shrink_warning = self.round_time
                self.sound_manager.play_platform_shrink()
                
        # Update platform
        if self.round_time > SHRINK_START_TIME:
            self.platform.update(dt)
            
        # Update AI
        self.ai_manager.update(dt, self.players, self.platform)
        
        # Update power-ups
        self.powerup_manager.update(dt, self.platform)
        
        # Update spatial grid
        self.spatial_grid.clear()
        
        # Update players
        alive_players = []
        for player in self.players:
            if player.alive:
                actual_dt = self.screen_shake.update(dt)
                player.update(actual_dt)
                
                # Check power-up pickup
                powerup_type = self.powerup_manager.check_pickups(player)
                if powerup_type:
                    self._apply_powerup(player, powerup_type)
                    self.sound_manager.play_menu_select()
                    self.particles.emit_sparkle(player.pos.x, player.pos.y, player.color)
                
                # Check platform collision
                if not self.platform.contains_point(player.pos):
                    player.eliminate()
                    self._on_player_eliminated(player)
                else:
                    alive_players.append(player)
                    self.spatial_grid.insert(player)
                    
                # Trail effects
                if player.is_dashing and player.vel.length() > 100:
                    self.particles.emit_trail(player.pos.x, player.pos.y,
                                            player.color, player.vel.x, player.vel.y)
                    self.trail_renderer.add_trail(player.pos.x, player.pos.y,
                                                 player.color, player.radius, 300)
                    
        # Collision detection
        checked_pairs = set()
        for p1 in alive_players:
            nearby = self.spatial_grid.get_nearby(p1)
            for p2 in nearby:
                if p1 != p2 and p1.alive and p2.alive:
                    pair = tuple(sorted([id(p1), id(p2)]))
                    if pair not in checked_pairs:
                        checked_pairs.add(pair)
                        
                        if check_collision(p1, p2):
                            resolve_collision(p1, p2)
                            
                            # Enhanced collision effects
                            mid_x = (p1.pos.x + p2.pos.x) / 2
                            mid_y = (p1.pos.y + p2.pos.y) / 2
                            impact = min(1.0, (p1.vel.length() + p2.vel.length()) / 1000)
                            
                            # Particles
                            self.particles.emit(mid_x, mid_y, (255, 255, 255), 
                                              count=int(10 + impact * 20), 
                                              speed=150 + impact * 200)
                            
                            # Impact ring effect
                            self.impact_effects.add_impact(mid_x, mid_y, (255, 255, 255),
                                                          size=30 + int(impact * 30))
                            
                            # Screen effects
                            self.screen_shake.add_trauma(0.3 * impact)
                            if impact > 0.6:
                                self.screen_shake.hitstop(40)
                                if self.enable_vfx:
                                    self.vfx_manager.add_chromatic_aberration(0.5, 200)
                                    self.vfx_manager.add_bloom(0.3, 300)
                                
                            self.sound_manager.play_collision(impact)
                            self.hud.add_hit()
                    
        # Check win condition
        if len(alive_players) <= 1:
            self._end_round(alive_players[0] if alive_players else None)
            
        # Update all systems
        self.particles.update(dt)
        self.vfx_manager.update(dt)
        self.trail_renderer.update(dt)
        self.impact_effects.update(dt)
        self.hud.update(dt)
        
        # Record frame for replay
        if self.is_recording:
            game_state = self._capture_game_state()
            self.replay_recorder.record_frame(game_state)
        
    def _apply_powerup(self, player, powerup_type):
        """Apply power-up effect to player"""
        if powerup_type == PowerUpType.SPEED_BOOST:
            # Increase speed temporarily
            player.dash_charges = min(player.max_dash_charges, player.dash_charges + 1)
        elif powerup_type == PowerUpType.SHIELD:
            # Add shield (would need to implement in Player class)
            pass
        elif powerup_type == PowerUpType.TRIPLE_DASH:
            player.dash_charges = player.max_dash_charges
            
    def _on_player_eliminated(self, player):
        """Enhanced elimination effects"""
        # Massive particle explosion
        self.particles.emit_explosion(player.pos.x, player.pos.y, player.color, intensity=80)
        
        # Screen effects
        self.screen_shake.add_trauma(0.8)
        self.screen_shake.hitstop(150)
        
        if self.enable_vfx:
            self.vfx_manager.add_chromatic_aberration(1.0, 500)
            self.vfx_manager.add_distortion(0.8, 400)
        
        # Impact ring
        self.impact_effects.add_impact(player.pos.x, player.pos.y, player.color, size=80, duration=500)
        
        # Sound
        self.sound_manager.play_elimination()
        
        # HUD notification
        self.hud.add_elimination(player.player_id, player.color, "fell off")
        
    def _end_round(self, winner):
        """End round with enhanced effects"""
        self.game_over = True
        self.winner = winner
        
        if winner:
            self.scores[winner.player_id] += 1
            winner.kills += 1
            
            # Victory effects
            for _ in range(150):
                angle = random.uniform(0, 360)
                speed = random.uniform(150, 500)
                self.particles.emit(winner.pos.x, winner.pos.y, winner.color,
                                  count=1, speed=speed, lifetime=2000, gravity=300)
                
            # Victory VFX
            if self.enable_vfx:
                self.vfx_manager.add_bloom(0.8, 2000)
                self.vfx_manager.add_chromatic_aberration(0.3, 1000)
            self.screen_shake.add_trauma(0.4)
            
            self.sound_manager.play_victory()
            
        # Stop recording
        if self.is_recording:
            self.replay_recorder.stop_recording()
                
    def _capture_game_state(self):
        """Capture current game state for replay"""
        return {
            'platform_radius': self.platform.radius,
            'round_time': self.round_time,
            'players': [
                {
                    'pos_x': p.pos.x,
                    'pos_y': p.pos.y,
                    'vel_x': p.vel.x,
                    'vel_y': p.vel.y,
                    'alive': p.alive,
                    'is_dashing': p.is_dashing,
                    'color': p.color
                } for p in self.players
            ]
        }
            
    def render(self, screen):
        """Enhanced rendering with VFX - FIXED VERSION"""
        # Clear screen
        screen.fill(COLORS['BG'])
        
        # Get screen shake offset
        offset_x, offset_y = self.screen_shake.get_offset()
        
        if self.enable_vfx:
            # Render with VFX post-processing
            self._render_with_vfx(screen, offset_x, offset_y)
        else:
            # Render directly to screen (stable, guaranteed to work)
            self._render_direct(screen, offset_x, offset_y)
        
        # Render HUD on top (no effects)
        if self.game_started:
            time_left = max(0, ROUND_TIME - self.round_time)
            self.hud.render(screen, self.players, self.scores, time_left)
            
        # Countdown overlay
        if not self.game_started:
            self._render_countdown(screen)
        
        # Game over overlay
        if self.game_over:
            self._render_game_over(screen)
            
        # Recording indicator
        if self.is_recording:
            rec_text = pygame.font.Font(None, 24).render("● REC", True, (255, 0, 0))
            screen.blit(rec_text, (SCREEN_WIDTH - 80, 10))
            
        # VFX status indicator
        vfx_text = pygame.font.Font(None, 20).render(
            f"VFX: {'ON' if self.enable_vfx else 'OFF'} (V to toggle)", 
            True, (150, 150, 150))
        screen.blit(vfx_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 25))
    
    def _render_direct(self, screen, offset_x, offset_y):
        """Render directly to screen without VFX post-processing"""
        # Render game elements
        self.platform.render(screen, offset_x, offset_y)
        self.trail_renderer.render(screen, offset_x, offset_y)
        self.powerup_manager.render(screen, offset_x, offset_y)
        self.particles.render(screen, offset_x, offset_y)
        self.impact_effects.render(screen, offset_x, offset_y)
        
        # Render players
        for player in self.players:
            if player.alive:
                player.render(screen, offset_x, offset_y)
    
    def _render_with_vfx(self, screen, offset_x, offset_y):
        """Render with VFX post-processing"""
        try:
            # Create game surface
            game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            game_surface.fill(COLORS['BG'])
            
            # Render game elements to surface
            self.platform.render(game_surface, offset_x, offset_y)
            self.trail_renderer.render(game_surface, offset_x, offset_y)
            self.powerup_manager.render(game_surface, offset_x, offset_y)
            self.particles.render(game_surface, offset_x, offset_y)
            self.impact_effects.render(game_surface, offset_x, offset_y)
            
            # Render players to surface
            for player in self.players:
                if player.alive:
                    player.render(game_surface, offset_x, offset_y)
            
            # Apply VFX post-processing
            processed_surface = game_surface.copy()
            
            if self.vfx_manager.chromatic_aberration > 0:
                processed_surface = self.vfx_manager.apply_chromatic_aberration(
                    processed_surface, self.vfx_manager.chromatic_aberration)
                
            if self.vfx_manager.bloom_intensity > 0:
                processed_surface = self.vfx_manager.apply_bloom(
                    processed_surface, self.vfx_manager.bloom_intensity)
                
            if self.vfx_manager.distortion > 0:
                processed_surface = self.vfx_manager.apply_distortion(
                    processed_surface, self.vfx_manager.distortion)
            
            # Apply vignette
            processed_surface = self.vfx_manager.apply_vignette(
                processed_surface, self.vfx_manager.vignette_intensity)
            
            # Blit to screen
            screen.blit(processed_surface, (0, 0))
            
        except Exception as e:
            print(f"⚠️ VFX rendering failed: {e}")
            # Fallback to direct rendering
            self._render_direct(screen, offset_x, offset_y)
            
    def _render_countdown(self, screen):
        """Render countdown with effects"""
        if self.countdown > 0:
            font = pygame.font.Font(None, 200)
            text = font.render(str(self.countdown), True, COLORS['HIGHLIGHT'])
            
            scale = 1.8 - (self.countdown_time / 1000) * 0.8
            scaled_text = pygame.transform.scale(text, 
                (int(text.get_width() * scale), int(text.get_height() * scale)))
            
            rect = scaled_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            
            # Glow effect
            for offset in [(3, 3), (-3, -3), (3, -3), (-3, 3)]:
                screen.blit(scaled_text, (rect.x + offset[0], rect.y + offset[1]))
                
            screen.blit(scaled_text, rect)
        else:
            font = pygame.font.Font(None, 120)
            text = font.render("FIGHT!", True, (255, 100, 100))
            rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, rect)
            
    def _render_game_over(self, screen):
        """Render enhanced game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 100)
        font_medium = pygame.font.Font(None, 40)
        font_small = pygame.font.Font(None, 28)
        
        if self.winner:
            text = font_large.render(f"PLAYER {self.winner.player_id + 1} WINS!", 
                                    True, self.winner.color)
        else:
            text = font_large.render("DRAW!", True, COLORS['TEXT'])
            
        rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        screen.blit(text, rect)
        
        # Stats
        if self.winner and hasattr(self.winner, 'kills'):
            stats_text = font_small.render(
                f"Kills: {self.winner.kills} | Max Combo: {self.hud.combo_tracker.max_combo}",
                True, (200, 200, 200))
            stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            screen.blit(stats_text, stats_rect)
        
        # Instructions
        inst = font_medium.render("R: Restart | ESC: Menu | F1: Save Replay | M: Sound | V: VFX", 
                                 True, COLORS['TEXT'])
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        screen.blit(inst, inst_rect)