from customObjects import custom_images, custom_text, custom_button
import random
import pygame
import json

# Copyright (C) 2025  Hohenzoler
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

class basic_display:
    def __init__(self, game):
        self.game = game
        self.screen = self.game.screen
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

class map_display(basic_display):
    def __init__(self, game):
        self.cx, self.cy = 0, 0
        basic_display.__init__(self, game)
        self.map = [[1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 1, 1],
                    [1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 1, 1],
                    [1, 0, 0, 0, 1, 1],
                    [1, 0, 0, 0, 1, 1],
                    [1, 0, 0, 0, 1, 1],
                    [1, 1, 1, 1, 1, 1]]
        self.block_width = self.game.width // len(self.map[0])
        self.block_height = self.game.height // len(self.map)

        self.export_button = custom_button.Button(self.game, self, 10, 10, 100, 50)
        self.export_button.color = (0, 255, 0)

    def mainloop(self):
        self.handle_mouse_events()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.cy += 5
        if keys[pygame.K_s]:
            self.cy -= 5
        if keys[pygame.K_a]:
            self.cx += 5
        if keys[pygame.K_d]:
            self.cx -= 5


    def render(self):
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                color = (255, 255, 255) if self.map[y][x] == 1 else (0, 0, 0)
                pygame.draw.rect(self.screen, color, (x * self.block_width + self.cx, y * self.block_height + self.cy, self.block_width, self.block_height))
        self.export_button.render()

    def events(self, event):
        for obj in self.objects:
            obj.events(event)
        if event.type == pygame.MOUSEBUTTONDOWN and self.export_button.rect.collidepoint(event.pos):
            self.export_map()

    def handle_mouse_events(self):
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            self.place_block()
        elif mouse_pressed[2]:
            self.remove_block()

    def place_block(self):
        x, y = pygame.mouse.get_pos()
        x -= self.cx
        y -= self.cy
        grid_x, grid_y = x // self.block_width, y // self.block_height
        if 0 <= grid_x < len(self.map[0]) and 0 <= grid_y < len(self.map):
            self.map[grid_y][grid_x] = 1

    def remove_block(self):
        x, y = pygame.mouse.get_pos()
        x -= self.cx
        y -= self.cy
        grid_x, grid_y = x // self.block_width, y // self.block_height
        if 0 <= grid_x < len(self.map[0]) and 0 <= grid_y < len(self.map):
            self.map[grid_y][grid_x] = 0

    def export_map(self):
        with open('map.json', 'w') as f:
            json.dump(self.map, f)



class main_menu_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        self.title_screen_text = custom_text.Custom_text(self, 500, 300, 'VROOM! VROOM!', text_color='white', font_height=100)
        self.to_game_button = custom_button.Button(self, 'to_game_display', 123, 543, 250, 67, text='Game goes brrrr',)
        self.to_map_maker_button = custom_button.Button(self, 'to_map_maker_display', 692, 715, 250, 67, text='Game goes brrrr', )

    def mainloop(self):
        pass




