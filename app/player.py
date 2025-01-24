import pygame
import math as lolino

class Player:
    def __init__(self, display, image, coordinates):
        self.display = display
        self.playerWidth, self.playerHeight = 25, 50
        self.color = (100, 200, 100)

        self.normalAcceleration = 0.2 * self.display.game.calibration
        self.normalBackceleration = 0.1 * self.display.game.calibration
        self.iceAcceleration = 0 * self.display.game.calibration
        self.iceBackceleration = 0 * self.display.game.calibration
        self.normalRotationSpeed = 0.03 * self.display.game.calibration
        self.gravelRotationSpeed = 0.01 * self.display.game.calibration
        self.normalMaxSpeed = 12 * self.display.game.calibration
        self.gravelMaxSpeed = 2 * self.display.game.calibration

        self.naturalSlowdown = 0.08 * self.display.game.calibration # when the player doesn't press W or S
        self.speedCorrection = 0.05 / self.display.game.calibration # when the car is going over the speed limit
        self.nitroPower = 0.4 * self.display.game.calibration
        self.borderForce = 2 * self.display.game.calibration
        self.oilDelay = 1000

        self.x, self.y = coordinates[0], coordinates[1]
        self.currentAcceleration = self.normalAcceleration
        self.currentBackceleration = self.normalBackceleration
        self.currentMaxSpeed = self.normalMaxSpeed
        self.currentRotationSpeed = self.normalRotationSpeed

        self.borderBounce = True # whether the bounce from borders depends on the player's velocity
        self.borderBounciness = 0.9
        self.WASD_steering = False # For debug only

        # self.image = pygame.Surface((self.playerWidth, self.playerHeight))
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y

        self.car_mask = pygame.mask.from_surface(self.image)
        self.mask_image = self.car_mask.to_surface()

        # self.image.set_colorkey((0, 0, 0))
        # self.image.fill(self.color)

        self.velUp, self.velLeft = 0, 0
        self.w, self.a, self.s, self.d, self.boost = False, False, False, False, False
        self.rotation = 0

        self.steer_rotation = 0
        self.delta_rotation = 0.01*self.display.game.calibration
        self.max_steer_rotation = 60
        self.min_steer_rotation = -self.max_steer_rotation

        self.steering_speed = 10 * self.display.game.calibration

        self.nitroAmount = 0

        self.particle_system = self.display.particle_system
        self.particle_counter = 0

    def render(self):
        self.center = self.rect.center
        # self.display.screen.blit(self.mask_image, self.rect)
        self.nitroAmount += 1
        self.newImg = pygame.transform.rotate(self.image, self.rotation + 90)
        self.rect = self.newImg.get_rect()
        self.rect.center = self.x, self.y
        self.car_mask = pygame.mask.from_surface(self.newImg)
        self.mask_image = self.car_mask.to_surface()
        # self.display.screen.blit(self.mask_image, self.mask_image.get_rect())
        self.display.screen.blit(self.newImg, self.rect)

        if self.display.game.debug:
            pygame.draw.rect(self.display.game.screen, (0, 255, 0), self.rect, width=1)

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
        for obstacle in self.display.obstacles:
            if self.collision_detection(obstacle.obstacle_mask, obstacle.rect.topleft[0], obstacle.rect.topleft[1]):
                if obstacle.type == 1:
                    print("spikes")
                elif obstacle.type == 2:
                    print("barrier")
        else:
            self.currentMaxSpeed = self.normalMaxSpeed
            self.currentAcceleration = self.normalAcceleration
            self.currentRotationSpeed = self.normalRotationSpeed

        if self.collision_detection(self.display.mapMask, 0, 0):
            self.collision_render(self.display.mapMask, 0, 0)
            self.check_color(self.display.mapMask, 0, 0)

        # Draw steering wheel
        wheel_center = (100, 100)
        wheel_radius = 50
        pygame.draw.circle(self.display.screen, (255, 255, 255), wheel_center, wheel_radius, 2)

        angle = lolino.radians(self.steer_rotation)
        line_length = 40
        line_end = (wheel_center[0] + line_length * lolino.cos(angle), wheel_center[1] - line_length * lolino.sin(angle))
        pygame.draw.line(self.display.screen, (255, 0, 0), wheel_center, line_end, 2)

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
            if event.key == pygame.K_SPACE:
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

    def movement(self):
        c, d = self.velLeft, self.velUp
        if self.w:
            if self.WASD_steering:
                self.velUp += self.currentAcceleration
            else:
                a, b = self.get_acceleration_with_trigonometry(1, self.currentAcceleration * self.display.game.delta_time * self.display.game.calibration / 2)
                self.velLeft += a
                self.velUp += b
        if self.s:
            if self.WASD_steering:
                self.velUp -= self.currentAcceleration
            else:
                a, b = self.get_acceleration_with_trigonometry(-1, self.currentBackceleration * self.display.game.delta_time * self.display.game.calibration / 2)
                self.velLeft += a
                self.velUp += b
        if self.a:
            if self.WASD_steering:
                self.velLeft += self.currentAcceleration
            else:
                self.steer_rotation += self.delta_rotation * self.display.game.delta_time * self.steering_speed
        if self.d:
            if self.WASD_steering:
                self.velLeft -= self.currentAcceleration
            else:
                self.steer_rotation += -self.delta_rotation * self.display.game.delta_time * self.steering_speed
        if not self.a and not self.d:
            self.steer_rotation -= 10*self.steer_rotation * self.display.game.delta_time
        if abs(self.steer_rotation) < 0.01:
            self.steer_rotation = 0


        self.steer_rotation = max(self.min_steer_rotation, min(self.steer_rotation, self.max_steer_rotation))

        if self.w:
            self.rotation += self.steer_rotation* self.display.game.delta_time * self.currentRotationSpeed
        if self.s:
            self.rotation -= self.steer_rotation* self.display.game.delta_time * self.currentRotationSpeed


        # print(self.steer_rotation)

        if self.boost and self.nitroAmount >= 1:
            self.nitroAmount -= 1
            a, b = self.get_acceleration_with_trigonometry(1, self.nitroPower)
            self.velLeft += a * self.display.game.delta_time * self.display.game.calibration
            self.velUp += b * self.display.game.delta_time * self.display.game.calibration

        magnitude = lolino.sqrt(self.velLeft ** 2 + self.velUp ** 2)
        if magnitude > self.currentMaxSpeed:
            self.slow_down(0.1 + self.speedCorrection * (magnitude - self.currentMaxSpeed))
        elif self.velLeft == c and self.velUp == d:
            if self.velLeft != 0 or self.velUp != 0:
                self.slow_down(self.naturalSlowdown / magnitude)


        # if not self.boost:
        #     magnitude = lolino.sqrt(self.velLeft ** 2 + self.velUp ** 2)
        #     if magnitude > self.currentMaxSpeed:
        #         self.velLeft = (self.velLeft / magnitude) * self.currentMaxSpeed
        #         self.velUp = (self.velUp / magnitude) * self.currentMaxSpeed

        if self.borderBounce:
            if self.x < 0:
                self.velLeft *= -self.borderBounciness
                self.x += 1
            if self.x > self.display.screenWidth:
                self.velLeft *= -self.borderBounciness
                self.x -= 1
            if self.y < 0:
                self.velUp *= -self.borderBounciness
                self.y += 1
            if self.y > self.display.screenHeight:
                self.velUp *= -self.borderBounciness
                self.y -= 1

        else:
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


    def slow_down(self, slowdown):
        self.velLeft -= self.velLeft * slowdown * self.display.game.delta_time * self.display.game.calibration
        self.velUp -= self.velUp * slowdown * self.display.game.delta_time * self.display.game.calibration

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
        if self.WASD_steering:
            return self.velLeft, self.velUp
        return (x * -acc), (y * acc)

    def loop(self):
        self.movement()
        self.collision_detection(self.display.enemy1.enemy_mask, self.display.enemy1.rect.topleft[0], self.display.enemy1.rect.topleft[1])
        self.collision_detection(self.display.mapMask, 0, 0)

    def collision_detection(self, mask, x, y):
        offset = (x - self.rect.topleft[0], y - self.rect.topleft[1])
        return self.car_mask.overlap(mask, offset)

    def collision_render(self, mask, x, y):
        offset = (x - self.rect.topleft[0], y - self.rect.topleft[1])
        sharedMask = self.car_mask.overlap_mask(mask, offset)
        sharedSurface = sharedMask.to_surface(setcolor=(0, 200, 0))
        sharedSurface.set_colorkey((0, 0, 0))
        self.display.screen.blit(sharedSurface, self.rect)

        blue_surface = sharedMask.to_surface(setcolor=(0, 0, 200))
        blue_surface.set_colorkey((0, 0, 0))
        self.display.screen.blit(blue_surface, (0, 0))

    def check_color(self, mask, x, y):
        offset = (x - self.rect.topleft[0], y - self.rect.topleft[1])
        sharedMask = self.car_mask.overlap_mask(mask, offset)
        sharedSurface = sharedMask.to_surface(setcolor=(0, 200, 0))
        sharedSurface.set_colorkey((0, 0, 0))
        size = sharedSurface.get_size()
        self.currentMaxSpeed = self.normalMaxSpeed
        self.currentRotationSpeed = self.normalRotationSpeed
        self.currentAcceleration = self.normalAcceleration
        for x in range(size[0]):
            for y in range(size[1]):
                if sharedSurface.get_at((x, y))[1] == 200:
                    tile = self.display.map[(self.rect.topleft[1] + y) // self.display.block_height][(self.rect.topleft[0] + x) // self.display.block_width]
                    if tile == 3:
                        self.currentMaxSpeed = self.gravelMaxSpeed
                        self.currentRotationSpeed = self.gravelRotationSpeed
                    # elif tile == 1:
                    #     self.velUp *= -1
                    #     self.velLeft *= -1