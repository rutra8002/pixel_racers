from customObjects import custom_images, custom_text, custom_button

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

class main_menu_display(basic_display):
    def __init__(self, game):
        basic_display.__init__(self, game)
        self.title_screen_text = custom_text.Custom_text(self, 500, 300, 'VROOM! VROOM!', text_color='white', font_height=100)
        self.to_game_button = custom_button.Button(self, 'to_game_display', 123, 543, 250, 67, text='Game goes brrrr',)
        self.to_map_maker_button = custom_button.Button(self, 'to_map_maker_display', 692, 715, 250, 67, text='Game goes brrrr', )

    def mainloop(self):
        pass




