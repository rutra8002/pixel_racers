import cv2
import pygame, json
from customObjects import custom_text

class Button:  # A button class
    def __init__(self, display, action, x, y, width, height, color=(255, 255, 255), text=None, text_color='black', outline_color=None, outline_width=5, append=True, border_radius = 10):  # Getting all the parameters of the button

        self.action = action
        self.display = display
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.append = append
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)  # Creating a rect object

        self.display.objects_in_memory += 1
        if self.append:
            self.display.objects.append(self)  # Adding self to objects of the screen


        self.text = text
        if self.text != None:  # if there is text it's put on the button
            self.text = custom_text.Custom_text(self.display, self.x + self.width / 2, self.y + self.height / 2, text, font=None,
                                   font_height=int(self.height // 3), text_color=text_color,)

        self.outline_color = outline_color
        self.outline_width = outline_width
        self.border_radius = border_radius

    def render(self):  # Rendering a button on screen
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.display.screen, self.get_hover_color(), self.rect, border_radius=self.border_radius)
        else:
            pygame.draw.rect(self.display.screen, self.color, self.rect, border_radius=self.border_radius)

        # pygame.draw.line(self.display.screen, (0, 255, 0), (self.x + self.width/2, self.y), (self.x + self.width/2, self.y + self.height))
        # pygame.draw.line(self.display.screen, (0, 255, 0), (self.x, self.y + self.height/2),
        #                  (self.x + self.width, self.y + self.height/2))

        if self.outline_color != None:
            pygame.draw.rect(self.display.screen, self.outline_color, self.rect, self.outline_width, border_radius=self.border_radius)

    def events(self, event):  # Checks events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):  # Checks if the button has been pressed
            if self.action == 'to_level_selector':
                self.display.game.change_display('level_selector')
            elif self.action == 'to_map_maker_display':
                self.display.game.change_display('map_display')
            elif self.action == "export_map":
                self.display.game.current_display.export_map()
            elif self.action == 'quit':
                self.display.game.run = False
            elif self.action == 'settings':
                self.display.game.change_display('settings_display')
            elif self.action == 'credits':
                self.display.game.change_display('credits')
                self.display.game.sound_manager.play_sound('Credits')
                self.display.game.displays['credits'].last_fps = self.display.game.fps
                self.display.game.displays['credits'].video = cv2.VideoCapture('videos/credits.mp4')
                self.display.game.fps = 30
            elif self.action == 'to_main_menu':
                self.display.game.change_display('main_menu_display')
            elif self.action == 'main_menu_credits':
                self.display.game.fps = self.display.game.displays['credits'].last_fps
                self.display.game.displays['credits'].video.release()
                self.display.game.sound_manager.stop_sound('Credits')
                self.display.game.change_display('main_menu_display')
            elif self.action == 'play_course':
                course_to_play = self.display.game.displays['level_selector'].currently_selected
                self.display.game.change_display(list(self.display.game.displays['level_selector'].levels.keys())[course_to_play])
            elif self.action == 'back_to_level_selector':
                self.display.game.displays['level_selector'].reload_maps()
                self.display.game.change_display('level_selector')
            elif self.action == 'move_selection_to_left':
                lvl_display = self.display.game.displays['level_selector']
                if lvl_display.currently_selected > 0:
                    lvl_display.currently_selected -= 1
                    lvl_display.update_surfaces(-1)
            elif self.action == 'move_selection_to_right':
                lvl_display = self.display.game.displays['level_selector']
                if lvl_display.currently_selected < len(list(lvl_display.levels.values())) - 1:
                    lvl_display.currently_selected += 1
                    lvl_display.update_surfaces(1)
            elif self.action == 'to_map_maker_menu':
                self.display.game.change_display('map_maker_menu')

            elif self.action == 'new_map':
                self.display.game.displays['map_display'].reset_map()
                self.display.game.change_display('map_display')

            elif self.action == 'change_vehicle':
                self.display.game.change_display('change_vehicle')

            elif self.action == 'move_selected_car_to_left':
                self.display.move_selected_car_to_left()

            elif self.action == 'move_selected_car_to_right':
                self.display.move_selected_car_to_right()

            elif self.action == 'select_car':
                self.display.game.player_model = self.display.selected_car_model
                self.display.game.update_player_model()
                self.display.game.change_display('main_menu_display')
            elif self.action == "export_png":
                self.display.export_png()
            elif 'edit_map_titled_' in self.action:
                with open(f"{self.display.game.map_dir}/{self.action.removeprefix('edit_map_titled_')}.json", 'r') as f:
                    map_data = json.load(f)
                    self.display.game.displays['map_display'].load_map(map_data)
                    f.close()
                self.display.game.change_display('map_display')
            else:
                print('No action assigned to this button')

    def delete(self):
        self.text.delete()
        self.display.objects_in_memory -= 1
        if self.append == True:
            self.display.objects.remove(self)
        del self

    def get_hover_color(self):
        biggest = max(self.color)
        if biggest <= 225:
            return tuple(color + 30 for color in self.color)
        else:
            return tuple(color - 30 if color >= 30 else 0 for color in self.color)

    def update_color(self, color):
        self.outline_color = color
        self.text.update_color(color, None)

    def update_text(self, text):
        self.text.update_text(text)

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update_position(self, x, y):
        self.x = x
        self.y = y
        self.update_rect()

        if self.text != None:  # if there is text it's put on the button
            self.text.update_position(self.x + self.width / 2, self.y + self.height / 2,)

    def update_pos_and_size(self, x, y, w, h):
        self.width = w
        self.height = h
        self.update_position(x, y)