from customObjects import custom_images, custom_text, custom_button
import random
import math as lolekszcz
import pygame
import json
from app import player, enemy, obstacle, images
from particle_system import ParticleSystem
from datetime import datetime
import os
import json

class basic_display:
    def __init__(self, game):
        self.game = game
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
        self.import_map()

        self.particle_system = ParticleSystem()
        self.block_width = self.game.width // len(self.map[0])
        self.block_height = self.game.height // len(self.map)
        self.p = player.Player(self, images.player, (500, 500), True)
        # self.e = player.Player(self, images.enemy, (200, 200), True)
        self.e = enemy.Enemy(self)
        self.obstacles = []
        # self.enemy1 = enemy.Enemy(self)
        # self.objects.append(self.enemy1)
        self.objects.append(self.p)
        self.objects.append(self.e)
        self.map_surface = pygame.Surface((self.game.width, self.game.height))
        self.draw_map()
        self.map_surface.set_colorkey(self.bgColor)
        self.mapMask = pygame.mask.from_surface(self.map_surface)
        # for y in range(len(self.map)):
        #     for x in range(len(self.map[y])):
        #         if self.map[y][x] == 1:
        #             color = (255, 255, 255)
        #         elif self.map[y][x] == 2:
        #             color = (0, 0, 0)
        #         elif self.map[y][x] == 3:
        #             color = (128, 128, 128)
        #         else:
        #             color = (26, 26, 26)


    def draw_map(self):
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
                pygame.draw.rect(self.map_surface, color,
                                 (x * self.block_width, y * self.block_height, self.block_width, self.block_height))
    def import_map(self):
        with open(f"{self.game.map_dir}\{self.difficulty}.json", 'r') as f:
            map_data = json.load(f)
            self.map = map_data
            f.close()


    def render(self):
        self.screen.fill(self.bgColor)
        self.screen.blit(self.map_surface, (0, 0))
        self.particle_system.draw(self.screen)
        for obj in self.objects:
            obj.render()
        for o in self.obstacles:
            o.render()

    def events(self, event):
        for obj in self.objects:
            obj.events(event)
        for o in self.obstacles:
            o.events(event)

        if event.type == pygame.KEYDOWN:
            angle = lolekszcz.radians(self.p.rotation)
            spawn_x = self.p.x - (50 * lolekszcz.cos(angle))
            spawn_y = self.p.y + (50 * lolekszcz.sin(angle))
            if event.key == pygame.K_ESCAPE:
                self.game.change_display('pause_display')
            if event.key == pygame.K_c:
                self.obstacles.append(obstacle.Obstacle(self, spawn_x, spawn_y, 'spikes', self.p.rotation - 90))
            if event.key == pygame.K_v:
                self.obstacles.append(obstacle.Obstacle(self, spawn_x, spawn_y, 'barrier', self.p.rotation - 90))


    def mainloop(self):
        self.particle_system.update(self.game.delta_time)
        self.p.loop()
        self.e.loop()
        # pygame.draw.rect(self.screen, (255, 255, 255), (600, 200, 50, 700))

