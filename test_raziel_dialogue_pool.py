"""
Unit tests for RazielDialoguePool class

Tests verify that the dialogue pool cycles through all key-related dialogues
correctly and handles missing dialogue keys gracefully.
"""

import pytest
from key_system import RazielDialoguePool


# Mock DIALOGS dictionary for testing
MOCK_DIALOGS = {
    "raziel_key_intro": [
        ("Raziel", "Eden has many keys."),
        ("Raziel", "Some open doors, others... well, they open different kinds of doors."),
    ],
    "raziel_key_gold": [
        ("Raziel", "That golden key? Yeah, that's mine."),
        ("Raziel", "I dropped it somewhere around here."),
        ("Raziel", "Nothing special about it, really. Just... shiny."),
    ],
    "raziel_key_bronze": [
        ("Raziel", "The bronze key has a story."),
        ("Raziel", "A young cherub once dropped it while guarding the tree of knowledge."),
        ("Raziel", "Got trapped in Eden for centuries because of it."),
        ("Raziel", "That cherub? You might meet them. They're still here, guarding."),
    ],
    "raziel_key_rusted": [
        ("Raziel", "That rusted key belonged to a seraph."),
        ("Raziel", "The one who banished your parents from Eden."),
        ("Raziel", "Dropped it in the chaos. Never bothered to pick it up."),
        ("Raziel", "Guess they figured humanity wouldn't be back."),
    ],
    "raziel_key_divine": [
        ("Raziel", "The divine key... that one's different."),
        ("Raziel", "Belonged to the watchers. You know, the ones who..."),
        ("Raziel", "...had relations with human women."),
        ("Raziel", "They were banished. Left their keys behind."),
        ("Raziel", "I wouldn't touch it if I were you. But you're not me."),
    ],
}


def test_dialogue_pool_cycles_through_all_dialogues():
    """Verify that dialogue pool cycles through all 5 dialogues"""
    pool = RazielDialoguePool()
    seen_keys = []
    
    # Get all 5 dialogues
    for _ in range(5):
        dialogue = pool.get_next_dialogue(MOCK_DIALOGS)
        # Find which key this dialogue corresponds to
        for key, value in MOCK_DIALOGS.items():
            if value == dialogue:
                seen_keys.append(key)
                break
    
    # Verify all 5 unique dialogue keys were seen
    assert len(seen_keys) == 5
    assert len(set(seen_keys)) == 5
    assert set(seen_keys) == {
        "raziel_key_intro",
        "raziel_key_gold",
        "raziel_key_bronze",
        "raziel_key_rusted",
        "raziel_key_divine"
    }


def test_dialogue_pool_repeats_after_cycle():
    """Verify that dialogue pool repeats after going through all dialogues"""
    pool = RazielDialoguePool()
    
    # Get first dialogue
    first_dialogue = pool.get_next_dialogue(MOCK_DIALOGS)
    
    # Cycle through remaining 4
    for _ in range(4):
        pool.get_next_dialogue(MOCK_DIALOGS)
    
    # Next should be first again
    repeated_dialogue = pool.get_next_dialogue(MOCK_DIALOGS)
    assert repeated_dialogue == first_dialogue


def test_dialogue_pool_tracks_seen_dialogues():
    """Verify that seen_dialogues set is updated correctly"""
    pool = RazielDialoguePool()
    
    assert len(pool.seen_dialogues) == 0
    
    pool.get_next_dialogue(MOCK_DIALOGS)
    assert len(pool.seen_dialogues) == 1
    
    for _ in range(4):
        pool.get_next_dialogue(MOCK_DIALOGS)
    
    assert len(pool.seen_dialogues) == 5


def test_dialogue_pool_fallback_for_missing_key(capsys):
    """Verify fallback for missing dialogue keys"""
    pool = RazielDialoguePool()
    
    # Use empty dictionary to trigger fallback
    empty_dialogs = {}
    
    dialogue = pool.get_next_dialogue(empty_dialogs)
    
    # Should return fallback dialogue
    assert dialogue == [("Raziel", "...")]
    
    # Should print warning
    captured = capsys.readouterr()
    assert "Warning: Dialogue key 'raziel_key_intro' not found" in captured.out


def test_dialogue_pool_maintains_order():
    """Verify that dialogues are returned in the expected order"""
    pool = RazielDialoguePool()
    
    expected_order = [
        "raziel_key_intro",
        "raziel_key_gold",
        "raziel_key_bronze",
        "raziel_key_rusted",
        "raziel_key_divine"
    ]
    
    for expected_key in expected_order:
        dialogue = pool.get_next_dialogue(MOCK_DIALOGS)
        assert dialogue == MOCK_DIALOGS[expected_key]


def test_dialogue_pool_current_index_wraps():
    """Verify that current_index wraps around correctly"""
    pool = RazielDialoguePool()
    
    assert pool.current_index == 0
    
    # Get 5 dialogues
    for i in range(5):
        pool.get_next_dialogue(MOCK_DIALOGS)
        expected_index = (i + 1) % 5
        assert pool.current_index == expected_index
    
    # After 5 calls, should be back to 0
    assert pool.current_index == 0


def test_dialogue_pool_seen_dialogues_accumulates():
    """Verify that seen_dialogues accumulates even after cycling"""
    pool = RazielDialoguePool()
    
    # Go through 2 complete cycles (10 dialogues)
    for _ in range(10):
        pool.get_next_dialogue(MOCK_DIALOGS)
    
    # Should still only have 5 unique dialogues in seen_dialogues
    assert len(pool.seen_dialogues) == 5
    assert pool.seen_dialogues == {
        "raziel_key_intro",
        "raziel_key_gold",
        "raziel_key_bronze",
        "raziel_key_rusted",
        "raziel_key_divine"
    }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
