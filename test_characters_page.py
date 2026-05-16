"""
Test for Characters Page functionality.

Verifies that the Characters screen has all required elements and data.
"""

import pytest
import pygame
import os

# Initialize pygame for testing
pygame.init()

# Import after pygame init
from CharactersPage import CHARACTERS, wrap_text, desc_font


class TestCharactersPage:
    """Test Characters Page implementation."""
    
    def test_all_characters_defined(self):
        """Verify all 7 characters are defined."""
        assert len(CHARACTERS) == 7, "Should have 7 characters"
        
        expected_names = [
            "Mikhail",
            "Raziel",
            "The Serpent",
            "Cain",
            "Abel",
            "The Guardian",
            "--. --- -.."
        ]
        
        actual_names = [char["name"] for char in CHARACTERS]
        assert actual_names == expected_names, f"Character names don't match. Got: {actual_names}"
        
        print("✓ All 7 characters defined with correct names")
    
    def test_all_characters_have_images(self):
        """Verify all characters have image paths defined."""
        for char in CHARACTERS:
            assert "image" in char, f"{char['name']} missing image path"
            assert "loaded_image" in char, f"{char['name']} missing loaded_image"
            
            # Check if image file exists
            image_path = char["image"]
            assert os.path.exists(image_path), f"Image not found: {image_path}"
        
        print("✓ All characters have valid image paths")
    
    def test_all_characters_have_descriptions(self):
        """Verify all characters have descriptions."""
        for char in CHARACTERS:
            assert "description" in char, f"{char['name']} missing description"
            assert len(char["description"]) > 0, f"{char['name']} has empty description"
        
        print("✓ All characters have descriptions")
    
    def test_special_character_has_red_color(self):
        """Verify the special character (God) has red text color."""
        god_char = CHARACTERS[-1]  # Last character
        assert god_char["name"] == "--. --- -..", "Last character should be God (morse code)"
        assert "special_color" in god_char, "God character should have special_color"
        assert god_char["special_color"] == (220, 50, 50), "God character should have red color"
        
        print("✓ Special character has red color")
    
    def test_character_descriptions_match_spec(self):
        """Verify character descriptions match the specification."""
        # Test a few key descriptions
        mikhail = CHARACTERS[0]
        assert "strict angel" in mikhail["description"].lower()
        assert "guards of the gates" in mikhail["description"].lower()
        
        raziel = CHARACTERS[1]
        assert "laid back" in raziel["description"].lower()
        assert "calmer" in raziel["description"].lower()
        
        serpent = CHARACTERS[2]
        assert "deceiver" in serpent["description"].lower()
        assert "fall of humanity" in serpent["description"].lower()
        
        cain = CHARACTERS[3]
        assert "older brother" in cain["description"].lower()
        assert "murder" in cain["description"].lower()
        
        abel = CHARACTERS[4]
        assert "younger brother" in abel["description"].lower()
        assert "shepherd" in abel["description"].lower()
        
        guardian = CHARACTERS[5]
        assert "cherubim" in guardian["description"].lower()
        assert "tree of knowledge" in guardian["description"].lower()
        
        god = CHARACTERS[6]
        assert "grave mistake" in god["description"].lower()
        
        print("✓ Character descriptions match specification")
    
    def test_wrap_text_function(self):
        """Test that text wrapping works correctly."""
        test_text = "This is a long line of text that should be wrapped into multiple lines"
        max_width = 200
        
        lines = wrap_text(test_text, desc_font, max_width)
        
        assert len(lines) > 1, "Long text should be wrapped into multiple lines"
        
        # Verify each line fits within max_width
        for line in lines:
            width = desc_font.size(line)[0]
            assert width <= max_width, f"Line '{line}' exceeds max width: {width} > {max_width}"
        
        print(f"✓ Text wrapping works correctly ({len(lines)} lines)")
    
    def test_character_image_files_exist(self):
        """Verify all character Full images exist in the file system."""
        expected_images = [
            "Sprites/Mikhail/MikhailFull.png",
            "Sprites/Raziel/RazielFull.png",
            "Sprites/Naga/NagaFull.png",
            "Sprites/Cain/CainFull.png",
            "Sprites/Abel/AbelFull.png",
            "Sprites/Guardian/GuardianFull.png",
            "Sprites/boss/BossFull.png"
        ]
        
        for img_path in expected_images:
            assert os.path.exists(img_path), f"Character image not found: {img_path}"
        
        print("✓ All character Full images exist")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
