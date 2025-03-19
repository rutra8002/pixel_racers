from random import random

import pygame
import math as jeszcze_nie_wiem_jak
import time
from app import images
import random
from random import randint

from jeff_the_objects import stacked_sprite
from jeff_the_objects.stacked_sprite import StackedSprite

class Obstacle:
    def __init__(self, display, x, y, type: str, angle=0):
        self.display = display
        self.x = x
        self.y = y
        if type in ("banana", "brama", "speedBump", "guideArrow", "coin"):
            self.x = x * self.display.block_width
            self.y = y * self.display.block_width
        self.falling = False
        self.target_y = y * self.display.block_width
        if type == "banana":
            self.y = -100
            self.falling = True
        if type == "coin":
            a, b = random.randint(-self.display.placement_variance, self.display.placement_variance), random.randint(-self.display.placement_variance, self.display.placement_variance)
            self.x += a
            self.y += b

        self.start_time = time.time()
        self.angle = angle
        self.alpha = 255
        types = {"spikes": 1, "barrier": 2, "banana": 3, "brama": 4, "speedBump": 5, "guideArrow": 6, "coin": 7}
        self.type = types[type]
        if type == "spikes":
            self.image = images.spikes.convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
            self.rect = self.image.get_rect()

        elif type == "barrier":
            self.image = images.barrier.convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
            self.rect = self.image.get_rect()

        elif type == "banana":
            self.image = images.banana.convert_alpha()
            self.image = pygame.transform.scale(self.image, (70, 70))
            self.image = pygame.transform.rotate(self.image, angle)
            self.rect = self.image.get_rect()

        elif type == "brama":
            self.image = images.barrier.convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
            self.rect = self.image.get_rect()

        elif type == "speedBump":
            self.image = images.speedBump.convert_alpha()
            self.image = pygame.transform.scale(self.image, (100, 100))
            self.image = pygame.transform.rotate(self.image, angle)
            self.rect = self.image.get_rect()

        elif type == "guideArrow":
            self.image = images.guideArrow.convert_alpha()
            self.image = pygame.transform.scale(self.image, (200, 100))
            self.image = pygame.transform.rotate(self.image, angle)
            self.rect = self.image.get_rect()
        elif type == "coin":
            self.angle = 0
            self.sprite = stacked_sprite.StackedSprite(self.display, images.coin, 12, (12, 2), 3)
            self.obstacle_mask = self.sprite.mask
            self.rect = self.sprite.rect
        if not type == "coin":
            self.obstacle_mask = pygame.mask.from_surface(self.image)

        self.rect.center = self.x, self.y

    def render(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        if self.type == 1:
            self.alpha = max(0, 255 - int((elapsed / 3) * 255))
        elif self.type == 2:
            self.alpha = max(0, 255 - int((elapsed / 5) * 255))

        if self.type == 4:
            if elapsed > 8:
                self.display.deadBramas.append([self.x / self.display.block_width, self.y / self.display.block_width, 6, self.angle])
                self.destroy()
        if self.type == 3:
            if self.y < self.target_y and self.falling:
                self.y += 580 * self.display.game.delta_time
                pygame.draw.circle(self.display.screen, (70, 70, 70), (self.x, self.target_y), 25)
            else:
                self.y = self.target_y
                self.falling = False

        if self.type == 7:
            self.sprite.update_mask_rotation(self.angle)
            self.rect.center = (self.x, self.y)
            self.angle += self.display.game.delta_time * self.display.game.calibration
            self.sprite.render(self.display.screen, (self.x, self.y))
        else:
            self.display.screen.blit(self.image, self.rect)
            self.rect.center = self.x, self.y
            self.obstacle_mask = pygame.mask.from_surface(self.image)
            self.image.set_alpha(self.alpha)

        if self.alpha == 0:
            self.display.obstacles.remove(self)
            del self

    def events(self, event):
        pass

    def destroy(self):
        self.display.obstacles.remove(self)
        if self.type == 3:
            self.display.banana = None
        if self.type == 7:
            self.display.hasCoin = 1
        del self