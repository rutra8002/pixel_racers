from customObjects import custom_images, custom_text, custom_button
import random
import pygame
import json
from app import player, enemy, parkinson

class basic_display:
    def __init__(self, game):
        self.game = game
        self.screen = self.game.screen
        self.screenWidth, self.screenHeight = self.game.width, self.game.height
        self.objects = []
        self.objects_in_memory = 0


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
    def __init__(self, game):
        basic_display.__init__(self, game)

        self.particle_system = parkinson.ParticleSystem()

        self.p = player.Player(self)
        self.objects.append(self.p)
        self.enemy1 = enemy.Enemy(self)
        self.objects.append(self.enemy1)

    def render(self):
        self.particle_system.draw(self.screen)
        for obj in self.objects:
            obj.render()


    def mainloop(self):
        self.particle_system.update()
        # pygame.draw.rect(self.screen, (255, 255, 255), (600, 200, 50, 700))



class map_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        self.cx, self.cy = 0, 0
        self.zoom_level = 1.0
        self.map = [[0] * 100 for _ in range(100)]
        self.block_width = self.game.width // len(self.map[0])
        self.block_height = self.game.height // len(self.map)

        self.export_button = custom_button.Button(self, "export_map", 10, 10, 100, 50, text="Export map", text_color=(0, 255, 0), color=(255, 0, 0), border_radius=0)

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


    def render(self):
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                color = (255, 255, 255) if self.map[y][x] == 1 else (0, 0, 0)
                pygame.draw.rect(self.screen, color, (x * self.block_width + self.cx, y * self.block_height + self.cy, self.block_width, self.block_height))
        pygame.draw.rect(self.screen, (155, 0, 0),(self.cx, self.cy, self.block_width*100, self.block_height*100), 2)
        for obj in self.objects:
            obj.render()

    def events(self, event):
        for obj in self.objects:
            obj.events(event)
        self.handle_mouse_events(event)
        self.handle_zoom(event)

    def handle_mouse_events(self, event):
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            self.place_block()
        elif mouse_pressed[2]:
            self.remove_block()

    def place_block(self):
        x, y = pygame.mouse.get_pos()
        x -= self.cx
        y -= self.cy
        x, y = int(x), int(y)
        grid_x, grid_y = x // self.block_width, y // self.block_height
        if 0 <= grid_x < len(self.map[0]) and 0 <= grid_y < len(self.map):
            self.map[grid_y][grid_x] = 1

    def remove_block(self):
        x, y = pygame.mouse.get_pos()
        x -= self.cx
        y -= self.cy
        x, y = int(x), int(y)
        grid_x, grid_y = x // self.block_width, y // self.block_height
        if 0 <= grid_x < len(self.map[0]) and 0 <= grid_y < len(self.map):
            self.map[grid_y][grid_x] = 0

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
        with open('map.json', 'w') as f:
            json.dump(self.map, f)
        self.export_button.update_text('Exported!')



class main_menu_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)

        self.amount_of_buttons = 4
        self.button_padding = 15
        self.title_screen_text = custom_text.Custom_text(self, self.game.width/2, self.game.height/3.8, 'VROOM!\n    VROOM!', text_color='white', font_height=95)
        self.to_game_button = custom_button.Button(self, 'to_game_display', self.button_padding, self.game.height + (- self.button_padding - 80) * self.amount_of_buttons, 350, 80, text='Game goes brrrr', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
        self.to_map_maker_button = custom_button.Button(self, '', self.button_padding, self.game.height + (- self.button_padding - 80) * (self.amount_of_buttons - 1), 350, 80, text='Settings', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
        self.to_map_maker_button = custom_button.Button(self, 'to_map_maker_display', self.button_padding, self.game.height + (- self.button_padding - 80) * (self.amount_of_buttons - 2), 350, 80, text='Map-maker goes brrrr', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)
        self.to_map_maker_button = custom_button.Button(self, 'quit', self.button_padding, self.game.height + (- self.button_padding - 80) * (self.amount_of_buttons - 3), 350, 80, text='Quit', border_radius=0, color=(26, 26, 26), text_color=(150, 150, 150), outline_color=(50, 50, 50), outline_width=2)


    def mainloop(self):
        pass




