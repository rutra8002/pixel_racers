import pygame
import math as lolino
import time
from app.car import Car
import math

class Player(Car):
    def __init__(self, display, image, coordinates, rotation):
        super().__init__(display, image, coordinates, rotation, isPlayer=True, model=3)

    def set_3d_parameters(self):
        # self.num_of_sprites = 9
        # self.img_size = (16, 16)
        # self.car3d_height = math.pi

        self.num_of_sprites = 13
        self.img_size = (15, 34)
        self.car3d_height = 1.5

    def events(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.w = True
            if event.key in (pygame.K_a, pygame.K_LEFT):
                self.a = True
            if event.key in (pygame.K_s, pygame.K_DOWN):
                self.s = True
            if event.key in (pygame.K_d, pygame.K_RIGHT):
                self.d = True
            if event.key == pygame.K_q:
                self.q = True
            if event.key == pygame.K_e:
                self.e = True
            if event.key == pygame.K_SPACE:
                if self.WASD_steering:
                    self.velUp, self.velLeft = 0, 0
                else:
                    self.boost = True
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.w = False
            if event.key in (pygame.K_a, pygame.K_LEFT):
                self.a = False
            if event.key in (pygame.K_s, pygame.K_DOWN):
                self.s = False
            if event.key in (pygame.K_d, pygame.K_RIGHT):
                self.d = False
            if event.key == pygame.K_SPACE:
                self.boost = False
            if event.key == pygame.K_q:
                self.q = False
            if event.key == pygame.K_e:
                self.e = False