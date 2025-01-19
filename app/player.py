import pygame
import math as lolino

class Player:
    def __init__(self, display):
        self.display = display
        self.x,self.y, self.playerWidth, self.playerHeight = 500, 500, 25, 50
        self.color = (100, 200, 100)
        self.acceleration = 0.2 * self.display.game.calibration
        self.backceleration = 0.1 * self.display.game.calibration
        self.rotationSpeed = 3 * self.display.game.calibration
        self.maxSpeed = 8 * self.display.game.calibration
        self.naturalSlowdown = 0.08 * self.display.game.calibration # when the player doesn't press W or S
        self.speedCorrection = 0.5 * self.display.game.calibration # when the car is going over the speed limit
        self.nitroPower = 0.5 * self.display.game.calibration
        self.borderForce = 2 * self.display.game.calibration

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
        self.rotation = 0
        self.nitroAmount = 0

        self.particle_system = self.display.particle_system
        self.particle_counter = 0

    def render(self):
        self.center = self.rect.center
        # self.display.screen.blit(self.mask_image, self.rect)
        self.nitroAmount += 0.3
        self.newImg = pygame.transform.rotate(self.image, self.rotation + 90)
        self.rect = self.newImg.get_rect()
        self.rect.center = self.x, self.y
        self.player_mask = pygame.mask.from_surface(self.newImg)
        self.mask_image = self.player_mask.to_surface()
        # self.display.screen.blit(self.mask_image, self.mask_image.get_rect())
        self.display.screen.blit(self.newImg, self.rect)

        if self.display.game.debug:
            pygame.draw.rect(self.display.game.screen, (0, 255, 0), self.rect, width=1)
        # if pygame.sprite.spritecollide(self.display.p, self.display.enemies, False):
        #     print("collision", )

        # print(self.velUp)

        back_wheel_offset = self.playerHeight / 2
        angle_rad = lolino.radians(-self.rotation)
        back_wheel_x_offset = lolino.cos(angle_rad) * back_wheel_offset
        back_wheel_y_offset = lolino.sin(angle_rad) * back_wheel_offset

        back_wheel1_x = self.x - back_wheel_x_offset - lolino.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel1_y = self.y - back_wheel_y_offset + lolino.cos(angle_rad) * (self.playerWidth / 2)
        back_wheel2_x = self.x - back_wheel_x_offset + lolino.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel2_y = self.y - back_wheel_y_offset - lolino.cos(angle_rad) * (self.playerWidth / 2)
        self.particle_counter += 1

        if self.particle_counter % 3 == 0:
            self.particle_system.add_particle(back_wheel1_x, back_wheel1_y, self.velLeft, self.velUp, -0.01 * self.velLeft, -0.01 * self.velUp, 0, 0, 1, 100, 3, 100, 100, 100, 150, 'square')
            self.particle_system.add_particle(back_wheel2_x, back_wheel2_y, self.velLeft, self.velUp, -0.01 * self.velLeft, -0.01 * self.velUp, 0, 0, 1, 100, 3, 100, 100, 100, 150, 'square')

        if self.boost:
            nitro_x = self.x - back_wheel_x_offset
            nitro_y = self.y - back_wheel_y_offset
            self.particle_system.add_particle(nitro_x, nitro_y, self.velLeft, self.velUp, 0, 0, 0, 0, 1, 200, 10, 200, 100, 30, 150, 'circle', True)

        if self.collision_detection(self.display.enemy1.enemy_mask, self.display.enemy1.rect.topleft[0],self.display.enemy1.rect.topleft[1]):
            self.collision_render(self.display.enemy1.enemy_mask, self.display.enemy1.rect.topleft[0],self.display.enemy1.rect.topleft[1])

        if self.collision_detection(self.display.mapMask, 0, 0):
            self.collision_render(self.display.mapMask, 0, 0)

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
            a, b = self.get_acceleration_with_trigonometry(1, self.acceleration * self.display.game.delta_time * self.display.game.calibration/2)
            self.velLeft += a
            self.velUp += b
        if self.s:
            a, b = self.get_acceleration_with_trigonometry(-1, self.backceleration * self.display.game.delta_time * self.display.game.calibration/2)
            # print(self.velUp, self.velLeft)
            self.velLeft += a
            self.velUp += b
        if self.a:
            self.rotation = (self.rotation + self.rotationSpeed * self.display.game.delta_time) % 360
        if self.d:
            self.rotation = (self.rotation - self.rotationSpeed * self.display.game.delta_time) % 360

        if self.boost and self.nitroAmount >= 1:
            self.nitroAmount -= 1
            a, b = self.get_acceleration_with_trigonometry(1, self.nitroPower)
            self.velLeft += a * self.display.game.delta_time * self.display.game.calibration
            self.velUp += b * self.display.game.delta_time * self.display.game.calibration

        if self.velLeft == c and self.velUp == d:
            if self.velLeft != 0 or self.velUp != 0:
                velocity = lolino.sqrt(self.velLeft ** 2 + self.velUp ** 2)
                slowdown = self.naturalSlowdown / velocity
                self.velLeft -= self.velLeft * slowdown * self.display.game.delta_time * self.display.game.calibration
                self.velUp -= self.velUp * slowdown * self.display.game.delta_time * self.display.game.calibration

        # if not self.boost:
        #     magnitude = lolino.sqrt(self.velLeft ** 2 + self.velUp ** 2)
        #     if magnitude > self.maxSpeed:
        #         self.velLeft = (self.velLeft / magnitude) * self.maxSpeed
        #         self.velUp = (self.velUp / magnitude) * self.maxSpeed

        if self.x < 0:
            self.velLeft = -self.borderForce
        if self.x > self.display.screenWidth:
            self.velLeft = self.borderForce
        if self.y < 0:
            self.velUp = -self.borderForce
        if self.y > self.display.screenHeight:
            self.velUp = self.borderForce

        self.x -= self.velLeft * self.display.game.delta_time
        self.y -= self.velUp * self.display.game.delta_time

    def get_rect_dimentions(self):
        alfa = 90 - self.rotation % 90
        alfa = lolino.radians(alfa)
        if self.rotation // 90 in (1, 3):
            height = self.playerHeight * lolino.sin(alfa) + self.playerWidth * lolino.cos(alfa)
            width = self.playerWidth * lolino.sin(alfa) + self.playerHeight * lolino.cos(alfa)
        else:
            height = self.playerWidth * lolino.sin(alfa) + self.playerHeight * lolino.cos(alfa)
            width = self.playerHeight * lolino.sin(alfa) + self.playerWidth * lolino.cos(alfa)
        return (width, height)


    def get_acceleration_with_trigonometry(self, direction, acc):
        if direction == 1:
            r = lolino.radians(self.rotation)
        else:
            r = lolino.radians(self.rotation - 180)

        x = lolino.cos(r)
        y = lolino.sin(r)
        return (x * -acc), (y * acc)

    def loop(self):
        self.movement()
        self.collision_detection(self.display.enemy1.enemy_mask, self.display.enemy1.rect.topleft[0], self.display.enemy1.rect.topleft[1])
        self.collision_detection(self.display.mapMask, 0, 0)

    def collision_detection(self, mask, x, y):
        offset = (x - self.rect.topleft[0], y - self.rect.topleft[1])
        return self.player_mask.overlap(mask, offset)

    def collision_render(self, mask, x, y):
        offset = (x - self.rect.topleft[0], y - self.rect.topleft[1])
        sharedMask = self.player_mask.overlap_mask(mask, offset)
        sharedSurface = sharedMask.to_surface(setcolor=(0, 200, 0))
        sharedSurface.set_colorkey((0, 0, 0))
        self.display.screen.blit(sharedSurface, self.rect)
