"""
Player control mappings
"""
import pygame

# Player 1 - WASD
PLAYER_1_CONTROLS = {
    'up': pygame.K_w,
    'down': pygame.K_s,
    'left': pygame.K_a,
    'right': pygame.K_d,
    'dash': pygame.K_LSHIFT
}

# Player 2 - Arrow Keys
PLAYER_2_CONTROLS = {
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'dash': pygame.K_RSHIFT
}

# Player 3 - IJKL
PLAYER_3_CONTROLS = {
    'up': pygame.K_i,
    'down': pygame.K_k,
    'left': pygame.K_j,
    'right': pygame.K_l,
    'dash': pygame.K_u
}

# Player 4 - Numpad
PLAYER_4_CONTROLS = {
    'up': pygame.K_KP8,
    'down': pygame.K_KP5,
    'left': pygame.K_KP4,
    'right': pygame.K_KP6,
    'dash': pygame.K_KP0
}

# Master control list
PLAYER_CONTROLS = [
    PLAYER_1_CONTROLS,
    PLAYER_2_CONTROLS,
    PLAYER_3_CONTROLS,
    PLAYER_4_CONTROLS
]