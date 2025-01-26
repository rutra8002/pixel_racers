import random
import math as lolekszcz

class Enemy:
    def __init__(self, display, car):
        self.display = display
        self.car = car
    def loop(self):
        self.car.a = random.choice((True, False))
        self.car.w = random.choice((True, False))
        self.car.s = random.choice((True, False))
        self.car.d = random.choice((True, False))
        self.car.boost = random.choice((True, False))