"""
Integration Tests for Raziel Key Dialogue System

This test file verifies the complete end-to-end functionality of the
Raziel Key Dialogue System, including:
- Key spawning after Mikhail chase
- Key discovery flow (proximity → narrator text → pickup prompt)
- Key swapping flow (hold key → discover new key → swap → old key drops)
- Raziel dialogue cycling through all 5 dialogues
- Key sprite rendering
- Guardian lore update in Characters screen
"""

import pytest
import pygame
import sys
import os

# Add parent directory to path to import game modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from key_system import KeyEntity, spawn_keys, RazielDialoguePool, KEY_SPAWN_LOCATIONS
import Start
from CharactersPage import CHARACTERS


class TestKeySpawning:
    """Test that keys spawn correctly after Mikhail chase is triggered."""
    
    def test_spawn_keys_creates_four_keys(self):
        """Verify that spawn_keys creates exactly 4 KeyEntity objects."""
        keys = spawn_keys()
        assert len(keys) == 4, f"Expected 4 keys, got {len(keys)}"
    
    def test_spawn_keys_correct_types(self):
        """Verify that all four key types are spawned."""
        keys = spawn_keys()
        key_types = {key.key_type for key in keys}
        expected_types = {"bronze", "gold", "rusted", "divine"}
        assert key_types == expected_types, f"Expected {expected_types}, got {key_types}"
    
    def test_spawn_keys_correct_positions(self):
        """Verify that keys spawn at designated locations."""
        keys = spawn_keys()
        for key in keys:
            expected_pos = KEY_SPAWN_LOCATIONS[key.key_type]
            actual_pos = (key.rect.x, key.rect.y)
            assert actual_pos == expected_pos, \
                f"Key {key.key_type} at {actual_pos}, expected {expected_pos}"
    
    def test_all_keys_have_sprites(self):
        """Verify that all keys have valid sprites loaded."""
        keys = spawn_keys()
        for key in keys:
            assert key.sprite is not None, f"Key {key.key_type} has no sprite"
            assert isinstance(key.sprite, pygame.Surface), \
                f"Key {key.key_type} sprite is not a pygame Surface"
            assert key.sprite.get_width() == 16, \
                f"Key {key.key_type} sprite width is {key.sprite.get_width()}, expected 16"
            assert key.sprite.get_height() == 16, \
                f"Key {key.key_type} sprite height is {key.sprite.get_height()}, expected 16"


