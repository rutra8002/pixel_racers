import random as ran
from random import *


import pygame.draw
from pygame import *
from app import images
from jeff_the_objects import stacked_sprite


class Powerup:
    def __init__(self, x, y, display):
        self.display = display
        self.variance = 10
        self.trueX, self.trueY = x + ran.randint(-self.variance, self.variance), y + ran.randint(-self.variance, self.variance)
        self.trueX, self.trueY = int(x), int(y)
        self.trueX *= self.display.block_width
        self.trueY *= self.display.block_height
        self.angle = 0
        self.sprite = stacked_sprite.StackedSprite(self.display, images.ball, 8, (8, 8), 3)

    def update(self):
        self.sprite.update_mask_rotation(self.angle)
        self.angle += self.display.game.delta_time * self.display.game.calibration

    def render(self):
        self.sprite.render(self.display.screen, (self.trueX, self.trueY))

    def kill(self):
        self.display.deadPowerups.append(self.x, self.y, 1)
        self.display.powerups.remove(self)
        del self