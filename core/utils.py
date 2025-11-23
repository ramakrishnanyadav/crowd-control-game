"""
Utility functions for the game
"""
import math

def lerp(start, end, t):
    """Linear interpolation between start and end"""
    return start + (end - start) * t

def distance(x1, y1, x2, y2):
    """Calculate distance between two points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def clamp(value, min_value, max_value):
    """Clamp value between min and max"""
    return max(min_value, min(value, max_value))

def normalize_vector(x, y):
    """Normalize a vector to unit length"""
    length = math.sqrt(x * x + y * y)
    if length == 0:
        return 0, 0
    return x / length, y / length

def angle_between(x1, y1, x2, y2):
    """Get angle between two points in degrees"""
    return math.degrees(math.atan2(y2 - y1, x2 - x1))