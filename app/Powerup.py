import pygame.draw
from pygame import *

import images

class Powerup:
    def __init__(self, x, y, display):
        self.display = display
        self.x, self.y = x, y
        self.img = images.ball


    def render(self):
        pygame.draw.circle(self.display.screen, (100, 100, 200), self.x, self.y, 10)

    def kill(self):
        self.display.objects.remove(self)
        del self