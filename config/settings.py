"""
Game configuration and constants
"""
import pygame

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "CROWD CONTROL"

# Colors
COLORS = {
    'BG': (20, 20, 30),
    'TEXT': (220, 220, 220),
    'HIGHLIGHT': (100, 200, 255),
    'PLATFORM': (50, 50, 70),
    'DANGER': (200, 50, 50)
}

# Player colors
PLAYER_COLORS = [
    (255, 100, 100),  # Red
    (100, 150, 255),  # Blue
    (100, 255, 100),  # Green
    (255, 200, 100)   # Orange
]

# Player settings
PLAYER_RADIUS = 20
PLAYER_SPEED = 300
PLAYER_DASH_SPEED = 600
PLAYER_DASH_DURATION = 150
PLAYER_DASH_COOLDOWN = 1000
PLAYER_MAX_HEALTH = 100

# Platform settings
PLATFORM_START_RADIUS = 300
PLATFORM_MIN_RADIUS = 100
SHRINK_START_TIME = 10000  # 10 seconds
SHRINK_RATE = 20  # pixels per second

# Game rules
PLAYER_COUNT = 4
ROUND_TIME = 120000  # 2 minutes in milliseconds
ROUNDS_TO_WIN = 3

# Physics
FRICTION = 0.92
BOUNCE_FACTOR = 0.5
COLLISION_PUSH = 250

# Effects
PARTICLE_LIFETIME = 1000
SCREENSHAKE_INTENSITY = 10
SCREENSHAKE_DURATION = 300

# Audio
AUDIO_ENABLED = True
AUDIO_VOLUME = 0.5