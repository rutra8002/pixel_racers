import pygame
import math as jeszcze_nie_wiem_jak
import time
from app import images
from jeff_the_objects.stacked_sprite import StackedSprite

class Obstacle:
    def __init__(self, display, x, y, type: str, angle=0):
        self.display = display
        self.x = x
        self.y = y
        self.start_time = time.time()
        self.angle = angle
        types = {"spikes": 1, "barrier": 2, "ball": 3}
        self.type = types[type]
        if type == "spikes":
            self.image = images.spikes.convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
        elif type == "barrier":
            self.image = images.barrier.convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
        elif type == "ball":
            self.sprite = StackedSprite(display, images.ball, 8, (8, 8), 5)
            self.rect = self.sprite.rect
            self.rect.center = self.x, self.y
            self.obstacle_mask = self.sprite.mask
            return
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y
        self.obstacle_mask = pygame.mask.from_surface(self.image)

    def render(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        #if self.type == 1:
        #    pygame.draw.rect(self.display.screen, (0, 0, 0), (self.x, self.y, self.width, self.height))
        #elif self.type == 2:
        #    pygame.draw.rect(self.display.screen, (200, 0, 0), (self.x, self.y, self.width, self.height))
        if self.type == 1:
            self.alpha = max(0, 255 - int((elapsed / 3) * 255))
        elif self.type == 2:
            self.alpha = max(0, 255 - int((elapsed / 5) * 255))
        elif self.type == 3:
            self.angle += self.display.game.delta_time * self.display.game.calibration
            self.sprite.render(self.display.screen, (self.x, self.y))
            self.sprite.update_mask_rotation(self.angle)
            return
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
        del self