import random
import math as lolekszcz
from app.car import Car

class Enemy(Car):
    def __init__(self, display, coordinates, rotation, model, crazy=False, name="None"):
        super().__init__(display, coordinates, rotation, isPlayer=False, model=model, name=name)
        self.crazy = crazy


    def loop(self):
        super().loop()

        if self.crazy and not self.in_oil:
            self.a = random.choice((True, False))
            self.w = random.choice((True, False))
            self.s = random.choice((True, False))
            self.d = random.choice((True, False))
            self.boost = random.choice((True, False))