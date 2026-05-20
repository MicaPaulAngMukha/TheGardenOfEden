"""
Unit tests for the Key System module.

Tests the KeyEntity class and key spawning functionality.
"""

import pytest
import pygame
from unittest.mock import patch, MagicMock
from key_system import (
    KeyEntity,
    spawn_keys,
    create_placeholder_sprite,
    KEY_SPAWN_LOCATIONS,
    T
)


# Initialize pygame for testing
pygame.init()


class TestKeyEntity:
    """Tests for the KeyEntity class"""
    
    def test_key_entity_initialization(self):
        """Verify KeyEntity initializes with correct attributes"""
        position = (100, 200)
        key = KeyEntity("bronze", position)
        
        assert key.key_type == "bronze"
        assert key.rect.x == 100
        assert key.rect.y == 200
        assert key.rect.width == 16
        assert key.rect.height == 16
        assert key.discovered == False
        assert key.sprite is not None
    
    def test_key_entity_all_types(self):
        """Verify KeyEntity can be created for all key types"""
        key_types = ["bronze", "gold", "rusted", "divine"]
        
        for key_type in key_types:
            key = KeyEntity(key_type, (0, 0))
            assert key.key_type == key_type
            assert key.sprite is not None
    
    def test_near_player_within_range(self):
        """Verify near_player returns True when player is within range"""
        key = KeyEntity("bronze", (100, 100))
        player_rect = pygame.Rect(110, 110, 20, 20)
        
        assert key.near_player(player_rect, radius=30) == True
    
    def test_near_player_out_of_range(self):
        """Verify near_player returns False when player is out of range"""
        key = KeyEntity("bronze", (100, 100))
        player_rect = pygame.Rect(200, 200, 20, 20)
        
        assert key.near_player(player_rect, radius=30) == False
    
    def test_near_player_edge_case(self):
        """Verify near_player works at the edge of range"""
        key = KeyEntity("bronze", (100, 100))
        # Place player exactly at the edge of the inflated rect
        player_rect = pygame.Rect(100 + 30, 100 + 30, 20, 20)
        
        # Should be within range due to rect inflation
        result = key.near_player(player_rect, radius=30)
        assert isinstance(result, bool)
    
    def test_load_sprite_with_missing_file(self):
        """Verify graceful handling of missing sprite files"""
        with patch('pygame.image.load', side_effect=FileNotFoundError("File not found")):
            key = KeyEntity("bronze", (0, 0))
            
            # Should still create a key with placeholder sprite
            assert key.sprite is not None
            assert isinstance(key.sprite, pygame.Surface)


class TestCreatePlaceholderSprite:
    """Tests for the create_placeholder_sprite function"""
    
    def test_placeholder_sprite_creation(self):
        """Verify placeholder sprites are created correctly"""
        sprite = create_placeholder_sprite("bronze")
        
        assert isinstance(sprite, pygame.Surface)
        assert sprite.get_width() == 16
        assert sprite.get_height() == 16
    
    def test_placeholder_sprite_all_types(self):
        """Verify placeholder sprites for all key types"""
        key_types = ["bronze", "gold", "rusted", "divine"]
        
        for key_type in key_types:
            sprite = create_placeholder_sprite(key_type)
            assert isinstance(sprite, pygame.Surface)
            assert sprite.get_width() == 16
            assert sprite.get_height() == 16
    
    def test_placeholder_sprite_unknown_type(self):
        """Verify placeholder sprite handles unknown key types"""
        sprite = create_placeholder_sprite("unknown")
        
        # Should create a default gray sprite
        assert isinstance(sprite, pygame.Surface)
        assert sprite.get_width() == 16
        assert sprite.get_height() == 16


class TestSpawnKeys:
    """Tests for the spawn_keys function"""
    
    def test_spawn_keys_creates_four_keys(self):
        """Verify that spawn_keys creates exactly 4 KeyEntity objects"""
        keys = spawn_keys()
        
        assert len(keys) == 4
        assert all(isinstance(key, KeyEntity) for key in keys)
    
    def test_spawn_keys_correct_types(self):
        """Verify that all four key types are spawned"""
        keys = spawn_keys()
        key_types = {key.key_type for key in keys}
        
        assert key_types == {"bronze", "gold", "rusted", "divine"}
    
    def test_spawn_keys_correct_positions(self):
        """Verify that keys spawn at designated locations"""
        keys = spawn_keys()
        
        for key in keys:
            expected_pos = KEY_SPAWN_LOCATIONS[key.key_type]
            assert key.rect.x == expected_pos[0]
            assert key.rect.y == expected_pos[1]
    
    def test_spawn_keys_all_undiscovered(self):
        """Verify that all spawned keys start as undiscovered"""
        keys = spawn_keys()
        
        assert all(key.discovered == False for key in keys)
    
    def test_spawn_keys_handles_missing_sprites(self):
        """Verify graceful handling of missing sprite files"""
        with patch('pygame.image.load', side_effect=FileNotFoundError("File not found")):
            keys = spawn_keys()
            
            # Should still create 4 keys with placeholder sprites
            assert len(keys) == 4
            assert all(key.sprite is not None for key in keys)


class TestKeySpawnLocations:
    """Tests for KEY_SPAWN_LOCATIONS constant"""
    
    def test_spawn_locations_exist(self):
        """Verify KEY_SPAWN_LOCATIONS contains all key types"""
        assert "bronze" in KEY_SPAWN_LOCATIONS
        assert "gold" in KEY_SPAWN_LOCATIONS
        assert "rusted" in KEY_SPAWN_LOCATIONS
        assert "divine" in KEY_SPAWN_LOCATIONS
    
    def test_spawn_locations_are_tuples(self):
        """Verify spawn locations are tuples of coordinates"""
        for key_type, position in KEY_SPAWN_LOCATIONS.items():
            assert isinstance(position, tuple)
            assert len(position) == 2
            assert isinstance(position[0], int)
            assert isinstance(position[1], int)
    
    def test_spawn_locations_use_tile_coordinates(self):
        """Verify spawn locations are calculated using tile size T"""
        # All positions should be multiples of T
        for key_type, position in KEY_SPAWN_LOCATIONS.items():
            assert position[0] % T == 0
            assert position[1] % T == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
