import pygame
from configparser import ConfigParser
from app.config import read_config, write_config_to_file

class Slider:
    def __init__(self, display, name, x, y, width, height, min_value, max_value, current_value, slider_type="fps"):
        self.display = display
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = current_value
        self.slider_type = slider_type

        self.dragging = False
        self.track_rect = pygame.Rect(x, y, width, height)
        self.handle_width = 20
        self.handle_height = height + 10

        # Calculate initial handle position
        value_range = max_value - min_value
        ratio = (current_value - min_value) / value_range
        handle_x = x + (width - self.handle_width) * ratio
        self.handle_rect = pygame.Rect(handle_x, y - 5, self.handle_width, self.handle_height)

        # Add to display objects
        self.display.objects.append(self)
        self.display.objects_in_memory += 1

    def render(self):
        # Draw track with different colors based on type
        if self.slider_type == "fps":
            track_color = (200, 200, 200)
            handle_color = (0, 150, 255)
            filled_color = (100, 100, 100)
        else:  # volume type
            track_color = (150, 150, 150)
            handle_color = (0, 255, 0)
            filled_color = (0, 200, 0)

        # Draw background track
        pygame.draw.rect(self.display.screen, track_color, self.track_rect)

        # Draw filled portion
        filled_width = self.handle_rect.centerx - self.track_rect.x
        filled_rect = pygame.Rect(self.track_rect.x, self.track_rect.y, filled_width, self.track_rect.height)
        pygame.draw.rect(self.display.screen, filled_color, filled_rect)

        # Draw handle
        pygame.draw.rect(self.display.screen, handle_color, self.handle_rect)

    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update handle position and value
            mouse_x = event.pos[0]
            # Constrain handle movement
            handle_x = min(max(mouse_x - self.handle_width / 2, self.x), self.x + self.width - self.handle_width)
            self.handle_rect.x = handle_x

            # Calculate and update current value
            ratio = (handle_x - self.x) / (self.width - self.handle_width)
            self.current_value = int(self.min_value + ratio * (self.max_value - self.min_value))

            # Update game settings based on slider type
            if self.slider_type == "fps":
                config = ConfigParser()
                config.read('config.ini')
                config.set('CONFIG', 'fps', str(int(self.current_value)))
                write_config_to_file(config, 'config.ini')
                self.display.game.fps = int(self.current_value)
                self.display.game.cfg = read_config()  # Refresh config
                self.display.game.debug_items[2].update_text(f'FPS cap: {self.display.game.fps}')
            else:  # volume type
                self.display.game.sound_manager.set_music_volume(self.current_value / 100)

    def delete(self):
        self.display.objects_in_memory -= 1
        if self in self.display.objects:
            self.display.objects.remove(self)
        del self