import pygame
from configparser import ConfigParser
from app.config import read_config, write_config_to_file

class Slider:
    def __init__(self, display, action, x, y, width, height, min_val, max_val, initial_val, append=True):
        self.display = display
        self.action = action
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min = min_val
        self.max = max_val
        self.val = initial_val
        self.append = append
        self.dragging = False

        self.track_rect = pygame.Rect(self.x, self.y + self.height//2 - 2, self.width, 4)
        self.handle_rect = pygame.Rect(self.x + (self.val - self.min)/(self.max - self.min) * self.width - 5, self.y, 10, self.height)

        self.display.objects_in_memory += 1
        if self.append:
            self.display.objects.append(self)

    def render(self):
        # Draw track
        pygame.draw.rect(self.display.screen, (200, 200, 200), self.track_rect)
        # Draw handle
        pygame.draw.rect(self.display.screen, (0, 150, 255), self.handle_rect)

    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update handle position and value
            mouse_x = event.pos[0]
            new_x = max(self.x, min(mouse_x, self.x + self.width))
            self.val = self.min + (new_x - self.x) / self.width * (self.max - self.min)
            self.handle_rect.x = new_x - 5  # Adjust handle position

            # Update FPS in config and game
            config = ConfigParser()
            config.read('config.ini')
            config.set('CONFIG', 'fps', str(int(self.val)))
            write_config_to_file(config, 'config.ini')
            self.display.game.fps = int(self.val)
            self.display.game.cfg = read_config()  #Refresh config

    def delete(self):
        self.display.objects_in_memory -= 1
        if self.append:
            self.display.objects.remove(self)
        del self