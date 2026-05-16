"""
Bug Condition Exploration Test for MainMenu→Prologue→Start Transition

**Validates: Requirements 1.1, 1.2, 2.1, 2.2**

This test is designed to FAIL on unfixed code to confirm the bug exists.
When the test fails, it demonstrates that the game exits instead of transitioning to Start.main().

CRITICAL: This test encodes the EXPECTED behavior. When it passes after the fix,
it confirms the bug is resolved.

This test uses static code analysis to verify the bug condition and expected behavior,
which is more appropriate for this type of integration bug in a Pygame application.
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
import re
import os


class TestBugConditionExploration:
    """
    Property 1: Bug Condition - Prologue Completion Exits Instead of Transitioning
    
    This test explores the bug condition where clicking "Start" and completing
    the prologue causes the game to exit instead of transitioning to Start.main().
    
    The test uses static code analysis to verify:
    1. The bug exists in the unfixed code (pygame.quit() and sys.exit() after prologue)
    2. The fix is correctly implemented (Start.main() after prologue)
    """
    
    def test_prologue_completion_should_call_start_main_not_exit(self):
        """
        **Validates: Requirements 1.1, 1.2, 2.1, 2.2**
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect that pygame.quit() and sys.exit() are in the Start button handler
        - This confirms the bug exists
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will detect that Start.main() is in the Start button handler
        - This confirms the bug is fixed
        
        Bug Condition:
        - current_scene = "MainMenu"
        - button_clicked = "start"
        - prologue_completed = true
        - next_scene = "Start"
        
        Expected Behavior:
        - result.called_function = "Start.main()"
        - result.game_continues = true
        - NOT result.game_exited
        """
        
        # Read the MainMenuPage.py file
        with open('MainMenuPage.py', 'r') as f:
            content = f.read()
        
        # Find the "start" button handler
        # Pattern: elif btn["id"] == "start": ... p.run() ... [next lines]
        start_handler_pattern = r'elif\s+btn\["id"\]\s*==\s*"start":(.*?)(?=elif|if\s+event\.type|for\s+btn|$)'
        match = re.search(start_handler_pattern, content, re.DOTALL)
        
        assert match, "Could not find the 'start' button handler in MainMenuPage.py"
        
        start_handler_code = match.group(1)
        
        # Verify that p.run() is called (prologue runs)
        assert 'p.run()' in start_handler_code, (
            "Prologue.run() is not called in the start button handler"
        )
        
        # Check what happens AFTER p.run()
        # Split the handler code by p.run() and look at what comes after
        parts = start_handler_code.split('p.run()')
        assert len(parts) >= 2, "Could not find code after p.run()"
        
        after_prologue = parts[1].strip()
        
        # EXPECTED BEHAVIOR: Start.main() should be called after prologue
        # BUGGY BEHAVIOR: pygame.quit() and sys.exit() are called after prologue
        
        has_start_main = 'Start.main()' in after_prologue
        has_pygame_quit = 'pygame.quit()' in after_prologue
        has_sys_exit = 'sys.exit()' in after_prologue
        
        # Build detailed counterexample message
        counterexample_details = []
        
        if has_pygame_quit:
            counterexample_details.append("pygame.quit() is called after prologue completion")
        
        if has_sys_exit:
            counterexample_details.append("sys.exit() is called after prologue completion")
        
        if not has_start_main:
            counterexample_details.append("Start.main() is NOT called after prologue completion")
        
        # ASSERTION 1: Start.main() MUST be called after prologue
        assert has_start_main, (
            f"COUNTEREXAMPLE FOUND: Start.main() is not called after prologue completion.\n"
            f"Bug confirmed in MainMenuPage.py start button handler.\n"
            f"After p.run(), the code contains:\n{after_prologue[:200]}\n"
            f"Expected: Start.main() call\n"
            f"This confirms the bug exists - the game does not transition to Start scene."
        )
        
        # ASSERTION 2: pygame.quit() should NOT be called after prologue
        assert not has_pygame_quit, (
            f"COUNTEREXAMPLE FOUND: pygame.quit() is called after prologue completion.\n"
            f"Bug confirmed in MainMenuPage.py start button handler.\n"
            f"After p.run(), the code contains:\n{after_prologue[:200]}\n"
            f"pygame.quit() should only be called for Exit button or ESC in menu, not after prologue.\n"
            f"Root cause: lines 128-129 in MainMenuPage.py contain incorrect exit logic."
        )
        
        # ASSERTION 3: sys.exit() should NOT be called after prologue
        assert not has_sys_exit, (
            f"COUNTEREXAMPLE FOUND: sys.exit() is called after prologue completion.\n"
            f"Bug confirmed in MainMenuPage.py start button handler.\n"
            f"After p.run(), the code contains:\n{after_prologue[:200]}\n"
            f"sys.exit() should only be called for Exit button or ESC in menu, not after prologue.\n"
            f"Root cause: lines 128-129 in MainMenuPage.py contain incorrect exit logic."
        )
        
        # If we reach here, all assertions passed - the fix is correct!
        print("\n✓ Bug condition test PASSED: Start.main() is called after prologue completion")
        print("✓ Game continues to Start scene instead of exiting")
        print("✓ pygame.quit() and sys.exit() are NOT called after prologue")
    
    @given(
        check_type=st.sampled_from(['start_main_present', 'pygame_quit_absent', 'sys_exit_absent'])
    )
    @settings(
        max_examples=10,  # Scoped PBT: limited examples for this deterministic bug
        phases=[Phase.generate, Phase.target]  # Skip shrinking for faster execution
    )
    def test_property_prologue_completion_transitions_to_start(self, check_type):
        """
        **Validates: Requirements 1.1, 1.2, 2.1, 2.2**
        
        Property-Based Test: For ANY aspect of the prologue completion behavior,
        the code MUST satisfy the expected behavior properties.
        
        This property test generates multiple checks to ensure the fix is complete:
        - Start.main() is present after prologue
        - pygame.quit() is absent after prologue
        - sys.exit() is absent after prologue
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS with counterexamples
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES for all generated checks
        """
        
        # Read the MainMenuPage.py file
        with open('MainMenuPage.py', 'r') as f:
            content = f.read()
        
        # Find the "start" button handler
        start_handler_pattern = r'elif\s+btn\["id"\]\s*==\s*"start":(.*?)(?=elif|if\s+event\.type|for\s+btn|$)'
        match = re.search(start_handler_pattern, content, re.DOTALL)
        
        assert match, "Could not find the 'start' button handler in MainMenuPage.py"
        
        start_handler_code = match.group(1)
        
        # Verify that p.run() is called
        assert 'p.run()' in start_handler_code, "Prologue.run() is not called"
        
        # Get code after p.run()
        parts = start_handler_code.split('p.run()')
        assert len(parts) >= 2, "Could not find code after p.run()"
        after_prologue = parts[1].strip()
        
        # Property checks based on generated check_type
        if check_type == 'start_main_present':
            # Property: Start.main() MUST be present after prologue
            assert 'Start.main()' in after_prologue, (
                f"Property violation: Start.main() is not called after prologue completion.\n"
                f"Code after p.run(): {after_prologue[:200]}"
            )
        
        elif check_type == 'pygame_quit_absent':
            # Property: pygame.quit() MUST NOT be present after prologue
            assert 'pygame.quit()' not in after_prologue, (
                f"Property violation: pygame.quit() is called after prologue completion.\n"
                f"This should only be called for Exit button or ESC in menu.\n"
                f"Code after p.run(): {after_prologue[:200]}"
            )
        
        elif check_type == 'sys_exit_absent':
            # Property: sys.exit() MUST NOT be present after prologue
            assert 'sys.exit()' not in after_prologue, (
                f"Property violation: sys.exit() is called after prologue completion.\n"
                f"This should only be called for Exit button or ESC in menu.\n"
                f"Code after p.run(): {after_prologue[:200]}"
            )
    



class TestPreservationProperties:
    """
    Property 2: Preservation - Other Exit Points Unchanged
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
    
    These tests verify that the fix does NOT break existing functionality.
    They observe behavior on UNFIXED code and verify it remains unchanged after the fix.
    
    EXPECTED OUTCOME ON UNFIXED CODE: All tests PASS (baseline behavior)
    EXPECTED OUTCOME ON FIXED CODE: All tests PASS (behavior preserved)
    """
    
    def test_exit_button_calls_pygame_quit_and_sys_exit(self):
        """
        **Validates: Requirement 3.1**
        
        Preservation Test: Exit button functionality
        
        Observes that Exit button handler calls pygame.quit() and sys.exit()
        on unfixed code, and verifies this behavior is preserved after fix.
        """
        
        # Read the MainMenuPage.py file
        with open('MainMenuPage.py', 'r') as f:
            content = f.read()
        
        # Find the "exit" button handler
        exit_handler_pattern = r'if\s+btn\["id"\]\s*==\s*"exit":(.*?)(?=elif|$)'
        match = re.search(exit_handler_pattern, content, re.DOTALL)
        
        assert match, "Could not find the 'exit' button handler in MainMenuPage.py"
        
        exit_handler_code = match.group(1)
        
        # Verify that pygame.quit() and sys.exit() are called for Exit button
        assert 'pygame.quit()' in exit_handler_code, (
            "Exit button handler should call pygame.quit()"
        )
        
        assert 'sys.exit()' in exit_handler_code, (
            "Exit button handler should call sys.exit()"
        )
        
        print("\n✓ Preservation: Exit button calls pygame.quit() and sys.exit()")
    
    def test_esc_key_in_menu_calls_pygame_quit_and_sys_exit(self):
        """
        **Validates: Requirement 3.2**
        
        Preservation Test: ESC key in MainMenu functionality
        
        Observes that ESC key handler calls pygame.quit() and sys.exit()
        on unfixed code, and verifies this behavior is preserved after fix.
        """
        
        # Read the MainMenuPage.py file
        with open('MainMenuPage.py', 'r') as f:
            content = f.read()
        
        # Find the ESC key handler in the main menu
        esc_handler_pattern = r'if\s+event\.key\s*==\s*pygame\.K_ESCAPE:(.*?)(?=if\s+event|$)'
        match = re.search(esc_handler_pattern, content, re.DOTALL)
        
        assert match, "Could not find the ESC key handler in MainMenuPage.py"
        
        esc_handler_code = match.group(1)
        
        # Verify that pygame.quit() and sys.exit() are called for ESC key
        assert 'pygame.quit()' in esc_handler_code, (
            "ESC key handler should call pygame.quit()"
        )
        
        assert 'sys.exit()' in esc_handler_code, (
            "ESC key handler should call sys.exit()"
        )
        
        print("\n✓ Preservation: ESC key in menu calls pygame.quit() and sys.exit()")
    
    def test_window_close_calls_pygame_quit_and_sys_exit(self):
        """
        **Validates: Requirement 3.3**
        
        Preservation Test: Window close (X button) functionality
        
        Observes that QUIT event handler calls pygame.quit() and sys.exit()
        on unfixed code, and verifies this behavior is preserved after fix.
        """
        
        # Read the MainMenuPage.py file
        with open('MainMenuPage.py', 'r') as f:
            content = f.read()
        
        # Find the QUIT event handler
        quit_handler_pattern = r'if\s+event\.type\s*==\s*pygame\.QUIT:(.*?)(?=if\s+event|$)'
        match = re.search(quit_handler_pattern, content, re.DOTALL)
        
        assert match, "Could not find the QUIT event handler in MainMenuPage.py"
        
        quit_handler_code = match.group(1)
        
        # Verify that pygame.quit() and sys.exit() are called for window close
        assert 'pygame.quit()' in quit_handler_code, (
            "QUIT event handler should call pygame.quit()"
        )
        
        assert 'sys.exit()' in quit_handler_code, (
            "QUIT event handler should call sys.exit()"
        )
        
        print("\n✓ Preservation: Window close calls pygame.quit() and sys.exit()")
    
    def test_button_hover_effects_exist(self):
        """
        **Validates: Requirement 3.4**
        
        Preservation Test: Button hover effects
        
        Observes that button hover logic exists in the draw_menu function
        on unfixed code, and verifies this behavior is preserved after fix.
        """
        
        # Read the MainMenuPage.py file
        with open('MainMenuPage.py', 'r') as f:
            content = f.read()
        
        # Find the draw_menu function
        draw_menu_pattern = r'def\s+draw_menu\((.*?)\):(.*?)(?=def\s+|if\s+__name__|$)'
        match = re.search(draw_menu_pattern, content, re.DOTALL)
        
        assert match, "Could not find the draw_menu function in MainMenuPage.py"
        
        draw_menu_code = match.group(2)
        
        # Verify that hover detection exists
        assert 'collidepoint' in draw_menu_code, (
            "Button hover detection (collidepoint) should exist in draw_menu"
        )
        
        # Verify that hover changes button appearance
        assert 'hovered' in draw_menu_code.lower() or 'hover' in draw_menu_code.lower(), (
            "Button hover state tracking should exist in draw_menu"
        )
        
        # Verify that different colors are used for hover state
        assert 'GOLD_HOVER' in draw_menu_code or 'hover' in draw_menu_code.lower(), (
            "Button hover color changes should exist in draw_menu"
        )
        
        print("\n✓ Preservation: Button hover effects are implemented")
    
    def test_characters_button_is_enabled_and_functional(self):
        """
        **Validates: Requirement 3.5**
        
        Test: "Characters" button is now enabled and functional
        
        Verifies that "Characters" button is marked as enabled (enabled=True)
        and has proper click handling to open the Characters page.
        """
        
        # Read the MainMenuPage.py file
        with open('MainMenuPage.py', 'r') as f:
            content = f.read()
        
        # Find the buttons configuration
        buttons_pattern = r'buttons\s*=\s*\[(.*?)\]'
        match = re.search(buttons_pattern, content, re.DOTALL)
        
        assert match, "Could not find the buttons configuration in MainMenuPage.py"
        
        buttons_config = match.group(1)
        
        # Find the "Characters" button entry
        characters_pattern = r'\{[^}]*"label":\s*"Characters"[^}]*\}'
        char_match = re.search(characters_pattern, buttons_config)
        
        assert char_match, "Could not find the 'Characters' button in buttons configuration"
        
        characters_button = char_match.group(0)
        
        # Verify that "Characters" button is enabled
        assert re.search(r'"enabled":\s*True', characters_button) or '"enabled": True' in characters_button, (
            "'Characters' button should be enabled (enabled: True)"
        )
        
        # Verify that click handler checks enabled state
        click_handler_pattern = r'if\s+event\.type\s*==\s*pygame\.MOUSEBUTTONDOWN.*?for\s+btn.*?if.*?collidepoint.*?and\s+btn\["enabled"\]'
        assert re.search(click_handler_pattern, content, re.DOTALL), (
            "Click handler should check btn['enabled'] before processing clicks"
        )
        
        # Verify that Characters button has a handler
        characters_handler_pattern = r'elif\s+btn\["id"\]\s*==\s*"characters"'
        assert re.search(characters_handler_pattern, content), (
            "Characters button should have a click handler"
        )
        
        # Verify CharactersPage is imported
        assert 'import CharactersPage' in content or 'from CharactersPage import' in content, (
            "CharactersPage should be imported"
        )
        
        print("\n✓ Characters button is enabled and functional")
    
    @given(
        exit_mechanism=st.sampled_from(['exit_button', 'esc_key', 'window_close'])
    )
    @settings(
        max_examples=15,  # Test each exit mechanism multiple times
        phases=[Phase.generate, Phase.target]
    )
    def test_property_all_exit_mechanisms_call_pygame_quit_and_sys_exit(self, exit_mechanism):
        """
        **Validates: Requirements 3.1, 3.2, 3.3**
        
        Property-Based Test: For ANY exit mechanism (Exit button, ESC key, window close),
        the code MUST call pygame.quit() and sys.exit() to properly terminate the game.
        
        This property test generates multiple checks across all exit mechanisms
        to ensure they all preserve the correct exit behavior.
        
        EXPECTED OUTCOME: Tests PASS on both unfixed and fixed code
        """
        
        # Read the MainMenuPage.py file
        with open('MainMenuPage.py', 'r') as f:
            content = f.read()
        
        if exit_mechanism == 'exit_button':
            # Find the "exit" button handler
            pattern = r'if\s+btn\["id"\]\s*==\s*"exit":(.*?)(?=elif|$)'
            match = re.search(pattern, content, re.DOTALL)
            assert match, "Could not find the 'exit' button handler"
            handler_code = match.group(1)
            mechanism_name = "Exit button"
        
        elif exit_mechanism == 'esc_key':
            # Find the ESC key handler
            pattern = r'if\s+event\.key\s*==\s*pygame\.K_ESCAPE:(.*?)(?=if\s+event|$)'
            match = re.search(pattern, content, re.DOTALL)
            assert match, "Could not find the ESC key handler"
            handler_code = match.group(1)
            mechanism_name = "ESC key"
        
        elif exit_mechanism == 'window_close':
            # Find the QUIT event handler
            pattern = r'if\s+event\.type\s*==\s*pygame\.QUIT:(.*?)(?=if\s+event|$)'
            match = re.search(pattern, content, re.DOTALL)
            assert match, "Could not find the QUIT event handler"
            handler_code = match.group(1)
            mechanism_name = "Window close"
        
        # Property: ALL exit mechanisms MUST call pygame.quit() and sys.exit()
        assert 'pygame.quit()' in handler_code, (
            f"Property violation: {mechanism_name} handler does not call pygame.quit()"
        )
        
        assert 'sys.exit()' in handler_code, (
            f"Property violation: {mechanism_name} handler does not call sys.exit()"
        )
    
    @given(
        button_name=st.sampled_from(['Start', 'Characters', 'Exit'])
    )
    @settings(
        max_examples=15,  # Test each button multiple times
        phases=[Phase.generate, Phase.target]
    )
    def test_property_all_buttons_have_hover_detection(self, button_name):
        """
        **Validates: Requirement 3.4**
        
        Property-Based Test: For ANY button in the menu, hover detection
        MUST be implemented to provide visual feedback.
        
        This property test generates checks for all buttons to ensure
        hover effects are preserved across the entire menu.
        
        EXPECTED OUTCOME: Tests PASS on both unfixed and fixed code
        """
        
        # Read the MainMenuPage.py file
        with open('MainMenuPage.py', 'r') as f:
            content = f.read()
        
        # Verify button exists in configuration
        buttons_pattern = r'buttons\s*=\s*\[(.*?)\]'
        match = re.search(buttons_pattern, content, re.DOTALL)
        assert match, "Could not find buttons configuration"
        
        buttons_config = match.group(1)
        
        # Check that the button is defined
        button_pattern = rf'\{{"label":\s*"{button_name}"'
        assert re.search(button_pattern, buttons_config), (
            f"Button '{button_name}' not found in buttons configuration"
        )
        
        # Verify hover detection exists in draw_menu
        draw_menu_pattern = r'def\s+draw_menu\((.*?)\):(.*?)(?=def\s+|if\s+__name__|$)'
        match = re.search(draw_menu_pattern, content, re.DOTALL)
        assert match, "Could not find draw_menu function"
        
        draw_menu_code = match.group(2)
        
        # Property: Hover detection MUST exist for all buttons
        assert 'collidepoint' in draw_menu_code, (
            f"Property violation: Hover detection (collidepoint) not found for button '{button_name}'"
        )
        
        assert 'hovered' in draw_menu_code.lower() or 'hover' in draw_menu_code.lower(), (
            f"Property violation: Hover state tracking not found for button '{button_name}'"
        )
    
    @given(
        ui_element=st.sampled_from([
            'button_border',
            'button_fill',
            'button_label',
            'title_text',
            'decorative_rule'
        ])
    )
    @settings(
        max_examples=20,  # Test various UI elements
        phases=[Phase.generate, Phase.target]
    )
    def test_property_ui_elements_are_rendered(self, ui_element):
        """
        **Validates: Requirement 3.4**
        
        Property-Based Test: For ANY UI element in the menu, rendering code
        MUST exist to display the element correctly.
        
        This property test generates checks for various UI elements to ensure
        the visual presentation is preserved after the fix.
        
        EXPECTED OUTCOME: Tests PASS on both unfixed and fixed code
        """
        
        # Read the MainMenuPage.py file
        with open('MainMenuPage.py', 'r') as f:
            content = f.read()
        
        # Find the draw_menu function
        draw_menu_pattern = r'def\s+draw_menu\((.*?)\):(.*?)(?=def\s+|if\s+__name__|$)'
        match = re.search(draw_menu_pattern, content, re.DOTALL)
        assert match, "Could not find draw_menu function"
        
        draw_menu_code = match.group(2)
        
        # Property checks based on UI element type
        if ui_element == 'button_border':
            assert 'pygame.draw.rect' in draw_menu_code and 'border' in draw_menu_code.lower(), (
                "Property violation: Button border rendering not found"
            )
        
        elif ui_element == 'button_fill':
            assert 'pygame.draw.rect' in draw_menu_code and 'fill' in draw_menu_code.lower(), (
                "Property violation: Button fill rendering not found"
            )
        
        elif ui_element == 'button_label':
            assert 'render' in draw_menu_code and 'label' in draw_menu_code.lower(), (
                "Property violation: Button label rendering not found"
            )
        
        elif ui_element == 'title_text':
            assert 'title' in draw_menu_code.lower() and 'render' in draw_menu_code, (
                "Property violation: Title text rendering not found"
            )
        
        elif ui_element == 'decorative_rule':
            assert 'pygame.draw.line' in draw_menu_code, (
                "Property violation: Decorative rule rendering not found"
            )


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])
