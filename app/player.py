import pygame
from pygame import *
import math as lolino

class Player:
    def __init__(self, display):
        self.display = display
        self.x,self.y, self.playerWidth, self.playerHeight = 500, 500, 25, 50
        self.color = (100, 200, 100)
        self.acceleration = 0.25
        self.backceleration = 0.1
        self.rotationSpeed = 3
        self.maxSpeed = 8
        self.naturalSlowdown = 0.08 # when the player doesn't press W or S
        self.speedCorrection = 0.5 # when the car is going over the speed limit
        self.nitroPower = 1

        # self.image = pygame.Surface((self.playerWidth, self.playerHeight))
        self.image = pygame.image.load("images/jeffcar.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y

        self.player_mask = pygame.mask.from_surface(self.image)
        self.mask_image = self.player_mask.to_surface()

        self.image.set_colorkey((0, 0, 0))
        # self.image.fill(self.color)

        self.velUp, self.velLeft = 0, 0
        self.w, self.a, self.s, self.d, self.boost = False, False, False, False, False
        self.rotation = 180
        self.nitroAmount = 0

    def render(self):
        self.center = self.rect.center
        self.movement()
        # self.display.screen.blit(self.mask_image, self.rect)
        self.nitroAmount += 0.3
        self.newMask = pygame.transform.rotate(self.mask_image, self.rotation+180)
        self.newImg = pygame.transform.rotate(self.image, self.rotation+180)

        self.rect = self.newImg.get_rect()
        self.rect.center = self.x, self.y
        self.display.screen.blit(self.newMask, self.rect)
        self.display.screen.blit(self.newImg, self.rect)
        # if pygame.sprite.spritecollide(self.display.p, self.display.enemies, False):
        #     print("collision", )
        self.collision_point = self.player_mask.overlap(self.display.enemy1.enemy_mask, (self.x - self.display.enemy1.x, self.y - self.display.enemy1.y))
        if self.player_mask.overlap(self.display.enemy1.enemy_mask, (self.x - self.display.enemy1.x, self.y - self.display.enemy1.y)):
            print("collision")
            print("COLLISION POINT: ", self.collision_point)
        print(self.velUp)
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
            if event.key == pygame.K_SPACE:
                self.boost = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.w = False
            if event.key == pygame.K_a:
                self.a = False
            if event.key == pygame.K_s:
                self.s = False
            if event.key == pygame.K_d:
                self.d = False
            if event.key == pygame.K_SPACE:
                self.boost = False
    def movement(self):
        c, d = self.velLeft, self.velUp
        if self.w:
            a, b = self.get_acceleration_with_trigonometry(1, self.acceleration)
            self.velLeft += a
            self.velUp += b
        if self.s:
            a, b = self.get_acceleration_with_trigonometry(-1, self.backceleration)
            self.velLeft += a
            self.velUp += b
        if self.a:
            self.rotation = (self.rotation + self.rotationSpeed) % 360
        if self.d:
            self.rotation = (self.rotation - self.rotationSpeed) % 360

        if self.boost and self.nitroAmount >= 1:
            self.nitroAmount -= 1
            a, b = self.get_acceleration_with_trigonometry(1, self.nitroPower)
            self.velLeft += a
            self.velUp += b

        if self.velLeft == c and self.velUp == d:
            if self.velUp > 0:
                self.velUp -= self.naturalSlowdown
                if self.velUp < 0:
                    self.velUp = 0
            elif self.velUp < 0:
                self.velUp += self.naturalSlowdown
                if self.velUp > 0:
                    self.velUp = 0
            if self.velLeft > 0:
                self.velLeft -= self.naturalSlowdown
                if self.velLeft < 0:
                    self.velLeft = 0
            elif self.velLeft < 0:
                self.velLeft += self.naturalSlowdown
                if self.velLeft > 0:
                    self.velLeft = 0

        # self.rect.center = (self.x + self.playerWidth / 2, self.y + self.playerHeight / 2)
        if self.velUp > self.maxSpeed + self.speedCorrection:
            self.velUp -= self.speedCorrection
        elif self.velUp > self.maxSpeed:
            self.velUp = self.maxSpeed
        if self.velLeft > self.maxSpeed + self.speedCorrection:
            self.velLeft -= self.speedCorrection
        elif self.velLeft  > self.maxSpeed:
            self.velLeft = self.maxSpeed
        if self.velUp < -self.maxSpeed -self.speedCorrection:
            self.velUp += self.speedCorrection
        elif self.velUp < -self.maxSpeed:
            self.velUp = -self.maxSpeed
        if self.velLeft < -self.maxSpeed -self.speedCorrection:
            self.velLeft += self.speedCorrection
        elif self.velLeft < -self.maxSpeed:
            self.velLeft = -self.maxSpeed

        magnitude = lolino.sqrt(self.velLeft ** 2 + self.velUp ** 2)
        if magnitude > self.maxSpeed:
            self.velLeft = (self.velLeft / magnitude) * self.maxSpeed
            self.velUp = (self.velUp / magnitude) * self.maxSpeed

        self.x -= self.velLeft
        self.y -= self.velUp

    def get_acceleration_with_trigonometry(self, direction, acc):
        r = lolino.radians(self.rotation + 90)
        x = lolino.cos(r)
        y = lolino.sin(r)
        return (x * acc * -direction), (y * acc * direction)


