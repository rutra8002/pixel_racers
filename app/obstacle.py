import pygame
import math as jeszcze_nie_wiem_jak

class Obstacle:
    def __init__(self, display, x, y, type: str):
        self.display = display
        self.x = x
        self.y = y
        types = {"spikes": 1, "barrier": 2}
        self.type = types[type]
    def render(self):
        if self.type == 1:
            pygame.draw.rect(self.display.screen, (0, 0, 0), (self.x, self.y, 25, 25))
        elif self.type == 2:
            pygame.draw.rect(self.display.screen, (200, 0, 0), (self.x, self.y, 25, 25))
    def events(self, event):
        pass