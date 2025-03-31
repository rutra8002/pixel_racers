import random
import math as m
from app.car import Car
from app import obstacle as obs
import random
import pygame
from jeff_the_objects.stacked_sprite import StackedSprite
class Enemy(Car):

    def __init__(self, display, coordinates, rotation,model,player, SubClass=2, name="None"):
        super().__init__(display, coordinates, rotation,isPlayer=False,model=model, name=name)
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


        self.force_push_x = 1
        self.force_push_y = 1

        self.starttime = pygame.time.get_ticks()
        self.cooldown = True
        self.homing = 0
        self.decide_to_wait = False
        self.hasControl = True
        self.prickedWheels = 0
        self.type = SubClass
        self.diff = [[0.73,200],[0.79,130],[0.85,160]]
        self.diff_indx = 1
        self.reset_counter = 6.5
        
        if self.type not in [0,1,2,3]:
            self.type = 0
        self.image = self.image.copy()

        if self.type == 0:
            self.image.fill((100, 0, 0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            self.image.fill((150, 0, 150, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.car3d_sprite = StackedSprite(self.display, self.image, self.num_of_sprites, self.img_size,
                                                             self.car3d_height, isenemy=(not self.isPlayer))
            self.name = "Violet"
        elif self.type == 1:
            self.image.fill((100, 0, 0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            self.image.fill((170, 170, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.car3d_sprite = StackedSprite(self.display, self.image, self.num_of_sprites, self.img_size,
                                              self.car3d_height, isenemy=(not self.isPlayer))
            self.name = "Yellow"
        elif self.type == 2:
            self.image.fill((100, 0, 0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            self.image.fill((0, 0, 150, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.car3d_sprite = StackedSprite(self.display, self.image, self.num_of_sprites, self.img_size,
                                              self.car3d_height, isenemy=(not self.isPlayer))
            self.name = "Blue"
        elif self.type == 3:
            self.image.fill((100, 0, 0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            self.image.fill((0, 80, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.car3d_sprite = StackedSprite(self.display, self.image, self.num_of_sprites, self.img_size,
                                              self.car3d_height, isenemy=(not self.isPlayer))
            self.name = "Green"
    def loop(self):
        super().loop()
        self.new_to_chk()
        self.avoid_walls()



        if self.enemy_spike_wheel:
            self.enemy_spike_wheel = False
            if self.prickedWheels < 4:
                        self.prickedWheels+=1
                        self.hits +=30


        if self.display.diff == "Finished_Level_1":
            self.diff_indx = 0
        elif self.display.diff == "Finished_Level_2":
            self.diff_indx = 1
        elif self.diff_indx == "Finished_Level_3":
            self.diff_indx = 2
        else:
            self.diff_indx = 1

        self.current_speed = m.sqrt((self.velLeft)**2+(self.velUp)**2)
        self.distance_player = m.sqrt( (self.x-self.player.x)**2 + (self.y-self.player.y) ** 2)
        self.dt = self.display.game.delta_time
        
        for obstacle in self.display.obstacles:
            if self.get_obstacle_colision(obstacle):
                if obstacle.type == 3 and not obstacle.falling:
                    self.enemy_on_banana = True

                    self.hasControl = False
                    self.regain_control_time = 2.5
                    self.bananaTime = 0.91 * random.choice((1, -1))
                    self.display.hasBanana = 1
                    obstacle.destroy() 


                elif obstacle.type == 1:
                    obstacle.destroy() 
                    if self.prickedWheels < 4:
                        self.prickedWheels+=1
                        self.hits +=30

        if self.hasControl:

            if len(self.inventory)>0:
                if self.inventory[0] == 4:
                    if len(self.inventory) == 2 or self.prickedWheels>0:
                        if self.prickedWheels>0:
                            self.prickedWheels-=1
                        self.inventory.pop(0)
                elif self.inventory[0] == 1:
                    if self.distance_player <150:
                        self.strenght = True
                        self.inventory.pop(0)
                elif self.inventory[0] == 2:
                    if self.distance_player < 150:
                        angle = m.radians(self.rotation)
                        spawn_x = self.x - (50 * m.cos(angle))
                        spawn_y = self.y + (50 * m.sin(angle))
                        self.display.obstacles.append(obs.Obstacle(self.display, spawn_x, spawn_y, 'barrier', self.rotation - 90))
                        self.inventory.pop(0)
                elif self.inventory[0] == 3:
                    if self.distance_player < 150:
                        angle = m.radians(self.rotation)
                        spawn_x = self.x - (50 * m.cos(angle))
                        spawn_y = self.y + (50 * m.sin(angle))
                        self.display.obstacles.append(obs.Obstacle(self.display, spawn_x, spawn_y, 'spikes', self.rotation - 90))
                        self.inventory.pop(0)

            if abs(self.velLeft) < 4 and 100 - pygame.time.get_ticks() < 0 :
                self.force_push_x = 10
            if abs(self.velUp) < 4 and 100 - pygame.time.get_ticks() < 0 :
                self.force_push_y = 10
            if self.current_speed<12:
                self.reset_counter -= self.dt
            else:
                self.reset_counter = 6.5
            if self.reset_counter <= 0:
                i_prev = self.list_of_checkpoints[self.chk_index-1]
                self.center_x_prev = (i_prev[0][0] + i_prev[1][0])/2 * self.display.block_width
                self.center_y_prev = (i_prev[0][1] + i_prev[1][1])/2 * self.display.block_height
                self.next_x = self.center_x_prev
                self.next_y = self.center_y_prev
                self.reset_counter = 6.5
            self.force_push_y = 1
            self.force_push_x = 1
            if self.type == 3:
                self.brakecheck()
                self.target_velocity = 350
                
                self.scale_x = abs(self.velLeft/(self.current_speed+0.000001))
                self.scale_y = abs(self.velUp/(self.current_speed+0.000001))
                self.scale_left = self.tanh(self.target_velocity, abs(self.velLeft)) * (self.scale_x+0.01)
                self.scale_up = self.tanh(self.target_velocity, abs(self.velUp)) * (self.scale_y+0.01)

                if self.decide_to_wait:
                    self.velLeft += (self.diff[self.diff_indx][1]/self.distance_right - self.diff[self.diff_indx][1]/self.distance_left - self.dx )*0.6 *0.97**(self.prickedWheels)
                    self.velUp -= (-self.diff[self.diff_indx][1]/self.distance_down + self.diff[self.diff_indx][1]/self.distance_up + self.dy)*0.6* 0.97**(self.prickedWheels)

                    if self.distance_player<200:
                        self.velLeft += ((-self.dx + self.diff[self.diff_indx][1]/self.distance_right - self.diff[self.diff_indx][1]/self.distance_left)*0.3 + (self.x-self.player.x)/(abs(self.x-self.player.x)+0.0001)*15)* 0.97**(self.prickedWheels)
                        self.velUp -= ((-self.diff[self.diff_indx][1]/self.distance_down + self.diff[self.diff_indx][1]/self.distance_up + self.dy)*0.3 - (self.y-self.player.y)/(abs(self.y-self.player.y)+0.0001)*15)* 0.97**(self.prickedWheels)



                else:
                    self.velLeft += (self.diff[self.diff_indx][1]/self.distance_right - self.diff[self.diff_indx][1]/self.distance_left - self.dx*self.force_push_x* self.scale_left)*self.diff[self.diff_indx][0]* 0.97**(self.prickedWheels)
                    self.velUp -= (-self.diff[self.diff_indx][1]/self.distance_down + self.diff[self.diff_indx][1]/self.distance_up + self.dy*self.force_push_y * self.scale_up)*self.diff[self.diff_indx][0]* 0.97**(self.prickedWheels)



            elif self.type == 2:


                if self.homing <= 0:
                    self.cooldown = True
                if self.homing>=5:
                    self.cooldown = False
                if self.cooldown:
                   self.homing += self.dt
                self.to_player_bump()
                if self.player_vector_x != 0 and not self.cooldown:
                    self.homing-=self.dt
                    self.velLeft += self.player_vector_x*16* 0.97**(self.prickedWheels)
                    self.velUp -= - self.player_vector_y*16* 0.97**(self.prickedWheels)
                    if self.distance_player<100:
                        self.homing -= 1.5*self.dt


                else:
                    self.velLeft += (self.diff[self.diff_indx][1]/self.distance_right - self.diff[self.diff_indx][1]/self.distance_left - self.dx*self.force_push_x)*self.diff[self.diff_indx][0]* 0.97**(self.prickedWheels)
                    self.velUp -= (-self.diff[self.diff_indx][1]/self.distance_down + self.diff[self.diff_indx][1]/self.distance_up + self.dy *self.force_push_y)*self.diff[self.diff_indx][0]* 0.97**(self.prickedWheels)


            elif self.type == 1:
                self.target_velocity = 320
                
                self.scale_x = abs(self.velLeft/(self.current_speed+0.000001))
                self.scale_y = abs(self.velUp/(self.current_speed+0.000001))
                self.scale_left = self.tanh(self.target_velocity, abs(self.velLeft)) * (self.scale_x+0.01)
                self.scale_up = self.tanh(self.target_velocity, abs(self.velUp)) * (self.scale_y+0.01)
                self.velLeft += (self.diff[self.diff_indx][1]/self.distance_right - self.diff[self.diff_indx][1]/self.distance_left - self.dx * self.scale_left)* 0.97**(self.prickedWheels)
                self.velUp -= (-self.diff[self.diff_indx][1]/self.distance_down + self.diff[self.diff_indx][1]/self.distance_up + self.dy* self.scale_up)* 0.97**(self.prickedWheels)
            elif self.type == 0:



                self.velLeft +=(-self.dx* self.force_push_x + self.diff[self.diff_indx][1]/self.distance_right - self.diff[self.diff_indx][1]/self.distance_left)*self.diff[self.diff_indx][0]* 0.97**(self.prickedWheels)
                self.velUp -=(-self.diff[self.diff_indx][1]/self.distance_down + self.diff[self.diff_indx][1]/self.distance_up + self.dy* self.force_push_y )*self.diff[self.diff_indx][0]* 0.97**(self.prickedWheels)
        
        else:
            if self.bananaTime == 0:
                self.hasControl = True
                self.enemy_on_banana = False
            else:
                self.regain_control_time -= self.dt
                


    def avoid_walls(self):
        self.distance_right = 10000
        self.distance_down = 10000
        self.distance_up = 10000
        self.distance_left = 10000
        self.detected_right = False
        self.detected_left = False
        self.detected_up = False
        self.detected_down = False
        self.adj_y = self.y//self.display.block_height
        self.adj_x = self.x//self.display.block_width
        try:
            self.x_axis = self.map[int(self.adj_y)]


            for i in range(60): 



                if int(self.adj_y)+i < len(self.map):
                    self.x_axis_down = self.map[int(self.adj_y)+i]
                    self.wall_down = self.x_axis_down[int(self.adj_x)]
                if int(self.adj_y)-i>=0:

                    self.x_axis_up = self.map[int(self.adj_y)-i]

                    self.wall_up = self.x_axis_up[int(self.adj_x)]


                if self.wall_up == 1 and not self.detected_up:
                    self.detected_up = True
                    self.distance_up = i + 0.000001
                if self.wall_down == 1 and not self.detected_down:
                    self.detected_down = True
                    self.distance_down = i + 0.000001
            for j in range(60):

                if int(self.adj_x ) -j >= 0:

                    self.wall_left = self.x_axis[int(self.adj_x)-j]

                if int(self.adj_x)+j < len(self.x_axis):
                    self.wall_right = self.x_axis[int(self.adj_x)+j]



                if self.wall_right == 1 and not self.detected_right:
                    self.detected_right = True
                    self.distance_right = j + 0.000001
                if self.wall_left == 1 and not self.detected_left:
                    self.detected_left = True
                    self.distance_left = j + 0.000001

        except:
                self.next_x = (self.list_of_checkpoints[self.chk_index-1][0][0] + self.list_of_checkpoints[self.chk_index-1][1][0])/2 * self.display.block_width
                self.next_y = (self.list_of_checkpoints[self.chk_index-1][0][1] + self.list_of_checkpoints[self.chk_index-1][1][1])/2 * self.display.block_height






    def sigmoid(self,center,x):
        return -(1/1+(m.exp(-((x/5)-center)))) + 1.5
    def tanh(self,center, x):
        return -m.tanh(x - center) + 1
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
        
        self.dx = 7*(self.center_x - self.x)/(abs(self.center_x - self.x)+0.000001) * self.display.game.delta_time * self.display.game.calibration
        self.dy = 7*(self.center_y - self.y)/(abs(self.center_y - self.y)+0.000001)* self.display.game.delta_time * self.display.game.calibration
        self.angle = m.degrees(m.atan2(-self.dy, self.dx))


    def to_player_bump(self):
        self.player_vector_x = 0
        self.player_vector_y = 0
        if self.distance_player<200 :
            self.player_vector_x = (self.x-self.player.x)/(abs(self.x-self.player.x)+0.0001)
            self.player_vector_y = (self.y-self.player.y)/(abs(self.y-self.player.y)+0.0001)

    def brakecheck(self):

        self.chk_dif = self.chk_index - self.player.current_checkpoint
        if self.player.lap != self.map_data['laps']:
            if self.chk_dif==2:
                self.decide_to_wait = True
            elif self.chk_dif > 2:
                if random.randint(0,10) == 7:
                    self.decide_to_wait = True



            else:
                self.decide_to_wait = False
        else:
            self.decide_to_wait = False

        if self.decide_to_wait:
            if random.randint(0,10) == 7:
                self.decide_to_wait = False
    def get_obstacle_colision(self, obstacle):
        return pygame.Rect.colliderect(self.rect, obstacle.rect)
    
