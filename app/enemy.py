import random
import math as lolekszcz
from app.car import Car
from app import player
from app import checkpoint as chk
from app import display as dsp
import random
import pygame
class Enemy(Car):
    def __init__(self, display, coordinates, rotation,model,player, SubClass=2):
        super().__init__(display, coordinates, rotation,isPlayer=False,model=model)
        self.game_dir = display.map_dir

        self.player = player
        self.lv = display.diff
        self.map_data = display.map_data
        self.coordinates = coordinates
        self.chk_index = 0
        self.list_of_checkpoints = self.map_data['checkpoints']
        self.map = self.display.map
        self.distance_right = 10000
        self.distance_down = 10000
        self.distance_up = 10000
        self.distance_left = 10000


        self.starttime = pygame.time.get_ticks()
        self.cooldown = True
        self.homing = 0
        self.decide_to_wait = False
        self.type = SubClass
        if self.type not in [0,1,2,3]:
            self.type = 0
    def loop(self):
        super().loop()
        self.new_to_chk()
        self.avoid_walls()
        self.dt = self.display.game.delta_time


        if self.type == 3:
            self.brakecheck()
            if self.decide_to_wait:
                self.velLeft += (-self.dx + 250/self.distance_right - 250/self.distance_left)*0.7
                self.velUp -= (-250/self.distance_down + 250/self.distance_up + self.dy)*0.7

                if self.distance_player<200:
                    self.velLeft += (-self.dx + 250/self.distance_right - 250/self.distance_left)*0.1 + (self.x-self.player.x)/(abs(self.x-self.player.x)+0.0001)*15
                    self.velUp -= (-250/self.distance_down + 250/self.distance_up + self.dy)*0.1 - (self.y-self.player.y)/(abs(self.y-self.player.y)+0.0001)*15
            
                    

            else:
                self.velLeft += (250/self.distance_right - 250/self.distance_left - self.dx) 
                self.velUp -= (-250/self.distance_down + 250/self.distance_up + self.dy ) 



        if self.type == 2:
            if self.homing <= 0:
                self.cooldown = True
            if self.homing>=5:
                self.cooldown = False
            if self.cooldown:
               self.homing += self.dt
            self.to_player_bump()
            if self.player_vector_x != 0 and not self.cooldown:
                self.homing-=self.dt
                self.velLeft += self.player_vector_x*16
                self.velUp -= - self.player_vector_y*16


            else:
                self.velLeft += (250/self.distance_right - 250/self.distance_left - self.dx) 
                self.velUp -= (-250/self.distance_down + 250/self.distance_up + self.dy ) 


        if self.type == 1:
            self.target_velocity = 350
            self.current_speed = lolekszcz.sqrt((self.velLeft)**2+(self.velUp)**2)
            self.scale_left = self.tanh(self.target_velocity, abs(self.velLeft))
            self.scale_up = self.tanh(self.target_velocity, abs(self.velUp))
            self.velLeft += (200/self.distance_right - 200/self.distance_left - self.dx * self.scale_left)
            self.velUp -= (-200/self.distance_down + 200/self.distance_up + self.dy* self.scale_up) 
        if self.type == 0:
            
            self.velLeft += (-self.dx) + 250/self.distance_right - 250/self.distance_left
            self.velUp -= -250/self.distance_down + 250/self.distance_up + self.dy


    def avoid_walls(self):
        self.distance_right = 10000
        self.distance_down = 10000
        self.distance_up = 10000
        self.distance_left = 10000
        self.detected_right = False
        self.detected_left = False
        self.detected_up = False
        self.detected_down = False
        self.x_axis = self.map[int(self.y//self.display.block_height)]
        self.adj_x = self.x//self.display.block_width
        for i in range(70): #MAŁO, BO PROBlEMY Z SKALOWALNOŚCIĄ (DLA 1,2 PRZECIWNIKÓW MOŻNA NA SPOKOJNIE 50/30 DAĆ)
            

            
            if int(self.y//self.display.block_height)+i < len(self.map):
                self.x_axis_down = self.map[int(self.y//self.display.block_height)+i]
                self.wall_down = self.x_axis_down[int(self.adj_x)]
            if int(self.y//self.display.block_height)-i>=0:
                    
                self.x_axis_up = self.map[int(self.y//self.display.block_height)-i]
                
                self.wall_up = self.x_axis_up[int(self.adj_x)]
            
            
            if self.wall_up == 1 and not self.detected_up:
                self.detected_up = True
                self.distance_up = i + 0.000001 
            if self.wall_down == 1 and not self.detected_down:
                self.detected_down = True
                self.distance_down = i + 0.000001
        for j in range(70):

            if int(self.x//self.display.block_width ) -j >= 0:
                
                self.wall_left = self.x_axis[int(self.x//self.display.block_width -j)]

            if int(self.x//self.display.block_width)+j < len(self.x_axis):
                self.wall_right = self.x_axis[int(self.x//self.display.block_width)+j]



            if self.wall_right == 1 and not self.detected_right:
                self.detected_right = True
                self.distance_right = j + 0.000001 #negligible value to avoid / by 0  

            if self.wall_left == 1 and not self.detected_left:
                self.detected_left = True
                self.distance_left = j + 0.000001 #negligible value to avoid / by 0  

        
                



    def sigmoid(self,center,x):
        return -(1/1+(lolekszcz.exp(-((x/5)-center)))) + 1.5
    def tanh(self,center, x):
        return -lolekszcz.tanh(x - center) + 1
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
        
        self.dx =7 *  (self.center_x - self.x)/(abs(self.center_x - self.x)+0.000001)
        self.dy = 7 *  (self.center_y - self.y)/(abs(self.center_y - self.y)+0.000001)
        self.angle = lolekszcz.degrees(lolekszcz.atan2(-self.dy, self.dx))
        self.rotation = self.angle #TEMP OFC

    def to_player_bump(self):
        self.player_vector_x = 0
        self.player_vector_y = 0
        if lolekszcz.sqrt( (self.x-self.player.x)**2 + (self.y-self.player.y) ** 2)<200 :
            self.player_vector_x = (self.x-self.player.x)/(abs(self.x-self.player.x)+0.0001)
            self.player_vector_y = (self.y-self.player.y)/(abs(self.y-self.player.y)+0.0001)
        
    def brakecheck(self):
        
        self.distance_player = lolekszcz.sqrt( (self.x-self.player.x)**2 + (self.y-self.player.y) ** 2)
        self.chk_dif = self.chk_index - self.player.current_checkpoint
        if self.chk_dif==2:
            self.decide_to_wait = True
        elif self.chk_dif > 2:
            if random.randint(0,20) == 7:
                self.decide_to_wait = True


        else:
            self.decide_to_wait = False
