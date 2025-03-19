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

    def set_laps(self):
        self.lap_text = custom_text.Custom_text(self.display, self.x + self.w / 7, self.y + self.h / 2.5 + 50,
                                                f'Lap: 1/{self.display.laps}', text_color='white')

    def set_player_standing(self):
        self.player_standing = custom_text.Custom_text(self.display, self.x + self.w*(6.5/7), self.y + self.h / 2,
                                                f'1st', text_color=(255, 215, 0))
    def render(self):
        pygame.draw.rect(self.game.screen, self.color, self.rect, border_radius=20)
        pygame.draw.rect(self.game.screen, self.outline_color, self.rect, width=5, border_radius=20)


    def mainloop(self):
        self.stopwatch.update_time()
        self.update_player_standing()

    def start_counting_time(self):
        self.stopwatch.start_time = time.time()
        self.stopwatch.start_counting_time = True

    def update_lap_text(self):
        self.lap_text.update_text(f'Lap: {self.display.p.lap}/5')

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
