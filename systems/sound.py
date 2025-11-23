"""
Enhanced sound manager with procedural audio generation
"""
import pygame
import math
import numpy as np

class SoundManager:
    """Enhanced sound manager with better audio generation"""
    def __init__(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.enabled = True
        except:
            print("Warning: Audio system failed to initialize")
            self.enabled = False
            
        self.sounds = {}
        self.volume = 0.5
        self.music_volume = 0.3
        
    def generate_tone(self, frequency, duration, volume=0.3, wave_type='sine'):
        """Generate a tone with different waveforms"""
        if not self.enabled:
            return None
            
        sample_rate = 22050
        n_samples = int(duration * sample_rate / 1000)
        
        samples = np.zeros((n_samples, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            
            if wave_type == 'sine':
                value = math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'square':
                value = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
            elif wave_type == 'triangle':
                value = 2 * abs(2 * ((frequency * t) % 1) - 1) - 1
            elif wave_type == 'sawtooth':
                value = 2 * ((frequency * t) % 1) - 1
            else:
                value = 0
                
            # Apply envelope (fade in/out)
            envelope = 1.0
            fade_duration = min(n_samples // 10, 1000)
            if i < fade_duration:
                envelope = i / fade_duration
            elif i > n_samples - fade_duration:
                envelope = (n_samples - i) / fade_duration
                
            sample_value = int(max_sample * volume * value * envelope)
            samples[i] = [sample_value, sample_value]
            
        return pygame.sndarray.make_sound(samples)
        
    def generate_noise(self, duration, volume=0.2):
        """Generate white noise"""
        if not self.enabled:
            return None
            
        sample_rate = 22050
        n_samples = int(duration * sample_rate / 1000)
        
        # Generate random samples
        samples = np.random.randint(-32768, 32767, (n_samples, 2), dtype=np.int16)
        samples = (samples * volume).astype(np.int16)
        
        return pygame.sndarray.make_sound(samples)
        
    def generate_sweep(self, start_freq, end_freq, duration, volume=0.3):
        """Generate frequency sweep"""
        if not self.enabled:
            return None
            
        sample_rate = 22050
        n_samples = int(duration * sample_rate / 1000)
        
        samples = np.zeros((n_samples, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            progress = i / n_samples
            
            # Linear frequency sweep
            freq = start_freq + (end_freq - start_freq) * progress
            value = math.sin(2 * math.pi * freq * t)
            
            # Envelope
            envelope = 1.0 - (i / n_samples) * 0.5
            
            sample_value = int(max_sample * volume * value * envelope)
            samples[i] = [sample_value, sample_value]
            
        return pygame.sndarray.make_sound(samples)
        
    def play_collision(self, intensity=1.0):
        """Play collision sound"""
        if not self.enabled:
            return
            
        key = f'collision_{int(intensity * 10)}'
        if key not in self.sounds:
            # Higher pitch for stronger collision
            freq = 200 + intensity * 200
            self.sounds[key] = self.generate_tone(freq, 100, 0.2 * intensity, 'square')
            
        if self.sounds[key]:
            self.sounds[key].set_volume(self.volume)
            self.sounds[key].play()
        
    def play_elimination(self):
        """Play elimination sound"""
        if not self.enabled:
            return
            
        if 'elimination' not in self.sounds:
            self.sounds['elimination'] = self.generate_sweep(400, 100, 500, 0.3)
            
        if self.sounds['elimination']:
            self.sounds['elimination'].set_volume(self.volume)
            self.sounds['elimination'].play()
        
    def play_dash(self):
        """Play dash sound"""
        if not self.enabled:
            return
            
        if 'dash' not in self.sounds:
            self.sounds['dash'] = self.generate_sweep(300, 600, 150, 0.25)
            
        if self.sounds['dash']:
            self.sounds['dash'].set_volume(self.volume)
            self.sounds['dash'].play()
        
    def play_menu_select(self):
        """Play menu selection sound"""
        if not self.enabled:
            return
            
        if 'select' not in self.sounds:
            self.sounds['select'] = self.generate_tone(440, 50, 0.15, 'sine')
            
        if self.sounds['select']:
            self.sounds['select'].set_volume(self.volume)
            self.sounds['select'].play()
            
    def play_menu_move(self):
        """Play menu move sound"""
        if not self.enabled:
            return
            
        if 'move' not in self.sounds:
            self.sounds['move'] = self.generate_tone(330, 30, 0.1, 'sine')
            
        if self.sounds['move']:
            self.sounds['move'].set_volume(self.volume)
            self.sounds['move'].play()
            
    def play_victory(self):
        """Play victory jingle"""
        if not self.enabled:
            return
            
        if 'victory' not in self.sounds:
            self.sounds['victory'] = self.generate_sweep(440, 880, 800, 0.3)
            
        if self.sounds['victory']:
            self.sounds['victory'].set_volume(self.volume)
            self.sounds['victory'].play()
            
    def play_countdown(self, number):
        """Play countdown beep"""
        if not self.enabled:
            return
            
        freq = 440 + (3 - number) * 110
        key = f'countdown_{number}'
        if key not in self.sounds:
            self.sounds[key] = self.generate_tone(freq, 100, 0.2, 'square')
            
        if self.sounds[key]:
            self.sounds[key].set_volume(self.volume)
            self.sounds[key].play()
            
    def play_platform_shrink(self):
        """Play platform shrink warning"""
        if not self.enabled:
            return
            
        if 'shrink' not in self.sounds:
            self.sounds['shrink'] = self.generate_tone(220, 200, 0.15, 'sawtooth')
            
        if self.sounds['shrink']:
            self.sounds['shrink'].set_volume(self.volume * 0.5)
            self.sounds['shrink'].play()
        
    def set_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        
    def toggle(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        return self.enabled