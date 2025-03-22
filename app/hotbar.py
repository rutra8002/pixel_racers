import pygame
from customObjects import custom_text
import time, datetime
class Hotbar:
    def __init__(self, display):
        self.display = display
        self.game = self.display.game
        self.w, self.h = self.game.hotbar_dimentions # 216px if screen height == 1080px

        self.color = (56, 56, 56)
        self.outline_color = (126, 126, 126)

        self.x = 0
        self.y = self.game.height-self.h

        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

        self.display.objects_in_memory += 1

        self.display.objects.append(self)

        self.stopwatch = StopWatch(self)



    def events(self, event):
        pass


    def after_player_setup(self):
        self.set_laps()
        self.set_player_standing()
        self.nitro_bar = Nitrobar(self.display, self.x + self.w*6/7, self.y+15,25,self.h*2/3,5, (150, 255, 255), (0, 0, 255))
        custom_text.Custom_text(self.display, self.x+self.w*6.05/7, self.y+30 + self.h*2/3, 'Nitro', text_color='white', font_height=15)

    def set_laps(self):
        self.lap_text = custom_text.Custom_text(self.display, self.x + self.w / 7, self.y + self.h / 2.5 + 50,
                                                f'Lap: 1/{self.display.laps}', text_color='white')

    def set_player_standing(self):
        self.player_standing = custom_text.Custom_text(self.display, self.x + self.w*(6.5/7), self.y + self.h / 2,
                                                f'1st', text_color=(255, 215, 0))
    def render(self):
        pygame.draw.rect(self.game.screen, self.color, self.rect, border_radius=20)
        pygame.draw.rect(self.game.screen, self.outline_color, self.rect, width=5, border_radius=20)
        self.nitro_bar.render()


    def mainloop(self):
        self.stopwatch.update_time()
        self.update_player_standing()
        self.nitro_bar.update_bar_height()

    def start_counting_time(self):
        self.stopwatch.start_time = time.time()
        self.stopwatch.start_counting_time = True

    def update_lap_text(self):
        self.lap_text.update_text(f'Lap: {self.display.p.lap}/{self.display.laps}')

    def update_player_standing(self):
        for i, car in enumerate(self.display.leaderboard_list):
            if car.isPlayer:

                if i == 0:
                    text = f"1st"
                    color = (255, 215, 0)
                elif i == 1:
                    text = f"2nd"
                    color = (192, 192, 192)
                elif i == 2:
                    text = f"3rd"
                    color = (205, 127, 50)
                else:
                    text = f"{i + 1}th"
                    color = (255, 255, 255)


                self.player_standing.update_text(text)
                self.player_standing.update_color(color, None)
                break


class StopWatch:
    def __init__(self, hotbar):
        self.hotbar = hotbar
        self.display = self.hotbar.display

        self.x = self.hotbar.x + self.hotbar.w / 7
        self.y = self.hotbar.y + self.hotbar.h / 2.5

        self.text = custom_text.Custom_text(self.display, self.x, self.y, '', text_color='white')

        self.start_time = 0
        self.current_time = 0
        self.start_counting_time = False

    def update_time(self):
        if self.start_counting_time:
            self.current_time = time.time() - self.start_time
            self.current_time = str(datetime.timedelta(seconds=self.current_time))

            split_str = self.current_time.split(":")

            seconds_time = int(float(split_str[2]))
            if seconds_time < 10:
                seconds_time = f'0{seconds_time}'
            else:
                seconds_time = f'{seconds_time}'

            self.text.update_text(f'Time: {split_str[1]}:{seconds_time}')


import pygame

class Nitrobar:
    def __init__(self, display, x, y, width, max_height, pixel_size, start_color, end_color):
        self.display = display
        self.screen = self.display.screen
        self.x = int(x)
        self.y = int(y)
        self.width = width
        self.max_height = max_height
        self.pixel_size = pixel_size
        self.start_color = start_color
        self.end_color = end_color

        self.update_bar_height()

    def lerp_color(self, color1, color2, t):
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t),
        )

    def render(self):
        bottom_y = int(self.y + self.max_height)

        adjusted_height = (self.height // self.pixel_size) * self.pixel_size
        start_y = bottom_y - adjusted_height


        for y in range(start_y, bottom_y, self.pixel_size):
            for x in range(self.x, self.x + self.width, self.pixel_size):
                t = (y - start_y) / adjusted_height if adjusted_height > 0 else 0
                color = self.lerp_color(self.start_color, self.end_color, t)
                pygame.draw.rect(self.screen, color, (x, y, self.pixel_size, self.pixel_size))


        pygame.draw.rect(self.screen, (26, 26, 26), (self.x, self.y, self.width, self.max_height), width=5)

    def update_bar_height(self):
        self.height = int(self.max_height * self.display.p.nitroAmount / 100)
