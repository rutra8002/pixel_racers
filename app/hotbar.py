import pygame
from customObjects import custom_text, custom_images
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
        self.inv = Inventory(self.display, self.x+self.w*5/7, self.y+15, 150, 150)
        self.undercarge = Undercarge(self.display, self.w/1.6, self.y, 300, 180)

        try:
            player_name = self.display.p.player_name if hasattr(self.display, 'p') else 'jeff'
        except AttributeError:
            player_name = 'jeff'

        self.player_name_text = custom_text.Custom_text(
            self.game, self.w / 2, self.h / 2, player_name,
            text_color=(255, 255, 255), font_height=30, append=False
        )


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
        self.inv.render()
        self.undercarge.render()
        self.player_name_text.render()

        if hasattr(self, 'coin_text'):
            self.coin_text.render()


    def mainloop(self):
        self.stopwatch.update_time()
        self.update_coin_display()
        self.update_player_standing()
        self.nitro_bar.update_bar_height()
        self.player_name_text.update_text(self.display.p.player_name)

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

    def update_coin_display(self):
        # Find the player car
        player_car = None
        for car in self.display.cars:
            if car.isPlayer:
                player_car = car
                break

        if player_car:
            # Get total coins from database
            total_coins = self.display.db_manager.get_coins()

            # Create or update coin text
            if hasattr(self, 'coin_text'):
                self.coin_text.update_text(f"Coins: {total_coins}")
            else:
                self.coin_text = custom_text.Custom_text(
                    self.display,
                    self.display.game.width - 100,
                    25,
                    f"Coins: {total_coins}",
                    font_height=20,
                    text_color=(255, 215, 0)
                )


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


class Inventory:
    def __init__(self, display, x, y, width, height):
        self.display = display
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen = self.display.screen
        self.inventory = self.display.p.inventory

        self.big_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.small_rect = pygame.Rect(self.x+self.width+10, self.y+self.height/2, self.width/2, self.height/2)

        self.big_img_rect = [self.big_rect[0] + self.big_rect[2]/2, self.big_rect[1] + self.big_rect[3]/2, self.big_rect[2]-45, self.big_rect[3]-45]
        self.small_img_rect = [self.small_rect[0] + self.small_rect[2]/2, self.small_rect[1] + self.small_rect[3]/2, self.small_rect[2]-23,
                                                    self.small_rect[3]-23]


        self.spike_img = custom_images.Custom_image(self.display, 'images/spikes.png', self.big_img_rect[0], self.big_img_rect[1], self.big_img_rect[2], self.big_img_rect[3], append=False)
        self.barrier_img = custom_images.Custom_image(self.display, 'images/barrier.png', self.big_img_rect[0], self.big_img_rect[1], self.big_img_rect[2], self.big_img_rect[3], append=False)
        self.strenght_img = custom_images.Custom_image(self.display, 'images/strength.png', self.big_img_rect[0], self.big_img_rect[1], self.big_img_rect[2], self.big_img_rect[3], append=False)
        self.heal_img = custom_images.Custom_image(self.display, 'images/tirehealth.png', self.big_img_rect[0], self.big_img_rect[1], self.big_img_rect[2], self.big_img_rect[3], append=False)

        self.small_spike_img = custom_images.Custom_image(self.display, 'images/spikes.png', self.small_img_rect[0], self.small_img_rect[1], self.small_img_rect[2],
                                                    self.small_img_rect[3], append=False)
        self.small_barrier_img = custom_images.Custom_image(self.display, 'images/barrier.png', self.small_img_rect[0], self.small_img_rect[1], self.small_img_rect[2],
                                                    self.small_img_rect[3], append=False)
        self.small_strenght_img = custom_images.Custom_image(self.display, 'images/strength.png', self.small_img_rect[0], self.small_img_rect[1], self.small_img_rect[2],
                                                    self.small_img_rect[3], append=False)
        self.small_heal_img = custom_images.Custom_image(self.display, 'images/tirehealth.png', self.small_img_rect[0], self.small_img_rect[1], self.small_img_rect[2],
                                                    self.small_img_rect[3], append=False)

        self.big_img = [self.strenght_img, self.barrier_img, self.spike_img, self.heal_img]
        self.small_img = [self.small_strenght_img, self.small_barrier_img, self.small_spike_img, self.small_heal_img]



    def render(self):
        pygame.draw.rect(self.screen, (26, 26, 26), self.big_rect, border_radius=20)
        pygame.draw.rect(self.screen, (126, 126, 126), self.big_rect, border_radius=20, width=5)
        pygame.draw.rect(self.screen, (26, 26, 26), self.small_rect, border_radius=10)
        pygame.draw.rect(self.screen, (126, 126, 126),
                         self.small_rect,
                         border_radius=10, width=3)

        if len(self.inventory) > 1:
            self.big_img[self.inventory[0] - 1].render()
            self.small_img[self.inventory[1] - 1].render()

        elif len(self.inventory) == 1:
            self.big_img[self.inventory[0] - 1].render()


