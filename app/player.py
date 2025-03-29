import pygame
import math as lolino
import time
from app.car import Car
import math

class Player(Car):
    def __init__(self, display, coordinates, rotation, model):
        super().__init__(display, coordinates, rotation, isPlayer=True, model=model)
        self.player_name = self.display.game.player_name
        self.wong_way_timer = 0

    def events(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.w = True
            if event.key in (pygame.K_a, pygame.K_LEFT):
                self.a = True
            if event.key in (pygame.K_s, pygame.K_DOWN):
                self.s = True
            if event.key in (pygame.K_d, pygame.K_RIGHT):
                self.d = True
            if event.key == pygame.K_q:
                self.q = True
            if event.key == pygame.K_e:
                self.e = True
            if event.key == pygame.K_SPACE:
                if self.WASD_steering:
                    self.velUp, self.velLeft = 0, 0
                else:
                    self.boost = True
            if event.key == pygame.K_c:
                self.use_powerup()
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.w = False
            if event.key in (pygame.K_a, pygame.K_LEFT):
                self.a = False
            if event.key in (pygame.K_s, pygame.K_DOWN):
                self.s = False
            if event.key in (pygame.K_d, pygame.K_RIGHT):
                self.d = False
            if event.key == pygame.K_SPACE:
                self.boost = False
            if event.key == pygame.K_q:
                self.q = False
            if event.key == pygame.K_e:
                self.e = False

    def return_to_last_checkpoint(self):
        checkpoint_to_return = self.display.checkpoints[self.current_checkpoint]
        self.next_x = (checkpoint_to_return.start_pos[0] + checkpoint_to_return.end_pos[0])/2
        self.next_y = (checkpoint_to_return.start_pos[1] + checkpoint_to_return.end_pos[1])/2
        self.x = self.next_x
        self.y = self.next_y

        if self.current_checkpoint + 1 == self.display.amount_of_checkpoints:
            checkpoint_to_rotate_towards = self.display.checkpoints[0]
        else:
            checkpoint_to_rotate_towards = self.display.checkpoints[self.current_checkpoint + 1]
        self.rotation = self.rotate_toward(((checkpoint_to_rotate_towards.start_pos[0] + checkpoint_to_rotate_towards.end_pos[0])/2, (checkpoint_to_rotate_towards.start_pos[1] + checkpoint_to_rotate_towards.end_pos[1])/2))
        self.next_rotation = self.rotation
        self.stunned = True
        self.stunned_timer = time.time()

        self.velUp = 0
        self.velLeft = 0

    def rotate_toward(self, pos):
        rel_x, rel_y = pos[0] - self.x, pos[1] - self.y

        angle = lolino.degrees(lolino.atan2(-rel_y, rel_x)) - 90
        return angle