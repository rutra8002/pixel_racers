import pygame.draw
from pygame import *
from app import images
from jeff_the_objects import stacked_sprite


class Powerup:
    def __init__(self, x, y, display):
        self.display = display
        self.x, self.y = int(x), int(y)
        self.x *= self.display.block_width
        self.y *= self.display.block_height
        self.angle = 0
        self.sprite = stacked_sprite.StackedSprite(self.display, images.ball, 8, (8, 8), 5)

    def update(self):
        self.sprite.update_mask_rotation(self.angle)
        self.angle += self.display.game.delta_time * self.display.game.calibration

    def render(self):
        self.sprite.render(self.display.screen, (self.x, self.y))

    def kill(self):
        self.display.objects.remove(self)
        del self