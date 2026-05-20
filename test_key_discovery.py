"""
Unit tests for key discovery system (Task 3)
"""
import pytest
import pygame
from key_system import KeyEntity, spawn_keys
from Start import check_key_discovery, KEY_NARRATOR_TEXT


# Initialize pygame for testing
pygame.init()
pygame.display.set_mode((1, 1))  # Minimal display for testing


class MockPlayer:
    """Mock player for testing"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)


def test_key_narrator_text_exists():
    """Verify KEY_NARRATOR_TEXT dictionary has all four key types"""
    assert "bronze" in KEY_NARRATOR_TEXT
    assert "gold" in KEY_NARRATOR_TEXT
    assert "rusted" in KEY_NARRATOR_TEXT
    assert "divine" in KEY_NARRATOR_TEXT


def test_key_narrator_text_content():
    """Verify KEY_NARRATOR_TEXT has correct content for each key"""
    assert "bronze key" in KEY_NARRATOR_TEXT["bronze"].lower()
    assert "golden key" in KEY_NARRATOR_TEXT["gold"].lower() or "gold key" in KEY_NARRATOR_TEXT["gold"].lower()
    assert "rusted" in KEY_NARRATOR_TEXT["rusted"].lower()
    # Divine key text is more atmospheric, just check it's not empty
    assert len(KEY_NARRATOR_TEXT["divine"]) > 0


def test_check_key_discovery_detects_nearby_key():
    """Verify that check_key_discovery detects keys within range"""
    player = MockPlayer(100, 100)
    key = KeyEntity("bronze", (110, 110))  # Within range (30 pixels)
    keys = [key]
    
    discovered = check_key_discovery(player, keys)
    
    assert discovered == key
    assert key.discovered == True


def test_check_key_discovery_ignores_distant_key():
    """Verify that check_key_discovery ignores keys out of range"""
    player = MockPlayer(100, 100)
    key = KeyEntity("bronze", (200, 200))  # Out of range
    keys = [key]
    
    discovered = check_key_discovery(player, keys)
    
    assert discovered is None
    assert key.discovered == False


def test_check_key_discovery_ignores_already_discovered():
    """Verify that already discovered keys are not re-discovered"""
    player = MockPlayer(100, 100)
    key = KeyEntity("bronze", (110, 110))
    key.discovered = True
    keys = [key]
    
    discovered = check_key_discovery(player, keys)
    
    assert discovered is None


def test_check_key_discovery_returns_first_undiscovered():
    """Verify that check_key_discovery returns first undiscovered key when multiple are nearby"""
    player = MockPlayer(100, 100)
    key1 = KeyEntity("bronze", (110, 110))
    key2 = KeyEntity("gold", (115, 115))
    keys = [key1, key2]
    
    discovered = check_key_discovery(player, keys)
    
    assert discovered == key1
    assert key1.discovered == True
    assert key2.discovered == False


def test_check_key_discovery_with_empty_list():
    """Verify that check_key_discovery handles empty key list"""
    player = MockPlayer(100, 100)
    keys = []
    
    discovered = check_key_discovery(player, keys)
    
    assert discovered is None


def test_check_key_discovery_all_key_types():
    """Verify that check_key_discovery works with all four key types"""
    player = MockPlayer(100, 100)
    
    for key_type in ["bronze", "gold", "rusted", "divine"]:
        key = KeyEntity(key_type, (110, 110))
        keys = [key]
        
        discovered = check_key_discovery(player, keys)
        
        assert discovered == key
        assert key.discovered == True
        assert key.key_type == key_type


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
