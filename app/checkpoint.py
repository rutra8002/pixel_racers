import pygame.draw
from customObjects import custom_text
from app import player

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

    def collision(self):
        for car in self.display.cars:
            if car.rect.clipline(self.start_pos, self.end_pos):
                if isinstance(car, player.Player):
                    if car.current_checkpoint == self.i or car.current_checkpoint == self.i - 1:
                        car.current_checkpoint = self.i
                        self.display.wong_way = False

                    elif self.i == 0 and car.current_checkpoint == len(self.display.checkpoints)-1:
                        car.current_checkpoint = self.i
                        car.lap += 1
                        self.display.wong_way = False
                        self.display.hotbar.update_lap_text()

                    else:
                        self.display.wong_way = True

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