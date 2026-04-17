import minescript as ms
import time
import os
import random
import math
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any
from enum import Enum

# ============= CONFIGURATION =============
LOG_FILE = "minescript/logs.txt"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

EYE_HEIGHT = 1.62
STEP_DEG = 5  # Base degrees per step

# Movement configuration thresholds
@dataclass
class MovementConfig:
    """Configuration for movement based on rotation distance."""
    max_move: float
    curve_range: Tuple[float, float]
    delay_range: Tuple[float, float]
    entity_multiplier: Optional[Tuple[float, float]] = None
    step_multiplier: float = 1.0

# Movement configurations sorted by threshold
MOVEMENT_CONFIGS = [
    MovementConfig(8, (0, 0.3), (0.8, 1.1), (1.8, 2.1), 1.5),  # Tiny moves
    MovementConfig(33, (0, 0.3), (0.8, 1.1), None, 1.0),        # Small moves
    MovementConfig(70, (1, 4), (0.8, 1.0), None, 1.0),          # Medium moves
    MovementConfig(140, (1.5, 6), (0.75, 1.0), None, 1.0),      # Large moves
    MovementConfig(float('inf'), (2.2, 7), (0.7, 0.85), None, 1.0) # Extra large
]

# Special multipliers
ENTITY_SMALL_MOVE_MULTIPLIER = (0.6, 0.73)  # For total_move < 8 and is_entity
ENTITY_LARGE_MOVE_MULTIPLIER = (0.55, 0.64)  # For total_move > 60 and is_entity

# Jitter and randomization constants
JITTER_RANGE = (-0.12, 0.12)
SLEEP_JITTER = (-0.001, 0.001)
STEP_RANDOM_FACTOR = (0.8, 1.5)
STEP_RANDOM_FACTOR_SMALL_ENTITY = (0.8, 1.5)

# Block targeting offsets
BLOCK_OFFSET = 0.5
BLOCK_XZ_RANDOM = 159
BLOCK_Y_RANDOM = 39
ENTITY_TARGET_HEIGHT = 0.4

# ============= HELPER FUNCTIONS =============
def normalize(angle: float) -> float:
    """Normalize angle to [-180, 180] degrees."""
    angle %= 360
    if angle > 180:
        angle -= 360
    elif angle < -180:
        angle += 360
    return angle

def calculate_target(x: float, y: float, z: float, is_entity: bool) -> Tuple[float, float, float]:
    """Calculate the exact target position with appropriate offsets."""
    if not is_entity:
        return (
            x + BLOCK_OFFSET + random.uniform(-BLOCK_XZ_RANDOM, BLOCK_XZ_RANDOM) / 1000,
            y + BLOCK_OFFSET + random.uniform(-BLOCK_Y_RANDOM, BLOCK_Y_RANDOM) / 1000,
            z + BLOCK_OFFSET + random.uniform(-BLOCK_XZ_RANDOM, BLOCK_XZ_RANDOM) / 1000
        )
    return (x, y + ENTITY_TARGET_HEIGHT, z)

def calculate_desired_angles(target: Tuple[float, float, float], 
                            player_pos: Tuple[float, float, float]) -> Tuple[float, float]:
    """Calculate desired yaw and pitch to face the target."""
    ex, ey, ez = player_pos
    tx, ty, tz = target
    
    dx, dy, dz = tx - ex, ty - (ey + EYE_HEIGHT), tz - ez
    horizontal_dist = math.hypot(dx, dz)
    
    desired_yaw = -math.degrees(math.atan2(dx, dz))
    desired_pitch = -math.degrees(math.atan2(dy, horizontal_dist))
    
    return desired_yaw, desired_pitch

def get_movement_config(total_move: float, is_entity: bool) -> Tuple[Tuple[float, float], float, float]:
    """Get movement configuration based on total rotation distance."""
    # Find appropriate config
    config = next(cfg for cfg in MOVEMENT_CONFIGS if total_move < cfg.max_move)
    
    # Apply base delay multiplier
    delay_multiplier = random.uniform(*config.delay_range)
    
    # Apply entity-specific multipliers
    if is_entity:
        if total_move < 8:
            delay_multiplier *= random.uniform(*ENTITY_SMALL_MOVE_MULTIPLIER)
        elif total_move > 60:
            delay_multiplier *= random.uniform(*ENTITY_LARGE_MOVE_MULTIPLIER)
        
        if config.entity_multiplier:
            delay_multiplier *= random.uniform(*config.entity_multiplier)
    
    return config.curve_range, delay_multiplier, config.step_multiplier

def calculate_steps(delta_y: float, delta_p: float, total_move: float, 
                   is_entity: bool, step_multiplier: float) -> int:
    """Calculate number of steps for smooth rotation."""
    # Determine step factor based on movement type
    if total_move < 8 and is_entity:
        step_factor = 1.5 * random.uniform(*STEP_RANDOM_FACTOR_SMALL_ENTITY)
    else:
        step_factor = random.uniform(*STEP_RANDOM_FACTOR)
    
    # Calculate steps needed
    steps_y = abs(delta_y) / STEP_DEG * step_factor * step_multiplier
    steps_p = abs(delta_p) / STEP_DEG * step_factor * step_multiplier
    
    return max(1, int(steps_y), int(steps_p))

