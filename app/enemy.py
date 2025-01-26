import pygame
from pygame import *
import math as lolekszcz
from app import images

class Enemy:
    def __init__(self, display):
        self.display = display
        self.x,self.y, self.enemyWidth, self.enemyHeight = 650, 500, 25, 50
        self.image= images.enemy.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y
        self.enemy_mask = pygame.mask.from_surface(self.image)
        self.mask_image = self.enemy_mask.to_surface()
        self.rotation = 0
        self.mass = 1
        self.velUp = 0
        self.velLeft = 0
    def render(self):
        self.rect = self.image.get_rect()
        self.enemy_mask = pygame.mask.from_surface(self.image)
        # self.mask_image = self.enemy_mask.to_surface()
        self.rect.center = self.x, self.y
        self.display.screen.blit(self.image, self.rect)
        # self.display.screen.blit(self.mask_image, self.rect)
        self.enemy_mask = pygame.mask.from_surface(self.image)
        # self.newMask = pygame.transform.rotate(self.mask_image, self.rotation)
        # self.newImg = pygame.transform.rotate(self.image, self.rotation)
    def events(self, event):
        pass
    def loop(self):
        pass