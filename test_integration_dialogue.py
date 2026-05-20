"""
Integration test for RazielDialoguePool with Start.py DIALOGS
"""

from Start import DIALOGS
from key_system import RazielDialoguePool


def test_integration():
    """Test that RazielDialoguePool works with actual DIALOGS from Start.py"""
    pool = RazielDialoguePool()
    
    print("\nTesting integration with Start.py DIALOGS:")
    print("-" * 50)
    
    for i in range(5):
        dialogue = pool.get_next_dialogue(DIALOGS)
        print(f"\n{i+1}. Retrieved dialogue with {len(dialogue)} lines")
        print(f"   First line: {dialogue[0]}")
    
    print("\n" + "-" * 50)
    print("✓ All dialogues retrieved successfully!")
    print(f"✓ Seen dialogues: {len(pool.seen_dialogues)}")
    print(f"✓ Current index: {pool.current_index}")


if __name__ == "__main__":
    test_integration()
