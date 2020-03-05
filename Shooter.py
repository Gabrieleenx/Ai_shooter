import pygame
import numpy as np
from Vision import sight
from Vision import bullet_colission
from Map_hitbox import create_map
from Player import Player
import math
from Vision import check_sight
from Vision import rotate


class Game(object):

    def __init__(self):
        self.win = pygame.display.set_mode((800, 800))
        self.clock = pygame.time.Clock()
        self.map = []
        self.delta_dist = 0
        self.vision_1 = []
        self.vision_2 = []
        self.player_1 = Player(position=[30, 30], rotation=math.pi)
        self.player_2 = Player(position=[770, 770], rotation=0)
        self.projectile = create_projectile()
        self.player_1_last_pos = [30, 30]
        self.player_2_last_pos = [770, 770]

    def create(self):
        self.map = create_map()

    def step_player_1(self, action):
        self.vision_1 = self.player_1.input(action[0], action[1], action[2], action[3])

    def step_player_2(self, action):
        self.vision_2 = self.player_2.input(action[0], action[1], action[2], action[3])

    def step(self):
        self.win.fill((50, 50, 50))
        done = 0
        enemy_visual_1 = 0
        enemy_visual_2 = 0
        observation_1 = []
        observation_2 = []
        self.vision_1 = sight(self.player_1.position, self.player_1.rotation, self.map, self.win)
        self.vision_2 = sight(self.player_2.position, self.player_2.rotation, self.map, self.win)
        self.projectile.update()
        pos_1, rot_1, life_1, fire_1 = self.player_1.info(self.vision_1)
        pos_2, rot_2, life_2, fire_2 = self.player_2.info(self.vision_2)

        if fire_1:
            self.projectile.create(self.player_1.position, self.player_1.rotation, 1)
        if fire_2:
            self.projectile.create(self.player_2.position, self.player_2.rotation, 2)

        projectiles_1, projectiles_2 = self.projectile.out()

        hit_player_1, remove_projectiles_2 = check_collision(self.player_1.position, projectiles_2, self.map, self.win)
        hit_player_2, remove_projectiles_1 = check_collision(self.player_2.position, projectiles_1, self.map, self.win)

        self.projectile.remove_projectile(remove_projectiles_1, 1)
        self.projectile.remove_projectile(remove_projectiles_2, 2)

        dead_1 = self.player_1.hit(hit_player_1)
        dead_2 = self.player_2.hit(hit_player_2)
        delta_dist = -self.delta_dist + math.sqrt((pos_1[0]-pos_2[0])**2 + (pos_1[1]-pos_2[1])**2)
        self.delta_dist = math.sqrt((pos_1[0]-pos_2[0])**2 +(pos_1[1]-pos_2[1])**2)

        reward_1 = reward_function(hit_player_1, dead_1, hit_player_2, dead_2, delta_dist)
        reward_2 = reward_function(hit_player_2, dead_2, hit_player_1, dead_1, delta_dist)

        pygame.event.get()  # to keep pygame happy!!!

        if check_sight(self.player_2.position, self.player_2.rotation, self.player_1.position, self.map, self.delta_dist, self.win) or fire_1:
            self.player_1_last_pos = [pos_1[0], pos_1[1]]
            enemy_visual_2 = 1
        if check_sight(self.player_1.position, self.player_1.rotation, self.player_2.position, self.map, self.delta_dist, self.win) or fire_2:
            self.player_2_last_pos = [pos_2[0], pos_2[1]]
            enemy_visual_1 = 1

        if dead_1 or dead_2:
            done = 1

        observation_1.extend([x / 400 for x in self.player_2_last_pos])
        observation_2.extend([x / 400 for x in self.player_1_last_pos])

        observation_1.extend([self.player_1.ammo/60])
        observation_2.extend([self.player_2.ammo/60])

        observation_1.extend([self.player_1.reloading])
        observation_2.extend([self.player_2.reloading])

        observation_1.extend([x/400 for x in self.player_1.position])
        observation_2.extend([x/400 for x in self.player_2.position])

        observation_1.extend([self.player_1.rotation % 2*math.pi])
        observation_2.extend([self.player_2.rotation % 2*math.pi])

        observation_1.extend(self.vision_1)
        observation_2.extend(self.vision_2)

        observation_1.extend([self.player_1.health/100])
        observation_2.extend([self.player_2.health/100])

        observation_1.extend([enemy_visual_1])
        observation_2.extend([enemy_visual_2])
        return observation_1, reward_1, observation_2, reward_2, done

    def render(self):
        #self.win.fill((50, 50, 50))
        for i in range(len(self.map)):
            pygame.draw.line(self.win, (0, 0, 0), (self.map[i][0], self.map[i][1]), (self.map[i][2], self.map[i][3]), 1)

        pygame.draw.rect(self.win, (0,200,0), (self.player_1.position[0]-10, self.player_1.position[1]-10, 20, 20))
        dx = math.sin(self.player_1.rotation) * 15
        dy = -math.cos(self.player_1.rotation) * 15
        pygame.draw.rect(self.win, (0,200,0), (self.player_1.position[0]+dx-3, self.player_1.position[1]+dy-3, 6, 6))

        pygame.draw.rect(self.win, (0, 0, 200),
                         (self.player_2.position[0] - 10, self.player_2.position[1] - 10, 20, 20))
        dx = math.sin(self.player_2.rotation) * 15
        dy = -math.cos(self.player_2.rotation) * 15
        pygame.draw.rect(self.win, (0, 0, 200),
                         (self.player_2.position[0] + dx - 3, self.player_2.position[1] + dy - 3, 6, 6))
        projectiles_1, projectiles_2 = self.projectile.out()
        for i in range(len(projectiles_1)):
            pygame.draw.rect(self.win, (200, 0, 0),
                             (projectiles_1[i][0] - 2, projectiles_1[i][1] - 2, 4, 4))
        for i in range(len(projectiles_2)):
            pygame.draw.rect(self.win, (200, 0, 0),
                             (projectiles_2[i][0] - 2, projectiles_2[i][1] - 2, 4, 4))

        pygame.display.update()

    def reset(self):
        self.delta_dist = 0
        self.vision_1 = []
        self.vision_2 = []
        self.player_1 = Player(position=[30, 30], rotation=math.pi)
        self.player_2 = Player(position=[770, 770], rotation=0)
        self.projectile = create_projectile()
        self.player_1_last_pos = [30, 30]
        self.player_2_last_pos = [770, 770]
        observation_1, reward_1, observation_2, reward_2, done = self.step()
        return observation_1, observation_2

