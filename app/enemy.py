import random
import math as lolekszcz
from app.car import Car
from app import checkpoint as chk
from app import display as dsp
import json

class Enemy(Car):
    def __init__(self, display, coordinates, rotation,model, crazy=False):
        super().__init__(display, coordinates, rotation,isPlayer=False,model=model)
        self.game_dir = display.map_dir
        self.lv = display.diff
        self.map_data = display.map_data
        self.coordinates = coordinates
        self.chk_index = 0
        self.list_of_checkpoints = self.map_data['checkpoints']
        self.map = self.display.map
        self.distance_right = 10000
        self.distance_down = 10000
        self.distance_up = 10000


    def loop(self):
        super().loop()
        self.new_to_chk()
        self.avoid_walls()
        self.velLeft += 30/self.distance_right
        self.velUp += 30/self.distance_down - 30/self.distance_up

    def avoid_walls(self):
        self.distance_right = 10000
        self.distance_down = 10000
        self.distance_up = 10000
        self.detected_right = False
        self.detected_up = False
        self.detected_down = False
        self.x_axis = self.map[int(self.y//self.display.block_height)]
        for i in range(190): #MAŁO, BO PROBlEMY Z SKALOWALNOŚCIĄ (DLA 1,2 PRZECIWNIKÓW MOŻNA NA SPOKOJNIE 50/30 DAĆ)
            if int(self.y//self.display.block_height)+i < len(self.map)-1:
                self.x_axis_up = self.map[int(self.y//self.display.block_height)+i]
            if int(self.y//self.display.block_height)-i>0:
                self.x_axis_down = self.map[int(self.y//self.display.block_height)-i]
            for j in range(30):
                if int(self.x//self.display.block_width)+j < len(self.x_axis)-1:
                    self.wall_right = self.x_axis[int(self.x//self.display.block_width)+j]
                
                self.adj_x = self.x//self.display.block_width

                self.wall_up = self.x_axis_up[int(self.adj_x)]
                self.wall_down = self.x_axis_down[int(self.adj_x)]
                if self.wall_right == 1 and not self.detected_right:
                    self.detected_right = True
                    self.distance_right = j + 0.000001 #negligible value to avoid / by 0  
                if self.wall_up == 1 and not self.detected_up:
                    self.detected_up = True
                    self.distance_up = i + 0.000001 
                if self.wall_down == 1 and not self.detected_down:
                    self.detected_down = True
                    self.distance_down = i + 0.000001


            
    def sigmoid(x):
        return 1/(1+lolekszcz.exp(-x))
    def new_to_chk(self):
        self.max_chk_indx = len(self.list_of_checkpoints)
        i = self.list_of_checkpoints[self.chk_index]
        self.center_x = (i[0][0] + i[1][0])/2 * self.display.block_width
        self.center_y = (i[0][1] + i[1][1])/2 * self.display.block_height
        self.true_i = [[i[0][0]* self.display.block_width, i[0][1]* self.display.block_height], [i[1][0]* self.display.block_width, i[1][1]* self.display.block_height]]
        
        if self.rect.clipline ((self.true_i[0][0],self.true_i[0][1]), (self.true_i[1][0], self.true_i[1][1])):
            if self.chk_index != self.max_chk_indx:
                self.chk_index+=1
            if self.chk_index == self.max_chk_indx:
                self.chk_index = 0
        
        self.dx = 8 *  (self.center_x - self.x)/(abs(self.center_x - self.x)+0.000001) * self.display.game.delta_time * self.display.game.calibration
        self.dy = 6 *  (self.center_y - self.y)/(abs(self.center_y - self.y)+0.000001) * self.display.game.delta_time * self.display.game.calibration
        self.velLeft -= self.dx
        self.velUp -= self.dy
        self.angle = lolekszcz.degrees(lolekszcz.atan2(-self.dy, self.dx))

        self.rotation = self.angle #TEMP OFC