def apply_rotation_step(yaw: float, pitch: float, delta_y: float, delta_p: float,
                       frac: float, perp_yaw: float, perp_pitch: float,
                       curve_strength: float, base_delay: float) -> None:
    """Apply a single rotation step with curve and jitter."""
    # Linear interpolation
    base_yaw = yaw + delta_y * frac
    base_pitch = pitch + delta_p * frac
    
    # Sine curve for natural movement
    curve_factor = math.sin(math.pi * frac) * curve_strength
    curve_yaw = perp_yaw * curve_factor
    curve_pitch = perp_pitch * curve_factor
    
    # Add jitter for human-like movement
    jitter_yaw = random.uniform(*JITTER_RANGE)
    jitter_pitch = random.uniform(*JITTER_RANGE)
    
    # Apply rotation
    next_yaw = base_yaw + curve_yaw + jitter_yaw
    next_pitch = base_pitch + curve_pitch + jitter_pitch
    
    ms.player_set_orientation(next_yaw, next_pitch)
    time.sleep(base_delay + random.uniform(*SLEEP_JITTER))

# ============= MAIN FUNCTION =============
def look_at_block(x: float, y: float, z: float, delay: float = 0.0035, 
                  is_entity: bool = False, callback: Optional[callable] = None) -> bool:
    """
    Smoothly rotate player view to look at a target block or entity.
    
    Args:
        x, y, z: Target coordinates
        delay: Base delay between rotation steps (default: 0.0035)
        is_entity: True if targeting an entity, False for blocks
        callback: Optional function to call after each step (receives progress 0-1)
    
    Returns:
        bool: True if rotation completed successfully
    """
    try:
        # Calculate target position
        target = calculate_target(x, y, z, is_entity)
        
        # Get current player state
        player_pos = ms.player_position()
        yaw, pitch = ms.player_orientation()
        
        # Calculate desired angles
        desired_yaw, desired_pitch = calculate_desired_angles(target, player_pos)
        
        # Calculate deltas
        delta_y = normalize(desired_yaw - yaw)
        delta_p = normalize(desired_pitch - pitch)
        
        # Early return if already looking at target
        if abs(delta_y) < 0.1 and abs(delta_p) < 0.1:
            return True
        
        # Calculate movement configuration
        total_move = abs(delta_y) + abs(delta_p) / 2
        curve_range, delay_multiplier, step_multiplier = get_movement_config(total_move, is_entity)
        
        base_delay = delay * delay_multiplier
        steps = calculate_steps(delta_y, delta_p, total_move, is_entity, step_multiplier)
        
        # Calculate curve parameters
        mag = math.hypot(delta_y, delta_p) or 1.0
        perp_yaw = -delta_p / mag
        perp_pitch = delta_y / mag
        curve_strength = random.uniform(*curve_range) * random.choice([-1, 1])
        
        # Perform smooth rotation
        for i in range(1, steps + 1):
            apply_rotation_step(yaw, pitch, delta_y, delta_p, i / steps,
                              perp_yaw, perp_pitch, curve_strength, base_delay)
            
            # Callback for progress tracking
            if callback:
                callback(i / steps)
        
        return True
        
    except Exception as e:
        print(f"Error in look_at_block: {e}")
        return False

# ============= ADVANCED FEATURES =============
class LookAtMode(Enum):
    """Different targeting modes for the look_at function."""
    BLOCK = "block"
    ENTITY = "entity"
    PRECISE = "precise"
    RANDOMIZED = "randomized"

def look_at_advanced(x: float, y: float, z: float, mode: LookAtMode = LookAtMode.BLOCK,
                    delay: float = 0.0035, precision: float = 0.1) -> bool:
    """
    Advanced look_at function with different targeting modes.
    
    Args:
        x, y, z: Target coordinates
        mode: Targeting mode (BLOCK, ENTITY, PRECISE, RANDOMIZED)
        delay: Base delay between steps
        precision: Precision for precise mode (degrees)
    """
    is_entity = (mode == LookAtMode.ENTITY)
    
    if mode == LookAtMode.PRECISE:
        # Use higher precision with no randomness
        old_jitter = JITTER_RANGE
        globals()['JITTER_RANGE'] = (-0.02, 0.02)
        result = look_at_block(x, y, z, delay, is_entity)
        globals()['JITTER_RANGE'] = old_jitter
        return result
    
    elif mode == LookAtMode.RANDOMIZED:
        # Add extra randomness to look more human
        delay *= random.uniform(0.8, 1.2)
        return look_at_block(x, y, z, delay, is_entity)
    
    else:
        return look_at_block(x, y, z, delay, is_entity)

# ============= EXAMPLE USAGE =============
if __name__ == "__main__":
    # Basic usage
    look_at_block(-11, 201, -145)
    look_at_block(-16, 204, -143)
    look_at_block(-20, 201, -141)

    # Advanced usage with callback
    # def on_progress(progress: float):
        # if progress == 1.0:
            # print("Finished looking at target!")
    
    # look_at_block(x, y, z, delay=0.005, is_entity=False, callback=on_progress)
    
    # Using different modes
    # look_at_advanced(x, y, z, mode=LookAtMode.PRECISE, delay=0.003)
    # look_at_advanced(x, y, z, mode=LookAtMode.RANDOMIZED)