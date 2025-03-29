import time

import pygame.draw
from customObjects import custom_text
from app import player, obstacle

class checkpoint: # A checkpoint is a line with 2 points
    def __init__(self, display, i, start_pos, end_pos):
        self.display = display
        self.i = i # i is the n-th + 1 checkpoint in the race (if i == 0 it's the finish/start line, if i == 1 it's the secound checkpoint)
        self.start_pos = (start_pos[0] * self.display.block_width, start_pos[1] * self.display.block_height)
        self.end_pos = (end_pos[0] * self.display.block_width, end_pos[1] * self.display.block_height)

        self.text = custom_text.Custom_text(self.display, start_pos[0] * self.display.block_width, start_pos[1] * self.display.block_height, str(self.i + 1), append=False, text_color='blue') # text that displays which checkpoint it is

        if self.i == 0:
            self.color = self.display.color_map['m']
        else:
            self.color = self.display.color_map['c']

    def render(self):
        pygame.draw.line(self.display.screen, self.color, self.start_pos, self.end_pos, width=self.display.block_width)
        self.text.render()
        pygame.draw.circle(self.display.screen, 'red', ((self.start_pos[0]+self.end_pos[0])/2, (self.start_pos[1]+self.end_pos[1])/2), 5)

    def collision(self):
        for car in self.display.cars:
            if car.rect.clipline(self.start_pos, self.end_pos):
                if isinstance(car, player.Player):

                    if car.current_checkpoint == self.i or car.current_checkpoint == self.i - 1 or car.current_checkpoint == self.i - 2 or car.current_checkpoint == self.i - 3:
                        car.current_checkpoint = self.i
                        self.display.wong_way = False

                    elif self.i == 0 and car.current_checkpoint == self.display.amount_of_checkpoints-1:
                        car.current_checkpoint = self.i
                        car.lap += 1
                        car.perfectLaps += car.perfectLap
                        self.display.wong_way = False
                        car.lap_times.append(time.time() - car.begining_lap_time)
                        car.begining_lap_time = time.time()
                        self.display.hotbar.reset_lap_timer()
                        if car.lap <= self.display.laps:
                            self.display.hotbar.update_lap_text()
                            if self.display.hasCoin == 0:
                                self.display.obstacles.append(obstacle.Obstacle(self.display, self.display.coin[0], self.display.coin[1], "coin"))
                                self.display.hasCoin = 1
                        else:
                            self.display.end_race()

                    else:
                        if not self.display.wong_way:
                            car.wong_way_timer = time.time()
                        self.display.wong_way = True


                    car.last_passed_checkpoint = self.i

                else:

                    if car.current_checkpoint == self.i or car.current_checkpoint == self.i - 1 or car.current_checkpoint == self.i - 2 or car.current_checkpoint == self.i - 3:
                        car.current_checkpoint = self.i

                    elif self.i == 0 and car.current_checkpoint == self.display.amount_of_checkpoints-1:
                        car.current_checkpoint = self.i
                        car.lap += 1
                        car.lap_times.append(time.time() - car.begining_lap_time)
                        car.begining_lap_time = time.time()
                        if car.lap >= self.display.laps:
                            car.end_race()


                self.color = (0, 0, 255)
                player_name = car.player_name
                self.display.leaderboard[player_name] = self.i
                return True
        if self.i == 0:
            self.color = self.display.color_map['m']
        else:
            self.color = self.display.color_map['c']
        return False

    def delete(self):
        self.text.delete()
        del self
