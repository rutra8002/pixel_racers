import pygame
import math as jeszcze_nie_wiem_jak
import time
from app import images
from jeff_the_objects.stacked_sprite import StackedSprite

class Obstacle:
    def __init__(self, display, x, y, type: str, angle=0):
        self.display = display
        self.x = x * self.display.block_width
        self.y = y * self.display.block_width
        self.start_time = time.time()
        self.angle = angle
        self.alpha = 255
        types = {"spikes": 1, "barrier": 2, "banana": 3, "brama": 4, "speedBump": 5}
        self.type = types[type]
        if type == "spikes":
            self.image = images.spikes.convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
        elif type == "barrier":
            self.image = images.barrier.convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
        elif type == "banana":
            self.image = images.banana.convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
            print('banana')
        elif type == "brama":
            self.image = images.spikes.convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
        elif type == "speedBump":
            self.image = images.spikes.convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y
        self.obstacle_mask = pygame.mask.from_surface(self.image)

    def render(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        if self.type == 1:
            self.alpha = max(0, 255 - int((elapsed / 3) * 255))
        elif self.type == 2:
            self.alpha = max(0, 255 - int((elapsed / 5) * 255))

        self.image.set_alpha(self.alpha)

        self.display.screen.blit(self.image, self.rect)

        self.obstacle_mask = pygame.mask.from_surface(self.image)
        self.rect.center = self.x, self.y
        if self.alpha == 0:
            self.display.obstacles.remove(self)
            del self

    def events(self, event):
        pass

    def destroy(self):
        self.display.obstacles.remove(self)
        if self.type == 3:
            self.display.banana = None
        del self