"""
Difficulty Configuration Module

Centralized configuration for all difficulty modifiers in the Garden of Eden game.
Maps player keys (Bronze, Gold, Rusted, Divine) to difficulty modes and provides
level-specific modifiers for enemy behavior, spawn rates, and timing mechanics.
"""

# Difficulty mode constants
EASY = "easy"
NORMAL = "normal"
HARD = "hard"
GOD_MODE = "god"

# Key type to difficulty mode mapping
KEY_TO_DIFFICULTY = {
    "bronze": EASY,
    "gold": NORMAL,
    "rusted": HARD,
    "divine": GOD_MODE,
    None: NORMAL  # Default when no key held
}

# Difficulty modifiers organized by level and mode
DIFFICULTY_MODIFIERS = {
    "TheNaga": {
        EASY: {
            "naga_speed": 5,  # No change from baseline
            "item_spawn_multiplier": 1.5,
            "abel_speed": 2.5,
            "cain_throw_cooldown_multiplier": 1.5,  # 50% slower
        },
        NORMAL: {},  # Empty dict = no modifiers
        HARD: {
            "naga_speed": 6,
            "item_spawn_multiplier": 0.5,
            "cain_throw_cooldown_multiplier": 0.5,  # 100% faster
            "abel_instant_kill": True,
        },
        GOD_MODE: {
            "spawn_god": True,
        }
    },
    "TheTwins": {
        EASY: {
            "abel_speed": 2.5,
            "cain_throw_cooldown_multiplier": 1.5,
            "cain_throw_range": 6,
        },
        NORMAL: {},
        HARD: {
            "cain_throw_cooldown_multiplier": 0.5,
            "cain_throw_range": 12,
            "abel_instant_kill": True,
        },
        GOD_MODE: {
            "spawn_god": True,
        }
    },
    "TheGuardian": {
        EASY: {
            "disable_enrage": True,
        },
        NORMAL: {},
        HARD: {
            "light_phase_duration": 120,
            "dark_phase_duration": 420,
            "guardian_chase_speed_multiplier": 1.2,
        },
        GOD_MODE: {
            "spawn_god": True,
        }
    },
    "TheStatues": {
        EASY: {
            "light_phase_duration": 240,
            "statue_speed_multiplier": 0.8,
        },
        NORMAL: {},
        HARD: {
            "light_phase_duration": 120,
            "dark_phase_duration": 420,
            "statue_speed_multiplier": 1.2,
        },
        GOD_MODE: {
            "spawn_god": True,
        }
    },
    "TheGarden": {
        EASY: {
            "tree_shakes_required": 3,
            "lightning_cooldown_multiplier": 1.5,
            "god_speed_multiplier": 0.8,
        },
        NORMAL: {},
        HARD: {
            "tree_shakes_required": 7,
            "lightning_cooldown_multiplier": 0.7,
            "god_speed_multiplier": 1.3,
            "lightning_count": 7,
        },
        GOD_MODE: {
            "lightning_count": 9,
            "lightning_cooldown_multiplier": 0.5,
            "god_speed_multiplier": 1.5,
            "god_smite_cooldown_multiplier": 0.6,
            "disable_prior_enemies": True,
        }
    }
}


def get_difficulty_from_key(key_entity):
    """
    Extract difficulty mode from player's held key.
    
    Args:
        key_entity: KeyEntity object or None
        
    Returns:
        str: Difficulty mode constant (EASY, NORMAL, HARD, GOD_MODE)
    """
    try:
        if key_entity is None:
            return NORMAL
        
        # Handle missing key_type attribute
        if not hasattr(key_entity, 'key_type'):
            print(f"WARNING: KeyEntity missing 'key_type' attribute. Defaulting to Normal Mode.")
            return NORMAL
        
        key_type = key_entity.key_type
        
        # Handle invalid key_type values
        if key_type not in KEY_TO_DIFFICULTY:
            print(f"WARNING: Invalid key_type '{key_type}'. Defaulting to Normal Mode.")
            return NORMAL
        
        return KEY_TO_DIFFICULTY[key_type]
    except Exception as e:
        print(f"ERROR: Exception in get_difficulty_from_key: {e}. Defaulting to Normal Mode.")
        return NORMAL


def get_modifiers(level_name, difficulty):
    """
    Retrieve difficulty modifiers for a specific level and difficulty.
    
    Args:
        level_name: str - Name of the level ("TheNaga", "TheTwins", etc.)
        difficulty: str - Difficulty mode constant
        
    Returns:
        dict: Modifier dictionary for the level/difficulty combination
    """
    try:
        if level_name not in DIFFICULTY_MODIFIERS:
            print(f"WARNING: Level '{level_name}' not found in difficulty configuration. Using no modifiers.")
            return {}
        
        if difficulty not in [EASY, NORMAL, HARD, GOD_MODE]:
            print(f"WARNING: Invalid difficulty mode '{difficulty}'. Defaulting to Normal Mode.")
            difficulty = NORMAL
        
        return DIFFICULTY_MODIFIERS[level_name].get(difficulty, {})
    except Exception as e:
        print(f"ERROR: Exception in get_modifiers for level '{level_name}', difficulty '{difficulty}': {e}")
        print("Falling back to Normal Mode (no modifiers).")
        return {}


def validate_modifiers():
    """
    Validate all modifier values at startup.
    
    Checks:
    - Speed modifiers > 0
    - Frequency modifiers > 0
    - Duration modifiers >= 30 frames
    - Range modifiers >= 1
    
    Returns:
        list: List of validation error messages (empty if valid)
    """
    errors = []
    
    for level, difficulties in DIFFICULTY_MODIFIERS.items():
        for diff, mods in difficulties.items():
            # Speed validation
            for key in ["naga_speed", "abel_speed", "cain_speed"]:
                if key in mods and mods[key] <= 0:
                    errors.append(f"{level}.{diff}.{key} must be > 0")
            
            # Multiplier validation
            for key in [k for k in mods if "multiplier" in k]:
                if mods[key] <= 0:
                    errors.append(f"{level}.{diff}.{key} must be > 0")
            
            # Duration validation
            for key in [k for k in mods if "duration" in k]:
                if mods[key] < 30:
                    errors.append(f"{level}.{diff}.{key} must be >= 30 frames")
            
            # Range validation
            for key in [k for k in mods if "range" in k]:
                if mods[key] < 1:
                    errors.append(f"{level}.{diff}.{key} must be >= 1")
    
    return errors
