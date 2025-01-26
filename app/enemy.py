import random
import math as lolekszcz

class Enemy:
    def __init__(self, display, car, crazy=True):
        self.display = display
        self.car = car
        self.crazy = crazy
    def loop(self):
        if self.crazy:
            self.car.a = random.choice((True, False))
            self.car.w = random.choice((True, False))
            self.car.s = random.choice((True, False))
            self.car.d = random.choice((True, False))
            self.car.boost = random.choice((True, False))