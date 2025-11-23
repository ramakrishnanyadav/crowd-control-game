"""
Replay recording and playback system
"""
import pygame
import json
import time
from pathlib import Path

class ReplayFrame:
    """Single frame of replay data"""
    def __init__(self, timestamp, game_state):
        self.timestamp = timestamp
        self.players = []
        self.platform_radius = game_state.get('platform_radius', 300)
        self.round_time = game_state.get('round_time', 0)
        
        # Record player states
        for player_data in game_state.get('players', []):
            self.players.append({
                'pos': (player_data['pos_x'], player_data['pos_y']),
                'vel': (player_data['vel_x'], player_data['vel_y']),
                'alive': player_data['alive'],
                'is_dashing': player_data.get('is_dashing', False),
                'color': player_data['color']
            })
            
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp,
            'players': self.players,
            'platform_radius': self.platform_radius,
            'round_time': self.round_time
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        frame = cls.__new__(cls)
        frame.timestamp = data['timestamp']
        frame.players = data['players']
        frame.platform_radius = data['platform_radius']
        frame.round_time = data['round_time']
        return frame

class ReplayRecorder:
    """Records gameplay for replay"""
    def __init__(self):
        self.recording = False
        self.frames = []
        self.start_time = 0
        self.metadata = {}
        
    def start_recording(self, player_count, player_colors):
        """Start recording"""
        self.recording = True
        self.frames = []
        self.start_time = time.time()
        self.metadata = {
            'player_count': player_count,
            'player_colors': player_colors,
            'start_time': self.start_time
        }
        
    def stop_recording(self):
        """Stop recording"""
        self.recording = False
        
    def record_frame(self, game_state):
        """Record a single frame"""
        if not self.recording:
            return
            
        timestamp = time.time() - self.start_time
        frame = ReplayFrame(timestamp, game_state)
        self.frames.append(frame)
        
    def save_replay(self, filename='replay.json'):
        """Save replay to file"""
        replay_dir = Path('replays')
        replay_dir.mkdir(exist_ok=True)
        
        filepath = replay_dir / filename
        
        data = {
            'metadata': self.metadata,
            'frames': [frame.to_dict() for frame in self.frames]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
            
        return str(filepath)
        
    def get_duration(self):
        """Get recording duration in seconds"""
        if not self.frames:
            return 0
        return self.frames[-1].timestamp

class ReplayPlayer:
    """Plays back recorded replays"""
    def __init__(self):
        self.playing = False
        self.frames = []
        self.current_frame_index = 0
        self.playback_time = 0
        self.playback_speed = 1.0
        self.metadata = {}
        self.paused = False
        
    def load_replay(self, filename):
        """Load replay from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            self.metadata = data['metadata']
            self.frames = [ReplayFrame.from_dict(frame) for frame in data['frames']]
            self.current_frame_index = 0
            self.playback_time = 0
            
            return True
        except Exception as e:
            print(f"Failed to load replay: {e}")
            return False
            
    def start_playback(self):
        """Start replay playback"""
        self.playing = True
        self.paused = False
        self.playback_time = 0
        self.current_frame_index = 0
        
    def stop_playback(self):
        """Stop playback"""
        self.playing = False
        
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        
    def set_speed(self, speed):
        """Set playback speed (0.25x to 2.0x)"""
        self.playback_speed = max(0.25, min(2.0, speed))
        
    def seek(self, timestamp):
        """Seek to specific timestamp"""
        self.playback_time = timestamp
        self.current_frame_index = 0
        
        # Find closest frame
        for i, frame in enumerate(self.frames):
            if frame.timestamp > timestamp:
                self.current_frame_index = max(0, i - 1)
                break
                
    def update(self, dt):
        """Update playback"""
        if not self.playing or self.paused:
            return None
            
        # Advance playback time
        self.playback_time += (dt / 1000.0) * self.playback_speed
        
        # Find current frame
        while (self.current_frame_index < len(self.frames) and 
               self.frames[self.current_frame_index].timestamp < self.playback_time):
            self.current_frame_index += 1
            
        # Check if replay ended
        if self.current_frame_index >= len(self.frames):
            self.playing = False
            return None
            
        return self.frames[self.current_frame_index]
        
    def get_current_frame(self):
        """Get current frame"""
        if 0 <= self.current_frame_index < len(self.frames):
            return self.frames[self.current_frame_index]
        return None
        
    def get_progress(self):
        """Get playback progress (0.0 to 1.0)"""
        if not self.frames:
            return 0.0
        return min(1.0, self.playback_time / self.frames[-1].timestamp)

class ReplayUI:
    """UI for replay controls"""
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
    def render_controls(self, screen, replay_player):
        """Render replay controls"""
        if not replay_player.playing:
            return
            
        # Control bar at bottom
        bar_height = 80
        bar_y = screen.get_height() - bar_height
        
        # Semi-transparent background
        bg = pygame.Surface((screen.get_width(), bar_height), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 200))
        screen.blit(bg, (0, bar_y))
        
        # Progress bar
        progress = replay_player.get_progress()
        bar_width = screen.get_width() - 40
        bar_x = 20
        progress_y = bar_y + 20
        
        # Background bar
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, progress_y, bar_width, 10))
        
        # Progress fill
        fill_width = int(bar_width * progress)
        pygame.draw.rect(screen, (100, 200, 255), (bar_x, progress_y, fill_width, 10))
        
        # Time display
        current_time = replay_player.playback_time
        total_time = replay_player.frames[-1].timestamp if replay_player.frames else 0
        
        time_text = f"{int(current_time)}s / {int(total_time)}s"
        time_surf = self.font.render(time_text, True, (255, 255, 255))
        screen.blit(time_surf, (bar_x, progress_y + 20))
        
        # Speed display
        speed_text = f"Speed: {replay_player.playback_speed:.2f}x"
        speed_surf = self.font.render(speed_text, True, (255, 255, 255))
        screen.blit(speed_surf, (bar_x + 150, progress_y + 20))
        
        # Pause indicator
        if replay_player.paused:
            pause_text = self.font.render("PAUSED", True, (255, 200, 50))
            pause_rect = pause_text.get_rect(center=(screen.get_width() // 2, progress_y + 25))
            screen.blit(pause_text, pause_rect)
            
        # Controls help
        help_text = "SPACE: Pause | +/-: Speed | R: Restart | ESC: Exit"
        help_surf = self.font_small.render(help_text, True, (180, 180, 180))
        screen.blit(help_surf, (bar_x, progress_y + 50))