class Undercarge:
    def __init__(self, display, x, y, width, height):
        self.display = display
        self.screen = self.display.screen
        self.x = x
        self.y = y
        self.w = width
        self.h = height

        self.xs = []
        self.img = None

        self.update()


    def render(self):
        if self.img != None:

            pygame.draw.rect(self.screen, (76, 76, 76), (self.x - self.w / 2, self.y + 10, self.w, self.h - 20),
                             border_radius=20)
            pygame.draw.rect(self.screen, (126, 126, 126), (self.x - self.w / 2, self.y + 10, self.w, self.h - 20),
                             border_radius=20, width=5)

            self.img.render()

            for _ in range(self.display.p.deadTires):
                self.xs[_].render()


    def update(self):
        if self.img != None:
            self.img.delete()
            for x in self.xs:
                x.delete()

        self.xs = []
        self.img = None
        if self.display.p.tireAmount == 4:
            self.img = custom_images.Custom_image(self.display, 'images/4-wheels.png', self.x, self.y + self.h / 2,
                                                  self.w, self.h, append=False)
            self.xs.append(
                custom_images.Custom_image(self.display, 'images/x.png', self.x - self.w / 4.1, self.y + self.h / 4.4,
                                           55, 50,
                                           append=False))

            self.xs.append(
                custom_images.Custom_image(self.display, 'images/x.png', self.x - self.w / 4.1,
                                           self.y + self.h - self.h / 4.4,
                                           55, 50,
                                           append=False))

            self.xs.append(
                custom_images.Custom_image(self.display, 'images/x.png', self.x - self.w / 4.1 + self.w / 1.95,
                                           self.y + self.h / 4.4,
                                           55, 50,
                                           append=False))

            self.xs.append(
                custom_images.Custom_image(self.display, 'images/x.png', self.x - self.w / 4.1 + self.w / 1.95,
                                           self.y + self.h - self.h / 4.4,
                                           55, 50,
                                           append=False))

        if self.display.p.tireAmount == 3:
            self.img = custom_images.Custom_image(self.display, 'images/3-wheels.png', self.x, self.y + self.h / 2,
                                                  self.w, self.h, append=False)

            self.xs.append(
                custom_images.Custom_image(self.display, 'images/x.png', self.x - self.w / 4.1, self.y + self.h / 2,
                                           55, 50,
                                           append=False))

            self.xs.append(
                custom_images.Custom_image(self.display, 'images/x.png', self.x - self.w / 4.1 + self.w / 2.05,
                                           self.y + self.h / 4.4,
                                           55, 50,
                                           append=False))

            self.xs.append(
                custom_images.Custom_image(self.display, 'images/x.png', self.x - self.w / 4.1 + self.w / 2.05,
                                           self.y + self.h - self.h / 4.4,
                                           55, 50,
                                           append=False))