class TestKeyDiscovery:
    """Test the key discovery flow: proximity → narrator text → pickup prompt."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        pygame.init()
        pygame.display.set_mode((100, 100))  # Minimal display for testing
    
    def test_key_discovery_detects_nearby_key(self):
        """Verify that check_key_discovery detects keys within range."""
        player = Start.Player()
        player.rect.center = (100, 100)
        
        key = KeyEntity("bronze", (110, 110))  # Within range (30 pixels)
        keys = [key]
        
        discovered = Start.check_key_discovery(player, keys)
        assert discovered == key, "Key should be discovered when player is nearby"
        assert key.discovered == True, "Key discovered flag should be set to True"
    
    def test_key_discovery_ignores_distant_key(self):
        """Verify that check_key_discovery ignores keys out of range."""
        player = Start.Player()
        player.rect.center = (100, 100)
        
        key = KeyEntity("bronze", (200, 200))  # Out of range
        keys = [key]
        
        discovered = Start.check_key_discovery(player, keys)
        assert discovered is None, "Key should not be discovered when player is far away"
        assert key.discovered == False, "Key discovered flag should remain False"
    
    def test_key_discovery_ignores_already_discovered(self):
        """Verify that already discovered keys are not re-discovered."""
        player = Start.Player()
        player.rect.center = (100, 100)
        
        key = KeyEntity("bronze", (110, 110))
        key.discovered = True  # Already discovered
        keys = [key]
        
        discovered = Start.check_key_discovery(player, keys)
        assert discovered is None, "Already discovered keys should not be re-discovered"
    
    def test_narrator_text_exists_for_all_keys(self):
        """Verify that narrator text is defined for all key types."""
        expected_keys = {"bronze", "gold", "rusted", "divine"}
        actual_keys = set(Start.KEY_NARRATOR_TEXT.keys())
        assert actual_keys == expected_keys, \
            f"Narrator text missing for keys: {expected_keys - actual_keys}"
    
    def test_narrator_text_content(self):
        """Verify that narrator text contains appropriate content for each key."""
        # Bronze key should mention "light as a feather"
        assert "light as a feather" in Start.KEY_NARRATOR_TEXT["bronze"].lower()
        
        # Gold key should mention "brand new" or "Raziel"
        gold_text = Start.KEY_NARRATOR_TEXT["gold"].lower()
        assert "brand new" in gold_text or "raziel" in gold_text
        
        # Rusted key should mention "rusted"
        assert "rusted" in Start.KEY_NARRATOR_TEXT["rusted"].lower()
        
        # Divine key should mention "overwhelming presence" or "blinks"
        divine_text = Start.KEY_NARRATOR_TEXT["divine"].lower()
        assert "overwhelming presence" in divine_text or "blinks" in divine_text


class TestPlayerInventory:
    """Test player inventory and key pickup mechanics."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        pygame.init()
        pygame.display.set_mode((100, 100))
    
    def test_player_starts_without_key(self):
        """Verify that player starts with no key."""
        player = Start.Player()
        assert player.held_key is None, "Player should start with no key"
        assert player.has_key() == False, "has_key() should return False initially"
    
    def test_player_pickup_key_when_empty(self):
        """Verify player can pick up key when not holding one."""
        player = Start.Player()
        key = KeyEntity("bronze", (100, 100))
        
        old_key = player.pickup_key(key)
        
        assert player.held_key == key, "Player should be holding the picked up key"
        assert old_key is None, "Should return None when picking up first key"
        assert player.has_key() == True, "has_key() should return True after pickup"
    
    def test_player_pickup_key_when_holding(self):
        """Verify player swaps keys when already holding one."""
        player = Start.Player()
        old_key = KeyEntity("bronze", (100, 100))
        new_key = KeyEntity("gold", (200, 200))
        
        player.pickup_key(old_key)
        returned_key = player.pickup_key(new_key)
        
        assert player.held_key == new_key, "Player should be holding the new key"
        assert returned_key == old_key, "Should return the old key when swapping"
    
    def test_player_drop_key(self):
        """Verify player can drop a held key."""
        player = Start.Player()
        key = KeyEntity("bronze", (100, 100))
        
        player.pickup_key(key)
        dropped = player.drop_key()
        
        assert dropped == key, "Should return the dropped key"
        assert player.held_key is None, "Player should no longer be holding a key"
        assert player.has_key() == False, "has_key() should return False after drop"


