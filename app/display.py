import copy
import time
from configparser import ConfigParser
import cv2
import numpy
import sqlite3

from app.database import DatabaseManager
from customObjects import custom_images, custom_text, custom_button
from jeff_the_objects.slider import Slider
from jeff_the_objects.stacked_sprite import StackedSprite
from app.config import read_config, write_config_to_file
import random
import math as m
import pygame
import json
from app import car, enemy, obstacle, images, player, enemy, checkpoint, hotbar, powerup, scoreboard
from particle_system import ParticleSystem
from datetime import datetime
import os
import json

class basic_display:
    def __init__(self, game):
        self.game = game
        self.map_dir = self.game.map_dir
        self.screen = self.game.screen
        self.screenWidth, self.screenHeight = self.game.width, self.game.height
        self.objects = []
        self.objects_in_memory = 0
        self.bgColor = (26,26,26)
        self.gravel_color = (128, 128, 128)
        self.oil_color = (235, 180, 3)
        self.asphalt_color = (26,26,26)
        self.wall_color = (255, 255, 255)
        self.ice_color = (63, 208, 212)
        self.spike_color = (255, 0, 0)
        self.pitstop_color = (50, 50, 200)

        self.db_manager = game.db_manager

        self.color_map = {
            0: self.asphalt_color,
            1: self.wall_color,
            2: self.oil_color,
            3: self.gravel_color,
            4: self.ice_color,
            5: self.spike_color,
            6: self.pitstop_color,
            'c': (0, 255, 0),
            'm': (255, 0, 0)
        }

        self.map_data = {
            'version': self.game.version,
            'map': [],
            'player': [[100, 100], 0],
            'enemies': [],
            'checkpoints': [],
            'powerups': [],
            'coin': 'None',
            'bananas': [],
            'barriers': [],
            'speedBumps': [],
            'guideArrows': [],
            'bramas': [],
            'laps': 5
        }


        self.loading_error = custom_text.Custom_text(self, self.game.width/2, self.game.height/2, 'Error, no display found!', text_color='white')
        self.loading_error.hidden = True


    def render(self):
        for obj in self.objects:
            obj.render()

    def events(self, event):
        for obj in self.objects:
            obj.events(event)

    def mainloop(self):
        self.loading_error.hidden = False


