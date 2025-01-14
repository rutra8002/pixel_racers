import pygame
from pygame import *

class Player:
    def __init__(self, display):
        self.display = display
        self.x,self.y, self.playerWidth, self.playerHeight = 500, 500, 25, 50
        self.color = (100, 200, 100)
        self.velUp, self.velLeft = 0, 0
        self.acceleration = 0.2
        self.w, self.a, self.s, self.d = False, False, False, False

    def render(self):
        pygame.draw.rect(self.display.screen, self.color, (self.x, self.y, self.playerWidth, self.playerHeight))
        self.movement()

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.w = True
            if event.key == pygame.K_a:
                self.a = True
            if event.key == pygame.K_s:
                self.s = True
            if event.key == pygame.K_d:
                self.d = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.w = False
            if event.key == pygame.K_a:
                self.a = False
            if event.key == pygame.K_s:
                self.s = False
            if event.key == pygame.K_d:
                self.d = False
    def movement(self):
        if self.w:
            self.velUp += self.acceleration
        if self.s:
            self.velUp -= self.acceleration
        if self.a:
            self.velLeft += self.acceleration
        if self.d:
            self.velLeft -= self.acceleration


        self.x -= self.velLeft
        self.y -= self.velUp
