import random
from operator import invert

import pygame
import math as lolino
import time
from particle_system import ParticleGenerator
from unicodedata import normalize
from customObjects.custom_text import Custom_text
from app import images, obstacle
from jeff_the_objects import stacked_sprite

#TO DO:
#powerups - Tobiasz
#leaderboard - ???


class Car:
    def __init__(self, display, coordinates, rotation, isPlayer, model):
        self.display = display
        self.playerWidth, self.playerHeight = 25, 50
        self.isPlayer = isPlayer
        self.borderBounce = False  # whether the bounce from borders depends on the player's velocity
        self.borderBounciness = 0.9
        self.borderForce = 0.5 * self.display.game.calibration
        self.WASD_steering = False  # For debug only
        self.collision_draw = True
        self.model = model

        self.damping = 0.7

        self.gravel_color = (128, 128, 128)
        self.oil_color = (235, 180, 3)
        self.asphalt_color = (26, 26, 26)
        self.wall_color = (255, 255, 255)
        self.ice_color = (63, 208, 212)
        self.spike_color = (255, 0, 0)

        self.particle_color = [0, 0, 0]
        self.tireHealth = 1
        self.inventory = [1, 2, 3, 4] # 1 to super siła, 2 to barierka, 3 to kolczatka, 4 to heal - leczy 1 oponę
        self.inventory_size = 2

        self.strength = False # następne zderzenie z autem nie daje tobie knockbacku. Przy zderzeniu ze ścianą znika i nic nie robi
        self.infiNitro = True


        #balanced:
        if self.model == 1:
            self.image = images.car3d
            self.set_3d_parameters(self.model)
            self.car3d_sprite = stacked_sprite.StackedSprite(self.display, self.image, self.num_of_sprites, self.img_size,
                                                             self.car3d_height)
            self.backDifference = 0.65
            self.mass = 1
            self.nitroPower = 0.4 * self.display.game.calibration

            self.tireAmount = 4
            self.deadTires = 0
            self.tireDamage = 0.09

            self.normalAcceleration = 0.4 * self.display.game.calibration
            self.oilAcceleration = 0 * self.display.game.calibration
            self.iceAcceleration = 0.1 * self.display.game.calibration

            self.normalRotationSpeed = 0.03 * self.display.game.calibration
            self.gravelRotationSpeed = 0.018 * self.display.game.calibration

            self.normalMaxSpeed = 12 * self.display.game.calibration
            self.gravelMaxSpeed = 3 * self.display.game.calibration
            self.iceMaxSpeed = 25 * self.display.game.calibration

            self.normalFriction = 0.08 * self.display.game.calibration
            self.iceFriction = 0.02 * self.display.game.calibration
            self.oilFriction = 0 * self.display.game.calibration
        #tank(not literally) /offroad:
        elif self.model == 2:
            self.image = images.bike
            self.set_3d_parameters(self.model)
            self.car3d_sprite = stacked_sprite.StackedSprite(self.display, self.image, self.num_of_sprites, self.img_size, self.car3d_height)
            self.backDifference = 0.7
            self.mass = 1.5
            self.nitroPower = 0.35 * self.display.game.calibration
            self.tireAmount = 4
            self.deadTires = 0
            self.tireDamage = 0.06

            self.normalAcceleration = 0.4 * self.display.game.calibration
            self.oilAcceleration = 0 * self.display.game.calibration
            self.iceAcceleration = 0.12 * self.display.game.calibration

            self.normalRotationSpeed = 0.022 * self.display.game.calibration
            self.gravelRotationSpeed = 0.020 * self.display.game.calibration

            self.normalMaxSpeed = 11 * self.display.game.calibration
            self.gravelMaxSpeed = 5 * self.display.game.calibration
            self.iceMaxSpeed = 23 * self.display.game.calibration

            self.normalFriction = 0.1 * self.display.game.calibration
            self.iceFriction = 0.03 * self.display.game.calibration
            self.oilFriction = 0 * self.display.game.calibration
        #accelerator:
        elif self.model == 3:
            self.image = images.police
            self.set_3d_parameters(self.model)
            self.car3d_sprite = stacked_sprite.StackedSprite(self.display, self.image, self.num_of_sprites, self.img_size, self.car3d_height)
            self.backDifference = 0.65
            self.mass = 0.8
            self.nitroPower = 0.5 * self.display.game.calibration
            self.tireAmount = 3
            self.deadTires = 0
            self.tireDamage = 0.15

            self.normalAcceleration = 0.8 * self.display.game.calibration
            self.oilAcceleration = 0 * self.display.game.calibration
            self.iceAcceleration = 0.2 * self.display.game.calibration

            self.normalRotationSpeed = 0.032 * self.display.game.calibration
            self.gravelRotationSpeed = 0.02 * self.display.game.calibration

            self.normalMaxSpeed = 10 * self.display.game.calibration
            self.gravelMaxSpeed = 2.5 * self.display.game.calibration
            self.iceMaxSpeed = 20 * self.display.game.calibration

            self.normalFriction = 0.08 * self.display.game.calibration
            self.iceFriction = 0.02 * self.display.game.calibration
            self.oilFriction = 0 * self.display.game.calibration
        #mater:
        elif self.model == 4:
            self.backDifference = 1.4
            self.mass = 1.1
            self.nitroPower = 0.3 * self.display.game.calibration
            self.tireAmount = 4
            self.deadTires = 0
            self.tireDamage = 0.08

            self.normalAcceleration = 0.39 * self.display.game.calibration
            self.oilAcceleration = 0 * self.display.game.calibration
            self.iceAcceleration = 0.09 * self.display.game.calibration

            self.normalRotationSpeed = 0.025 * self.display.game.calibration
            self.gravelRotationSpeed = 0.018 * self.display.game.calibration

            self.normalMaxSpeed = 14 * self.display.game.calibration
            self.gravelMaxSpeed = 4 * self.display.game.calibration
            self.iceMaxSpeed = 25 * self.display.game.calibration

            self.normalFriction = 0.14 * self.display.game.calibration
            self.iceFriction = 0.03 * self.display.game.calibration
            self.oilFriction = 0 * self.display.game.calibration

        # elif self.model == 5 paweł jumper


        self.speedCorrection = 0.05 / self.display.game.calibration # when the car is going over the speed limit
        self.bumpingCooldown = 0.3
        self.wallCollisionCooldown = 0.05
        self.wallCollTime = 0

        self.x, self.y = coordinates[0], coordinates[1]
        self.archiveCords = [self.x, self.y]
        self.prevPos = [self.x, self.y]
        self.prevRotation = 0
        self.currentAcceleration = self.normalAcceleration
        self.currentMaxSpeed = self.normalMaxSpeed
        self.currentRotationSpeed = self.normalRotationSpeed
        self.currentFriction = self.normalFriction


        self.rect = self.car3d_sprite.rect
        self.rect.center = self.x, self.y

        self.car_mask = self.car3d_sprite.mask
        self.mask_image = self.car_mask.to_surface()


        self.velUp, self.velLeft, self.velAng = 0, 0, 0
        self.w, self.a, self.s, self.d, self.boost, self.q, self.e = False, False, False, False, False, False, False
        self.in_oil = False
        self.invincibility = 0
        self.inviFlicker = False
        self.rotation = rotation
        self.recentCollisions = {}
        self.timeToCheck = 5
        self.goingForward = True
        # self.wall = False

        self.steer_rotation = 0
        self.delta_rotation = 0.01*self.display.game.calibration
        self.max_steer_rotation = 60
        self.min_steer_rotation = -self.max_steer_rotation

        self.steering_speed = 9 * self.display.game.calibration

        self.nitroAmount = 0

        self.particle_system = self.display.particle_system

        back_wheel_offset = self.playerHeight / 2
        angle_rad = lolino.radians(-self.rotation)
        back_wheel_x_offset = lolino.cos(angle_rad) * back_wheel_offset
        back_wheel_y_offset = lolino.sin(angle_rad) * back_wheel_offset

        back_wheel1_x = self.x - back_wheel_x_offset - lolino.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel1_y = self.y - back_wheel_y_offset + lolino.cos(angle_rad) * (self.playerWidth / 2)
        back_wheel2_x = self.x - back_wheel_x_offset + lolino.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel2_y = self.y - back_wheel_y_offset - lolino.cos(angle_rad) * (self.playerWidth / 2)
        nitro_x = self.x - back_wheel_x_offset
        nitro_y = self.y - back_wheel_y_offset

        self.backwheel1_pgen = ParticleGenerator(self.particle_system, back_wheel1_x, back_wheel1_y, self.velLeft, self.velUp, -0.01 * self.velLeft,
                                          -0.01 * self.velUp, 0, 0, 1, 100, 3, self.particle_color[0], self.particle_color[1], self.particle_color[2], 150, 'square', False, 20)
        self.backwheel2_pgen = ParticleGenerator(self.particle_system, back_wheel2_x, back_wheel2_y, self.velLeft, self.velUp, -0.01 * self.velLeft,
                                          -0.01 * self.velUp, 0, 0, 1, 100, 3, self.particle_color[0], self.particle_color[1], self.particle_color[2], 150, 'square', False, 20)
        self.nitrogen = ParticleGenerator(self.particle_system, nitro_x, nitro_y, self.velLeft, self.velUp, 0, 0, 0, 0, 1, 200, 10, 200, 100,
                                          30, 150, 'circle', True, 100)


        self.particle_system.add_generator(self.backwheel1_pgen)
        self.particle_system.add_generator(self.backwheel2_pgen)
        self.particle_system.add_generator(self.nitrogen)

        self.backwheel1_pgen.start()
        self.backwheel2_pgen.start()

        self.display.objects.append(self)
        self.display.cars.append(self)

    def set_3d_parameters(self, model):
        if model == 1:
            self.num_of_sprites = 9
            self.img_size = (16, 16)
            self.car3d_height = 2.5
        elif model == 2:
            self.num_of_sprites = 11
            self.img_size = (4, 18)
            self.car3d_height = 3
        elif model == 3:
            self.num_of_sprites = 13
            self.img_size = (15, 34)
            self.car3d_height = 1.5

    def render(self):
        self.center = self.rect.center
        if self.inviFlicker:
            pygame.draw.circle(self.display.screen, (102, 100, 100), self.center, 25)
        # self.display.screen.blit(self.mask_image, self.rect)


        self.mask_image = self.car_mask.to_surface()
        # self.display.screen.blit(self.mask_image, self.mask_image.get_rect())
        # self.display.screen.blit(self.newImg, self.rect)
        self.car3d_sprite.render(self.display.screen, (self.x, self.y))

        back_wheel_offset = self.playerHeight / 2
        angle_rad = lolino.radians(-self.rotation)
        back_wheel_x_offset = lolino.cos(angle_rad) * back_wheel_offset
        back_wheel_y_offset = lolino.sin(angle_rad) * back_wheel_offset

        back_wheel1_x = self.x - back_wheel_x_offset - lolino.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel1_y = self.y - back_wheel_y_offset + lolino.cos(angle_rad) * (self.playerWidth / 2)
        back_wheel2_x = self.x - back_wheel_x_offset + lolino.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel2_y = self.y - back_wheel_y_offset - lolino.cos(angle_rad) * (self.playerWidth / 2)

        self.backwheel1_pgen.edit(back_wheel1_x, back_wheel1_y, self.velLeft, self.velUp)
        self.backwheel2_pgen.edit(back_wheel2_x, back_wheel2_y, self.velLeft, self.velUp)

        if self.boost and not self.WASD_steering:
            nitro_x = self.x - back_wheel_x_offset
            nitro_y = self.y - back_wheel_y_offset
            if self.nitrogen.active:
                self.nitrogen.edit(nitro_x, nitro_y, self.velLeft, self.velUp)
            else:
                self.nitrogen.start()
        elif self.nitrogen.active:
            self.nitrogen.stop()


        if self.collision_detection(self.display.mapMask, 0, 0):
            self.collision_render(self.display.mapMask, 0, 0)

        for c in self.display.cars:
            if not self == c:
                if self.collision_detection(c.car_mask, c.rect.topleft[0], c.rect.topleft[1]):
                    self.collision_render(c.car_mask, c.rect.topleft[0], c.rect.topleft[1])
                    self.block(c.rect.topleft[0], c.rect.topleft[1])
                    try:
                        if self.recentCollisions[c] == 0:
                            self.handle_bumping(c)
                            self.recentCollisions[c] = time.time()
                            c.recentCollisions[self] = time.time()
                    except:
                        pass

        for p in self.display.powerups:
            if self.collision_detection(p.mask, p.rect.topleft[0], p.rect.topleft[1]):
                if self.isPlayer:
                    self.display.game.sound_manager.play_sound('Powerup')
                bonus = random.randint(0, 4)
                if bonus == 0:
                    self.nitroAmount += 20
                    if self.nitroAmount > 100:
                        self.nitroAmount = 100
                elif len(self.inventory) < self.inventory_size:
                    self.inventory.append(bonus)
                p.kill()


        if self.display.game.debug:
            pygame.draw.rect(self.display.game.screen, (0, 255, 0), self.rect, width=1)

            # Create/reuse debug text elements
            if not hasattr(self, 'debug_texts'):
                # Initialize debug texts once
                self.debug_texts = [
                    Custom_text(self.display, 0, 0, "", font_height=18, text_color=(255, 255, 255),
                                background_color=(0, 0, 0, 128), center=False),
                    Custom_text(self.display, 0, 0, "", font_height=18, text_color=(255, 255, 255),
                                background_color=(0, 0, 0, 128), center=False),
                    Custom_text(self.display, 0, 0, "", font_height=18, text_color=(255, 255, 255),
                                background_color=(0, 0, 0, 128), center=False),
                    Custom_text(self.display, 0, 0, "", font_height=18, text_color=(255, 255, 255),
                                background_color=(0, 0, 0, 128), center=False)
                ]
            else:
                for i, text_obj in enumerate(self.debug_texts):
                    text_obj.hidden = False

            # Calculate debug info
            speed = lolino.hypot(self.velLeft, self.velUp)
            surface_type = "Normal"
            if self.currentMaxSpeed == self.gravelMaxSpeed:
                surface_type = "Gravel"
            elif self.currentMaxSpeed == self.iceMaxSpeed:
                surface_type = "Ice"

            # Update text contents
            texts = [
                f"Speed: {speed:.1f}",
                f"Rotation: {self.rotation:.1f}°",
                f"Surface: {surface_type}",
                f"Nitro: {self.nitroAmount}"
            ]

            # Position texts above the car
            base_y = self.rect.top - 70
            for i, text_obj in enumerate(self.debug_texts):
                text_obj.update_text(texts[i])
                text_obj.update_position(self.rect.centerx, base_y + i * 20)
                text_obj.render()

            # Steering wheel visualization
            wheel_radius = 15
            wheel_center = (self.rect.centerx-30, self.rect.top - 30)
            line_length = 12
            pygame.draw.circle(self.display.screen, (200, 200, 200), wheel_center, wheel_radius, 2)
            angle = lolino.radians(self.steer_rotation)
            line_end = (
                wheel_center[0] + line_length * lolino.cos(angle),
                wheel_center[1] - line_length * lolino.sin(angle)
            )
            pygame.draw.line(self.display.screen, (255, 40, 40), wheel_center, line_end, 2)
        else:
            if hasattr(self, 'debug_texts'):
                for text_obj in self.debug_texts:
                    text_obj.hidden = True

    def events(self, event):
        pass

    def movement(self):
        self.prevPos = [self.x, self.y]
        self.prevRotation = self.rotation
        c, d = self.velLeft, self.velUp
        if self.w and not self.in_oil:
            if self.WASD_steering:
                self.velUp += self.currentAcceleration
            else:
                a, b = self.get_acceleration_with_trigonometry(1, self.currentAcceleration * self.display.game.delta_time * self.display.game.calibration * self.tireHealth / 2)
                self.velLeft += a
                self.velUp += b
        if self.s and not self.in_oil:
            if self.WASD_steering:
                self.velUp -= self.currentAcceleration
            else:
                a, b = self.get_acceleration_with_trigonometry(-1, self.currentAcceleration * self.backDifference * self.display.game.delta_time * self.display.game.calibration * self.tireHealth / 2)
                self.velLeft += a
                self.velUp += b
        if self.a and not self.in_oil:
            if self.WASD_steering:
                self.velLeft += self.currentAcceleration
            else:
                self.steer_rotation += self.delta_rotation * self.display.game.delta_time * self.steering_speed
        if self.d and not self.in_oil:
            if self.WASD_steering:
                self.velLeft -= self.currentAcceleration
            else:
                self.steer_rotation += -self.delta_rotation * self.display.game.delta_time * self.steering_speed
        if self.q and self.WASD_steering:
            self.steer_rotation += self.delta_rotation * self.display.game.delta_time * self.steering_speed
        if self.e and self.WASD_steering:
            self.steer_rotation += -self.delta_rotation * self.display.game.delta_time * self.steering_speed
        if not self.a and not self.d and not self.in_oil:
            self.steer_rotation -= 10*self.steer_rotation * self.display.game.delta_time
        if abs(self.steer_rotation) < 0.01:
            self.steer_rotation = 0



        self.steer_rotation = max(self.min_steer_rotation, min(self.steer_rotation, self.max_steer_rotation))

        if self.WASD_steering:
            self.rotation += self.steer_rotation* self.display.game.delta_time * self.currentRotationSpeed * 2

        if self.boost and self.nitroAmount >= 1 and not self.WASD_steering:
            if not self.infiNitro:
                self.nitroAmount -= 1
            a, b = self.get_acceleration_with_trigonometry(1, self.nitroPower)
            self.velLeft += a * self.display.game.delta_time * self.display.game.calibration
            self.velUp += b * self.display.game.delta_time * self.display.game.calibration

        magnitude = lolino.sqrt(self.velLeft ** 2 + self.velUp ** 2)
        if magnitude > self.currentMaxSpeed:
            self.slow_down(0.1 + self.speedCorrection * (magnitude - self.currentMaxSpeed))
        # elif self.velLeft == c and self.velUp == d:
        if self.velLeft != 0 or self.velUp != 0:
            self.slow_down(self.currentFriction / magnitude / (self.tireHealth ** 0.2))

        if magnitude > self.currentFriction:
            modifier = magnitude / 200
            if modifier > 2:
                modifier = 2
            if modifier < 0.2:
                modifier = 0.2
            if self.timeToCheck >= 0:
                self.timeToCheck = 5
                self.goingForward = self.check_if_forward(self.get_direction_with_trigonometry((self.x - self.archiveCords[0]), (self.y - self.archiveCords[1])))
            else:
                self.timeToCheck -= 1
            if self.goingForward:
                self.rotation += self.steer_rotation * self.display.game.delta_time * self.currentRotationSpeed * modifier
            else:
                self.rotation -= self.steer_rotation * self.display.game.delta_time * self.currentRotationSpeed * modifier

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
            if self.y > self.display.screenHeight_without_hotbar:
                self.velUp *= -self.borderBounciness
                self.y -= 1

        else:
            if self.x < 0:
                self.x += 2
                self.velLeft = -self.borderForce
            if self.x > self.display.screenWidth:
                self.x -= 2
                self.velLeft = self.borderForce
            if self.y < 0:
                self.y += 2
                self.velUp = -self.borderForce
            if self.y > self.display.screenHeight_without_hotbar:
                self.y -= 2
                self.velUp = self.borderForce

        self.archiveCords = [self.x, self.y]
        self.x -= self.velLeft * self.display.game.delta_time
        self.y -= self.velUp * self.display.game.delta_time
        self.rotation += lolino.degrees(self.velAng * self.display.game.delta_time)
        self.velAng *= self.damping

    def use_powerup(self):
        if len(self.inventory) == 0:
            return
        if self.inventory[0] == 1:
            pass
            self.strength = True
        elif self.inventory[0] == 2:
            pass
            angle = lolino.radians(self.rotation)
            spawn_x = self.x - (50 * lolino.cos(angle))
            spawn_y = self.y + (50 * lolino.sin(angle))
            self.display.obstacles.append(obstacle.Obstacle(self.display, spawn_x, spawn_y, 'barrier', self.rotation - 90))
        elif self.inventory[0] == 3:
            angle = lolino.radians(self.rotation)
            spawn_x = self.x - (50 * lolino.cos(angle))
            spawn_y = self.y + (50 * lolino.sin(angle))
            self.display.obstacles.append(obstacle.Obstacle(self.display, spawn_x, spawn_y, 'spikes', self.rotation - 90))
        elif self.inventory[0] == 4:
            if self.deadTires > 0:
                 self.deadTires -= 1
        self.inventory.pop(0)


    def slow_down(self, slowdown):
        self.velLeft -= self.velLeft * slowdown * self.display.game.delta_time * self.display.game.calibration
        self.velUp -= self.velUp * slowdown * self.display.game.delta_time * self.display.game.calibration

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

    def get_direction_with_trigonometry(self, xStep, yStep):
        if xStep >= 0:
            if yStep < 0:
                quarter = 1
            else:
                quarter = 4
        else:
            if yStep <= 0:
                quarter = 2
            else:
                quarter = 3


        xStep, yStep = abs(xStep), abs(yStep)

        if quarter == 1:
            a, b = xStep, yStep
        elif quarter == 2:
            a, b = yStep, xStep
        elif quarter == 3:
            a, b = yStep, xStep
        elif quarter == 4:
            a, b = xStep, yStep

        try:
            tan = a/b
        except ZeroDivisionError:
            tan = lolino.inf

        rads = lolino.atan(tan)
        degs = int(lolino.degrees(rads))

        if quarter == 1:
            return 90 - degs
        elif quarter == 2:
            return 180 - degs
        elif quarter == 3:
            return 180 + degs
        elif quarter == 4:
            return 270 + degs

    def check_if_forward(self, direction):
        if direction >= 360:
            direction -= 360
        if self.model == 4:
            min, max = direction - 90, direction + 90
        else:
            min, max = direction - 110, direction + 110
        r = self.normalize_angle(self.rotation)
        if r < max and min < r:
            return True
        else:
            if min < 0:
                if r < max + 360 and min + 360 < r:
                    return True
            elif max > 360:
                if r < max - 360 and min - 360 < r:
                    return True
        return False

    def normalize_angle(self, angle):
        while angle <= 0:
            angle += 360
        while angle > 360:
            angle -= 360
        return angle

    def block(self, x, y):
        dx = x - self.rect.centerx
        dy = y - self.rect.centery
        distance = lolino.sqrt(dx ** 2 + dy ** 2)
        if distance == 0:
            return

        nx = dx / distance
        ny = dy / distance

        # Move car back along collision normal
        separation = 2  # Adjust this value based on penetration depth if available
        self.x -= nx * separation
        self.y -= ny * separation

        # Reset rotation to prevent clipping
        self.rotation = self.prevRotation

    # def get_penetration(self, mask, x, y):
    #     xs = 0
    #     ys = 0
    #     offset = (x - self.rect.topleft[0], y - self.rect.topleft[1])
    #     sharedMask = self.car_mask.overlap_mask(mask, offset)
    #     sharedSurface = sharedMask.to_surface(setcolor=(0, 200, 0))
    #     sharedSurface.set_colorkey((0, 0, 0))
    #     size = sharedSurface.get_size()
    #
    #     for x in range(size[0]):
    #         for y in range(size[1]):
    #             if sharedSurface.get_at((x, y))[1] == 200:
    #                 xs += 1
    #                 break
    #     for y in range(size[1]):
    #         for x in range(size[0]):
    #             if sharedSurface.get_at((x, y))[1] == 200:
    #                 ys += 1
    #                 break
    #
    #     return xs, ys

    def loop(self):
        self.movement()
        self.invincibility -= 5 * self.display.game.delta_time
        if self.invincibility > 0 and self.isPlayer:
            if int(self.invincibility) % 2 == 0:
                self.inviFlicker = not self.inviFlicker
                self.invincibility -= 1
        else:
            self.inviFlicker = False
        if len(self.recentCollisions) != len(self.display.cars) - 1:
            for car in self.display.cars:
                if not self == car:
                    if car not in self.recentCollisions:
                        self.recentCollisions[car] = 0

        for car in self.recentCollisions:
            if self.recentCollisions[car] != 0 and not self.collision_detection(car.car_mask, car.rect.topleft[0], car.rect.topleft[1]):
                if time.time() - self.recentCollisions[car] > self.bumpingCooldown:
                    self.recentCollisions[car] = 0

        if self.wallCollTime != 0:
            if time.time() - self.wallCollTime > self.wallCollisionCooldown:
                self.wallCollTime = 0



        for obstacle in self.display.obstacles:
            if self.collision_detection(obstacle.obstacle_mask, obstacle.rect.topleft[0], obstacle.rect.topleft[1]):
                if obstacle.type == 1:
                    if self.prickWheels():
                        obstacle.destroy()
                elif obstacle.type == 2:
                    self.block(obstacle.rect.topleft[0], obstacle.rect.topleft[1])
                    self.velUp *= -0.5
                    self.velLeft *= -0.5


        self.currentMaxSpeed = self.normalMaxSpeed
        self.currentAcceleration = self.normalAcceleration
        self.currentRotationSpeed = self.normalRotationSpeed
        self.currentFriction = self.normalFriction
        self.in_oil = False

        self.car_mask = self.car3d_sprite.update_mask_rotation(int(self.rotation))
        self.rect = self.car3d_sprite.rect
        self.rect.center = self.x, self.y
        # self.wall = False
        if self.collision_detection(self.display.mapMask, 0, 0):
            self.check_color(self.display.mapMask, 0, 0)
        else:
            self.particle_color = (100, 100, 100)
            self.backwheel1_pgen.edit(red=self.particle_color[0], green=self.particle_color[1],blue=self.particle_color[2])
            self.backwheel2_pgen.edit(red=self.particle_color[0], green=self.particle_color[1],blue=self.particle_color[2])

    def prickWheels(self):
        if self.invincibility < 1 and self.deadTires < self.tireAmount:
            self.invincibility = 20
            self.deadTires += 1
            self.tireHealth -= self.tireDamage
            self.display.game.sound_manager.play_sound('boom')
            return True
        else:
            return False

    def wall_collision(self, mask, x, y):
        dx = x - self.x
        dy = y - self.y
        distance = lolino.sqrt(dx ** 2 + dy ** 2)
        if distance == 0:
            n = (0, 0)
        else:
            n = (dx / distance, dy / distance)

        t = (-n[1], n[0])

        v1n = self.velLeft * n[0] + self.velUp * n[1]
        v1t = self.velLeft * t[0] + self.velUp * t[1]

        v1n_new = -v1n

        self.velLeft = v1n_new * n[0] + v1t * t[0]
        self.velUp = v1n_new * n[1] + v1t * t[1]
        r = (self.x - x, self.y - y)
        delta_px = self.mass * self.velLeft
        delta_py = self.mass * self.velUp
        L =  r[0] * delta_py - r[1] * delta_px
        d = (r[0] ** 2 + r[1] ** 2) ** 0.5
        I = (1 / 12) * self.mass * (self.playerWidth ** 2 + self.playerHeight ** 2) + self.mass * d ** 2
        impulse = 2 * self.mass * abs(v1n)

        self.velAng = L / I
        # self.x += n[0]
        # self.y += n[1]
        self.wall_separation(x, y)

    def teleport(self, coords):
        if self.isPlayer:
            self.x = coords[0]
            self.y = coords[1]

    def wall_separation(self, x, y):
        dx = x - self.x
        dy = y - self.y
        distance = lolino.sqrt(dx ** 2 + dy ** 2)

        if distance == 0:
            return

        sum_radii = (self.playerWidth / 2 + self.display.block_width / 2)
        overlap = sum_radii - distance

        if overlap > 0:
            nx = dx / distance
            ny = dy / distance

            self.x -= nx * overlap
            self.y -= ny * overlap


    def handle_bumping(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        distance = lolino.sqrt(dx ** 2 + dy ** 2)
        if distance == 0:
            return "GET OUT"

        sum_radii = (self.playerWidth + other.playerWidth) / 2
        overlap = sum_radii - distance
        if overlap > 0:
            # Normalize direction vector
            nx = dx / distance
            ny = dy / distance

            # Separate the cars
            separation = overlap * 0.5
            self.x -= nx * separation
            self.y -= ny * separation
            other.x += nx * separation
            other.y += ny * separation


        # coll_x, coll_y = self.get_coordinates(other.car_mask, other.rect.topleft[0], other.rect.topleft[1])
        # # print(coll_x, coll_y)
        # r_self = (coll_x - self.x, coll_y - self.y)
        # r_other = (coll_x - other.x, coll_y - other.y)
        # px_self = self.mass * self.velLeft
        # py_self = self.mass * self.velUp
        # px_other = other.mass * other.velLeft
        # py_other = other.mass * other.velUp
        # La = r_self[0] * py_self - r_self[1] * px_self
        # Lb = r_other[0] * py_other - r_other[1] * px_other
        # Ia = 1/12 * self.mass * (self.playerWidth ** 2 + self.playerHeight ** 2)
        # Ib = 1/12 * other.mass * (other.playerWidth ** 2 + other.playerHeight ** 2)
        # omega_A = La / Ia
        # omega_B = Lb / Ib
        # self.velAng = omega_A
        # other.velAng = omega_B
        coll_x, coll_y = self.get_coordinates(other.car_mask, other.rect.topleft[0], other.rect.topleft[1])
        r_self = (coll_x - self.x, coll_y - self.y)
        r_other = (coll_x - other.x, coll_y - other.y)
        delta_px = (self.mass * self.velLeft) - (other.mass * other.velLeft)
        delta_py = (self.mass * self.velUp) - (other.mass * other.velUp)
        La = r_self[0] * delta_py - r_self[1] * delta_px
        Lb = r_other[0] * delta_py - r_other[1] * delta_px
        d_self = (r_self[0] ** 2 + r_self[1] ** 2) ** 0.5
        d_other = (r_other[0] ** 2 + r_other[1] ** 2) ** 0.5
        Ia = (1 / 12 * self.mass * (self.playerWidth ** 2 + self.playerHeight ** 2)) + self.mass * d_self ** 2
        Ib = (1 / 12 * other.mass * (other.playerWidth ** 2 + other.playerHeight ** 2)) + other.mass * d_other ** 2

        omega_A = La / Ia
        omega_B = Lb / Ib

        self.velAng = omega_A
        other.velAng = omega_B
        # self.rotation += lolino.degrees(omega_A * self.display.game.delta_time)
        # other.rotation += lolino.degrees(omega_B * self.display.game.delta_time)
        n = ((other.x - self.x) / lolino.sqrt((other.x - self.x)**2 + (other.y - self.y)**2), (other.y - self.y) / lolino.sqrt((other.x - self.x)**2 + (other.y - self.y)**2))
        t = (-n[1], n[0])
        v1n = self.velLeft * n[0] + self.velUp * n[1]
        v1t = self.velLeft * t[0] + self.velUp * t[1]
        v2n = other.velLeft * n[0] + other.velUp * n[1]
        v2t = other.velLeft * t[0] + other.velUp * t[1]

        v1n_new = (v1n * (self.mass - other.mass) + 2 * other.mass * v2n) / (self.mass + other.mass)
        v2n_new = (v2n * (other.mass - self.mass) + 2 * self.mass * v1n) / (self.mass + other.mass)

        v1 = (v1n_new * n[0] + v1t * t[0], v1n_new * n[1] + v1t * t[1])
        v2 = (v2n_new * n[0] + v2t * t[0], v2n_new * n[1] + v2t * t[1])
        self.velLeft, other.velLeft = v1[0], v2[0]
        self.velUp, other.velUp = v1[1], v2[1]

    def collision_detection(self, mask, x, y):
        offset = (x - self.rect.topleft[0], y - self.rect.topleft[1])
        return self.car_mask.overlap(mask, offset)

    def get_coordinates(self, mask, x, y):
        xs = []
        xy = []
        offset = (x - self.rect.topleft[0], y - self.rect.topleft[1])
        sharedMask = self.car_mask.overlap_mask(mask, offset)
        sharedSurface = sharedMask.to_surface(setcolor=(0, 200, 0))
        sharedSurface.set_colorkey((0, 0, 0))
        for x in range(sharedSurface.get_size()[0]):
            for y in range(sharedSurface.get_size()[1]):
                if sharedSurface.get_at((x, y))[1] == 200:
                    xs.append(x + self.rect.topleft[0])
                    xy.append(y + self.rect.topleft[1])
        return sum(xs) // len(xs), sum(xy) // len(xy)

    def collision_render(self, mask, x, y):

        offset = (x - self.rect.topleft[0], y - self.rect.topleft[1])
        sharedMask = self.car_mask.overlap_mask(mask, offset)
        sharedSurface = sharedMask.to_surface(setcolor=(0, 200, 0))
        sharedSurface.set_colorkey((0, 0, 0))
        if self.collision_draw:
            self.display.screen.blit(sharedSurface, self.rect)

        blue_surface = sharedMask.to_surface(setcolor=(0, 0, 200))
        blue_surface.set_colorkey((0, 0, 0))
        if self.collision_draw:
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
        self.currentFriction = self.normalFriction
        self.in_oil = False

        for x in range(size[0]):
            for y in range(size[1]):
                if sharedSurface.get_at((x, y))[1] == 200:
                    tile = self.display.map[int((self.rect.topleft[1] + y) // self.display.block_height)][(self.rect.topleft[0] + x) // self.display.block_width]
                    if tile == 2:
                        self.currentAcceleration = self.oilAcceleration
                        self.currentFriction = self.oilFriction
                        self.in_oil = True
                        self.steer_rotation = 0
                        self.particle_color = self.oil_color
                        self.backwheel1_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                        self.backwheel2_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                    elif tile == 1:
                        # self.wall = True
                        self.particle_color = self.wall_color
                        self.backwheel1_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                        self.backwheel2_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                        center_x = ((self.rect.topleft[
                                         0] + x) // self.display.block_width) * self.display.block_width + self.display.block_width // 2
                        center_y = ((self.rect.topleft[
                                         1] + y) // self.display.block_height) * self.display.block_height + self.display.block_height // 2
                        if self.wallCollTime == 0:
                            if self.isPlayer:
                                self.display.game.sound_manager.play_sound('bounce')
                            self.wallCollTime = time.time()
                            self.wall_collision(sharedMask, center_x, center_y)
                        else:
                            self.wall_separation(center_x, center_y)

                    elif tile == 3:
                        self.currentMaxSpeed = self.gravelMaxSpeed
                        self.currentRotationSpeed = self.gravelRotationSpeed
                        self.particle_color = self.gravel_color
                        self.backwheel1_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                        self.backwheel2_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                    elif tile == 4:
                        self.currentAcceleration = self.iceAcceleration
                        self.currentMaxSpeed = self.iceMaxSpeed
                        self.currentFriction = self.iceFriction
                        self.particle_color = self.ice_color
                        self.backwheel1_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                        self.backwheel2_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                    elif tile == 5:
                        self.particle_color = self.spike_color
                        self.backwheel1_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                        self.backwheel2_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                        self.prickWheels()