class game_display(basic_display):
    def __init__(self, game, difficulty):
        basic_display.__init__(self, game)
        self.difficulty = difficulty
        self.diff = difficulty


        self.hotbar = hotbar.Hotbar(self)
        self.screenHeight_without_hotbar = self.screenHeight - self.hotbar.h

        self.obstacles = []
        self.import_map()
        self.amount_of_checkpoints = len(self.checkpoints)

        self.wong_way = False
        self.wong_way_image = custom_images.Custom_image(self, 'images/wong_way.png', self.game.width/2, self.game.height/8, 100, 96, append=False)

        self.cars = []


        self.particle_system = ParticleSystem()
        self.placement_variance = 10
        self.deadPowerups = []
        self.deadBramas = []
        self.hasBanana = 1
        self.banana = None

        self.mnoznikcoinow = 1.0

        self.coiny = 0

        self.paused = False
        self.pause_start_time = 0

        self.started_race = False


        self.snow_timer = 0
        self.snowing = False

        self.p = player.Player(self, self.player_position, self.player_rotation, self.game.player_model)


        self.placements = []
        self.hotbar.after_player_setup()
        for i, e in enumerate(self.enemies):
            enemy.Enemy(self, e[0], e[1], 1, player = self.p, SubClass=i, name=f'Enemy {i+1}')

        self.leaderboard_list = list(sorted(self.cars, key=lambda car: (
        -car.lap, -car.current_checkpoint, car.get_distance_to_nearest_checkpoint())))

        self.map_surface = pygame.Surface((self.game.width, self.screenHeight_without_hotbar))
        self.img_map_surface = pygame.Surface((self.game.width, self.screenHeight_without_hotbar))

        self.draw_map()
        self.map_surface.set_colorkey(self.bgColor)
        self.mapMask = pygame.mask.from_surface(self.map_surface)

    def add_snow_particles(self):
        for _ in range(30):
            x = random.randint(0, self.game.width)
            y = random.randint(-50, 10)

            vel_x = random.uniform(-0.5, 0.5)
            vel_y = random.uniform(0.5, 2)

            acc_x = 0
            acc_y = 0.05

            ang_vel = 0
            ang_acc = 0

            size = random.randint(2, 6)
            lifetime = 690

            speed = 100

            r = random.randint(200, 255)
            g = random.randint(200, 255)
            b = random.randint(240, 255)
            alpha = random.randint(200, 250)

            shape = 'circle'

            self.particle_system.add_particle(x, y, vel_x, vel_y, acc_x, acc_y,
                                              ang_vel, ang_acc, speed, lifetime, size,
                                              r, g, b, alpha, shape)

    def check_particle_collision(self, particle):
        if particle.x < 0 or particle.x > self.game.width or particle.y < 0 or particle.y > self.screenHeight_without_hotbar:
            return True
        overlap_point = self.mapMask.overlap(particle.mask, (particle.x, particle.y))
        if overlap_point:
            self.overlap_point = overlap_point
            if self.map_surface.get_at(overlap_point)[:3] == self.wall_color:
                return True
        return False

    def draw_map(self):
        if self.difficulty == "Finished_Level_1":
            self.img_map_surface.blit(images.mapone, (0, 0))

        elif self.difficulty == "Finished_Level_2":
            self.img_map_surface.blit(images.maptwo, (0, 0))

        elif self.difficulty == "Finished_Level_3":
            self.img_map_surface.blit(images.mapthree, (0, 0))

        else:
            self.img_map_surface = None
        self.map_surface.fill(self.bgColor)
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x] == 0:
                    continue
                elif self.map[y][x] == 1:
                    color = self.wall_color
                elif self.map[y][x] == 2:
                    color = self.oil_color
                elif self.map[y][x] == 3:
                    color = self.gravel_color
                elif self.map[y][x] == 4:
                    color = self.ice_color
                elif self.map[y][x] == 5:
                    color = self.spike_color
                elif self.map[y][x] == 6:
                    color = self.pitstop_color
                else:
                    color = self.asphalt_color
                if self.map[y][x] in (0, 1, 3, 4, 5):
                    color = (
                        min(max(color[0] + random.randint(-10, 10), 0), 255),
                        min(max(color[1] + random.randint(-10, 10), 0), 255),
                        min(max(color[2] + random.randint(-10, 10), 0), 255)
                    )

                pygame.draw.rect(self.map_surface, color,
                                 (x * self.block_width, y * self.block_height, self.block_width, self.block_height))
        if not self.img_map_surface:
            self.img_map_surface = pygame.Surface((self.game.width, self.screenHeight_without_hotbar))
            self.img_map_surface.fill(self.bgColor)
            for y in range(len(self.map)):
                for x in range(len(self.map[y])):
                    if self.map[y][x] == 0:
                        continue
                    elif self.map[y][x] == 1:
                        color = self.wall_color
                    elif self.map[y][x] == 2:
                        color = self.oil_color
                    elif self.map[y][x] == 3:
                        color = self.gravel_color
                    elif self.map[y][x] == 4:
                        color = self.ice_color
                    elif self.map[y][x] == 5:
                        color = self.spike_color
                    elif self.map[y][x] == 6:
                        color = self.pitstop_color
                    else:
                        color = self.asphalt_color
                    if self.map[y][x] in (0, 1, 3, 4, 5):
                        color = (
                            min(max(color[0] + random.randint(-10, 10), 0), 255),
                            min(max(color[1] + random.randint(-10, 10), 0), 255),
                            min(max(color[2] + random.randint(-10, 10), 0), 255)
                        )

                    pygame.draw.rect(self.img_map_surface, color,
                                     (x * self.block_width, y * self.block_height, self.block_width, self.block_height))

    def import_map(self):
        with open(f"{self.game.map_dir}/{self.difficulty}.json", 'r') as f:
            map_data = json.load(f)
            self.player_position = [100, 100]
            self.player_rotation = 0
            self.map_data.update(map_data)
            self.map = self.map_data['map']

            self.block_width = self.game.width // len(self.map[0])
            self.block_height = (self.screenHeight_without_hotbar) // len(self.map)

            player_info = self.map_data.get('player')

            self.player_position = player_info[0]
            self.player_rotation = player_info[1]

            temp_list_of_checkpoints = self.map_data['checkpoints']
            self.checkpoints = []
            for i, chekpoint in enumerate(temp_list_of_checkpoints):
                self.checkpoints.append(checkpoint.checkpoint(self, i, chekpoint[0], chekpoint[1]))

            temp_list_of_powerups =self.map_data['powerups']
            self.powerups = []

            for i, pup in enumerate(temp_list_of_powerups):
                self.powerups.append(powerup.Powerup(pup[0], pup[1], self))

            self.bananas = self.map_data['bananas']

            self.coin = self.map_data['coin']
            if self.coin == "None":
                self.hasCoin = 1
            else:
                self.hasCoin = 0
            temp_list_of_bramas = self.map_data['bramas']
            for i, br in enumerate(temp_list_of_bramas):
                self.obstacles.append(obstacle.Obstacle(self, br[0], br[1], "brama", br[2]))

            temp_list_of_speedBumps = self.map_data['speedBumps']
            for i, sb in enumerate(temp_list_of_speedBumps):
                self.obstacles.append(obstacle.Obstacle(self, sb[0], sb[1], "speedBump", sb[2]))

            temp_list_of_guideArrows = self.map_data['guideArrows']
            for i, sb in enumerate(temp_list_of_guideArrows):
                self.obstacles.append(obstacle.Obstacle(self, sb[0], sb[1], "guideArrow", sb[2]))
            self.enemies = self.map_data['enemies']

            self.laps = self.map_data['laps']
            f.close()


    def render(self):
        self.screen.fill(self.bgColor)
        self.screen.blit(self.map_surface, (0, 0))
        self.screen.blit(self.img_map_surface, (0, 0))

        for o in self.obstacles:
            o.render()
        for obj in self.objects:
            obj.render()



        for pupo in self.powerups:
            pupo.render()
        if self.game.debug:
            for chpo in self.checkpoints:
                chpo.render()



            if hasattr(self, 'overlap_point') and self.overlap_point:
                pygame.draw.circle(self.screen, (255, 0, 0), self.overlap_point, 5)

        if self.wong_way:
            self.wong_way_image.render()
        self.particle_system.draw(self.screen)


    def events(self, event):
        for obj in self.objects:
            obj.events(event)
        for o in self.obstacles:
            o.events(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                 self.paused = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if 0 < pygame.mouse.get_pos()[0] < self.screenWidth and 0 < pygame.mouse.get_pos()[1] < self.screenHeight_without_hotbar:
                self.p.teleport(pygame.mouse.get_pos())


    def mainloop(self):
        if self.paused == True:
            self.paused = 3
            self.pause_start_time = time.time()
            self.game.current_display = self.game.displays['pause_display']

        elif self.paused == 3:
            time_offset_caused_by_pause = time.time() - self.pause_start_time
            for car in self.cars:
                car.begining_lap_time += time_offset_caused_by_pause

            self.hotbar.stopwatch.start_time += time_offset_caused_by_pause
            self.hotbar.stopwatch2.start_time += time_offset_caused_by_pause
            self.paused = 0



        if self.started_race == False:
            for car in self.cars:
                car.start_race()
            self.started_race = True

        self.snow_timer += self.game.delta_time
        if self.snow_timer >= 10.0:
            if self.difficulty == "Finished_Level_3":
                if self.snowing:
                    self.snowing = False
                else:
                    self.snowing = True
            self.snow_timer = 0

        if self.snowing:
            self.add_snow_particles()

        if self.hotbar.stopwatch.start_time == 0:
            self.hotbar.start_counting_time()

        self.update_standings()
        self.hotbar.mainloop()
        self.p.get_distance_to_nearest_checkpoint()
        if len(self.deadPowerups) > 0:
            for p in self.deadPowerups:
                if p[2] > 0:
                    p[2] -= self.game.delta_time
                else:
                    self.powerups.append(powerup.Powerup(p[0], p[1], self))
                    self.deadPowerups.remove(p)
        if len(self.deadBramas) > 0:
            for p in self.deadBramas:
                if p[2] > 0:
                    p[2] -= self.game.delta_time
                else:
                    self.obstacles.append(obstacle.Obstacle(self, p[0], p[1], "brama", p[3]))
                    self.deadBramas.remove(p)

        if self.p.stunned and time.time() - self.p.stunned_timer >= 1:
            self.p.stunned = False

        self.particle_system.update(self.game.delta_time)

        for particle in self.particle_system.particles:
            if self.check_particle_collision(particle):
                self.particle_system.particles.remove(particle)
        for c in self.cars:
            c.loop()




        for chpo in self.checkpoints:
            chpo.collision()

        for pupo in self.powerups:
            pupo.update()

        if self.hasBanana > 0:
            self.hasBanana -= self.game.delta_time
        elif len(self.bananas) > 0 and self.banana == None:
            a = random.choice(self.bananas)
            self.banana = obstacle.Obstacle(self, a[0], a[1], 'banana')
            self.obstacles.append(self.banana)



    def update_player_model(self, model):
        self.p.change_model(model)
        self.hotbar.undercarge.update()


    def update_standings(self):
        self.leaderboard_list = sorted(self.leaderboard_list, key=lambda car: (-car.lap, -car.current_checkpoint, car.get_distance_to_nearest_checkpoint()))

    def end_race(self):
        self.game.db_manager.add_time(self.p.player_name, self.difficulty, sum(self.p.lap_times), min(self.p.lap_times))

        for car in self.cars:
            car.end_race(after_player=True)

        self.player_placement = self.placements.index(self.p)

        kolejnymnoznik = int(self.difficulty[-1])

        if self.player_placement == 0:
            self.mnoznikcoinow = 5.0*kolejnymnoznik
        elif self.player_placement == 1:
            self.mnoznikcoinow = 3.0*kolejnymnoznik
        elif self.player_placement ==2:
            self.mnoznikcoinow = 2.0*kolejnymnoznik
        else:
            self.mnoznikcoinow = 1.0*kolejnymnoznik

        self.game.db_manager.add_coins(int(self.mnoznikcoinow * self.coiny))


        self.game.displays['leaderboard'].leaderboard_list = self.placements
        self.game.displays['leaderboard'].coin = self.coiny * self.mnoznikcoinow
        self.game.displays['leaderboard'].update_placements()
        self.game.change_display('leaderboard')



class map_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        self.cx, self.cy = 0.0, 0.0
        self.zoom_level = 1.0
        self.tool = 1
        self.shape = 1 # 0 is square, 1 is circle

        self.height = 5/6*self.game.height

        self.player_position = None
        self.player_rotation = 0
        self.player_width_blocks = 10
        self.player_height_blocks = 4

        self.temp_map_data = dict(self.map_data)

        self.gcd = 5
        self.temp_width = self.game.width // self.gcd
        self.temp_height = int(self.height // self.gcd)
        self.map = [[0] * self.temp_width for _ in range(self.temp_height)]

        self.angle = 0

        self.archiveStates = []
        self.archiveStates.append(copy.deepcopy(self.map))

        self.block_width = float(self.gcd)
        self.block_height = float(self.gcd)

        self.enemies = []
        self.enemy_rotation = 0

        self.laps = 5

        self.brush_size = 30
        self.dragging = False

        self.checkpoints = []
        self.current_checkpoint = []

        self.powerups = []
        self.bananas = []
        self.bramas = []
        self.speedBumps = []
        self.guideArrows = []
        self.coin = None


        self.brushtext = custom_text.Custom_text(self, 10, 70, f'Brush size: {self.brush_size}', text_color='white', font_height=30, center=False)
        self.tooltext = custom_text.Custom_text(self, 10, 100, f'Tool: {self.tool}  Angle: {self.angle}', text_color='white', font_height=30, center=False)

        custom_text.Custom_text(self, 10, 160, f'Laps:', text_color='white', font_height=30, center=False)

        self.lapstext = custom_text.Custom_text(self, 250, 160, f'{self.laps}', text_color='white', font_height=30, center=False)
        custom_button.Button(self, 'substract_lap', 150, 160, 70, 35, (16, 16, 16), text='-', text_color='white', outline_color='white', outline_width=2, border_radius=3)
        custom_button.Button(self, 'add_lap', 300, 160, 70, 35, (16, 16, 16), text='+', text_color='white',
                             outline_color='white', outline_width=2, border_radius=3)


        self.player_pos_text = custom_text.Custom_text(self, 10, 220, f'Player position: {self.player_position}',
                                                       text_color='white', font_height=30, center=False)
        self.cursor_pos_text = custom_text.Custom_text(self, 10, 250, f'Cursor position: (0, 0)',
                                                       text_color='white', font_height=30, center=False)

        self.export_button = custom_button.Button(self, "export_map", 10, 10, 100, 50, text="Export map", text_color=(0, 255, 0), color=(255, 0, 0), border_radius=0)
        self.export_png_button = custom_button.Button(self, "export_png", 120, 10, 100, 50, text="Export PNG",
                    text_color=(0, 255, 0), color=(26, 26, 26),
                    outline_color=(50, 50, 50), outline_width=2)

        self.dragging = False
        self.start_x = 0
        self.start_y = 0
        self.start_cx = 0
        self.start_cy = 0


        self.noplayertext = custom_text.Custom_text(self, self.game.width/2, self.height/20, 'No player position set!', text_color='white', font_height=30, center=True, append=False)

    def reset_map(self):
        self.gcd = 5
        self.temp_width = self.game.width // self.gcd
        self.temp_height = int(self.height // self.gcd)

        self.map = [[0] * self.temp_width for _ in range(self.temp_height)]

        self.powerups = []
        self.bananas = []
        self.bramas = []
        self.speedBumps = []
        self.guideArrows = []
        self.coin = None

        self.checkpoints = []
        self.current_checkpoint = []
        self.temp_map_data = dict(self.map_data)
        self.enemies = []
        self.laps = 5
        self.lapstext.update_text(f'{self.laps}')


    def add_lap(self, amount):
        if self.laps + amount >= 1:
            self.laps += amount
            self.lapstext.update_text(f'{self.laps}')

    def load_map(self, map_data):
        self.reset_map()
        self.temp_map_data.update(map_data)
        self.map = self.temp_map_data['map']
        player_info = self.temp_map_data.get('player')
        self.player_position = player_info[0]
        self.player_rotation = player_info[1]
        self.player_position = (self.player_position[0] * self.zoom_level / self.block_width, self.player_position[
            1] * self.zoom_level / self.block_height) if self.player_position else None
        self.checkpoints = self.temp_map_data['checkpoints']
        self.enemies = self.temp_map_data['enemies']
        self.powerups = self.temp_map_data['powerups']
        self.bananas = self.temp_map_data['bananas']
        self.bramas = self.temp_map_data['bramas']
        self.speedBumps = self.temp_map_data['speedBumps']
        self.guideArrows = self.temp_map_data['guideArrows']
        self.coin = self.temp_map_data['coin']
        self.laps = self.temp_map_data['laps']

        self.lapstext.update_text(f'{self.laps}')
        for e in self.enemies:
            e[0][0] = e[0][0] * self.zoom_level / self.block_width
            e[0][1] = e[0][1] * self.zoom_level / self.block_height

        self.temp_width = len(self.map[0])
        self.temp_height = len(self.map)
        self.gcd = self.game.width / self.temp_width
        self.update_block_dimensions()

    def update_block_dimensions(self):
        self.block_width = self.gcd * self.zoom_level
        self.block_height = self.gcd * self.zoom_level


    def mainloop(self):

        self.delta_time = self.game.delta_time
        keys = pygame.key.get_pressed()

        speed = 500 * self.delta_time / self.zoom_level
        if keys[pygame.K_w]:
            self.cy += speed
        if keys[pygame.K_s]:
            self.cy -= speed
        if keys[pygame.K_a]:
            self.cx += speed
        if keys[pygame.K_d]:
            self.cx -= speed

        self.brushtext.update_text(f'Brush size: {self.brush_size}')

        t = self.tool
        if self.tool == 'p':
            t = 'player'
        if self.tool == 'c':
            t = 'checkpoint'
        if self.tool == 'm':
            t = 'checkpoint?'
        if self.tool == 'e':
            t = 'enemy'
        if self.tool == 'u':
            t = 'powerup'
        if self.tool == 'v':
            t = 'speedBump'
        if self.tool == 'b':
            t = 'banana'
        if self.tool == 'n':
            t = 'brama'
        if self.tool == 'o':
            t = 'arrow'
        if self.tool == 'q':
            t = 'coin'

        self.tooltext.update_text(f'Tool: {t}  Angle: {self.angle}')

        self.player_pos_text.update_text(f'Player position: {self.player_position}')

    def add_powerup(self, x, y):
        self.powerups.append((x, y))

    def add_banana(self, x, y):
        self.bananas.append((x, y))

    def add_brama(self, x, y):
        self.bramas.append((x, y, self.angle))

    def add_speedBump(self, x, y):
        self.speedBumps.append((x, y, self.angle))

    def add_guideArrow(self, x, y):
        self.guideArrows.append((x, y, self.angle))

    def add_coin(self, x, y):
        self.coin = [x,y]

    def render(self):
        vis_x_start = max(0, m.floor((-self.cx) / self.block_width))
        vis_x_end = min(self.temp_width, m.ceil((-self.cx + self.game.width) / self.block_width))
        vis_y_start = max(0, m.floor((-self.cy) / self.block_height))
        vis_y_end = min(self.temp_height, m.ceil((-self.cy + self.game.height) / self.block_height))

        for y in range(vis_y_start, vis_y_end):
            for x in range(vis_x_start, vis_x_end):
                try:
                    color = self.color_map.get(self.map[y][x], self.asphalt_color)
                except:
                    pass
                pygame.draw.rect(self.screen, color, (
                x * self.block_width + self.cx,
                y * self.block_height + self.cy,
                self.block_width+1,
                self.block_height+1
                ))

        if self.player_position:
            px, py = self.player_position
            pw = self.player_width_blocks * self.block_width
            ph = self.player_height_blocks * self.block_height
            pygame.draw.rect(self.screen, (255, 0, 0), (
                px * self.block_width + self.cx,
                py * self.block_height + self.cy,
                pw,
                ph
            ))

        else:
            self.noplayertext.render()


        for enemy in self.enemies:
            ex, ey = enemy[0]
            ew = self.player_width_blocks * self.block_width
            eh = self.player_height_blocks * self.block_height
            pygame.draw.rect(self.screen, (0, 255, 0), (
                ex * self.block_width + self.cx,
                ey * self.block_height + self.cy,
                ew,
                eh
            ))


        pygame.draw.rect(self.screen, (155, 0, 0),
                         (self.cx, self.cy,
                          self.block_width * self.temp_width,
                          self.block_height * self.temp_height), 2)
        for obj in self.objects:
            obj.render()
        b = self.brush_size * self.block_width
        if self.tool not in ['p', 'c', 'm', 'e', 'u', 'v', 'b', 'n', 'o', 'q']:
            c = self.color_map.get(self.tool)
            if self.shape == 0:
                pygame.draw.rect(self.screen, c, (pygame.mouse.get_pos()[0] - b / 2, pygame.mouse.get_pos()[1] - b / 2, b, b), 2)
            elif self.shape == 1:
                pygame.draw.circle(self.screen, c, (int(pygame.mouse.get_pos()[0]), int(pygame.mouse.get_pos()[1])), self.brush_size * self.block_width / 2, 2)

        for i in range(len(self.checkpoints)):
            if i == 0:
                color = self.color_map['m']
            else:
                color = self.color_map['c']
            pygame.draw.line(self.screen, color, (self.checkpoints[i][0][0] * self.block_width + self.cx, self.checkpoints[i][0][1] * self.block_height + self.cy), (self.checkpoints[i][1][0] * self.block_width + self.cx, self.checkpoints[i][1][1] * self.block_height + self.cy), width=int(self.block_width))

        for i in self.powerups:
            pygame.draw.circle(self.screen, (0, 0, 255), (i[0] * self.block_width + self.cx, i[1] * self.block_height + self.cy), 10)
        for i in self.bananas:
            pygame.draw.rect(self.screen, (200, 200, 0), (i[0] * self.block_width + self.cx - 10, i[1] * self.block_height + self.cy - 5, 20, 10))
        for i in self.bramas:
            pygame.draw.circle(self.screen, (255, 0, 0), (i[0] * self.block_width + self.cx, i[1] * self.block_height + self.cy), 10)
        for i in self.speedBumps:
            pygame.draw.circle(self.screen, (0, 255, 0), (i[0] * self.block_width + self.cx, i[1] * self.block_height + self.cy), 10)
        for i in self.guideArrows:
            pygame.draw.rect(self.screen, (0, 0, 255), (i[0] * self.block_width + self.cx - 10, i[1] * self.block_height + self.cy - 5, 20, 10))
        if self.coin != None and self.coin != 'None' and len(self.coin) > 0:
            pygame.draw.circle(self.screen, (200, 200, 0), (self.coin[0] * self.block_width + self.cx, self.coin[1] * self.block_height + self.cy), 10)



        if (self.tool == 'c' or self.tool == 'm') and len(self.current_checkpoint) == 1:

            pygame.draw.line(self.screen, self.color_map[self.tool], (self.current_checkpoint[0][0] * self.block_width + self.cx,
                                                  self.current_checkpoint[0][1] * self.block_height + self.cy), (
                             pygame.mouse.get_pos()[0],
                             pygame.mouse.get_pos()[1]), width=int(self.block_width))

        elif self.tool == 'p' or self.tool == 'e':
            color = (120, 0, 0)
            if self.tool == 'e':
                color = (0, 120, 0)

            mouse_pos = pygame.mouse.get_pos()

            pw = self.player_width_blocks * self.block_width
            ph = self.player_height_blocks * self.block_height

            px = m.floor((mouse_pos[0] - self.cx) / self.block_width)
            py = m.floor((mouse_pos[1] - self.cy) / self.block_height)

            pygame.draw.rect(self.screen, color, (
                px * self.block_width + self.cx,
                py * self.block_height + self.cy,
                pw,
                ph
            ))

    def events(self, event):
        for obj in self.objects:
            obj.events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.tool = 1
            elif event.key == pygame.K_2:
                self.tool = 2
            elif event.key == pygame.K_3:
                self.tool = 3
            elif event.key == pygame.K_4:
                self.tool = 4
            elif event.key == pygame.K_5:
                self.tool = 5
            elif event.key == pygame.K_6:
                self.tool = 6
            elif event.key == pygame.K_p:
                self.tool = 'p'
            elif event.key == pygame.K_0:
                self.map = [[0] * self.temp_width for _ in range(self.temp_height)]
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                self.brush_size = min(self.brush_size + 1, max(self.temp_width, self.temp_height))
            elif event.key == pygame.K_MINUS:
                self.brush_size = max(self.brush_size - 1, 1)
            elif event.key == pygame.K_u:
                self.tool = 'u'

            elif event.key == pygame.K_c:
                self.tool = 'c'
                self.current_checkpoint = []
                if len(self.checkpoints) == 0:
                    self.tool = 'm'
            elif event.key == pygame.K_m:
                self.tool = 'm'
                self.current_checkpoint = []
            elif event.key == pygame.K_n:
                self.tool = 'n'
            elif event.key == pygame.K_b:
                self.tool = 'b'
            elif event.key == pygame.K_v:
                self.tool = 'v'
            elif event.key == pygame.K_o:
                self.tool = 'o'
            elif event.key == pygame.K_UP:
                self.brush_size += 10
            elif event.key == pygame.K_DOWN:
                self.brush_size -= 10
            elif event.key == pygame.K_e:
                self.tool = 'e'
            elif event.key == pygame.K_z:
                if len(self.archiveStates) > 1:
                    self.map = self.archiveStates[-1]
                    self.archiveStates.pop(-1)
            elif event.key == pygame.K_x:
                self.angle += 10
                if self.angle >= 360:
                    self.angle -= 360
                elif self.angle < 0:
                    self.angle += 360
            elif event.key == pygame.K_q:
                self.tool = 'q'
            elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                if self.shape == 1:
                    self.shape = 0
                elif self.shape == 0:
                    self.shape = 1
        self.handle_mouse_events(event)
        self.handle_zoom(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_display('map_maker_menu')

    def handle_mouse_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        grid_x = m.floor((mouse_pos[0] - self.cx) / self.block_width)
        grid_y = m.floor((mouse_pos[1] - self.cy) / self.block_height)

        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]:
            if self.valid_grid_pos(grid_x, grid_y):
                if self.is_painting(event) and self.tool != 'c' and self.tool != 'm' and self.tool != 'p' and self.tool != 'e' and self.tool != 'u':
                    self.apply_brush(grid_x, grid_y, self.tool)
                elif self.is_erasing(event):
                    self.apply_brush(grid_x, grid_y, 0)
                    if self.player_position != None:
                        if (grid_x >= self.player_position[0] and grid_x <= self.player_position[0] + self.player_width_blocks) and (grid_y >= self.player_position[1] and grid_y <= self.player_position[1] + self.player_height_blocks):
                            self.player_position = None
                    for e in self.enemies:
                        if (grid_x >= e[0][0] and grid_x <= e[0][0] + self.player_width_blocks) and (grid_y >= e[0][1] and grid_y <= e[0][1] + self.player_height_blocks):
                            self.enemies.remove(e)

                    for chpo in self.checkpoints:
                        if pygame.Rect(grid_x, grid_y, 5 * self.block_width, 5 * self.block_width).clipline(chpo):
                            self.checkpoints.remove(chpo)

                elif self.checkpoint_placing(event):
                    self.current_checkpoint.append((grid_x, grid_y))
                    if len(self.current_checkpoint) == 2:
                        if self.tool != 'm':
                            self.checkpoints.append((self.current_checkpoint[0], self.current_checkpoint[1]))
                        else:
                            self.checkpoints.insert(0, (self.current_checkpoint[0], self.current_checkpoint[1]))
                            self.tool = 'c'
                        self.current_checkpoint = []




        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            if self.tool == 'p' and self.valid_grid_pos(grid_x, grid_y):
                self.player_position = (grid_x, grid_y)

            elif self.tool == 'e' and self.valid_grid_pos(grid_x, grid_y):
                self.enemies.append(((grid_x, grid_y), self.enemy_rotation))

            elif self.tool == 'u' and self.valid_grid_pos(grid_x, grid_y):
                self.add_powerup(grid_x, grid_y)
            elif self.tool == 'b' and self.valid_grid_pos(grid_x, grid_y):
                self.add_banana(grid_x, grid_y)
            elif self.tool == 'n' and self.valid_grid_pos(grid_x, grid_y):
                self.add_brama(grid_x, grid_y)
            elif self.tool == 'v' and self.valid_grid_pos(grid_x, grid_y):
                self.add_speedBump(grid_x, grid_y)
            elif self.tool == 'o' and self.valid_grid_pos(grid_x, grid_y):
                self.add_guideArrow(grid_x, grid_y)
            elif self.tool == 'q' and self.valid_grid_pos(grid_x, grid_y):
                self.add_coin(grid_x, grid_y)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_MIDDLE:
            self.dragging = True
            self.start_x, self.start_y = mouse_pos
            self.start_cx, self.start_cy = self.cx, self.cy
        elif event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_MIDDLE:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            delta_x = mouse_pos[0] - self.start_x
            delta_y = mouse_pos[1] - self.start_y
            self.cx = self.start_cx + delta_x
            self.cy = self.start_cy + delta_y

    def handle_zoom(self, event):
        if event.type == pygame.MOUSEWHEEL:
            old_zoom = self.zoom_level
            self.zoom_level *= 1.1 ** event.y
            self.zoom_level = max(0.1, min(self.zoom_level, 5.0))
            self.update_block_dimensions()

            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.cx = mouse_x - (mouse_x - self.cx) * (self.zoom_level / old_zoom)
            self.cy = mouse_y - (mouse_y - self.cy) * (self.zoom_level / old_zoom)

    def export_png(self):
        map_surface = pygame.Surface((self.temp_width * self.block_width,
                                      self.temp_height * self.block_height))
        map_surface.fill(self.bgColor)

        for y in range(self.temp_height):
            for x in range(self.temp_width):
                tile = self.map[y][x]
                if tile == 0:
                    continue
                color = self.color_map.get(tile, self.asphalt_color)
                if tile in (0, 1, 3, 4, 5):
                    color = (
                        min(max(color[0] + random.randint(-10, 10), 0), 255),
                        min(max(color[1] + random.randint(-10, 10), 0), 255),
                        min(max(color[2] + random.randint(-10, 10), 0), 255)
                    )
                pygame.draw.rect(map_surface, color,
                                 (x * self.block_width, y * self.block_height,
                                  self.block_width+1, self.block_height+1))


        for chp in self.checkpoints:
            if chp == self.checkpoints[0]:
                color = self.color_map['m']
                pygame.draw.line(map_surface, color,
                                 (chp[0][0] * self.block_width, chp[0][1] * self.block_height),
                                 (chp[1][0] * self.block_width, chp[1][1] * self.block_height),
                                 width=int(self.block_width))
            else:
                color = self.color_map['c']

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'images/maps/map_{timestamp}.png'

        if not os.path.exists('images/maps'):
            os.makedirs('images/maps')

        pygame.image.save(map_surface, filename)

    def export_map(self):
        if not os.path.exists('maps'):
            os.makedirs('maps')
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'maps/map_{current_time}.json'

        temp_player_position = (self.player_position[0]/self.zoom_level*self.block_width, self.player_position[1]/self.zoom_level*self.block_height) if self.player_position else self.map_data['player'][0]

        temp_enemies = []

        for enemy in self.enemies:
            temp_enemies.append(((enemy[0][0]/self.zoom_level*self.block_width, enemy[0][1]/self.zoom_level*self.block_height), enemy[1]))

        map_data = {
            'map': self.map,
            'player': [temp_player_position, self.player_rotation],
            'enemies': temp_enemies,
            'checkpoints': self.checkpoints,
            'powerups': self.powerups,
            'coin': self.coin,
            'bananas': self.bananas,
            'bramas': self.bramas,
            'speedBumps': self.speedBumps,
            'guideArrows': self.guideArrows,
            'laps': self.laps
        }

        self.temp_map_data.update(map_data)

        with open(filename, 'w') as f:
            json.dump(self.temp_map_data, f)
            f.close()
        self.game.displays['level_selector'].load_maps()
        self.game.change_display('map_maker_menu')

    def apply_brush(self, x, y, value):
        self.archiveStates.append(copy.deepcopy(self.map))
        half_brush = self.brush_size // 2
        for dy in range(-half_brush, half_brush + 1):
            for dx in range(-half_brush, half_brush + 1):
                nx, ny = x + dx, y + dy
                if self.shape == 0 or (self.shape == 1 and (nx - x) ** 2 + (ny - y) ** 2 < half_brush ** 2):
                    if 0 <= nx < self.temp_width and 0 <= ny < self.temp_height:
                        self.map[ny][nx] = value
        if self.archiveStates[-1] == self.map and len(self.archiveStates) > 1:
            self.archiveStates.pop(-1)

    def valid_grid_pos(self, x, y):
        return 0 <= x < self.temp_width and 0 <= y < self.temp_height

    def is_painting(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT) or \
               (event.type == pygame.MOUSEMOTION and event.buttons[0])

    def is_erasing(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_RIGHT) or \
               (event.type == pygame.MOUSEMOTION and event.buttons[2])

    def checkpoint_placing(self, event):
        if (self.tool == 'c' or self.tool == 'm') and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return True
        return False


class main_menu_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)

        self.amount_of_buttons = 6
        self.button_padding = self.game.height * (1/96)
        self.button_width_modifier = 45.5/256
        self.button_heigh_modifier = 10.4/144
        self.button_width = self.game.width*self.button_width_modifier
        self.button_height = self.game.height*self.button_heigh_modifier

        custom_text.Custom_text(self, self.game.width / 2, self.game.height / 5, 'Pixel!\n    Racers!',
                                text_color='white', font_height=int(self.game.height * (19 / 216)))

        if self.game.enable_debug == False:
            self.amount_of_buttons -= 1
            custom_button.Button(self, 'to_level_selector', self.button_padding, self.game.height + (
                        - self.button_padding - self.button_height) * self.amount_of_buttons, self.button_width,
                                 self.button_height, text='Play', border_radius=0, color=(26, 26, 26),
                                 text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
            custom_button.Button(self, 'change_vehicle', self.button_padding,
                                 self.game.height + (- self.button_padding - self.button_height) * (
                                         self.amount_of_buttons - 1), self.button_width, self.button_height,
                                 text='Change vehicle', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150),
                                 outline_color=(50, 50, 50), outline_width=2)

            custom_button.Button(self, 'settings', self.button_padding,
                                 self.game.height + (- self.button_padding - self.button_height) * (
                                             self.amount_of_buttons - 2), self.button_width, self.button_height,
                                 text='Settings', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150),
                                 outline_color=(50, 50, 50), outline_width=2)

            custom_button.Button(self, 'credits', self.button_padding,
                                 self.game.height + (- self.button_padding - self.button_height) * (
                                         self.amount_of_buttons - 3), self.button_width, self.button_height,
                                 text='Credits', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150),
                                 outline_color=(50, 50, 50), outline_width=2)

            custom_button.Button(self, 'quit', self.button_padding,
                                 self.game.height + (- self.button_padding - self.button_height) * (
                                             self.amount_of_buttons - 4), self.button_width, self.button_height,
                                 text='Quit', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150),
                                 outline_color=(50, 50, 50), outline_width=2)
            custom_button.Button(self, 'change_player_name', self.game.width - (self.button_width + 75) - self.button_padding,
                                 self.game.height + (- self.button_padding - self.button_height) * (
                                         self.amount_of_buttons - 4), self.button_width + 75, self.button_height,
                                text = "CHANGE PLAYER NAME", border_radius = 0, color = (26, 26, 26),
                                text_color = (150, 150, 150), outline_color = (50, 50, 50),
                                outline_width = 2)


        else:

            custom_button.Button(self, 'to_level_selector', self.button_padding, self.game.height + (- self.button_padding - self.button_height) * self.amount_of_buttons, self.button_width, self.button_height, text='Play', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
            custom_button.Button(self, 'change_vehicle', self.button_padding,
                                 self.game.height + (- self.button_padding - self.button_height) * (
                                             self.amount_of_buttons - 1), self.button_width, self.button_height,
                                 text='Change vehicle', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150),
                                 outline_color=(50, 50, 50), outline_width=2)

            custom_button.Button(self, 'settings', self.button_padding, self.game.height + (- self.button_padding - self.button_height) * (self.amount_of_buttons - 2), self.button_width, self.button_height, text='Settings', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
            custom_button.Button(self, 'to_map_maker_menu', self.button_padding, self.game.height + (- self.button_padding - self.button_height) * (self.amount_of_buttons - 3), self.button_width, self.button_height, text='Make a map', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
            custom_button.Button(self, 'credits', self.button_padding,self.game.height + (- self.button_padding - self.button_height) * (self.amount_of_buttons - 4), self.button_width, self.button_height, text='Credits', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
            custom_button.Button(self, 'quit', self.button_padding, self.game.height + (- self.button_padding - self.button_height) * (self.amount_of_buttons - 5), self.button_width, self.button_height, text='Quit', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
            custom_button.Button(self, 'change_player_name', self.game.width - (self.button_width + 75) - self.button_padding,
                                 self.game.height + (- self.button_padding - self.button_height) * (
                                         self.amount_of_buttons - 5), self.button_width + 75, self.button_height,
                                text = "CHANGE PLAYER NAME", border_radius = 0, color = (26, 26, 26),
                                text_color = (150, 150, 150), outline_color = (50, 50, 50),
                                outline_width = 2)
        self.particle_system = self.game.menu_particle_system

    def render(self):
        self.particle_system.add_particle(random.randint(0, self.game.width), random.uniform(0, self.game.height), random.uniform(-1, 1), random.randint(-1, 1), 0, 0, 0, 0, 10, 600, random.randint(1, 2), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 100, 'square')
        self.particle_system.draw(self.screen)

        for obj in self.objects:
            obj.render()


    def mainloop(self):
        self.particle_system.update(self.game.delta_time)
    def events(self, event):
        for obj in self.objects:
            obj.events(event)

class settings_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)

        self.button_width_modifier = 45.5 / 256
        self.button_heigh_modifier = 10.4 / 144
        self.button_width = self.game.width * self.button_width_modifier
        self.button_height = self.game.height * self.button_heigh_modifier

        custom_text.Custom_text(self, self.game.width/2, self.game.height/8, 'SETTINGS', text_color='white', font_height=int(self.game.height*(19/216)))
        custom_text.Custom_text(self, self.game.width/2, self.game.height - 22.5, self.game.version, text_color='white', font_height=25)
        self.back_button = custom_button.Button(self, 'to_main_menu', self.game.width/2, self.game.height/2, self.button_width, self.button_height, text='Back to menu', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        cfg = read_config()
        current_fps = int(cfg['fps'])

        self.fps_text = custom_text.Custom_text(self, self.game.width/4, self.game.height/2 - 50, f'FPS: {current_fps}', text_color='white', font_height=30)
        self.fps_slider = Slider(self, 'fps_slider', self.game.width/4 - 100, self.game.height/2, 200, 20, 30, 144, current_fps)

        current_volume = int(self.game.sound_manager.sounds["engine"].get_volume() * 100 if "engine" in self.game.sound_manager.sounds else 50)

        self.volume_text = custom_text.Custom_text(
            self,
            self.game.width / 4,
            self.game.height / 2 + 100,
            f'Volume: {current_volume}%',
            text_color='white',
            font_height=30
        )

        self.volume_slider = Slider(
            self,
            'volume_slider',
            self.game.width / 4 - 100,
            self.game.height / 2 + 150,
            200,
            20,
            0,
            100,
            current_volume,
            slider_type="volume"
        )

        self.particle_system = self.game.menu_particle_system

    def render(self):
        self.particle_system.add_particle(random.randint(0, self.game.width), random.uniform(0, self.game.height),
                                          random.uniform(-1, 1), random.randint(-1, 1), 0, 0, 0, 0, 10, 600,
                                          random.randint(1, 2), random.randint(0, 255), random.randint(0, 255),
                                          random.randint(0, 255), 100, 'square')
        self.particle_system.draw(self.screen)

        self.fps_text.update_text(f'FPS: {self.game.fps}')
        self.volume_text.update_text(f'Volume: {int(self.volume_slider.current_value)}%')

        for obj in self.objects:
            obj.render()


    def mainloop(self):
        self.particle_system.update(self.game.delta_time)

    def events(self, event):
        for obj in self.objects:
            obj.events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_display('main_menu_display')

    def update_button(self, to_main_menu=1):
        if to_main_menu:
            self.back_button.action = 'to_main_menu'
            self.back_button.update_text('Back to menu')

        else:
            self.back_button.action = 'to_pause_display'
            self.back_button.update_text('Back')

class pause_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        custom_text.Custom_text(self, self.game.width/2, self.game.height/6.5, 'paused', text_color='white')
        custom_text.Custom_text(self, self.game.width/2, self.game.height - 22.5, self.game.version, text_color='white', font_height=25)
        width = 460

        custom_button.Button(self, 'back_to_race', self.game.width / 2 - width // 2, self.game.height / 2 - 90,
                             width, 80,
                             text='Resume', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150),
                             outline_color=(50, 50, 50), outline_width=2)

        custom_button.Button(self, 'to_in_game_settings_display', self.game.width / 2 - width // 2, self.game.height / 2,
                             width, 80,
                             text='Settings', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150),
                             outline_color=(50, 50, 50), outline_width=2)


        custom_button.Button(self, 'back_to_level_selector', self.game.width / 2 - width // 2, self.game.height / 2 + 90, width, 80,
                             text='Quit', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150),
                             outline_color=(50, 50, 50), outline_width=2)

        self.overlay = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 200))


    def mainloop(self):
        pass

    def events(self, event):
        for obj in self.objects:
            obj.events(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.current_display = self.game.displays[list(self.game.displays['level_selector'].levels.keys())[self.game.displays['level_selector'].currently_selected]]

    def render(self):
        self.game.displays[list(self.game.displays['level_selector'].levels.keys())[self.game.displays['level_selector'].currently_selected]].render()
        self.game.screen.blit(self.overlay, (0, 0))
        super().render()


class level_selector(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        self.bg = (100, 30, 30)
        custom_text.Custom_text(self, self.game.width/2, self.game.height/9, 'SELECT A COURSE', text_color='white', font_height=int(self.game.height*(19/216)))

        self.button_width_modifier = 45.5 / 256
        self.button_heigh_modifier = 10.4 / 144
        self.button_width = self.game.width * self.button_width_modifier
        self.button_height = self.game.height * self.button_heigh_modifier

        custom_button.Button(self, 'play_course', self.game.width/2 + 7.5, self.game.height - 150, self.button_width, self.button_height, text='PLAY', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
        custom_button.Button(self, 'to_main_menu', self.game.width / 2 - self.button_width - 7.5, self.game.height - 150,
                             self.button_width, self.button_height, text='BACK', border_radius=0, color=(26, 26, 26),
                             text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        custom_button.Button(self, 'to_new_leaderboard', self.game.width / 2 + 21.5 + self.button_width, self.game.height - 150, self.button_height,
                             self.button_height, text='', border_radius=0, color=(26, 26, 26),
                             text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        custom_images.Custom_image(self, 'images/puchar.png', self.game.width / 2 + 21.5 + self.button_width + self.button_height/2, self.game.height - 150 + self.button_height/2, self.button_height,
                             self.button_height, )

        self.particle_system = self.game.menu_particle_system
        self.top = 3
        self.descaling_factor = 3
        self.currently_selected = 0

        self.selected_surface_width = self.game.width/self.descaling_factor
        self.selected_surface_height = (self.game.height - self.game.hotbar_dimentions[1])/self.descaling_factor

        self.not_selected_surface_width = self.selected_surface_width/2
        self.not_selected_surface_height = self.selected_surface_height/2

        custom_button.Button(self, 'move_selection_to_left', self.game.width / 2 - self.button_width - 7.5,
                             (self.game.height - 150 -  self.button_height - 15),
                             self.button_width, self.button_height, text='<-', border_radius=0, color=(26, 26, 26),
                             text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        custom_button.Button(self, 'move_selection_to_right', self.game.width / 2 + 7.5,
                             (self.game.height - 150  - self.button_height - 15),
                             self.button_width, self.button_height, text='->', border_radius=0, color=(26, 26, 26),
                             text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        self.pb_text = custom_text.Custom_text(self, self.game.width//2, self.game.height//5 + 80, 'Personal Best: N/A', text_color=(255, 223, 0))
    def mainloop(self):
        self.particle_system.update(self.game.delta_time)

    def events(self, event):
        for obj in self.objects:
            obj.events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_display('main_menu_display')
            elif event.key == pygame.K_LEFT:
                if self.currently_selected > 0:
                    self.currently_selected -= 1
                    self.update_surfaces(-1)
                self.update_pb_text()
            elif event.key == pygame.K_RIGHT:
                if self.currently_selected < len(list(self.levels.values())) - 1:
                    self.currently_selected += 1
                    self.update_surfaces(1)
                self.update_pb_text()

            elif event.key == pygame.K_RETURN:
                course_to_play = self.currently_selected
                self.game.change_display(
                    list(self.levels.keys())[course_to_play])
                if course_to_play == 0:
                    self.game.sound_manager.unload_music()
                    self.game.sound_manager.load_music('sounds/music/Neon Rush.wav')
                    self.game.sound_manager.play_music()

                if course_to_play == 1:
                    self.game.sound_manager.unload_music()
                    self.game.sound_manager.load_music('sounds/music/Volcanic Rush.wav')
                    self.game.sound_manager.play_music()


                elif course_to_play == 2:
                    self.game.sound_manager.unload_music()
                    self.game.sound_manager.load_music('sounds/music/Chasing Snowflakes.wav')

                    self.game.sound_manager.play_music()

            elif event.key == pygame.K_l:
                self.game.change_display('new_leaderboard')
                self.game.current_display.level = list(self.levels.keys())[
                    self.currently_selected]
                self.game.current_display.loaded = 0

    def get_pb(self):
        levels_list = list(self.levels.keys())
        self.pb_times = {}
        for level in levels_list:
            time = self.db_manager.get_personal_best(self.game.player_name, level)
            if time != None:
                self.pb_times[level] = time
            else:
                self.pb_times[level] = 'N/A'

    def update_pb_text(self):
        full_time = self.pb_times[list(self.levels.keys())[self.currently_selected]]
        if full_time != 'N/A':
            milliseconds = int((full_time % 1) * 1000)
            total_seconds = int(full_time)
            minutes, seconds = divmod(total_seconds, 60)

            if total_seconds < 60:
                formatted_time = f"{total_seconds}:{milliseconds:03d}"
            else:
                formatted_time = f"{minutes}:{seconds:02d}:{milliseconds:03d}"


            self.pb_text.update_text(f'Personal Best: {formatted_time}')
        else:
            self.pb_text.update_text(f'Personal Best: N/A')
    def render(self):
        if self.currently_selected == 0:
            self.bg = (25, 90, 25)
        elif self.currently_selected == 1:
            self.bg = (100, 100, 30)
        elif self.currently_selected == 2:
            self.bg = (100, 30, 30)

        self.screen.fill(self.bg)
        self.particle_system.add_particle(random.randint(0, self.game.width), random.uniform(0, self.game.height),
                                          random.uniform(-1, 1), random.randint(-1, 1), 0, 0, 0, 0, 10, 600,
                                          random.randint(1, 2), random.randint(0, 255), random.randint(0, 255),
                                          random.randint(0, 255), 100, 'square')
        self.particle_system.draw(self.screen)
        for i, lvl in enumerate(list(self.levels.values())):
            if i - self.currently_selected == 0:
                pygame.draw.rect(self.game.screen, self.bgColor, (self.game.width/2 - self.selected_surface_width/2 -5, self.game.height/2 - self.selected_surface_height/2-5, self.selected_surface_width + 10, self.selected_surface_height + 10))
                pygame.draw.rect(self.game.screen, (0, 125, 0), (self.game.width/2 - self.selected_surface_width/2 -5, self.game.height/2 - self.selected_surface_height/2-5, self.selected_surface_width + 10, self.selected_surface_height + 10), width=10)
                self.game.screen.blit(lvl, (self.game.width/2 - self.selected_surface_width/2, self.game.height/2 - self.selected_surface_height/2))

            else:
                a = 0
                if i - self.currently_selected < 0:
                    a = 1

                pygame.draw.rect(self.game.screen, self.bgColor, (
                    self.game.width / 2 - (self.selected_surface_width / 2) * a + (
                            self.not_selected_surface_width + 25) * (i - self.currently_selected) - 5,
                    self.game.height / 2 - self.not_selected_surface_height / 2 - 5,
                    self.not_selected_surface_width + 10,
                    self.not_selected_surface_height + 10))

                self.game.screen.blit(lvl, (
                self.game.width / 2 - (self.selected_surface_width / 2) * a + (self.not_selected_surface_width + 25) * (i - self.currently_selected), self.game.height / 2 - self.not_selected_surface_height / 2))

        for obj in self.objects:
            obj.render()

    def load_maps(self):
        levels = self.game.get_level_names()
        self.levels = {}
        for i, lvl in enumerate(levels):
            self.game.displays[lvl] = game_display(self.game, lvl )
            if i - self.currently_selected == 0:
                sur = pygame.transform.scale(self.game.displays[lvl].img_map_surface, (self.selected_surface_width, self.selected_surface_height))
            else:
                sur = pygame.transform.scale(self.game.displays[lvl].img_map_surface,
                                             (self.not_selected_surface_width, self.not_selected_surface_height))
            self.levels[lvl] = sur

        self.get_pb()
        self.update_pb_text()

    def reload_maps(self):
        try:
            for i, lvl in enumerate(list(self.levels.keys())):
                difficulty = self.game.displays[lvl].difficulty
                del self.game.displays[lvl]
                self.game.displays[lvl] = game_display(self.game, difficulty)
                if i - self.currently_selected == 0:
                    sur = pygame.transform.scale(self.game.displays[lvl].img_map_surface,
                                                 (self.selected_surface_width, self.selected_surface_height))
                else:
                    sur = pygame.transform.scale(self.game.displays[lvl].img_map_surface, (self.not_selected_surface_width, self.not_selected_surface_height))
                self.levels[lvl] = sur
                self.get_pb()
                self.update_pb_text()
        except:
            self.load_maps()


    def update_surfaces(self, dir):
        for i, lvl in enumerate(list(self.levels.values())):
            if i - self.currently_selected == 0:
                del lvl
                sur = pygame.transform.scale(self.game.displays[list(self.levels.keys())[i]].img_map_surface,
                                             (self.selected_surface_width, self.selected_surface_height))
                self.levels[list(self.levels.keys())[i]] = sur

                sur = pygame.transform.scale(self.game.displays[list(self.levels.keys())[i - dir]].img_map_surface,
                                             (self.not_selected_surface_width, self.not_selected_surface_height))
                self.levels[list(self.levels.keys())[i - dir]] = sur
                break


class map_maker_menu(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        custom_button.Button(self, 'new_map', self.game.width/2 - self.game.width*40/384 - self.game.width*40/192 - 15, self.game.height/1.2, self.game.width*40/192, self.game.height*10/108, self.bgColor, text='NEW MAP', text_color=(150, 150, 150), outline_color=(150, 150, 150), border_radius=0, outline_width=1)
        custom_button.Button(self, 'to_map_maker_display', self.game.width/2 - self.game.width*40/384, self.game.height/1.2, self.game.width*40/192, self.game.height*10/108, self.bgColor,
                             text='CONTINUE', text_color=(150, 150, 150), outline_color=(150, 150, 150), border_radius=0,
                             outline_width=1)

        custom_button.Button(self, 'to_main_menu', self.game.width/2 + self.game.width*40/384 + 15, self.game.height/1.2, self.game.width*40/192, self.game.height*10/108,
                             self.bgColor,
                             text='BACK', text_color=(150, 150, 150), outline_color=(150, 150, 150),
                             border_radius=0,
                             outline_width=1)

        self.menu_w = self.game.width * 142/192
        self.menu_h = self.game.height * 50/108
        self.padding = 15

        self.menu_x = self.game.width * 15/192
        self.menu_y = self.game.height * 22/108

        custom_text.Custom_text(self, self.game.width/2, self.game.height/10, 'MAP MAKER MENU', font_height=100, text_color='white')

        self.file_names = self.game.get_level_names()
        self.lists_len = len(self.file_names)
        self.text_list = [custom_text.Custom_text(self, 0, 0, '', text_color=(150, 150, 150)) for _ in range(self.lists_len)]
        self.edit_button_list = [custom_button.Button(self, 'blank', 0, 0, 100, 50, self.bgColor, text='Edit', text_color=(150, 150, 150), outline_color=(150, 150, 150), border_radius=0, outline_width=1) for _ in range(self.lists_len)]
    def mainloop(self):
        pass

    def render(self):
        try:
            self.file_names = self.game.get_level_names()

            l = len(self.file_names)

            if l != self.lists_len:
                if l < self.lists_len:
                    for _ in range(self.lists_len - l):
                        self.text_list[-1].delete()
                        self.text_list.pop(-1)

                        self.edit_button_list[-1].delete()
                        self.edit_button_list.pop(-1)

                else:
                    for _ in range(l - self.lists_len):
                        self.text_list.append(custom_text.Custom_text(self, 0, 0, '', text_color=(150, 150, 150)))
                        self.edit_button_list.append(custom_button.Button(self, 'blank', 0, 0, 100, 50, self.bgColor, text='Edit', text_color=(150, 150, 150), outline_color=(150, 150, 150), border_radius=0, outline_width=1))

                self.lists_len = l


            for x in range(l):
                pygame.draw.rect(self.game.screen, self.bgColor, (self.menu_x, (self.menu_h/l + self.padding) * x + self.menu_y, self.menu_w, self.menu_h/l))

                self.text_list[x].update_text(self.file_names[x])
                self.text_list[x].update_position(self.menu_x + self.menu_w / 2, self.menu_y + (self.menu_h/l + self.padding) * x + ((self.menu_h/l + self.padding))/2)

                self.edit_button_list[x].update_pos_and_size(self.menu_x + self.menu_w + self.padding, self.menu_y + (self.menu_h/l + self.padding) * x + ((self.menu_h/l + self.padding))/2 - self.menu_h/l/2 - self.padding/2, self.menu_h/l, self.menu_h/l)
                self.edit_button_list[x].action = f'edit_map_titled_{self.file_names[x]}'
        except Exception as e:
            print(e)



        for o in self.objects:
            o.render()

    def events(self, event):
        for obj in self.objects:
            obj.events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_display('main_menu_display')

class change_vehicle(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        self.particle_system = self.game.menu_particle_system
        self.cars = []
        self.large_cars = []
        self.small_cars = []
        self.selected_car_model = 1

        self.car_prices = {
            1: 0,
            2: 100,
            3: 250,
            4: 500,
            5: 100000,
            6: 2000
        }

        if not self.db_manager.is_car_unlocked(1):
            self.db_manager.unlock_car(1)

        for i in range(5):
            large_car = car.Car(self, (self.game.width / 2, self.game.height / 2), 0, True, i + 1,
                                car3d_height_factor=2.8)
            initial_x = self.game.width / 2 + (i - self.selected_car_model + 1) * 250
            small_car = car.Car(self, (initial_x, self.game.height / 2), 0, True, i + 1)

            self.large_cars.append(large_car)
            self.small_cars.append(small_car)
            self.cars.remove(large_car)
            self.cars.remove(small_car)
            self.objects.remove(large_car)
            self.objects.remove(small_car)

        self.amount_of_car = len(self.large_cars)

        self.button_width_modifier = 45.5 / 256
        self.button_heigh_modifier = 10.4 / 144
        self.button_width = self.game.width * self.button_width_modifier
        self.button_height = self.game.height * self.button_heigh_modifier

        custom_text.Custom_text(self, self.game.width / 2, self.game.height / 5, 'SELECT A VEHICLE', text_color='white',
                                font_height=int(self.game.height * (19 / 216)))

        self.coins_text = custom_text.Custom_text(self, self.game.width - 350, 50,
                                                  f"Coins: {self.db_manager.get_coins()}",
                                                  text_color=(255, 223, 0),
                                                  font_height=30,
                                                  center=False)

        self.price_text = custom_text.Custom_text(self, self.game.width / 2,
                                                  self.game.height - 400,
                                                  "",
                                                  text_color=(255, 223, 0),
                                                  font_height=30)

        custom_button.Button(self, 'move_selected_car_to_left', self.game.width / 2 - self.button_width - 7.5,
                             (self.game.height - 150) - self.button_height - 15,
                             self.button_width, self.button_height, text='<-', border_radius=0, color=(26, 26, 26),
                             text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        custom_button.Button(self, 'move_selected_car_to_right', self.game.width / 2 + 7.5,
                             (self.game.height - 150) - self.button_height - 15,
                             self.button_width, self.button_height, text='->', border_radius=0, color=(26, 26, 26),
                             text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        self.action_button = custom_button.Button(self, 'car_action', self.game.width / 2 + 7.5, self.game.height - 150,
                                                  self.button_width, self.button_height, text='SELECT',
                                                  border_radius=0,
                                                  color=(26, 26, 26), text_color=(150, 150, 150),
                                                  outline_color=(50, 50, 50), outline_width=2)

        custom_button.Button(self, 'to_main_menu', self.game.width / 2 - self.button_width - 7.5,
                             self.game.height - 150,
                             self.button_width, self.button_height, text='BACK', border_radius=0, color=(26, 26, 26),
                             text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        self.animation_progress = 0
        self.target_positions = []
        self.start_positions = []
        self.is_animating = False
        self.animation_speed = 5.0

    def mainloop(self):
        self.particle_system.update(self.game.delta_time)

    def render(self):
        self.particle_system.add_particle(random.randint(0, self.game.width), random.uniform(0, self.game.height),
                                          random.uniform(-1, 1), random.randint(-1, 1), 0, 0, 0, 0, 10, 600,
                                          random.randint(1, 2), random.randint(0, 255), random.randint(0, 255),
                                          random.randint(0, 255), 100, 'square')
        self.particle_system.draw(self.game.screen)

        self.coins_text.update_text(f"Coins: {self.db_manager.get_coins()}")

        is_unlocked = self.db_manager.is_car_unlocked(self.selected_car_model)

        if is_unlocked:
            self.action_button.update_text("Select")
            self.action_button.update_color((150, 150, 150))
            self.action_button.outline_color = (50, 50, 50)
            self.price_text.update_text("")
        else:
            price = self.car_prices[self.selected_car_model]
            self.action_button.update_text(f"Buy: {price}")
            self.action_button.update_color((255, 223, 0))
            self.price_text.update_text(f"Price: {price} coins")

        if self.selected_car_model < 1:
            self.selected_car_model = 1
        elif self.selected_car_model > self.amount_of_car:
            self.selected_car_model = self.amount_of_car

        if self.is_animating:
            self.animation_progress = min(1.0, self.animation_progress + self.game.delta_time * self.animation_speed)
            if self.animation_progress >= 1.0:
                self.is_animating = False
                # Update final positions
                for i, car in enumerate(self.small_cars):
                    car.x = self.target_positions[i]

        for i, car in enumerate(self.small_cars):
            if i == self.selected_car_model - 1:
                self.large_cars[i].rotation -= 80 * self.game.delta_time
                self.large_cars[i].car_mask = self.large_cars[i].car3d_sprite.update_mask_rotation(
                    int(self.large_cars[i].rotation))
                self.large_cars[i].render_model()
            else:
                if self.is_animating:
                    start_pos = self.start_positions[i]
                    target_pos = self.target_positions[i]
                    car.x = start_pos + (target_pos - start_pos) * self.animation_progress
                else:
                    car.x = self.game.width / 2 + (i - self.selected_car_model + 1) * 250
                car.render_model()

        for obj in self.objects:
            obj.render()

    def handle_car_action(self):
        is_unlocked = self.db_manager.is_car_unlocked(self.selected_car_model)

        if is_unlocked:
            self.game.player_model = self.selected_car_model
            self.game.update_player_model()
            self.game.change_display('main_menu_display')
        else:
            price = self.car_prices[self.selected_car_model]
            self.db_manager.buy_car(self.selected_car_model, price)

    def start_animation(self):
        self.animation_progress = 0
        self.is_animating = True
        self.start_positions = [car.x for car in self.small_cars]
        self.target_positions = [self.game.width / 2 + (i - self.selected_car_model + 1) * 250 for i in
                                 range(len(self.small_cars))]
    def move_selected_car_to_left(self):
        if self.selected_car_model > 1 and not self.is_animating:
            self.selected_car_model -= 1
            self.start_animation()

    def move_selected_car_to_right(self):
        if self.selected_car_model < self.amount_of_car and not self.is_animating:
            self.selected_car_model += 1
            self.start_animation()
    def events(self, event):
        for obj in self.objects:
            obj.events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_display('main_menu_display')


class credits(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        self.button_width_modifier = 45.5 / 256
        self.button_heigh_modifier = 10.4 / 144
        self.last_update_time = pygame.time.get_ticks()
        self.button_width = self.game.width * self.button_width_modifier
        self.button_height = self.game.height * self.button_heigh_modifier
        custom_button.Button(self, 'main_menu_credits',50,
                             self.game.height - 50 - self.button_height,
                             self.button_width, self.button_height, text='BACK', border_radius=0, color=(26, 26, 26),
                             text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
        self.video = cv2.VideoCapture('videos/credits.mp4')
        self.currentText = 0
        self.last_fps = self.game.fps
        custom_text.Custom_text(self, self.game.width/2, self.game.height/11, 'Credits', font_height=int(self.game.height*(19/216)),text_color=(255, 255, 255),
                                background_color=(0, 0, 0), center=True)

        self.texts = {}
        names = ("rutra8002", "MalyszekTobias", "Hohenzoler", "Saniccxx", "O5Romano")
        for i in range(5):
            self.texts[f'text_{i}'] = custom_text.Custom_text(self, self.game.width // 2, self.game.height // 3 + 60 * i,
                                                         f'{names[i]}', font_height=45, text_color=(255, 255, 255),
                                                         background_color=(0, 0, 0), center=True)
    def mainloop(self):
        pass
    def render(self):
        ret, frame = self.video.read()
        if not ret:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.video.read()
            if not ret:
                return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = numpy.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        self.game.screen.blit(frame, (0, 0))

        for obj in self.objects:
            obj.render()

    def events(self, event):
        for obj in self.objects:
            obj.events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.fps = self.game.displays['credits'].last_fps
                self.game.displays['credits'].video.release()
                self.game.sound_manager.stop_sound('Credits')
                self.game.change_display('main_menu_display')

class leaderboard(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        self.leaderboard_list = []
        self.coin = 0
        custom_text.Custom_text(self, self.game.width/2, self.game.height/7, 'Placements', text_color=(255, 223, 0), font_height=60)
        custom_button.Button(self, 'back_to_level_selector', self.game.width / 2 - 460 // 2, 952,
                             460, 80,
                             text='continue', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150),
                             outline_color=(50, 50, 50), outline_width=2)
        self.text_obj = []

        self.particle_system = self.game.menu_particle_system
    def mainloop(self):
        self.particle_system.update(self.game.delta_time)


    def render(self):
        super().render()
        self.particle_system.add_particle(random.randint(0, self.game.width), random.uniform(0, self.game.height),
                                          random.uniform(-1, 1), random.randint(-1, 1), 0, 0, 0, 0, 10, 600,
                                          random.randint(1, 2), random.randint(0, 255), random.randint(0, 255),
                                          random.randint(0, 255), 100, 'square')
        self.particle_system.draw(self.screen)

    def update_placements(self):
        for t in self.text_obj:
            t.delete()
        self.text_obj = []


        self.text_obj.append(
            custom_text.Custom_text(self, self.game.width / 3 - 76.5, self.game.height / 4,
                                    f"   name   |",
                                    text_color='white', font_height=40))
        og_n = self.text_obj[-1].rect

        self.text_obj.append(custom_text.Custom_text(self, og_n.x + og_n.width, og_n.y, '    time    |', text_color='white', center=False, font_height=40))

        og_t = self.text_obj[-1].rect

        self.text_obj.append((custom_text.Custom_text(self, og_t.x + og_t.w, og_t.y, '    fastest lap    ', text_color='white', center=False, font_height=40)))

        og_f = self.text_obj[-1].rect



        for _ in range(len(self.leaderboard_list)):

            if _ == 0:
                if self.leaderboard_list[_].isPlayer:
                    p_placement = f"1st"
                    p_color = (255, 223, 0)
                color = (255, 223, 0)
            elif _ == 1:
                if self.leaderboard_list[_].isPlayer:
                    p_placement = f"2nd"
                    p_color = (192, 192, 192)
                color = (192, 192, 192)
            elif _ == 2:
                if self.leaderboard_list[_].isPlayer:
                    p_placement = f"3rd"
                    p_color = (205, 127, 50)
                color = (205, 127, 50)
            else:
                if self.leaderboard_list[_].isPlayer:
                    p_color = (255, 255, 255)
                    p_placement = f"{_ + 1}th"
                color = (255, 255, 255)

            if self.leaderboard_list[_].isPlayer:
                color2= (0, 255, 255)
            else:
                color2 = (255, 255, 255)



            self.text_obj.append(custom_text.Custom_text(self, og_n.x - 70, self.game.height / 4 + 100 + 75 * _, f"{_ + 1}.",
                                        text_color=color, font_height=40))


            if self.leaderboard_list[_].finished:
                full_time = self.format(self.leaderboard_list[_].full_time)
                fastest_lap = self.format(min(self.leaderboard_list[_].lap_times))
            else:
                full_time = 'Not Finished'
                fastest_lap = "Not Finished"

            if len(self.leaderboard_list[_].name) < 11:
                self.text_obj.append(
                    custom_text.Custom_text(self, og_n.center[0], self.game.height / 4 + 100 + 75 * _, f"{self.leaderboard_list[_].name}",
                                            text_color=color2, font_height=40))
            else:
                self.text_obj.append(
                    custom_text.Custom_text(self, og_n.center[0], self.game.height / 4 + 100 + 75 * _,
                                            f"{self.leaderboard_list[_].name[:11]}",
                                            text_color=color2, font_height=40))

            self.text_obj.append(
                custom_text.Custom_text(self, og_t.center[0], self.game.height / 4 + 100 + 75 * _,
                                        f"{full_time}",
                                        text_color=color2, font_height=40))

            self.text_obj.append(
                custom_text.Custom_text(self, og_f.center[0], self.game.height / 4 + 100 + 75 * _,
                                        f"{fastest_lap}",
                                        text_color=color2, font_height=40))



        self.text_obj.append(custom_text.Custom_text(self, 0, 0, f'Collected coins: {int(self.coin)}', text_color=(255, 223, 0), font_height=25))
        self.text_obj[-1].update_position(960, 800)

        self.text_obj.append(custom_text.Custom_text(self, 614, 850, "You've placed", text_color='white', center=False))
        r = self.text_obj[-1].rect
        self.text_obj.append(
            custom_text.Custom_text(self, r.x + r.width + 20, r.y , f"{p_placement}", text_color=p_color, center=False))
    def format(self, t):
        full_time = t
        milliseconds = int((full_time % 1) * 1000)
        total_seconds = int(full_time)
        minutes, seconds = divmod(total_seconds, 60)

        if total_seconds < 60:
            formatted_time = f"{total_seconds}:{milliseconds:03d}"
        else:
            formatted_time = f"{minutes}:{seconds:02d}:{milliseconds:03d}"
        return formatted_time

class new_leaderboard(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        self.level = None
        self.loaded = False

        self.leaderboard = self.leaderboard = scoreboard.Scoreboard(self, ("name", 'Time', 'Fastest Lap'), [], max_height=550)

        self.button_width_modifier = 45.5 / 256
        self.button_heigh_modifier = 10.4 / 144
        self.button_width = self.game.width * self.button_width_modifier
        self.button_height = self.game.height * self.button_heigh_modifier
        custom_text.Custom_text(self, self.game.width/2, self.game.height/7, 'Leaderboard', text_color=(255, 223, 0))
        custom_button.Button(self, 'back_to_level_selector_no_reload', self.game.width/2 - self.button_width/2, self.game.height*5.5/7, self.button_width, self.button_height, text='Back', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        self.particle_system = self.game.menu_particle_system
    def mainloop(self):
        if not self.loaded:
            self.load_leaderboard()
            self.loaded = 1
        self.particle_system.update(self.game.delta_time)
    def load_leaderboard(self):
        self.leaderboard.delete()
        times = self.db_manager.get_times(self.level)
        self.leaderboard = scoreboard.Scoreboard(self, ("name", 'Time', 'Fastest Lap'), times, max_height=550)

    def render(self):
        super().render()
        self.particle_system.add_particle(random.randint(0, self.game.width), random.uniform(0, self.game.height),
                                          random.uniform(-1, 1), random.randint(-1, 1), 0, 0, 0, 0, 10, 600,
                                          random.randint(1, 2), random.randint(0, 255), random.randint(0, 255),
                                          random.randint(0, 255), 100, 'square')
        self.particle_system.draw(self.screen)

class change_player_name(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        self.particle_system = self.game.menu_particle_system

        self.button_width_modifier = 45.5 / 256
        self.button_heigh_modifier = 10.4 / 144
        self.button_width = self.game.width * self.button_width_modifier
        self.button_height = self.game.height * self.button_heigh_modifier

        custom_text.Custom_text(self, self.game.width / 2, self.game.height / 5,
                                'CHANGE PLAYER NAME', text_color='white',
                                font_height=int(self.game.height * (19 / 216)))


        self.name_input = self.game.player_name
        self.cursor_visible = True
        self.cursor_timer = 0

        self.name_display = custom_text.Custom_text(
            self, self.game.width / 2, self.game.height / 2,
                  self.name_input + '|', text_color='white', font_height=40
        )

        custom_text.Custom_text(
            self, self.game.width / 2, self.game.height / 2 + 60,
            'Type your name and press Enter', text_color=(150, 150, 150), font_height=25
        )

        custom_button.Button(
            self, 'save_player_name', self.game.width / 2 + 7.5,
                                      self.game.height - 150, self.button_width, self.button_height,
            text='SAVE', border_radius=0, color=(26, 26, 26),
            text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2
        )

        custom_button.Button(
            self, 'to_main_menu', self.game.width / 2 - self.button_width - 7.5,
                                  self.game.height - 150, self.button_width, self.button_height,
            text='CANCEL', border_radius=0, color=(26, 26, 26),
            text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2
        )

    def mainloop(self):
        self.particle_system.update(self.game.delta_time)
        self.cursor_timer += self.game.delta_time
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

            if self.cursor_visible:
                self.name_display.update_text(self.name_input + '|')
            else:
                self.name_display.update_text(self.name_input)

    def render(self):
        self.particle_system.add_particle(
            random.randint(0, self.game.width), random.uniform(0, self.game.height),
            random.uniform(-1, 1), random.randint(-1, 1), 0, 0, 0, 0, 10, 600,
            random.randint(1, 2), random.randint(0, 255), random.randint(0, 255),
            random.randint(0, 255), 100, 'square'
        )
        self.particle_system.draw(self.game.screen)
        for obj in self.objects:
            obj.render()

    def events(self, event):
        for obj in self.objects:
            obj.events(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_display('main_menu_display')
            elif event.key == pygame.K_BACKSPACE:
                if len(self.name_input) > 0:
                    self.name_input = self.name_input[:-1]
                    self.name_display.update_text(self.name_input + '|' if self.cursor_visible else self.name_input)
            elif event.key == pygame.K_RETURN:
                self.save_player_name()
            elif event.unicode and len(self.name_input) < 15:  # Limit name length
                # Only allow alphanumeric characters and underscore
                if event.unicode.isalnum() or event.unicode == '_':
                    self.name_input += event.unicode
                    self.name_display.update_text(self.name_input + '|' if self.cursor_visible else self.name_input)

    def save_player_name(self):
        if not self.name_input:
            return
        try:
            stored_name = self.name_input.capitalize()
            for display_name, display_instance in self.game.displays.items():
                if hasattr(display_instance, 'p') and hasattr(display_instance.p, 'player_name'):
                    display_instance.p.player_name = stored_name

            self.db_manager.add_player(stored_name)
            self.game.player_name = self.name_input

            self.game.change_display('main_menu_display')
        except Exception as e:
            print(f"Error saving player name: {e}")
