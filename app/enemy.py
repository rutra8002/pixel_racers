import pygame
from pygame import *
import math as lolekszcz

class Enemy(pygame.sprite.Sprite):
    def __init__(self, display):
        pygame.sprite.Sprite.__init__(self)
        self.display = display
        self.x,self.y, self.enemyWidth, self.enemyHeight = 650, 500, 25, 50
        self.image= pygame.image.load("images/jeffcar.png").convert_alpha()
        self.enemy_mask = pygame.mask.from_surface(self.image)
        self.mask_image = self.enemy_mask.to_surface()
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y
        self.rotation = 0
    def render(self):
        self.display.screen.blit(self.enemy_mask.to_surface(), self.rect)
        self.display.screen.blit(self.image, self.rect)
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y
        self.newMask = pygame.transform.rotate(self.mask_image, self.rotation)
        self.newImg = pygame.transform.rotate(self.image, self.rotation)
    def events(self, event):
        pass


