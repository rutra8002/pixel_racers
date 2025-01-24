import pygame
import math as jeszcze_nie_wiem_jak

class Obstacle:
    def __init__(self, display, x, y, type: str):
        self.display = display
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        types = {"spikes": 1, "barrier": 2}
        self.type = types[type]
        #self.image = pygame.image.load("images/enemycar.png").convert_alpha()
        if type == "spikes":
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((0, 0, 0))
        elif type == "barrier":
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((200, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y
        self.obstacle_mask = pygame.mask.from_surface(self.image)
    def render(self):

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

    def events(self, event):
        pass