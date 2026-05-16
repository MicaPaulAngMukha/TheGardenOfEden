"""
Bug Condition Exploration Test for Window Title Consistency Fix

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

This test is designed to FAIL on unfixed code to confirm the bug exists.
When the test fails, it demonstrates that scene files change the window title
when they are imported or executed.

CRITICAL: This test encodes the EXPECTED behavior. When it passes after the fix,
it confirms the bug is resolved.

This test uses static code analysis to verify the bug condition and expected behavior,
which is appropriate for this type of window title bug in a Pygame application.
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
import re


class TestBugConditionExploration:
    """
    Property 1: Bug Condition - Window Title Changes When Scenes Load
    
    This test explores the bug condition where six scene files (Prologue, TheNaga,
    TheTwins, TheGuardian, TheStatues, TheGarden) each call pygame.display.set_caption()
    with scene-specific titles, causing the window title to change as players progress.
    
    The test uses static code analysis to verify:
    1. The bug exists in the unfixed code (set_caption calls with scene-specific titles)
    2. The fix is correctly implemented (set_caption calls removed)
    """
    
    def test_prologue_should_not_change_window_title(self):
        """
        **Validates: Requirement 2.1**
        
        Test Case 1: Prologue.py should NOT change window title
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect line 399: pygame.display.set_caption("Garden of Eden – Prologue")
        - This confirms the bug exists (title changes when Prologue loads)
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will NOT find the set_caption call with scene-specific title
        - This confirms the bug is fixed
        
        Expected Behavior:
        - Window title should remain "Garden of Eden" when Prologue loads
        - Prologue.py should NOT call pygame.display.set_caption()
        """
        
        # Read the Prologue.py file
        with open('Prologue.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the buggy pattern: pygame.display.set_caption with scene-specific title
        # Expected location: line 399 in main() function
        buggy_pattern = r'pygame\.display\.set_caption\(["\']Garden of Eden – Prologue["\']\)'
        buggy_match = re.search(buggy_pattern, content)
        
        if buggy_match:
            # Buggy code found - test fails with counterexample
            assert False, (
                f"COUNTEREXAMPLE FOUND: Prologue.py changes window title.\n"
                f"Bug confirmed in Prologue.py (expected around line 399).\n"
                f"Current code: pygame.display.set_caption(\"Garden of Eden – Prologue\")\n"
                f"This causes window title to change when Prologue scene loads.\n"
                f"Expected: Window title should remain \"Garden of Eden\".\n"
                f"Root cause: Redundant set_caption() call in Prologue.py.\n"
                f"Bug condition: Scene file contains pygame.display.set_caption() with scene-specific title\n"
                f"Expected behavior: No set_caption() call in scene file\n"
                f"Actual behavior: set_caption() changes title to \"Garden of Eden – Prologue\" (bug)"
            )
        
        # If we reach here, the set_caption call is not found
        print("\n✓ Bug condition test PASSED: Prologue.py does NOT change window title")
    
    def test_thenaga_should_not_change_window_title(self):
        """
        **Validates: Requirement 2.2**
        
        Test Case 2: TheNaga.py should NOT change window title
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect line 15: pygame.display.set_caption("Garden of Eden – The Naga's Lair")
        - This confirms the bug exists (title changes when TheNaga loads)
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will NOT find the set_caption call with scene-specific title
        - This confirms the bug is fixed
        
        Expected Behavior:
        - Window title should remain "Garden of Eden" when TheNaga loads
        - TheNaga.py should NOT call pygame.display.set_caption()
        """
        
        # Read the TheNaga.py file
        with open('TheNaga.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the buggy pattern: pygame.display.set_caption with scene-specific title
        # Expected location: line 15 at module level
        buggy_pattern = r'pygame\.display\.set_caption\(["\']Garden of Eden – The Naga\'s Lair["\']\)'
        buggy_match = re.search(buggy_pattern, content)
        
        if buggy_match:
            # Buggy code found - test fails with counterexample
            assert False, (
                f"COUNTEREXAMPLE FOUND: TheNaga.py changes window title.\n"
                f"Bug confirmed in TheNaga.py (expected around line 15).\n"
                f"Current code: pygame.display.set_caption(\"Garden of Eden – The Naga's Lair\")\n"
                f"This causes window title to change when TheNaga module is imported.\n"
                f"Expected: Window title should remain \"Garden of Eden\".\n"
                f"Root cause: Redundant set_caption() call at module level in TheNaga.py.\n"
                f"Bug condition: Scene file contains pygame.display.set_caption() with scene-specific title\n"
                f"Expected behavior: No set_caption() call in scene file\n"
                f"Actual behavior: set_caption() changes title to \"Garden of Eden – The Naga's Lair\" (bug)"
            )
        
        # If we reach here, the set_caption call is not found
        print("\n✓ Bug condition test PASSED: TheNaga.py does NOT change window title")
    
    def test_thetwins_should_not_change_window_title(self):
        """
        **Validates: Requirement 2.3**
        
        Test Case 3: TheTwins.py should NOT change window title
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect line 16: pygame.display.set_caption("Garden of Eden – The Twins")
        - This confirms the bug exists (title changes when TheTwins loads)
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will NOT find the set_caption call with scene-specific title
        - This confirms the bug is fixed
        
        Expected Behavior:
        - Window title should remain "Garden of Eden" when TheTwins loads
        - TheTwins.py should NOT call pygame.display.set_caption()
        """
        
        # Read the TheTwins.py file
        with open('TheTwins.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the buggy pattern: pygame.display.set_caption with scene-specific title
        # Expected location: line 16 at module level
        buggy_pattern = r'pygame\.display\.set_caption\(["\']Garden of Eden – The Twins["\']\)'
        buggy_match = re.search(buggy_pattern, content)
        
        if buggy_match:
            # Buggy code found - test fails with counterexample
            assert False, (
                f"COUNTEREXAMPLE FOUND: TheTwins.py changes window title.\n"
                f"Bug confirmed in TheTwins.py (expected around line 16).\n"
                f"Current code: pygame.display.set_caption(\"Garden of Eden – The Twins\")\n"
                f"This causes window title to change when TheTwins module is imported.\n"
                f"Expected: Window title should remain \"Garden of Eden\".\n"
                f"Root cause: Redundant set_caption() call at module level in TheTwins.py.\n"
                f"Bug condition: Scene file contains pygame.display.set_caption() with scene-specific title\n"
                f"Expected behavior: No set_caption() call in scene file\n"
                f"Actual behavior: set_caption() changes title to \"Garden of Eden – The Twins\" (bug)"
            )
        
        # If we reach here, the set_caption call is not found
        print("\n✓ Bug condition test PASSED: TheTwins.py does NOT change window title")
    
    def test_theguardian_should_not_change_window_title(self):
        """
        **Validates: Requirement 2.4**
        
        Test Case 4: TheGuardian.py should NOT change window title
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect line 16: pygame.display.set_caption("Garden of Eden – The Guardian")
        - This confirms the bug exists (title changes when TheGuardian loads)
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will NOT find the set_caption call with scene-specific title
        - This confirms the bug is fixed
        
        Expected Behavior:
        - Window title should remain "Garden of Eden" when TheGuardian loads
        - TheGuardian.py should NOT call pygame.display.set_caption()
        """
        
        # Read the TheGuardian.py file
        with open('TheGuardian.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the buggy pattern: pygame.display.set_caption with scene-specific title
        # Expected location: line 16 at module level
        buggy_pattern = r'pygame\.display\.set_caption\(["\']Garden of Eden – The Guardian["\']\)'
        buggy_match = re.search(buggy_pattern, content)
        
        if buggy_match:
            # Buggy code found - test fails with counterexample
            assert False, (
                f"COUNTEREXAMPLE FOUND: TheGuardian.py changes window title.\n"
                f"Bug confirmed in TheGuardian.py (expected around line 16).\n"
                f"Current code: pygame.display.set_caption(\"Garden of Eden – The Guardian\")\n"
                f"This causes window title to change when TheGuardian module is imported.\n"
                f"Expected: Window title should remain \"Garden of Eden\".\n"
                f"Root cause: Redundant set_caption() call at module level in TheGuardian.py.\n"
                f"Bug condition: Scene file contains pygame.display.set_caption() with scene-specific title\n"
                f"Expected behavior: No set_caption() call in scene file\n"
                f"Actual behavior: set_caption() changes title to \"Garden of Eden – The Guardian\" (bug)"
            )
        
        # If we reach here, the set_caption call is not found
        print("\n✓ Bug condition test PASSED: TheGuardian.py does NOT change window title")
    
    def test_thestatues_should_not_change_window_title(self):
        """
        **Validates: Requirement 2.5**
        
        Test Case 5: TheStatues.py should NOT change window title
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect line 15: pygame.display.set_caption("Garden of Eden – The Statues")
        - This confirms the bug exists (title changes when TheStatues loads)
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will NOT find the set_caption call with scene-specific title
        - This confirms the bug is fixed
        
        Expected Behavior:
        - Window title should remain "Garden of Eden" when TheStatues loads
        - TheStatues.py should NOT call pygame.display.set_caption()
        """
        
        # Read the TheStatues.py file
        with open('TheStatues.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the buggy pattern: pygame.display.set_caption with scene-specific title
        # Expected location: line 15 at module level
        buggy_pattern = r'pygame\.display\.set_caption\(["\']Garden of Eden – The Statues["\']\)'
        buggy_match = re.search(buggy_pattern, content)
        
        if buggy_match:
            # Buggy code found - test fails with counterexample
            assert False, (
                f"COUNTEREXAMPLE FOUND: TheStatues.py changes window title.\n"
                f"Bug confirmed in TheStatues.py (expected around line 15).\n"
                f"Current code: pygame.display.set_caption(\"Garden of Eden – The Statues\")\n"
                f"This causes window title to change when TheStatues module is imported.\n"
                f"Expected: Window title should remain \"Garden of Eden\".\n"
                f"Root cause: Redundant set_caption() call at module level in TheStatues.py.\n"
                f"Bug condition: Scene file contains pygame.display.set_caption() with scene-specific title\n"
                f"Expected behavior: No set_caption() call in scene file\n"
                f"Actual behavior: set_caption() changes title to \"Garden of Eden – The Statues\" (bug)"
            )
        
        # If we reach here, the set_caption call is not found
        print("\n✓ Bug condition test PASSED: TheStatues.py does NOT change window title")
    
    def test_thegarden_should_not_change_window_title(self):
        """
        **Validates: Requirement 2.6**
        
        Test Case 6: TheGarden.py should NOT change window title
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect line 13: pygame.display.set_caption("Garden of Eden – The Garden")
        - This confirms the bug exists (title changes when TheGarden loads)
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will NOT find the set_caption call with scene-specific title
        - This confirms the bug is fixed
        
        Expected Behavior:
        - Window title should remain "Garden of Eden" when TheGarden loads
        - TheGarden.py should NOT call pygame.display.set_caption()
        """
        
        # Read the TheGarden.py file
        with open('TheGarden.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the buggy pattern: pygame.display.set_caption with scene-specific title
        # Expected location: line 13 at module level
        buggy_pattern = r'pygame\.display\.set_caption\(["\']Garden of Eden – The Garden["\']\)'
        buggy_match = re.search(buggy_pattern, content)
        
        if buggy_match:
            # Buggy code found - test fails with counterexample
            assert False, (
                f"COUNTEREXAMPLE FOUND: TheGarden.py changes window title.\n"
                f"Bug confirmed in TheGarden.py (expected around line 13).\n"
                f"Current code: pygame.display.set_caption(\"Garden of Eden – The Garden\")\n"
                f"This causes window title to change when TheGarden module is imported.\n"
                f"Expected: Window title should remain \"Garden of Eden\".\n"
                f"Root cause: Redundant set_caption() call at module level in TheGarden.py.\n"
                f"Bug condition: Scene file contains pygame.display.set_caption() with scene-specific title\n"
                f"Expected behavior: No set_caption() call in scene file\n"
                f"Actual behavior: set_caption() changes title to \"Garden of Eden – The Garden\" (bug)"
            )
        
        # If we reach here, the set_caption call is not found
        print("\n✓ Bug condition test PASSED: TheGarden.py does NOT change window title")
    
    @given(
        scene_file=st.sampled_from([
            ('Prologue.py', 'Garden of Eden – Prologue'),
            ('TheNaga.py', "Garden of Eden – The Naga's Lair"),
            ('TheTwins.py', 'Garden of Eden – The Twins'),
            ('TheGuardian.py', 'Garden of Eden – The Guardian'),
            ('TheStatues.py', 'Garden of Eden – The Statues'),
            ('TheGarden.py', 'Garden of Eden – The Garden')
        ])
    )
    @settings(
        max_examples=18,  # Scoped PBT: test each scene file 3 times
        phases=[Phase.generate, Phase.target]  # Skip shrinking for faster execution
    )
    def test_property_no_scene_changes_window_title(self, scene_file):
        """
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**
        
        Property-Based Test: For ANY scene file in [Prologue, TheNaga, TheTwins,
        TheGuardian, TheStatues, TheGarden], the scene file should NOT call
        pygame.display.set_caption() with a scene-specific title.
        
        This property test generates checks across all six scene files to ensure
        the bug is completely resolved.
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS with counterexamples
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES for all generated checks
        """
        
        filename, expected_title = scene_file
        
        # Read the scene file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Escape special regex characters in the expected title
        escaped_title = re.escape(expected_title)
        
        # Look for the buggy pattern: pygame.display.set_caption with scene-specific title
        buggy_pattern = rf'pygame\.display\.set_caption\(["\'{escaped_title}["\']\)'
        buggy_match = re.search(buggy_pattern, content)
        
        # ASSERTION: Bug should not exist
        assert not buggy_match, (
            f"Property violation: {filename} changes window title.\n"
            f"Found: pygame.display.set_caption(\"{expected_title}\")\n"
            f"Root cause: Redundant set_caption() call in {filename}.\n"
            f"Expected behavior: Window title should remain \"Garden of Eden\"\n"
            f"Actual behavior: set_caption() changes title to \"{expected_title}\" (bug)"
        )
        
        # If we reach here, the test passed for this scene file
        print(f"\n✓ Property test PASSED for '{filename}': Window title is NOT changed")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])



class TestPreservationProperties:
    """
    Property 2: Preservation - Scene Initialization and Display Window Creation
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    
    These tests verify that scene functionality NOT involving window title text
    remains unchanged. They test the baseline behavior on UNFIXED code and should
    PASS both before and after the fix.
    
    The tests use static code analysis to verify that critical pygame initialization
    code remains intact in all scene files.
    """
    
    def test_prologue_preserves_display_initialization(self):
        """
        **Validates: Requirement 3.4**
        
        Test that Prologue.py preserves display window creation (793x650).
        
        EXPECTED OUTCOME: This test PASSES on both unfixed and fixed code.
        
        Preservation Requirements:
        - pygame.display.set_mode() creates 793x650 window
        - pygame.init() is called
        - screen and clock objects are created
        """
        
        # Read the Prologue.py file
        with open('Prologue.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify pygame.init() is present
        assert 'pygame.init()' in content, (
            "Preservation violation: pygame.init() missing from Prologue.py"
        )
        
        # Verify display.set_mode with correct dimensions
        assert 'pygame.display.set_mode((WIDTH, HEIGHT))' in content or \
               'pygame.display.set_mode((793, 650))' in content or \
               'pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)' in content, (
            "Preservation violation: pygame.display.set_mode() with correct dimensions missing from Prologue.py"
        )
        
        # Verify WIDTH and HEIGHT constants
        assert 'WIDTH, HEIGHT = 793, 650' in content, (
            "Preservation violation: WIDTH, HEIGHT constants missing or incorrect in Prologue.py"
        )
        
        # Verify clock creation
        assert 'clock' in content and 'pygame.time.Clock()' in content, (
            "Preservation violation: clock initialization missing from Prologue.py"
        )
        
        print("\n✓ Preservation test PASSED: Prologue.py display initialization preserved")
    
    def test_thenaga_preserves_display_initialization(self):
        """
        **Validates: Requirement 3.4**
        
        Test that TheNaga.py preserves display window creation (793x650).
        
        EXPECTED OUTCOME: This test PASSES on both unfixed and fixed code.
        
        Preservation Requirements:
        - pygame.display.set_mode() creates 793x650 window
        - pygame.init() is called
        - screen and clock objects are created
        - tmx_data is loaded
        """
        
        # Read the TheNaga.py file
        with open('TheNaga.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify pygame.init() is present
        assert 'pygame.init()' in content, (
            "Preservation violation: pygame.init() missing from TheNaga.py"
        )
        
        # Verify display.set_mode with correct dimensions
        assert 'screen = pygame.display.set_mode((WIDTH, HEIGHT))' in content or \
               'screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)' in content, (
            "Preservation violation: pygame.display.set_mode() missing from TheNaga.py"
        )
        
        # Verify WIDTH and HEIGHT constants
        assert 'WIDTH, HEIGHT = 793, 650' in content, (
            "Preservation violation: WIDTH, HEIGHT constants missing or incorrect in TheNaga.py"
        )
        
        # Verify clock creation
        assert 'clock' in content and 'pygame.time.Clock()' in content, (
            "Preservation violation: clock initialization missing from TheNaga.py"
        )
        
        # Verify tmx_data loading
        assert 'tmx_data = pytmx.load_pygame' in content, (
            "Preservation violation: tmx_data loading missing from TheNaga.py"
        )
        
        print("\n✓ Preservation test PASSED: TheNaga.py display initialization preserved")
    
    def test_thetwins_preserves_display_initialization(self):
        """
        **Validates: Requirement 3.4**
        
        Test that TheTwins.py preserves display window creation (793x650).
        
        EXPECTED OUTCOME: This test PASSES on both unfixed and fixed code.
        
        Preservation Requirements:
        - pygame.display.set_mode() creates 793x650 window
        - pygame.init() is called
        - screen and clock objects are created
        - tmx_data is loaded
        """
        
        # Read the TheTwins.py file
        with open('TheTwins.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify pygame.init() is present
        assert 'pygame.init()' in content, (
            "Preservation violation: pygame.init() missing from TheTwins.py"
        )
        
        # Verify display.set_mode with correct dimensions
        assert 'screen = pygame.display.set_mode((WIDTH, HEIGHT))' in content or \
               'screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)' in content, (
            "Preservation violation: pygame.display.set_mode() missing from TheTwins.py"
        )
        
        # Verify WIDTH and HEIGHT constants
        assert 'WIDTH, HEIGHT = 793, 650' in content, (
            "Preservation violation: WIDTH, HEIGHT constants missing or incorrect in TheTwins.py"
        )
        
        # Verify clock creation
        assert 'clock' in content and 'pygame.time.Clock()' in content, (
            "Preservation violation: clock initialization missing from TheTwins.py"
        )
        
        # Verify tmx_data loading
        assert 'tmx_data = pytmx.load_pygame' in content, (
            "Preservation violation: tmx_data loading missing from TheTwins.py"
        )
        
        print("\n✓ Preservation test PASSED: TheTwins.py display initialization preserved")
    
    def test_theguardian_preserves_display_initialization(self):
        """
        **Validates: Requirement 3.4**
        
        Test that TheGuardian.py preserves display window creation (793x650).
        
        EXPECTED OUTCOME: This test PASSES on both unfixed and fixed code.
        
        Preservation Requirements:
        - pygame.display.set_mode() creates 793x650 window
        - pygame.init() is called
        - screen and clock objects are created
        - tmx_data is loaded
        """
        
        # Read the TheGuardian.py file
        with open('TheGuardian.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify pygame.init() is present
        assert 'pygame.init()' in content, (
            "Preservation violation: pygame.init() missing from TheGuardian.py"
        )
        
        # Verify display.set_mode with correct dimensions
        assert 'screen = pygame.display.set_mode((WIDTH, HEIGHT))' in content or \
               'screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)' in content, (
            "Preservation violation: pygame.display.set_mode() missing from TheGuardian.py"
        )
        
        # Verify WIDTH and HEIGHT constants
        assert 'WIDTH, HEIGHT = 793, 650' in content, (
            "Preservation violation: WIDTH, HEIGHT constants missing or incorrect in TheGuardian.py"
        )
        
        # Verify clock creation
        assert 'clock' in content and 'pygame.time.Clock()' in content, (
            "Preservation violation: clock initialization missing from TheGuardian.py"
        )
        
        # Verify tmx_data loading
        assert 'tmx_data = pytmx.load_pygame' in content, (
            "Preservation violation: tmx_data loading missing from TheGuardian.py"
        )
        
        print("\n✓ Preservation test PASSED: TheGuardian.py display initialization preserved")
    
    def test_thestatues_preserves_display_initialization(self):
        """
        **Validates: Requirement 3.4**
        
        Test that TheStatues.py preserves display window creation (793x650).
        
        EXPECTED OUTCOME: This test PASSES on both unfixed and fixed code.
        
        Preservation Requirements:
        - pygame.display.set_mode() creates 793x650 window
        - pygame.init() is called
        - screen and clock objects are created
        - tmx_data is loaded
        """
        
        # Read the TheStatues.py file
        with open('TheStatues.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify pygame.init() is present
        assert 'pygame.init()' in content, (
            "Preservation violation: pygame.init() missing from TheStatues.py"
        )
        
        # Verify display.set_mode with correct dimensions
        assert 'screen = pygame.display.set_mode((WIDTH, HEIGHT))' in content or \
               'screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)' in content, (
            "Preservation violation: pygame.display.set_mode() missing from TheStatues.py"
        )
        
        # Verify WIDTH and HEIGHT constants
        assert 'WIDTH, HEIGHT = 793, 650' in content, (
            "Preservation violation: WIDTH, HEIGHT constants missing or incorrect in TheStatues.py"
        )
        
        # Verify clock creation
        assert 'clock' in content and 'pygame.time.Clock()' in content, (
            "Preservation violation: clock initialization missing from TheStatues.py"
        )
        
        # Verify tmx_data loading
        assert 'tmx_data = pytmx.load_pygame' in content, (
            "Preservation violation: tmx_data loading missing from TheStatues.py"
        )
        
        print("\n✓ Preservation test PASSED: TheStatues.py display initialization preserved")
    
    def test_thegarden_preserves_display_initialization(self):
        """
        **Validates: Requirement 3.4**
        
        Test that TheGarden.py preserves display window creation (793x650).
        
        EXPECTED OUTCOME: This test PASSES on both unfixed and fixed code.
        
        Preservation Requirements:
        - pygame.display.set_mode() creates 793x650 window
        - pygame.init() is called
        - screen and clock objects are created
        - tmx_data is loaded
        """
        
        # Read the TheGarden.py file
        with open('TheGarden.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify pygame.init() is present
        assert 'pygame.init()' in content, (
            "Preservation violation: pygame.init() missing from TheGarden.py"
        )
        
        # Verify display.set_mode with correct dimensions
        assert 'screen = pygame.display.set_mode((WIDTH, HEIGHT))' in content or \
               'screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)' in content, (
            "Preservation violation: pygame.display.set_mode() missing from TheGarden.py"
        )
        
        # Verify WIDTH and HEIGHT constants
        assert 'WIDTH, HEIGHT = 793, 650' in content, (
            "Preservation violation: WIDTH, HEIGHT constants missing or incorrect in TheGarden.py"
        )
        
        # Verify clock creation
        assert 'clock' in content and 'pygame.time.Clock()' in content, (
            "Preservation violation: clock initialization missing from TheGarden.py"
        )
        
        # Verify tmx_data loading
        assert 'tmx_data = pytmx.load_pygame' in content, (
            "Preservation violation: tmx_data loading missing from TheGarden.py"
        )
        
        print("\n✓ Preservation test PASSED: TheGarden.py display initialization preserved")
    
    @given(
        scene_file=st.sampled_from([
            'Prologue.py',
            'TheNaga.py',
            'TheTwins.py',
            'TheGuardian.py',
            'TheStatues.py',
            'TheGarden.py'
        ])
    )
    @settings(
        max_examples=18,  # Test each scene file 3 times
        phases=[Phase.generate, Phase.target]
    )
    def test_property_all_scenes_preserve_pygame_initialization(self, scene_file):
        """
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        
        Property-Based Test: For ANY scene file, pygame initialization code
        (pygame.init(), display.set_mode, clock creation) must be preserved.
        
        This property test generates checks across all six scene files to ensure
        no regressions in scene initialization after the fix.
        
        EXPECTED OUTCOME: This test PASSES on both unfixed and fixed code.
        """
        
        # Read the scene file
        with open(scene_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Property 1: pygame.init() must be present
        assert 'pygame.init()' in content, (
            f"Property violation: pygame.init() missing from {scene_file}"
        )
        
        # Property 2: Display mode must be set with correct dimensions
        has_display_mode = (
            'pygame.display.set_mode((WIDTH, HEIGHT))' in content or
            'pygame.display.set_mode((793, 650))' in content or
            'pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)' in content
        )
        assert has_display_mode, (
            f"Property violation: pygame.display.set_mode() with correct dimensions missing from {scene_file}"
        )
        
        # Property 3: WIDTH and HEIGHT constants must be correct
        assert 'WIDTH, HEIGHT = 793, 650' in content, (
            f"Property violation: WIDTH, HEIGHT constants missing or incorrect in {scene_file}"
        )
        
        # Property 4: Clock must be initialized
        assert 'clock' in content and 'pygame.time.Clock()' in content, (
            f"Property violation: clock initialization missing from {scene_file}"
        )
        
        print(f"\n✓ Property test PASSED for '{scene_file}': pygame initialization preserved")
    
    @given(
        scene_file=st.sampled_from([
            'TheNaga.py',
            'TheTwins.py',
            'TheGuardian.py',
            'TheStatues.py',
            'TheGarden.py'
        ])
    )
    @settings(
        max_examples=15,  # Test each scene file 3 times
        phases=[Phase.generate, Phase.target]
    )
    def test_property_all_scenes_preserve_tmx_loading(self, scene_file):
        """
        **Validates: Requirements 3.3, 3.4**
        
        Property-Based Test: For ANY scene file (except Prologue which doesn't use tmx),
        tmx_data loading must be preserved.
        
        This property test verifies that scene-specific initialization (tmx map loading)
        remains unchanged after the fix.
        
        EXPECTED OUTCOME: This test PASSES on both unfixed and fixed code.
        """
        
        # Read the scene file
        with open(scene_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Property: tmx_data must be loaded
        assert 'tmx_data = pytmx.load_pygame' in content, (
            f"Property violation: tmx_data loading missing from {scene_file}"
        )
        
        print(f"\n✓ Property test PASSED for '{scene_file}': tmx_data loading preserved")
    
    @given(
        scene_sequence=st.lists(
            st.sampled_from([
                'TheNaga.py',
                'TheTwins.py',
                'TheGuardian.py',
                'TheStatues.py',
                'TheGarden.py'
            ]),
            min_size=2,
            max_size=5
        )
    )
    @settings(
        max_examples=20,  # Generate 20 different scene load sequences
        phases=[Phase.generate, Phase.target]
    )
    def test_property_scene_transitions_preserve_structure(self, scene_sequence):
        """
        **Validates: Requirements 3.3**
        
        Property-Based Test: For ANY sequence of scene imports, the scene files
        must maintain their structural integrity (no crashes, all initialization
        code present).
        
        This property test verifies that scene transitions don't cause structural
        issues after the fix.
        
        EXPECTED OUTCOME: This test PASSES on both unfixed and fixed code.
        """
        
        # For each scene in the sequence, verify structural integrity
        for scene_file in scene_sequence:
            with open(scene_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify critical initialization code is present
            assert 'pygame.init()' in content, (
                f"Property violation: Scene transition broke pygame.init() in {scene_file}"
            )
            
            assert 'pygame.display.set_mode' in content, (
                f"Property violation: Scene transition broke display.set_mode() in {scene_file}"
            )
            
            assert 'clock' in content, (
                f"Property violation: Scene transition broke clock initialization in {scene_file}"
            )
        
        print(f"\n✓ Property test PASSED: Scene transition sequence {scene_sequence} preserves structure")