class TestKeySwapping:
    """Test the key swapping flow: hold key → discover new key → swap → old key drops."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        pygame.init()
        pygame.display.set_mode((100, 100))
    
    def test_handle_key_swap_drops_old_key(self):
        """Verify that key swapping drops old key at player location."""
        player = Start.Player()
        player.rect.center = (150, 150)
        
        old_key = KeyEntity("bronze", (100, 100))
        new_key = KeyEntity("gold", (200, 200))
        
        player.pickup_key(old_key)
        keys_in_world = [new_key]
        
        Start.handle_key_swap(player, new_key, keys_in_world)
        
        assert player.held_key == new_key, "Player should be holding the new key"
        assert old_key in keys_in_world, "Old key should be in the world"
        assert old_key.rect.center == (150, 150), \
            f"Old key should be at player location {(150, 150)}, got {old_key.rect.center}"
        assert old_key.discovered == False, "Old key discovered flag should be reset"
    
    def test_handle_key_swap_removes_new_key_from_world(self):
        """Verify that picked up key is removed from world."""
        player = Start.Player()
        new_key = KeyEntity("gold", (200, 200))
        keys_in_world = [new_key]
        
        Start.handle_key_swap(player, new_key, keys_in_world)
        
        assert new_key not in keys_in_world, "New key should be removed from world"
        assert player.held_key == new_key, "Player should be holding the new key"
    
    def test_handle_key_swap_first_pickup(self):
        """Verify that first key pickup works correctly (no old key to drop)."""
        player = Start.Player()
        new_key = KeyEntity("bronze", (100, 100))
        keys_in_world = [new_key]
        
        Start.handle_key_swap(player, new_key, keys_in_world)
        
        assert player.held_key == new_key, "Player should be holding the key"
        assert new_key not in keys_in_world, "Key should be removed from world"
        assert len(keys_in_world) == 0, "World should have no keys after pickup"
    
    def test_handle_key_swap_validation(self):
        """Verify that handle_key_swap validates key is in world."""
        player = Start.Player()
        fake_key = KeyEntity("bronze", (100, 100))
        keys_in_world = []
        
        # Should not crash, just print warning
        Start.handle_key_swap(player, fake_key, keys_in_world)
        
        # Player should not have picked up the fake key
        assert player.held_key is None, "Player should not have picked up invalid key"


class TestRazielDialoguePool:
    """Test Raziel dialogue cycling through all 5 dialogues."""
    
    def test_dialogue_pool_initialization(self):
        """Verify that dialogue pool initializes with correct dialogues."""
        pool = RazielDialoguePool()
        
        assert len(pool.dialogue_keys) == 5, "Should have 5 dialogue keys"
        assert pool.current_index == 0, "Should start at index 0"
        assert len(pool.seen_dialogues) == 0, "Should have no seen dialogues initially"
    
    def test_dialogue_pool_cycles_through_all_dialogues(self):
        """Verify that dialogue pool cycles through all 5 dialogues."""
        pool = RazielDialoguePool()
        seen_keys = []
        
        for _ in range(5):
            dialogue = pool.get_next_dialogue(Start.DIALOGS)
            # Find which key this dialogue corresponds to
            for key, value in Start.DIALOGS.items():
                if value == dialogue:
                    seen_keys.append(key)
                    break
        
        # Should have seen all 5 key dialogues
        expected_keys = [
            "raziel_key_intro",
            "raziel_key_gold",
            "raziel_key_bronze",
            "raziel_key_rusted",
            "raziel_key_divine"
        ]
        assert seen_keys == expected_keys, \
            f"Expected dialogue order {expected_keys}, got {seen_keys}"
    
    def test_dialogue_pool_repeats_after_cycle(self):
        """Verify that dialogue pool repeats after going through all dialogues."""
        pool = RazielDialoguePool()
        
        # Get first dialogue
        first_dialogue = pool.get_next_dialogue(Start.DIALOGS)
        
        # Cycle through remaining 4
        for _ in range(4):
            pool.get_next_dialogue(Start.DIALOGS)
        
        # Next should be first again
        repeated_dialogue = pool.get_next_dialogue(Start.DIALOGS)
        assert repeated_dialogue == first_dialogue, \
            "Dialogue pool should repeat after cycling through all dialogues"
    
    def test_dialogue_pool_tracks_seen_dialogues(self):
        """Verify that seen_dialogues set is updated correctly."""
        pool = RazielDialoguePool()
        
        assert len(pool.seen_dialogues) == 0, "Should start with no seen dialogues"
        
        pool.get_next_dialogue(Start.DIALOGS)
        assert len(pool.seen_dialogues) == 1, "Should have 1 seen dialogue"
        
        for _ in range(4):
            pool.get_next_dialogue(Start.DIALOGS)
        
        assert len(pool.seen_dialogues) == 5, "Should have all 5 dialogues seen"
    
    def test_all_raziel_key_dialogues_exist(self):
        """Verify that all Raziel key dialogues are defined in DIALOGS."""
        expected_dialogues = [
            "raziel_key_intro",
            "raziel_key_gold",
            "raziel_key_bronze",
            "raziel_key_rusted",
            "raziel_key_divine"
        ]
        
        for dialogue_key in expected_dialogues:
            assert dialogue_key in Start.DIALOGS, \
                f"Dialogue '{dialogue_key}' not found in DIALOGS"
            
            dialogue = Start.DIALOGS[dialogue_key]
            assert isinstance(dialogue, list), \
                f"Dialogue '{dialogue_key}' should be a list"
            assert len(dialogue) > 0, \
                f"Dialogue '{dialogue_key}' should not be empty"
            
            # Verify format: list of (speaker, text) tuples
            for entry in dialogue:
                assert isinstance(entry, tuple), \
                    f"Dialogue entry should be a tuple, got {type(entry)}"
                assert len(entry) == 2, \
                    f"Dialogue entry should have 2 elements, got {len(entry)}"
                assert entry[0] == "Raziel", \
                    f"Speaker should be 'Raziel', got '{entry[0]}'"
    
    def test_dialogue_pool_fallback_for_missing_key(self):
        """Verify that dialogue pool handles missing dialogue keys gracefully."""
        pool = RazielDialoguePool()
        # Temporarily replace dialogue keys with invalid ones
        pool.dialogue_keys = ["nonexistent_dialogue"]
        
        # Should return fallback dialogue without crashing
        dialogue = pool.get_next_dialogue(Start.DIALOGS)
        assert dialogue == [("Raziel", "...")], \
            "Should return fallback dialogue for missing key"


class TestGuardianLoreUpdate:
    """Test that Guardian lore update appears in Characters screen."""
    
    def test_guardian_character_exists(self):
        """Verify that Guardian character exists in CHARACTERS list."""
        guardian = None
        for char in CHARACTERS:
            if char["name"] == "The Guardian":
                guardian = char
                break
        
        assert guardian is not None, "Guardian character not found in CHARACTERS"
    
    def test_guardian_lore_mentions_bronze_key(self):
        """Verify that Guardian description references bronze key backstory."""
        guardian = None
        for char in CHARACTERS:
            if char["name"] == "The Guardian":
                guardian = char
                break
        
        assert guardian is not None, "Guardian character not found"
        
        description = guardian["description"].lower()
        
        # Should mention bronze key
        assert "bronze key" in description, \
            "Guardian description should mention 'bronze key'"
        
        # Should mention being trapped
        assert "trapped" in description, \
            "Guardian description should mention being 'trapped'"
        
        # Should mention Eden
        assert "eden" in description, \
            "Guardian description should mention 'Eden'"
        
        # Should mention centuries
        assert "centuries" in description or "century" in description, \
            "Guardian description should mention time period"
    
    def test_guardian_lore_consistency_with_raziel_dialogue(self):
        """Verify Guardian lore is consistent with Raziel's bronze key dialogue."""
        # Get Raziel's bronze key dialogue
        raziel_dialogue = Start.DIALOGS["raziel_key_bronze"]
        raziel_text = " ".join([text for _, text in raziel_dialogue]).lower()
        
        # Get Guardian description
        guardian = None
        for char in CHARACTERS:
            if char["name"] == "The Guardian":
                guardian = char
                break
        
        guardian_desc = guardian["description"].lower()
        
        # Both should mention:
        # - Young cherub/cherubim
        assert ("cherub" in raziel_text and "cherub" in guardian_desc), \
            "Both should mention cherub"
        
        # - Dropped key
        assert ("dropped" in raziel_text and "dropped" in guardian_desc), \
            "Both should mention dropping the key"
        
        # - Trapped in Eden
        assert ("trapped" in raziel_text and "trapped" in guardian_desc), \
            "Both should mention being trapped"


