import random
import time
from operator import invert, index
import string

import pygame
import math as m
from particle_system import ParticleGenerator
from unicodedata import normalize

import app.display
import customObjects.custom_text
from app.images import police
from customObjects.custom_text import Custom_text
from app import images, obstacle
from jeff_the_objects import stacked_sprite


class Car:
    def __init__(self, display, coordinates, rotation, isPlayer, model, name: str="None", car3d_height_factor=None):
        self.display = display
        self.playerWidth, self.playerHeight = 25, 50
        self.isPlayer = isPlayer
        self.borderBounce = False  # whether the bounce from borders depends on the player's velocity
        self.borderBounciness = 0.9
        self.borderForce = 0.5 * self.display.game.calibration
        self.WASD_steering = False  # For debug only
        self.collision_draw = False
        self.wall = False
        self.barrier = False
        self.finished = False
        self.full_time = 0
        self.model = model
        self.car3d_height_factor = car3d_height_factor
        self.wall_frames = 0
        self.last_frames_len = 3
        self.name = name
        self.current_checkpoint = -1
        self.lap = 1
        self.damping = 0.7

        self.nitrogen_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]
        self.nitrogen_color = random.choice(self.nitrogen_colors)

        self.gravel_color = (128, 128, 128)
        self.oil_color = (235, 180, 3)
        self.asphalt_color = (26, 26, 26)
        self.wall_color = (255, 255, 255)
        self.ice_color = (63, 208, 212)
        self.spike_color = (255, 0, 0)

        self.particle_color = [0, 0, 0]
        self.tireHealth = 1
        self.inventory = [] # 1 to super siła, 2 to barierka, 3 to kolczatka, 4 to heal - leczy 1 oponę
        self.inventory_size = 2

        self.lap_times = []

        self.strength = False # następne zderzenie z autem nie daje tobie knockbacku. Przy zderzeniu ze ścianą znika i nic nie robi
        self.infiNitro = True
        self.player_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        self.hits = 0
        self.perfectLap = True
        self.perfectLaps = 0
        self.pupscollected = 0


        self.velUp, self.velLeft, self.velAng = 0, 0, 0
        self.rotation = rotation
        self.x, self.y = coordinates[0], coordinates[1]
        self.next_x, self.next_y = coordinates[0], coordinates[1]
        self.particle_system = self.display.particle_system

        # if self.display.game.enable_debug:
        #     self.placement = customObjects.custom_text.Custom_text(self.display, self.x, self.y, '0', text_color='white', append=False)

        back_wheel_offset = self.playerHeight / 2
        angle_rad = m.radians(-self.rotation)
        back_wheel_x_offset = m.cos(angle_rad) * back_wheel_offset
        back_wheel_y_offset = m.sin(angle_rad) * back_wheel_offset

        back_wheel1_x = self.x - back_wheel_x_offset - m.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel1_y = self.y - back_wheel_y_offset + m.cos(angle_rad) * (self.playerWidth / 2)
        back_wheel2_x = self.x - back_wheel_x_offset + m.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel2_y = self.y - back_wheel_y_offset - m.cos(angle_rad) * (self.playerWidth / 2)
        nitro_x = self.x - back_wheel_x_offset
        nitro_y = self.y - back_wheel_y_offset

        if isinstance(self.display, app.display.game_display):
            self.backwheel1_pgen = ParticleGenerator(self.particle_system, back_wheel1_x, back_wheel1_y, self.velLeft, self.velUp, -0.01 * self.velLeft,
                                              -0.01 * self.velUp, 0, 0, 1, 100, 3, self.particle_color[0], self.particle_color[1], self.particle_color[2], 150, 'square', False, 20)
            self.backwheel2_pgen = ParticleGenerator(self.particle_system, back_wheel2_x, back_wheel2_y, self.velLeft, self.velUp, -0.01 * self.velLeft,
                                              -0.01 * self.velUp, 0, 0, 1, 100, 3, self.particle_color[0], self.particle_color[1], self.particle_color[2], 150, 'square', False, 20)
            self.nitrogen = ParticleGenerator(self.particle_system, nitro_x, nitro_y, self.velLeft, self.velUp, 0, 0, 0, 0, 1, 200, 10, self.nitrogen_color[0], self.nitrogen_color[1],
                                              self.nitrogen_color[2], 150, 'circle', True, 100)
        self.change_model(model)


        self.speedCorrection = 0.05 / self.display.game.calibration # when the car is going over the speed limit
        self.bumpingCooldown = 10
        self.wallCollisionCooldown = 10
        self.wallCollTime = 0



        self.delta_x, self.delta_y = 0, 0
        self.archiveCords = [self.x, self.y]
        self.prevPos = [self.x, self.y]
        self.prevRotation = 0
        self.archiveWall = [[self.x, self.y, self.rotation] for _ in range(self.last_frames_len)]
        self.archiveCars = [[self.x, self.y, self.rotation] for _ in range(self.last_frames_len)]
        self.archiveBarrier = [[self.x, self.y, self.rotation] for _ in range(self.last_frames_len)]
        self.currentAcceleration = self.normalAcceleration
        self.currentMaxSpeed = self.normalMaxSpeed
        self.currentRotationSpeed = self.normalRotationSpeed
        self.currentFriction = self.normalFriction


        self.rect = self.car3d_sprite.rect
        self.rect.center = self.x, self.y

        self.car_mask = self.car3d_sprite.mask
        self.mask_image = self.car_mask.to_surface()

        self.stunned = False
        self.stunned_timer = 0

        self.w, self.a, self.s, self.d, self.boost, self.q, self.e = False, False, False, False, False, False, False
        self.in_oil = False
        self.bananaTime = 0

        self.enemy_on_banana = False
        self.enemy_spike_wheel = False

        self.invincibility = 0
        self.inviFlicker = False

        self.next_rotation = self.rotation
        self.recentCollisions = {}
        self.goingForward = True

        self.steer_rotation = 0
        self.delta_rotation = 0.01*self.display.game.calibration
        self.max_steer_rotation = 60
        self.min_steer_rotation = -self.max_steer_rotation

        self.steering_speed = 9 * self.display.game.calibration

        self.nitroAmount = 1

        self.bounce_sound_timer = 0

        if isinstance(self.display, app.display.game_display):
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
            if self.car3d_height_factor == None:
                self.car3d_height = 2.5
            else:
                self.car3d_height = 2.5 *self.car3d_height_factor
        elif model == 2:
            self.num_of_sprites = 14
            self.img_size = (15, 32)
            if self.car3d_height_factor == None:
                self.car3d_height = 1.5
            else:
                self.car3d_height = 1.5 * self.car3d_height_factor
        elif model == 4:
            self.num_of_sprites = 13
            self.img_size = (15, 34)
            if self.car3d_height_factor == None:
                self.car3d_height = 1.5
            else:
                self.car3d_height = 1.5 * self.car3d_height_factor
        elif model == 3:
            self.num_of_sprites = 11
            self.img_size = (10, 18)
            if self.car3d_height_factor == None:
                self.car3d_height = 3
            else:
                self.car3d_height = 3 *self.car3d_height_factor
        elif model == 5:
            self.num_of_sprites = 6
            self.img_size = (33, 29)
            if self.car3d_height_factor == None:
                self.car3d_height = 2
            else:
                self.car3d_height = 2 *self.car3d_height_factor


    def render(self):
        # if self.display.game.enable_debug:
        #     for i, car in enumerate(self.display.leaderboard_list):
        #         if car == self:
        #             self.placement.update_text(f"{i+1} {self.lap} {int(self.get_distance_to_nearest_checkpoint())}")
        #             self.placement.update_position(self.x, self.y)
        #


        self.center = self.rect.center
        if self.inviFlicker:
            pygame.draw.circle(self.display.screen, (102, 100, 100), self.center, 25)


        self.mask_image = self.car_mask.to_surface()
        self.car3d_sprite.render(self.display.screen, (self.x, self.y))

        back_wheel_offset = self.playerHeight / 2
        angle_rad = m.radians(-self.rotation)
        back_wheel_x_offset = m.cos(angle_rad) * back_wheel_offset
        back_wheel_y_offset = m.sin(angle_rad) * back_wheel_offset

        back_wheel1_x = self.x - back_wheel_x_offset - m.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel1_y = self.y - back_wheel_y_offset + m.cos(angle_rad) * (self.playerWidth / 2)
        back_wheel2_x = self.x - back_wheel_x_offset + m.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel2_y = self.y - back_wheel_y_offset - m.cos(angle_rad) * (self.playerWidth / 2)

        self.backwheel1_pgen.edit(back_wheel1_x, back_wheel1_y, self.velLeft, self.velUp)
        self.backwheel2_pgen.edit(back_wheel2_x, back_wheel2_y, self.velLeft, self.velUp)

        if self.boost and not self.WASD_steering:
            nitro_x = self.x - back_wheel_x_offset
            nitro_y = self.y - back_wheel_y_offset
            if self.nitroAmount > 0:
                if self.nitrogen.active:
                    self.nitrogen_color = random.choice(self.nitrogen_colors)
                    self.nitrogen.red, self.nitrogen.green, self.nitrogen.blue = self.nitrogen_color[0], \
                    self.nitrogen_color[1], self.nitrogen_color[2]

                    self.nitrogen.edit(nitro_x, nitro_y, self.velLeft, self.velUp)
                else:
                    self.nitrogen.start()
                    self.nitrogen_color = random.choice(self.nitrogen_colors)
                    self.nitrogen.red,self.nitrogen.green,self.nitrogen.blue = self.nitrogen_color[0], self.nitrogen_color[1], self.nitrogen_color[2]
                    self.nitrogen.edit(nitro_x, nitro_y, self.velLeft, self.velUp)
        elif self.nitrogen.active:
            self.nitrogen.stop()

        if self.collision_detection(self.display.mapMask, 0, 0):
            self.collision_render(self.display.mapMask, 0, 0)

        for p in self.display.powerups:
            if self.collision_detection(p.mask, p.rect.topleft[0], p.rect.topleft[1]):
                if self.isPlayer:
                    self.display.game.sound_manager.play_sound('Powerup')
                bonus = random.randint(0, 4)
                self.pupscollected += 1

                powerup_names = ["NITRO", "STRENGTH", "BARRIER", "SPIKES", "HEAL"]
                if self.isPlayer:
                    font = pygame.font.Font("fonts/joystix monospace.otf", 30)
                    text_surface = font.render(f"Collected: {powerup_names[bonus]}", True, (255, 255, 255))

                    text_rect = text_surface.get_rect(
                        center=(self.display.game.width // 2, self.display.game.height // 5))

                    bg_rect = text_rect.copy()
                    bg_rect.inflate_ip(20, 10)

                    self.display.powerup_text = {
                        'surface': text_surface,
                        'rect': text_rect,
                        'bg_rect': bg_rect,
                        'bg_color': (0, 0, 0)
                    }
                    self.display.powerup_text_timer = 7



                if bonus == 0:
                    self.nitroAmount += 50

                    if self.nitroAmount > 100:
                        self.nitroAmount = 100
                elif len(self.inventory) < self.inventory_size:
                    self.inventory.append(bonus)
                p.kill()

        if hasattr(self.display, 'powerup_text') and hasattr(self.display, 'powerup_text_timer') and self.display.powerup_text_timer > 0:
            pygame.draw.rect(
                self.display.screen,
                self.display.powerup_text['bg_color'],
                self.display.powerup_text['bg_rect']
            )

            self.display.screen.blit(
                self.display.powerup_text['surface'],
                self.display.powerup_text['rect']
            )

            self.display.powerup_text_timer -= self.display.game.delta_time
        if self.display.game.debug:
            pygame.draw.rect(self.display.game.screen, (0, 255, 0), self.rect, width=1)

            if not hasattr(self, 'debug_texts'):
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

            speed = m.hypot(self.velLeft, self.velUp)
            surface_type = "Normal"
            if self.currentMaxSpeed == self.gravelMaxSpeed:
                surface_type = "Gravel"
            elif self.currentMaxSpeed == self.iceMaxSpeed:
                surface_type = "Ice"

            texts = [
                f"Speed: {speed:.1f}",
                f"Rotation: {self.rotation:.1f}°",
                f"Surface: {surface_type}",
                f"Nitro: {self.nitroAmount}"
            ]

            base_y = self.rect.top - 70
            for i, text_obj in enumerate(self.debug_texts):
                text_obj.update_text(texts[i])
                text_obj.update_position(self.rect.centerx, base_y + i * 20)
                text_obj.render()

            wheel_radius = 15
            wheel_center = (self.rect.centerx-30, self.rect.top - 30)
            line_length = 12
            pygame.draw.circle(self.display.screen, (200, 200, 200), wheel_center, wheel_radius, 2)
            angle = m.radians(self.steer_rotation)
            line_end = (
                wheel_center[0] + line_length * m.cos(angle),
                wheel_center[1] - line_length * m.sin(angle)
            )
            pygame.draw.line(self.display.screen, (255, 40, 40), wheel_center, line_end, 2)
        else:
            if hasattr(self, 'debug_texts'):
                for text_obj in self.debug_texts:
                    text_obj.hidden = True
        # if self.display.game.enable_debug:
        #     self.placement.render()
    def render_model(self):
        self.center = self.rect.center
        if self.inviFlicker:
            pygame.draw.circle(self.display.screen, (102, 100, 100), self.center, 25)

        self.mask_image = self.car_mask.to_surface()
        self.car3d_sprite.render(self.display.screen, (self.x, self.y))

    def change_model(self, model):
        self.model = model
        if self.model == 1:
            self.image = images.car3d
            self.set_3d_parameters(self.model)
            self.car3d_sprite = stacked_sprite.StackedSprite(self.display, self.image, self.num_of_sprites, self.img_size,
                                                             self.car3d_height, isenemy=(not self.isPlayer))
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
            self.image = images.newcar
            self.set_3d_parameters(self.model)
            self.car3d_sprite = stacked_sprite.StackedSprite(self.display, self.image, self.num_of_sprites, self.img_size, self.car3d_height, isenemy=not self.isPlayer)
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
            self.image = images.bike
            self.set_3d_parameters(self.model)
            self.car3d_sprite = stacked_sprite.StackedSprite(self.display, self.image, self.num_of_sprites,
                                                             self.img_size, self.car3d_height, isenemy=not self.isPlayer)

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
            self.image = images.police
            self.set_3d_parameters(self.model)
            self.car3d_sprite = stacked_sprite.StackedSprite(self.display, self.image, self.num_of_sprites,
                                                             self.img_size, self.car3d_height, isenemy=not self.isPlayer)

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



        elif self.model == 5:
            self.image = images.plane
            self.set_3d_parameters(self.model)
            self.car3d_sprite = stacked_sprite.StackedSprite(self.display, self.image, self.num_of_sprites, self.img_size, self.car3d_height, collision=False, isenemy=(not self.isPlayer))
            self.backDifference = 0.65
            self.mass = 100
            self.nitroPower = 4 * self.display.game.calibration
            self.tireAmount = 0
            self.deadTires = 0
            self.tireDamage = 0

            self.normalAcceleration = 0.5 * self.display.game.calibration
            self.oilAcceleration = 0 * self.display.game.calibration
            self.iceAcceleration = 0.1 * self.display.game.calibration

            self.normalRotationSpeed = 0.03 * self.display.game.calibration
            self.gravelRotationSpeed = 0.018 * self.display.game.calibration

            self.normalMaxSpeed = 200 * self.display.game.calibration
            self.gravelMaxSpeed = 50 * self.display.game.calibration
            self.iceMaxSpeed = 300 * self.display.game.calibration

            self.normalFriction = 0
            self.iceFriction = 0
            self.oilFriction = 0

        back_wheel_offset = self.playerHeight / 2
        angle_rad = m.radians(-self.rotation)
        back_wheel_x_offset = m.cos(angle_rad) * back_wheel_offset
        back_wheel_y_offset = m.sin(angle_rad) * back_wheel_offset

        back_wheel1_x = self.x - back_wheel_x_offset - m.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel1_y = self.y - back_wheel_y_offset + m.cos(angle_rad) * (self.playerWidth / 2)
        back_wheel2_x = self.x - back_wheel_x_offset + m.sin(angle_rad) * (self.playerWidth / 2)
        back_wheel2_y = self.y - back_wheel_y_offset - m.cos(angle_rad) * (self.playerWidth / 2)
        if isinstance(self.display, app.display.game_display):
            self.backwheel1_pgen.edit(back_wheel1_x, back_wheel1_y, self.velLeft, self.velUp)
            self.backwheel2_pgen.edit(back_wheel2_x, back_wheel2_y, self.velLeft, self.velUp)
    def events(self, event):
        pass

    def movement(self):
        global dire
        if not self.stunned:
            if self.display.game.delta_time < self.bananaTime:
                self.bananaTime -= self.display.game.delta_time
                self.velAng = 13
            elif -self.display.game.delta_time > self.bananaTime:
                self.bananaTime += self.display.game.delta_time
                self.velAng = -13
            else:
                self.bananaTime = 0
            self.prevPos = [self.x, self.y]
            self.prevRotation = self.rotation
            self.x, self.y = self.next_x, self.next_y
            self.rotation = self.next_rotation
            c, d = self.velLeft, self.velUp
            if self.w and not self.in_oil:
                if self.WASD_steering:
                    self.velUp += self.currentAcceleration
                else:
                    a, b = self.get_acceleration_with_trigonometry(1,
                                                                   self.currentAcceleration * self.display.game.delta_time * self.display.game.calibration * self.tireHealth / 2)
                    self.velLeft += a
                    self.velUp += b
            if self.s and not self.in_oil:
                if self.WASD_steering:
                    self.velUp -= self.currentAcceleration
                else:
                    a, b = self.get_acceleration_with_trigonometry(-1,
                                                                   self.currentAcceleration * self.backDifference * self.display.game.delta_time * self.display.game.calibration * (
                                                                               self.tireHealth ** 0.5) / 2)
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
                self.steer_rotation -= 10 * self.steer_rotation * self.display.game.delta_time
            if abs(self.steer_rotation) < 0.01:
                self.steer_rotation = 0

            self.steer_rotation = max(self.min_steer_rotation, min(self.steer_rotation, self.max_steer_rotation))

            if self.WASD_steering:
                self.next_rotation += self.steer_rotation * self.display.game.delta_time * self.currentRotationSpeed * 2

            if self.boost and self.nitroAmount >= 1 and not self.WASD_steering:
                if not self.infiNitro:
                    self.nitroAmount -= 1
                a, b = self.get_acceleration_with_trigonometry(1, self.nitroPower)
                self.velLeft += a * self.display.game.delta_time * self.display.game.calibration
                self.velUp += b * self.display.game.delta_time * self.display.game.calibration

            magnitude = m.sqrt(self.velLeft ** 2 + self.velUp ** 2)
            dire = self.get_direction_with_trigonometry((self.x - self.archiveCords[0]), (self.y - self.archiveCords[1]))
            if not self.isPlayer and magnitude > 0 and not self.enemy_on_banana:
                self.rotation = dire
            if magnitude > self.currentFriction:
                modifier = magnitude / 200
                if modifier > 2:
                    modifier = 2
                if modifier < 0.2:
                    modifier = 0.2
                self.goingForward = self.check_if_forward(dire)
                if self.goingForward:
                    self.next_rotation += self.steer_rotation * self.display.game.delta_time * self.currentRotationSpeed * modifier
                else:
                    self.next_rotation -= self.steer_rotation * self.display.game.delta_time * self.currentRotationSpeed * modifier
            if magnitude > self.currentMaxSpeed:
                self.slow_down(0.1 + self.speedCorrection * (magnitude - self.currentMaxSpeed))
            if self.velLeft != 0 or self.velUp != 0:
                s = self.check_if_sideways(dire)
                self.slow_down(self.currentFriction * s / magnitude / (self.tireHealth ** 0.2))

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
            self.next_x -= self.velLeft * self.display.game.delta_time
            self.next_y -= self.velUp * self.display.game.delta_time
            self.delta_x, self.delta_y = self.next_x - self.x, self.next_y - self.y
            self.next_rotation += m.degrees(self.velAng * self.display.game.delta_time)
            self.velAng *= self.damping


    def get_distance_to_nearest_checkpoint(self):
        try:
            if self.current_checkpoint + 1 == self.display.amount_of_checkpoints:
                x1, y1 = self.display.checkpoints[0].start_pos
                x2, y2 = self.display.checkpoints[0].end_pos
            else:
                x1, y1 = self.display.checkpoints[self.current_checkpoint + 1].start_pos
                x2, y2 = self.display.checkpoints[self.current_checkpoint + 1].end_pos

            segment_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
            if segment_length_sq == 0:
                return m.dist(self.display.checkpoints[0].start_pos, (self.x, self.y))

            t = ((self.x - x1) * (x2 - x1) + (self.y - y1) * (y2 - y1)) / segment_length_sq


            t = max(0, min(1, t))

            closest_x = x1 + t * (x2 - x1)
            closest_y = y1 + t * (y2 - y1)


            return m.dist((closest_x, closest_y), (self.x, self.y))
        except Exception as e:
            print(f"Error in function: {e}")




    def use_powerup(self):
        if len(self.inventory) == 0:
            return
        if self.inventory[0] == 1:
            pass
            self.display.game.sound_manager.play_sound('Strength')

            self.strength = True
        elif self.inventory[0] == 2:
            angle = m.radians(self.rotation)
            spawn_x = self.x - (50 * m.cos(angle))
            spawn_y = self.y + (50 * m.sin(angle))
            self.display.obstacles.append(obstacle.Obstacle(self.display, spawn_x, spawn_y, 'barrier', self.rotation - 90))
        elif self.inventory[0] == 3:
            angle = m.radians(self.rotation)
            spawn_x = self.x - (50 * m.cos(angle))
            spawn_y = self.y + (50 * m.sin(angle))
            self.display.obstacles.append(obstacle.Obstacle(self.display, spawn_x, spawn_y, 'spikes', self.rotation - 90))
        elif self.inventory[0] == 4:
            if self.deadTires > 0:
                self.deadTires -= 1
                self.tireHealth += self.tireDamage
                self.display.game.sound_manager.play_sound('Heal')
        self.inventory.pop(0)


    def slow_down(self, slowdown):
        self.velLeft -= self.velLeft * slowdown * self.display.game.delta_time * self.display.game.calibration
        self.velUp -= self.velUp * slowdown * self.display.game.delta_time * self.display.game.calibration

    def get_acceleration_with_trigonometry(self, direction, acc):
        if direction == 1:
            r = m.radians(self.next_rotation)
        else:
            r = m.radians(self.next_rotation - 180)

        x = m.cos(r)
        y = m.sin(r)
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
            tan = m.inf

        rads = m.atan(tan)
        degs = int(m.degrees(rads))

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
        a = False
        if r < max and min < r:
            a = True
        else:
            if min < 0:
                if r < max + 360 and min + 360 < r:
                    a = True
            elif max > 360:
                if r < max - 360 and min - 360 < r:
                    a = True
        return a

    def check_if_sideways(self, dire):
        if self.model == 3:
            return 1
        if dire >= 360:
            dire -= 360

        r = self.normalize_angle(self.rotation)

        forward_diff = (dire - r) % 360
        backward_diff = (r - dire) % 360

        if forward_diff > 180:
            forward_diff = 360 - forward_diff

        if backward_diff > 180:
            backward_diff = 360 - backward_diff

        if (forward_diff > 45 and forward_diff < 135) or (backward_diff > 45 and backward_diff < 135):
            return 1.5

        return 1

    def normalize_angle(self, angle):
        while angle <= 0:
            angle += 360
        while angle > 360:
            angle -= 360
        return angle

    def loop(self):
        self.movement()
        self.invincibility -= 5 * self.display.game.delta_time
        if self.isPlayer:
            self.name = self.display.p.player_name
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

        self.bounce_sound_timer -= self.display.game.delta_time

        for car in self.recentCollisions:
            if self.recentCollisions[car] != 0 and not self.collision_detection(car.car_mask, car.rect.topleft[0] + car.delta_x, car.rect.topleft[1] + car.delta_y):
                if pygame.time.get_ticks() - self.recentCollisions[car] > self.bumpingCooldown:
                    self.recentCollisions[car] = 0

        if self.strength and self.isPlayer:
            self.particle_system.add_particle(self.x, self.y, random.randint(-10, 10), random.randint(-10, 10), 0, 0, 0,
                                              0, 10, 50, 2, (150), (150),
                                              (100), (255), 'square')

        if self.wallCollTime != 0 and not self.wall:
            if pygame.time.get_ticks() - self.wallCollTime > self.wallCollisionCooldown:
                self.wallCollTime = 0



        self.currentMaxSpeed = self.normalMaxSpeed
        self.currentAcceleration = self.normalAcceleration
        self.currentRotationSpeed = self.normalRotationSpeed
        self.currentFriction = self.normalFriction
        self.in_oil = False

        self.car_mask = self.car3d_sprite.update_mask_rotation(int(self.rotation))
        self.rect = self.car3d_sprite.rect
        self.rect.center = self.x, self.y

        self.wall = False
        if self.collision_detection(self.display.mapMask, 0, 0):
            self.check_color(self.display.mapMask, 0, 0)
        else:
            self.particle_color = (100, 100, 100)
            self.backwheel1_pgen.edit(red=self.particle_color[0], green=self.particle_color[1],blue=self.particle_color[2])
            self.backwheel2_pgen.edit(red=self.particle_color[0], green=self.particle_color[1],blue=self.particle_color[2])

        self.barrier = False
        for obstacle in self.display.obstacles:
            if self.collision_detection(obstacle.obstacle_mask, obstacle.rect.topleft[0], obstacle.rect.topleft[1]):
                if obstacle.type == 1 and self.isPlayer:
                    if self.prickWheels():
                        obstacle.destroy()
                elif obstacle.type == 2:
                    self.barrier = True
                    self.next_x, self.next_y, self.x, self.y = self.archiveBarrier[-1][0], self.archiveBarrier[-1][1], \
                    self.archiveBarrier[-2][0], self.archiveBarrier[-2][1]
                    self.next_rotation, self.rotation = self.archiveBarrier[-1][2], self.archiveBarrier[-2][2]
                    self.velUp *= -0.5
                    self.velLeft *= -0.5
                elif obstacle.type == 3 and not obstacle.falling and self.isPlayer:
                    self.bananaTime = 0.91 * random.choice((1, -1))
                    obstacle.destroy()
                    self.display.hasBanana = 1
                    self.display.game.sound_manager.play_sound('Banana')

                elif obstacle.type == 4:
                    self.barrier = True
                    self.next_x, self.next_y, self.x, self.y = self.archiveBarrier[-1][0], self.archiveBarrier[-1][1], \
                    self.archiveBarrier[-2][0], self.archiveBarrier[-2][1]
                    self.next_rotation, self.rotation = self.archiveBarrier[-1][2], self.archiveBarrier[-2][2]
                    self.velUp *= -0.5
                    self.velLeft *= -0.5
                    elapsed = time.time() - obstacle.start_time
                    if elapsed < 0.15:
                        self.x -= 20
                        self.barrier = False
                elif obstacle.type == 5:
                    self.currentMaxSpeed = self.gravelMaxSpeed
                elif obstacle.type == 7:


                    if self.isPlayer:
                        self.display.game.sound_manager.play_sound('coin')
                        self.display.coiny +=1
                        obstacle.destroy()

        self.car = False
        for c in self.display.cars:
            if not self == c and c in self.recentCollisions:
                if self.collision_detection(c.car_mask, c.rect.topleft[0] + c.delta_x, c.rect.topleft[1] + c.delta_y):
                    self.car = True
                    self.collision_render(c.car_mask, c.rect.topleft[0] + c.delta_x, c.rect.topleft[1] + c.delta_y)
                    if self.recentCollisions[c] == 0:
                        self.handle_bumping(c)
                        self.push_away_from_closest_enemy(c)
                        self.recentCollisions[c] = pygame.time.get_ticks()
                        c.recentCollisions[self] = pygame.time.get_ticks()

        if not self.wall:
            self.wall_frames = 0
            self.archiveWall.append([self.x, self.y, self.rotation])
            if len(self.archiveWall) > self.last_frames_len:
                self.archiveWall.pop(0)
        else:
            self.wall_frames += 1
            if self.wall_frames > 10:
                self.push_away_from_closest_wall()

        if not self.car:
            self.archiveCars.append([self.x, self.y, self.rotation])
            if len(self.archiveCars) > self.last_frames_len:
                self.archiveCars.pop(0)

        if not self.barrier:
            self.archiveBarrier.append([self.x, self.y, self.rotation])
            if len(self.archiveBarrier) > 10:
                self.archiveBarrier.pop(0)

    def prickWheels(self):
        if self.invincibility < 1 and self.deadTires < self.tireAmount:
            self.invincibility = 20
            self.deadTires += 1
            self.hits += 30
            self.tireHealth -= self.tireDamage
            self.display.game.sound_manager.play_sound('Boom')
            return True
        else:
            return False

    def countPoints(self):

        p = self.display.leaderboard_list.index(self) + 1
        t = self.full_time
        o = self.hits
        l = self.perfectLaps
        u = self.pupscollected
        return 100 * (5 - p) + 5 * (100 - t) - o + 100 * l + 10 * u

    def detect_collision_area(self, mask, x, y):
        xs, ys = [], []
        offset = (x - (self.rect.topleft[0] + self.delta_x), y - (self.rect.topleft[1] + self.delta_y))
        sharedMask = self.car_mask.overlap_mask(mask, offset)
        sharedSurface = sharedMask.to_surface(setcolor=(0, 200, 0))
        sharedSurface.set_colorkey((0, 0, 0))
        for x in range(sharedSurface.get_width()):
            for y in range(sharedSurface.get_height()):
                if sharedSurface.get_at((x, y))[1] == 200:
                    xs.append(x + self.rect.topleft[0] + self.delta_x)
                    ys.append(y + self.rect.topleft[1] + self.delta_y)

        if xs and ys:
            center_x = sum(xs) // len(xs)
            center_y = sum(ys) // len(ys)
            return center_x, center_y
        return None, None

    def compute_wall_normal(self, center_x, center_y):
        width, height = self.display.block_width, self.display.block_height
        grid_size = 5
        offset = grid_size // 2

        map_width = len(self.display.map[0])
        map_height = len(self.display.map)
        map_x = int(center_x // width)
        map_y = int(center_y // height)

        if map_x <= 0:
            return (1, 0), (0, 1)
        if map_x >= map_width - 1:
            return (-1, 0), (0, 1)
        if map_y <= 0:
            return (0, 1), (1, 0)
        if map_y >= map_height - 1:
            return (0, -1), (1, 0)

        total_x, total_y = 0, 0
        count = 0

        for dy in range(-offset, offset + 1):
            for dx in range(-offset, offset + 1):
                check_x = map_x + dx
                check_y = map_y + dy

                if 0 <= check_y < map_height and 0 <= check_x < map_width:
                    if self.display.map[check_y][check_x] == 1:
                        total_x += dx
                        total_y += dy
                        count += 1

        if count == 0:
            return (0, 1), (-1, 0)

        avg_x = total_x / count
        avg_y = total_y / count

        normal_length = (avg_x ** 2 + avg_y ** 2) ** 0.5

        if normal_length < 1e-5:
            if abs(total_x) > abs(total_y):
                normal = (1, 0) if total_x > 0 else (-1, 0)
            else:
                normal = (0, 1) if total_y > 0 else (0, -1)
        else:
            normal = (avg_x / normal_length, avg_y / normal_length)

        tangent = (-normal[1], normal[0])

        return normal, tangent

    def improved_wall_collision(self, mask, x, y):
        center_x, center_y = x, y
        if center_x is None or center_y is None:
            return

        normal, tangent = self.compute_wall_normal(center_x, center_y)

        v1n = self.velLeft * normal[0] + self.velUp * normal[1]
        v1t = self.velLeft * tangent[0] + self.velUp * tangent[1]

        if abs(v1n) > abs(v1t):
            v1n_new = -v1n * 0.6
        else:
            v1n_new = -v1n * 0.15

        self.velLeft = (v1n_new * normal[0] + v1t * tangent[0] * 0.7) * 0.9
        self.velUp = (v1n_new * normal[1] + v1t * tangent[1] * 0.7) * 0.9

        r = (self.next_x - center_x, self.next_y - center_y)
        delta_px = self.mass * self.velLeft
        delta_py = self.mass * self.velUp
        L = r[0] * delta_py - r[1] * delta_px
        d = (r[0] ** 2 + r[1] ** 2) ** 0.5
        I = (1 / 12) * self.mass * (self.playerWidth ** 2 + self.playerHeight ** 2) + self.mass * d ** 2

        self.velAng = -L / I


    def teleport(self, coords):
        if self.isPlayer and self.display.game.enable_debug:
            self.next_x = coords[0]
            self.next_y = coords[1]



    def handle_bumping(self, other):
        dx = other.next_x - self.next_x
        dy = other.next_y - self.next_y
        distance = m.sqrt(dx ** 2 + dy ** 2)
        if distance == 0:
            return "GET OUT"

        coll_x, coll_y = self.get_coordinates(other.car_mask, other.rect.topleft[0] + other.delta_x, other.rect.topleft[1] + other.delta_y)
        r_self = (coll_x - self.next_x, coll_y - self.next_y)
        r_other = (coll_x - other.next_x, coll_y - other.next_y)
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


        n = ((other.next_x - self.next_x) / m.sqrt((other.next_x - self.next_x) ** 2 + (other.next_y - self.next_y) ** 2), (other.next_y - self.next_y) / m.sqrt((other.next_x - self.next_x) ** 2 + (other.next_y - self.next_y) ** 2))
        t = (-n[1], n[0])
        v1n = self.velLeft * n[0] + self.velUp * n[1]
        v1t = self.velLeft * t[0] + self.velUp * t[1]
        v2n = other.velLeft * n[0] + other.velUp * n[1]
        v2t = other.velLeft * t[0] + other.velUp * t[1]

        v1n_new = (v1n * (self.mass - other.mass) + 2 * other.mass * v2n) / (self.mass + other.mass)
        v2n_new = (v2n * (other.mass - self.mass) + 2 * self.mass * v1n) / (self.mass + other.mass)

        v1 = (v1n_new * n[0] + v1t * t[0], v1n_new * n[1] + v1t * t[1])
        v2 = (v2n_new * n[0] + v2t * t[0], v2n_new * n[1] + v2t * t[1])
        if not self.strength:
            self.velLeft, self.velUp, self.velAng = v1[0], v1[1], omega_A
        else:
            self.strength = False

        if not other.strength:
             other.velLeft, other.velUp, other.velAng = v2[0], v2[1], omega_B
        else:
            other.strength = False

    def collision_detection(self, mask, x, y):
        offset = (x - (self.rect.topleft[0] + self.delta_x), y - (self.rect.topleft[1] + self.delta_y))
        return self.car_mask.overlap(mask, offset)

    def get_coordinates(self, mask, x, y):
        xs = []
        xy = []
        offset = (x - (self.rect.topleft[0] + self.delta_x), y - (self.rect.topleft[1] + self.delta_y))
        sharedMask = self.car_mask.overlap_mask(mask, offset)
        sharedSurface = sharedMask.to_surface(setcolor=(0, 200, 0))
        sharedSurface.set_colorkey((0, 0, 0))
        for x in range(sharedSurface.get_size()[0]):
            for y in range(sharedSurface.get_size()[1]):
                if sharedSurface.get_at((x, y))[1] == 200:
                    xs.append(x + self.rect.topleft[0] + self.delta_x)
                    xy.append(y + self.rect.topleft[1] + self.delta_y)
        return sum(xs) // len(xs), sum(xy) // len(xy)

    def collision_render(self, mask, x, y):

        offset = (x - (self.rect.topleft[0] + self.delta_x), y - (self.rect.topleft[1] + self.delta_y))
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
        offset = (x - (self.rect.topleft[0] + self.delta_x), y - (self.rect.topleft[1] + self.delta_y))
        sharedMask = self.car_mask.overlap_mask(mask, offset)
        sharedSurface = sharedMask.to_surface(setcolor=(0, 200, 0))
        sharedSurface.set_colorkey((0, 0, 0))
        size = sharedSurface.get_size()
        wall_count = 0

        self.currentMaxSpeed = self.normalMaxSpeed
        self.currentRotationSpeed = self.normalRotationSpeed
        self.currentAcceleration = self.normalAcceleration
        self.currentFriction = self.normalFriction
        self.in_oil = False

        for x in range(size[0]):
            for y in range(size[1]):
                if sharedSurface.get_at((x, y))[1] == 200:
                    yy = int((self.rect.topleft[1] + y + self.delta_y) // self.display.block_height)
                    xx = int((self.rect.topleft[0] + x + self.delta_x) // self.display.block_width)
                    if yy >= len(self.display.map):
                        yy = len(self.display.map) - 1
                    elif yy < 0:
                        yy = 0

                    if xx >= len(self.display.map[0]):
                        xx = len(self.display.map[0]) - 1
                    elif xx < 0:
                        xx = 0

                    tile = self.display.map[yy][xx]
                    if tile == 2:
                        self.currentAcceleration = self.oilAcceleration
                        self.currentFriction = self.oilFriction
                        self.in_oil = True
                        self.steer_rotation = 0
                        self.particle_color = self.oil_color
                        self.backwheel1_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                        self.backwheel2_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                    elif tile == 1:
                        self.wall = True
                        wall_count += 1
                        self.hits += 1
                        self.perfectLap = False
                        self.backwheel1_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])
                        self.backwheel2_pgen.edit(red=self.particle_color[0], green=self.particle_color[1], blue=self.particle_color[2])

                        if self.wallCollTime == 0:
                            center_x, center_y = self.detect_collision_area(mask, 0, 0)
                            if center_x and center_y:
                                self.improved_wall_collision(mask, int(center_x), int(center_y))
                            if self.isPlayer and self.bounce_sound_timer <= 0:
                                self.bounce_sound_timer = 0.3
                                self.display.game.sound_manager.play_sound('bounce')
                                self.strength = False
                            self.push_away_from_closest_wall()
                            self.wallCollTime = pygame.time.get_ticks()


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
                        if not self.isPlayer:
                            self.enemy_spike_wheel = True
                        else:
                            self.prickWheels()
                    elif tile == 6:
                        while self.deadTires > 0:
                            self.display.game.sound_manager.play_sound('Pitstop')
                            self.deadTires -= 1
                            self.tireHealth += self.tireDamage


    def find_closest_wall(self):
        for x in range(self.rect.topleft[0], self.rect.bottomright[0]):
            for y in range(self.rect.topleft[1], self.rect.bottomright[1]):
                yy = int((y + self.delta_y) // self.display.block_height)
                xx = int((x + self.delta_x) // self.display.block_width)
                if self.display.map[yy][xx] == 1:
                    return x, y
        return None, None

    def push_away_from_closest_wall(self, power=0.1):
        x, y = self.find_closest_wall()
        if x is not None and y is not None:
            back = 1
            self.next_x, self.next_y = self.archiveWall[-back][0], self.archiveWall[-back][1]
            self.next_rotation = self.archiveWall[-back][2]
            self.next_x += (self.x - x) * power
            self.next_y += (self.y - y) * power

    def push_away_from_closest_enemy(self, enemy):
        if enemy is not None:
            back = 1
            self.next_x, self.next_y = self.archiveCars[-back][0], self.archiveCars[-back][1]
            enemy.next_x, enemy.next_y = enemy.archiveCars[-back][0], enemy.archiveCars[-back][1]
            self.next_rotation = self.archiveCars[-back][2]
            enemy.next_rotation = enemy.archiveCars[-back][2]
            self.next_x += (self.x - enemy.x) * 0.1
            enemy.next_x += (enemy.x - self.x) * 0.1
            self.next_y += (self.y - enemy.y) * 0.1
            enemy.next_y += (enemy.y - self.y) * 0.1

    def start_race(self):
        self.begining_lap_time = time.time()

    def end_race(self, after_player=False):
        if not self.finished:
            if self.isPlayer:
                self.finished = True
            elif after_player ==  False:
                self.finished = True
            self.full_time = sum(self.lap_times)
            self.points = self.countPoints()
            self.display.leaderboard_list.remove(self)
            self.display.placements.append(self)