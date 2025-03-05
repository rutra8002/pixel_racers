import sys
import os
import pygame
import pytest

# Add the directory containing customObjects to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from customObjects.custom_text import Custom_text

class MockDisplay:
    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height))
        self.objects_in_memory = 0
        self.objects = []

@pytest.fixture
def setup_pygame():
    pygame.init()
    display = MockDisplay(800, 600)
    yield display
    pygame.quit()

def test_custom_text_rendering(setup_pygame):
    display = setup_pygame
    custom_text = Custom_text(display, 100, 100, "Hello, World!", font_height=30, text_color=(255, 255, 255))

    # Render the text
    custom_text.render()

    # Check if the text is rendered at the correct position
    assert custom_text.rect.center == (100, 103)  # Adjusted for the y-offset in the center calculation
    assert custom_text.text == "Hello, World!"
    assert custom_text.text_color == (255, 255, 255)