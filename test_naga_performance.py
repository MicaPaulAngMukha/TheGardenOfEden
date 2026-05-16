"""
Performance test for Naga pathfinding optimization.

This test verifies that the Naga class now caches pathfinding results
instead of recalculating every frame, which was causing severe lag when
the Naga was far from the player.
"""

import pytest
import pygame
import collections
import math

# Initialize pygame for testing
pygame.init()

# Import after pygame init
from TheNaga import Naga, T, COLS, ROWS


class TestNagaPerformance:
    """Test that Naga pathfinding is cached for performance."""
    
    def test_naga_has_path_caching_attributes(self):
        """
        Verify that Naga class has path caching attributes.
        
        This confirms the performance fix is in place:
        - cached_path: stores the last calculated path
        - path_recalc_timer: controls when to recalculate
        - PATH_RECALC_INTERVAL: defines recalculation frequency
        """
        naga = Naga((10, 10))
        
        # Verify caching attributes exist
        assert hasattr(naga, 'cached_path'), "Naga should have cached_path attribute"
        assert hasattr(naga, 'path_recalc_timer'), "Naga should have path_recalc_timer attribute"
        assert hasattr(naga, 'PATH_RECALC_INTERVAL'), "Naga should have PATH_RECALC_INTERVAL attribute"
        
        # Verify initial values
        assert isinstance(naga.cached_path, list), "cached_path should be a list"
        assert naga.path_recalc_timer == 0, "path_recalc_timer should start at 0"
        assert naga.PATH_RECALC_INTERVAL > 0, "PATH_RECALC_INTERVAL should be positive"
        
        print(f"✓ Naga has path caching with interval: {naga.PATH_RECALC_INTERVAL} frames")
    
    def test_naga_path_caching_reduces_recalculations(self):
        """
        Verify that path is not recalculated every frame.
        
        This is the core performance fix - the path should only be
        recalculated every PATH_RECALC_INTERVAL frames, not every frame.
        """
        naga = Naga((10, 10))
        player_rect = pygame.Rect(500, 500, 14, 14)
        walls = []
        green_walls = []
        red_walls = []
        
        # First update should calculate path
        naga.update(player_rect, walls, green_walls, red_walls, True, True)
        first_path = naga.cached_path.copy()
        first_timer = naga.path_recalc_timer
        
        assert len(first_path) > 0, "Path should be calculated on first update"
        assert first_timer == naga.PATH_RECALC_INTERVAL, "Timer should be reset after calculation"
        
        # Second update should use cached path (timer > 0)
        naga.update(player_rect, walls, green_walls, red_walls, True, True)
        second_timer = naga.path_recalc_timer
        
        assert second_timer == first_timer - 1, "Timer should decrement each frame"
        
        # Verify the caching interval is reasonable (not recalculating every frame)
        assert naga.PATH_RECALC_INTERVAL >= 2, "Recalc interval should be at least 2 frames for performance benefit"
        
        print(f"✓ Path caching working: recalculates every {naga.PATH_RECALC_INTERVAL} frames instead of every frame")
    
    def test_naga_recalculates_when_cache_empty(self):
        """
        Verify that path is recalculated immediately if cache is empty.
        
        This ensures the Naga doesn't get stuck if the cached path becomes invalid.
        """
        naga = Naga((10, 10))
        player_rect = pygame.Rect(500, 500, 14, 14)
        walls = []
        green_walls = []
        red_walls = []
        
        # Set timer to non-zero but clear cache
        naga.path_recalc_timer = 5
        naga.cached_path = []
        
        # Update should recalculate despite timer > 0
        naga.update(player_rect, walls, green_walls, red_walls, True, True)
        
        assert len(naga.cached_path) > 0, "Path should be recalculated when cache is empty"
        assert naga.path_recalc_timer == naga.PATH_RECALC_INTERVAL, "Timer should reset"
        
        print("✓ Path recalculates immediately when cache is empty")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
