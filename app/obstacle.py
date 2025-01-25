import pygame
import math as jeszcze_nie_wiem_jak
import time

class Obstacle:
    def __init__(self, display, x, y, type: str, angle=0):
        self.display = display
        self.x = x
        self.y = y
        types = {"spikes": 1, "barrier": 2}
        self.type = types[type]
        if type == "spikes":
            self.image = pygame.image.load("images/spikes.png").convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
        elif type == "barrier":
            self.start_time = time.time()
            self.image = pygame.image.load("images/barrier.png").convert_alpha()
            self.image = pygame.transform.rotate(self.image, angle)
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
            self.display.screen.blit(self.image, self.rect)
        elif self.type == 2:
            self.display.screen.blit(self.image, self.rect)
        self.obstacle_mask = pygame.mask.from_surface(self.image)
        self.rect.center = self.x, self.y
        if self.type == 1:
            if elapsed >= 30:
                self.display.obstacles.remove(self)
                del self
        elif self.type == 1:
            if elapsed >= 5:
                self.display.obstacles.remove(self)
                del self

    def events(self, event):
        pass
    def destroy(self):
        self.display.obstacles.remove(self)
        del self