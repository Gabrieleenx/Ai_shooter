from Vision import sight
import math

class Player(object):
    def __init__(self, position, rotation):
        self.position = position
        self.rotation = rotation
        self.ammo = 60
        self.reload_time = 60
        self.reloading = 0
        self.health = 100
        self.action_F = 0
        self.action_S = 0
        self.rotate = 0
        self.fire = 0

    def input(self, forward, side, rotate, fire):
        self.action_F = forward
        self.action_S = side
        self.rotate = rotate
        self.fire = fire

    def info(self, vision):
        front_ = 0
        right_ = 0
        left_ = 0
        back_ = 0
        d_rot = 0
        if self.action_F != 0 or self.action_S != 0:
            d_rot = math.atan2(self.action_S, self.action_F)

        speed = abs(self.action_F) + abs(self.action_S)
        if speed > 1:
            speed = 1
        rot = self.rotation + d_rot

        if vision[0] < 0.03:
            front_ = 1
        if vision[2] < 0.03:
            right_ = 1
        if vision[4] < 0.03:
            back_ = 1
        if vision[6] < 0.03:
            left_ = 1
        dx = math.sin(rot)*speed*3
        dy = -math.cos(rot)*speed*3
        if math.cos(self.rotation) >= 1/math.sqrt(2):
            if front_ and dy < 0:
                dy = 0
            if back_ and dy > 0:
                dy = 0
            if right_ and dx > 0:
                dx = 0
            if left_ and dx < 0:
                dx = 0

        elif math.cos(self.rotation) <= -1/math.sqrt(2):
            if front_ and dy > 0:
                dy = 0
            if back_ and dy < 0:
                dy = 0
            if right_ and dx < 0:
                dx = 0
            if left_ and dx > 0:
                dx = 0
        elif math.sin(self.rotation) >= 1 / math.sqrt(2):
            if front_ and dx > 0:
                dx = 0
            if back_ and dx < 0:
                dx = 0
            if right_ and dy > 0:
                dy = 0
            if left_ and dy < 0:
                dy = 0
        elif math.sin(self.rotation) <= -1/ math.sqrt(2):
            if front_ and dx < 0:
                dx = 0
            if back_ and dx > 0:
                dx = 0
            if right_ and dy < 0:
                dy = 0
            if left_ and dy > 0:
                dy = 0


        elif math.cos(rot) <= -1/math.sqrt(2):
            pass
        elif math.sin(rot) <= -1/math.sqrt(2):
            pass
        else:
            pass

        self.position[0] += dx
        self.position[1] += dy

        self.rotation += self.rotate*math.pi/30

        fire = 0
        if self.reloading == 0:
            if self.fire:
                self.ammo -= 1
                fire = self.fire
            if self.ammo <= 0:
                self.reloading = 1

        if self.reloading == 1:
            self.reload_time -= 1
            if self.reload_time <= 0:
                self.reloading = 0
                self.reload_time = 60
                self.ammo = 60

        return self.position, self.rotation, self.health, fire

    def hit(self, hits):
        dead = 0
        for i in range(hits):
            self.health -= 10
        if self.health <= 0:
            dead = 1
        return dead