class map_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        self.cx, self.cy = 0, 0
        self.zoom_level = 1.0
        self.tool = 1

        self.player_position = None
        self.player_width = 50
        self.player_height = 25

        self.gcd = 5
        self.temp_width = self.game.width // self.gcd
        self.temp_height = self.game.height // self.gcd
        # print(self.game.width // self.gcd, self.game.height // self.gcd)
        self.map = [[0] * self.temp_width for _ in range(self.temp_height)]

        self.block_width = self.gcd
        self.block_height = self.gcd

        self.brush_size = 1

        self.brushtext = custom_text.Custom_text(self, 10, 70, f'Brush size: {self.brush_size}', text_color='white', font_height=30, center=False)
        self.tooltext = custom_text.Custom_text(self, 10, 100, f'Tool: {self.tool}', text_color='white', font_height=30, center=False)
        # self.block_width = self.game.width // len(self.map[0])
        # self.block_height = self.game.height // len(self.map)

        self.export_button = custom_button.Button(self, "export_map", 10, 10, 100, 50, text="Export map", text_color=(0, 255, 0), color=(255, 0, 0), border_radius=0)


        self.dragging = False
        self.start_x = 0
        self.start_y = 0
        self.start_cx = 0
        self.start_cy = 0

    def reset_map(self):
        self.gcd = 5
        self.temp_width = self.game.width // self.gcd
        self.temp_height = self.game.height // self.gcd

        self.map = [[0] * self.temp_width for _ in range(self.temp_height)]


    def load_map(self, map):
        self.map = map


        self.temp_width = len(self.map[0])
        self.temp_height = len(self.map)

        self.gdc = self.temp_width / self.game.width




    def mainloop(self):

        self.delta_time = self.game.delta_time
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.cy += 500 * self.delta_time
        if keys[pygame.K_s]:
            self.cy -= 500 * self.delta_time
        if keys[pygame.K_a]:
            self.cx += 500 * self.delta_time
        if keys[pygame.K_d]:
            self.cx -= 500 * self.delta_time
        self.brushtext.update_text(f'Brush size: {self.brush_size}')
        self.tooltext.update_text(f'Tool: {self.tool}')


    def render(self):
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x] == 1:
                    color = self.wall_color
                elif self.map[y][x] == 2:
                    color = self.oil_color
                elif self.map[y][x] == 3:
                    color = self.gravel_color
                elif self.map[y][x] == 4:
                    color = self.ice_color
                else:
                    color = self.asphalt_color
                pygame.draw.rect(self.screen, color, (x * self.block_width + self.cx, y * self.block_height + self.cy, self.block_width, self.block_height))
        if self.player_position:
            player_width_scaled = self.player_width * self.zoom_level
            player_height_scaled = self.player_height * self.zoom_level
            pygame.draw.rect(self.screen, (255, 0, 0), (self.player_position[0] * self.block_width + self.cx, self.player_position[1] * self.block_height + self.cy, player_width_scaled, player_height_scaled))
        pygame.draw.rect(self.screen, (155, 0, 0),(self.cx, self.cy, self.block_width*self.temp_width, self.block_height*self.temp_height), 2)


        for obj in self.objects:
            obj.render()

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
            elif event.key == pygame.K_p:
                self.tool = 'p'
            elif event.key == pygame.K_0:
                self.map = [[0] * self.temp_width for _ in range(self.temp_height)]
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # Increase brush size
                self.brush_size = min(self.brush_size + 1, max(self.temp_width, self.temp_height))
            elif event.key == pygame.K_MINUS:  # Decrease brush size
                self.brush_size = max(self.brush_size - 1, 1)
        self.handle_mouse_events(event)
        self.handle_zoom(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_display('map_maker_menu')

    def handle_mouse_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT  or (event.type == pygame.MOUSEMOTION and event.buttons[0]):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = int((mouse_x - self.cx) // self.block_width)
            grid_y = int((mouse_y - self.cy) // self.block_height)
            if self.tool == 'p':
                self.player_position = (grid_x, grid_y)
            else:
                for dy in range(-self.brush_size // 2, self.brush_size // 2 + 1):
                    for dx in range(-self.brush_size // 2, self.brush_size // 2 + 1):
                        if 0 <= grid_x + dx < self.temp_width and 0 <= grid_y + dy < self.temp_height:
                            self.map[grid_y + dy][grid_x + dx] = self.tool
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_RIGHT or (event.type == pygame.MOUSEMOTION and event.buttons[2]):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = int((mouse_x - self.cx) // self.block_width)
            grid_y = int((mouse_y - self.cy) // self.block_height)
            for dy in range(-self.brush_size // 2, self.brush_size // 2 + 1):
                for dx in range(-self.brush_size // 2, self.brush_size // 2 + 1):
                    if 0 <= grid_x + dx < self.temp_width and 0 <= grid_y + dy < self.temp_height:
                        self.map[grid_y + dy][grid_x + dx] = 0
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_MIDDLE:
            self.dragging = True
            self.start_x, self.start_y = event.pos
            self.start_cx = self.cx
            self.start_cy = self.cy
        elif event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_MIDDLE:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            current_x, current_y = event.pos
            delta_x = current_x - self.start_x
            delta_y = current_y - self.start_y
            self.cx = self.start_cx + delta_x
            self.cy = self.start_cy + delta_y
    def handle_zoom(self, event):
        if event.type == pygame.MOUSEWHEEL:
            old_block_width = self.block_width
            old_block_height = self.block_height

            if event.y > 0:
                self.zoom_level *= 1.1
            elif event.y < 0 and self.block_width > 1 and self.block_height > 1:
                self.zoom_level /= 1.1
            self.block_width = int((self.game.width // len(self.map[0])) * self.zoom_level)
            self.block_height = int((self.game.height // len(self.map)) * self.zoom_level)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.cx -= (mouse_x - self.cx) * (self.block_width / old_block_width - 1)
            self.cy -= (mouse_y - self.cy) * (self.block_height / old_block_height - 1)

    def export_map(self):
        if not os.path.exists('maps'):
            os.makedirs('maps')
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'maps/map_{current_time}.json'
        # map_data = {
        #     'map': self.map,
        #     'player_position': self.player_position
        # }
        map_data = self.map
        with open(filename, 'w') as f:
            json.dump(map_data, f)
            f.close()
        self.game.displays['level_selector'].load_maps()
        self.game.change_display('map_maker_menu')



class main_menu_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)

        self.amount_of_buttons = 4
        self.button_padding = self.game.height * (1/96)
        self.button_width_modifier = 45.5/256
        self.button_heigh_modifier = 10.4/144
        self.button_width = self.game.width*self.button_width_modifier
        self.button_height = self.game.height*self.button_heigh_modifier

        custom_text.Custom_text(self, self.game.width/2, self.game.height/5, 'VROOM!\n    VROOM!', text_color='white', font_height=int(self.game.height*(19/216)))
        custom_button.Button(self, 'to_level_selector', self.button_padding, self.game.height + (- self.button_padding - self.button_height) * self.amount_of_buttons, self.button_width, self.button_height, text='Game goes brrrr', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
        custom_button.Button(self, 'settings', self.button_padding, self.game.height + (- self.button_padding - self.button_height) * (self.amount_of_buttons - 1), self.button_width, self.button_height, text='Settings', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
        custom_button.Button(self, 'to_map_maker_menu', self.button_padding, self.game.height + (- self.button_padding - self.button_height) * (self.amount_of_buttons - 2), self.button_width, self.button_height, text='Map-maker goes brrrr', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
        custom_button.Button(self, 'quit', self.button_padding, self.game.height + (- self.button_padding - self.button_height) * (self.amount_of_buttons - 3), self.button_width, self.button_height, text='Quit', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        self.particle_system = self.game.menu_particle_system

    def render(self):
        self.particle_system.add_particle(random.randint(0, self.game.width), random.uniform(0, self.game.height), random.uniform(-1, 1), random.randint(-1, 1), 0, 0, 0, 0, 10, 600, random.randint(1, 2), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 100, 'square')
        self.particle_system.draw(self.screen)

        for obj in self.objects:
            obj.render()


    def mainloop(self):
        self.particle_system.update(self.game.delta_time)

class settings_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)

        self.button_width_modifier = 45.5 / 256
        self.button_heigh_modifier = 10.4 / 144
        self.button_width = self.game.width * self.button_width_modifier
        self.button_height = self.game.height * self.button_heigh_modifier

        custom_text.Custom_text(self, self.game.width/2, self.game.height/8, 'SETTINGS', text_color='white', font_height=int(self.game.height*(19/216)))
        custom_text.Custom_text(self, self.game.width/2, self.game.height - 22.5, self.game.version, text_color='white', font_height=25)
        custom_button.Button(self, 'to_level_selector', self.game.width/2, self.game.height/2, self.button_width, self.button_height, text='Back to menu', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        self.particle_system = self.game.menu_particle_system

    def render(self):
        self.particle_system.add_particle(random.randint(0, self.game.width), random.uniform(0, self.game.height),
                                          random.uniform(-1, 1), random.randint(-1, 1), 0, 0, 0, 0, 10, 600,
                                          random.randint(1, 2), random.randint(0, 255), random.randint(0, 255),
                                          random.randint(0, 255), 100, 'square')
        self.particle_system.draw(self.screen)

        for obj in self.objects:
            obj.render()


    def mainloop(self):
        self.particle_system.update(self.game.delta_time)

    def events(self, event):
        for obj in self.objects:
            obj.events(event)



class pause_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        custom_text.Custom_text(self, self.game.width/2, self.game.height - 22.5, self.game.version, text_color='white', font_height=25)
        custom_button.Button(self, 'back_to_level_selector', self.game.width / 2, self.game.height / 2, 350, 80,
                             text='Back to menu', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150),
                             outline_color=(50, 50, 50), outline_width=2)


    def mainloop(self):
        pass

    def events(self, event):
        for obj in self.objects:
            obj.events(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_display(list(self.game.displays['level_selector'].levels.keys())[self.game.displays['level_selector'].currently_selected])


class level_selector(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        custom_text.Custom_text(self, self.game.width/2, self.game.height/5, 'SELECT A COURSE', text_color='white', font_height=int(self.game.height*(19/216)))

        self.button_width_modifier = 45.5 / 256
        self.button_heigh_modifier = 10.4 / 144
        self.button_width = self.game.width * self.button_width_modifier
        self.button_height = self.game.height * self.button_heigh_modifier

        custom_button.Button(self, 'play_course', self.game.width/2 + 7.5, self.game.height - 150, self.button_width, self.button_height, text='PLAY', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
        custom_button.Button(self, 'to_main_menu', self.game.width / 2 - self.button_width - 7.5, self.game.height - 150,
                             self.button_width, self.button_height, text='BACK', border_radius=0, color=(26, 26, 26),
                             text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        self.particle_system = self.game.menu_particle_system

        self.descaling_factor = 3
        self.currently_selected = 0

        self.selected_surface_width = self.game.width/self.descaling_factor
        self.selected_surface_height = self.game.height/self.descaling_factor

        self.not_selected_surface_width = self.selected_surface_width/2
        self.not_selected_surface_height = self.selected_surface_height/2

        custom_button.Button(self, 'move_selection_to_left', self.game.width / 2 - self.button_width - 7.5,
                             (self.game.height - 150 - (self.game.height/2 - self.selected_surface_height/2 + self.selected_surface_height) - self.button_height)/2 + (self.game.height/2 - self.selected_surface_height/2 + self.selected_surface_height),
                             self.button_width, self.button_height, text='<-', border_radius=0, color=(26, 26, 26),
                             text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)

        custom_button.Button(self, 'move_selection_to_right', self.game.width / 2 + 7.5,
                             (self.game.height - 150 - (
                                         self.game.height / 2 - self.selected_surface_height / 2 + self.selected_surface_height) - self.button_height) / 2 + (
                                         self.game.height / 2 - self.selected_surface_height / 2 + self.selected_surface_height),
                             self.button_width, self.button_height, text='->', border_radius=0, color=(26, 26, 26),
                             text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)


    def mainloop(self):
        self.particle_system.update(self.game.delta_time)

    def render(self):
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
            self.game.displays[lvl] = game_display(self.game, lvl)
            if i - self.currently_selected == 0:
                sur = pygame.transform.scale(self.game.displays[lvl].map_surface, (self.selected_surface_width, self.selected_surface_height))
            else:
                sur = pygame.transform.scale(self.game.displays[lvl].map_surface,
                                             (self.not_selected_surface_width, self.not_selected_surface_height))
            self.levels[lvl] = sur

    def reload_maps(self):
        try:
            for i, lvl in enumerate(list(self.levels.keys())):
                difficulty = self.game.displays[lvl].difficulty
                del self.game.displays[lvl]
                self.game.displays[lvl] = game_display(self.game, difficulty)
                if i - self.currently_selected == 0:
                    sur = pygame.transform.scale(self.game.displays[lvl].map_surface,
                                                 (self.selected_surface_width, self.selected_surface_height))
                else:
                    sur = pygame.transform.scale(self.game.displays[lvl].map_surface, (self.not_selected_surface_width, self.not_selected_surface_height))
                self.levels[lvl] = sur

        except:
            self.load_maps()

    def update_surfaces(self, dir): # if changing to the left dir = -1, if changing to the right dir = 1
        for i, lvl in enumerate(list(self.levels.values())):
            if i - self.currently_selected == 0:
                del lvl
                sur = pygame.transform.scale(self.game.displays[list(self.levels.keys())[i]].map_surface,
                                             (self.selected_surface_width, self.selected_surface_height))
                self.levels[list(self.levels.keys())[i]] = sur

                sur = pygame.transform.scale(self.game.displays[list(self.levels.keys())[i - dir]].map_surface,
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
                        print(l - self.lists_len)
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