class TestGameStates:
    """Test that game states for key system are properly defined."""
    
    def test_key_discovery_state_exists(self):
        """Verify that STATE_KEY_DISCOVERY is defined."""
        assert hasattr(Start, "STATE_KEY_DISCOVERY"), \
            "STATE_KEY_DISCOVERY should be defined"
        assert Start.STATE_KEY_DISCOVERY == "key_discovery", \
            "STATE_KEY_DISCOVERY should equal 'key_discovery'"
    
    def test_key_pickup_prompt_state_exists(self):
        """Verify that STATE_KEY_PICKUP_PROMPT is defined."""
        assert hasattr(Start, "STATE_KEY_PICKUP_PROMPT"), \
            "STATE_KEY_PICKUP_PROMPT should be defined"
        assert Start.STATE_KEY_PICKUP_PROMPT == "key_pickup_prompt", \
            "STATE_KEY_PICKUP_PROMPT should equal 'key_pickup_prompt'"


class TestIntegrationScenarios:
    """Test complete integration scenarios."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        pygame.init()
        pygame.display.set_mode((100, 100))
    
    def test_complete_key_discovery_flow(self):
        """Test complete flow: spawn → discover → pickup."""
        # Spawn keys
        keys = spawn_keys()
        assert len(keys) == 4
        
        # Create player near a key
        player = Start.Player()
        bronze_key = [k for k in keys if k.key_type == "bronze"][0]
        player.rect.center = bronze_key.rect.center
        
        # Discover key
        discovered = Start.check_key_discovery(player, keys)
        assert discovered == bronze_key
        assert bronze_key.discovered == True
        
        # Pick up key
        Start.handle_key_swap(player, bronze_key, keys)
        assert player.held_key == bronze_key
        assert bronze_key not in keys
    
    def test_complete_key_swapping_flow(self):
        """Test complete flow: hold key → discover new → swap → old drops."""
        # Spawn keys
        keys = spawn_keys()
        
        # Create player and pick up first key
        player = Start.Player()
        bronze_key = [k for k in keys if k.key_type == "bronze"][0]
        player.rect.center = (150, 150)
        
        Start.handle_key_swap(player, bronze_key, keys)
        assert player.held_key == bronze_key
        
        # Move to second key
        gold_key = [k for k in keys if k.key_type == "gold"][0]
        player.rect.center = gold_key.rect.center
        
        # Discover second key
        discovered = Start.check_key_discovery(player, keys)
        assert discovered == gold_key
        
        # Swap keys
        Start.handle_key_swap(player, gold_key, keys)
        
        # Verify swap
        assert player.held_key == gold_key
        assert bronze_key in keys  # Old key dropped back into world
        assert gold_key not in keys  # New key removed from world
        assert bronze_key.discovered == False  # Old key discovery reset
    
    def test_raziel_dialogue_full_cycle(self):
        """Test that Raziel cycles through all 5 dialogues and repeats."""
        pool = RazielDialoguePool()
        dialogues_seen = []
        
        # Go through 10 dialogues (2 full cycles)
        for _ in range(10):
            dialogue = pool.get_next_dialogue(Start.DIALOGS)
            # Get the first line of dialogue to identify it
            first_line = dialogue[0][1] if dialogue else ""
            dialogues_seen.append(first_line)
        
        # First 5 should be unique
        first_cycle = dialogues_seen[:5]
        assert len(set(first_cycle)) == 5, "First 5 dialogues should be unique"
        
        # Second 5 should match first 5 (repeating)
        second_cycle = dialogues_seen[5:10]
        assert first_cycle == second_cycle, "Dialogue should repeat after full cycle"


def run_manual_test_checklist():
    """
    Print a manual test checklist for visual verification.
    This should be run in the actual game to verify visual elements.
    """
    print("\n" + "="*70)
    print("MANUAL TEST CHECKLIST - Raziel Key Dialogue System")
    print("="*70)
    print("\n1. KEY SPAWNING")
    print("   [ ] Start game and trigger Mikhail chase (approach him 3 times)")
    print("   [ ] Verify 4 keys spawn in the world after chase starts")
    print("   [ ] Verify keys are visible and positioned correctly")
    print()
    print("2. KEY DISCOVERY FLOW")
    print("   [ ] Walk near a key")
    print("   [ ] Verify narrator text appears with key description")
    print("   [ ] Verify 'Pick it up?' prompt appears with Y/N options")
    print("   [ ] Test declining (N) - key should remain in world")
    print("   [ ] Test accepting (Y) - key should be added to inventory")
    print()
    print("3. KEY SPRITES")
    print("   [ ] Bronze key sprite renders correctly")
    print("   [ ] Gold key sprite renders correctly")
    print("   [ ] Rusted key sprite renders correctly")
    print("   [ ] Divine key sprite renders correctly")
    print("   [ ] Key icon appears above player when holding a key")
    print()
    print("4. KEY SWAPPING")
    print("   [ ] Pick up first key")
    print("   [ ] Walk to second key and discover it")
    print("   [ ] Accept pickup of second key")
    print("   [ ] Verify first key drops at player's location")
    print("   [ ] Verify player now holds second key")
    print("   [ ] Verify dropped key can be picked up again")
    print()
    print("5. RAZIEL DIALOGUE CYCLING")
    print("   [ ] Interact with Raziel 5 times during roaming")
    print("   [ ] Verify dialogue 1: 'Eden has many keys...'")
    print("   [ ] Verify dialogue 2: 'That golden key? Yeah, that's mine...'")
    print("   [ ] Verify dialogue 3: 'The bronze key has a story...'")
    print("   [ ] Verify dialogue 4: 'That rusted key belonged to a seraph...'")
    print("   [ ] Verify dialogue 5: 'The divine key... that one's different...'")
    print("   [ ] Interact again - should cycle back to dialogue 1")
    print()
    print("6. GUARDIAN LORE")
    print("   [ ] Open Characters screen from main menu")
    print("   [ ] Navigate to Guardian character")
    print("   [ ] Verify description mentions bronze key")
    print("   [ ] Verify description mentions being trapped for centuries")
    print("   [ ] Verify lore is consistent with Raziel's dialogue")
    print()
    print("="*70)
    print("All manual tests should be verified in the actual game.")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run automated tests
    print("Running automated integration tests...")
    pytest.main([__file__, "-v", "--tb=short"])
    
    # Print manual test checklist
    run_manual_test_checklist()
