"""
Integration test for Task 8: Raziel Dialogue Pool Integration

This test verifies that:
1. raziel_dialogue_pool instance is created in main()
2. The dialogue pool is used during STATE_ANGEL_DIALOG for roaming interactions
3. The dialogue pool cycles through key dialogues instead of fixed "raziel_roaming"
"""

import re


def test_raziel_dialogue_pool_instance_created():
    """
    Verify that raziel_dialogue_pool instance is created in main() function.
    
    **Validates: Requirements 2.7**
    """
    with open("Start.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check that RazielDialoguePool is imported
    assert "from key_system import" in content, \
        "key_system import not found"
    assert "RazielDialoguePool" in content, \
        "RazielDialoguePool not imported from key_system"
    
    # Check that raziel_dialogue_pool instance is created
    pattern = r'raziel_dialogue_pool\s*=\s*RazielDialoguePool\(\)'
    match = re.search(pattern, content)
    
    assert match, \
        "raziel_dialogue_pool instance not created in main(). Expected: raziel_dialogue_pool = RazielDialoguePool()"


def test_dialogue_pool_used_for_roaming():
    """
    Verify that dialogue pool is used for Raziel roaming interactions.
    
    **Validates: Requirements 2.7**
    """
    with open("Start.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check that raziel_dialogue_pool.get_next_dialogue() is called
    pattern = r'raziel_dialogue_pool\.get_next_dialogue\(DIALOGS\)'
    match = re.search(pattern, content)
    
    assert match, \
        "raziel_dialogue_pool.get_next_dialogue(DIALOGS) not found. The dialogue pool should be used for roaming interactions."


def test_dialogue_pool_replaces_fixed_dialogue():
    """
    Verify that the dialogue pool replaces the fixed "raziel_roaming" dialogue.
    
    **Validates: Requirements 2.7**
    """
    with open("Start.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the roaming interaction section
    pattern = r'elif\s+raziel\.roaming.*?and\s+raziel\.near_player.*?and\s+raziel_cooldown\s*==\s*0.*?angel_dialog\s*=\s*raziel_dialogue_pool\.get_next_dialogue\(DIALOGS\)'
    match = re.search(pattern, content, re.DOTALL)
    
    assert match, \
        "Roaming interaction should use raziel_dialogue_pool.get_next_dialogue(DIALOGS) instead of fixed DIALOGS['raziel_roaming']"


def test_state_angel_dialog_used():
    """
    Verify that STATE_ANGEL_DIALOG is set during roaming interactions.
    
    **Validates: Requirements 2.7**
    """
    with open("Start.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the roaming interaction section and verify STATE_ANGEL_DIALOG is set
    pattern = r'elif\s+raziel\.roaming.*?state\s*=\s*STATE_ANGEL_DIALOG'
    match = re.search(pattern, content, re.DOTALL)
    
    assert match, \
        "STATE_ANGEL_DIALOG should be set during roaming interactions"


def test_dialogue_pool_integration_complete():
    """
    Comprehensive test to verify complete integration of dialogue pool.
    
    **Validates: Requirements 2.7**
    """
    with open("Start.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Verify all components are present
    checks = [
        ("RazielDialoguePool import", r'from key_system import.*RazielDialoguePool'),
        ("raziel_dialogue_pool instance", r'raziel_dialogue_pool\s*=\s*RazielDialoguePool\(\)'),
        ("get_next_dialogue call", r'raziel_dialogue_pool\.get_next_dialogue\(DIALOGS\)'),
        ("STATE_ANGEL_DIALOG", r'state\s*=\s*STATE_ANGEL_DIALOG'),
    ]
    
    for check_name, pattern in checks:
        match = re.search(pattern, content)
        assert match, f"{check_name} not found in Start.py"
    
    print("✓ All integration checks passed")
    print("✓ raziel_dialogue_pool instance created")
    print("✓ Dialogue pool used for roaming interactions")
    print("✓ STATE_ANGEL_DIALOG properly set")