class create_projectile():
    def __init__(self):
        # projectiles have data form [pos_x, pos_y, angle]
        self.projectiles_1 = []
        self.projectiles_2 = []

    def create(self, pos, rot, player):
        x1, y1 = rotate(pos[0], pos[1], pos[0], pos[1]-20, rot)
        if player == 1:
            self.projectiles_1.append([x1, y1, rot])
        else:
            self.projectiles_2.append([x1, y1, rot])

    def update(self):
        dx = 10
        for i in range(len(self.projectiles_1)):
            self.projectiles_1[i] = [self.projectiles_1[i][0]+dx*math.cos(self.projectiles_1[i][2]-math.pi/2),
                                     self.projectiles_1[i][1]+dx*math.sin(self.projectiles_1[i][2]-math.pi/2),
                                     self.projectiles_1[i][2]]
        for j in range(len(self.projectiles_2)):
            self.projectiles_2[j] = [self.projectiles_2[j][0]+dx*math.cos(self.projectiles_2[j][2]-math.pi/2),
                                     self.projectiles_2[j][1]+dx*math.sin(self.projectiles_2[j][2]-math.pi/2),
                                     self.projectiles_2[j][2]]

    def out(self):
        return self.projectiles_1, self.projectiles_2

    def remove_projectile(self, delete_proj, player):

        for del_ in sorted(delete_proj, reverse=True):
            if player == 1:
                del self.projectiles_1[del_]
            else:
                del self.projectiles_2[del_]


def check_collision(player, projectiles, map_, win):
    hit_player = 0
    remove_projectiles = []
    if not projectiles:
        return hit_player, remove_projectiles
    for i in range(len(projectiles)):
        if abs(player[0] - projectiles[i][0]) <= 10 and abs(player[1] - projectiles[i][1]) <= 10:
            hit_player += 1
            remove_projectiles.extend([i])
        elif bullet_colission([projectiles[i][0], projectiles[i][1]], projectiles[i][2], map_, win):
            remove_projectiles.extend([i])
    return hit_player, remove_projectiles


def reward_function(shoot, dead, hit, kill, delta_distance):  # add rotation??
    reward = 0
    if shoot:
        reward += -50
    if dead:
        reward += -200
    if hit:
        reward += 50
    if kill:
        reward += 300
    if delta_distance < 0:
        reward += 0.01

    return reward









