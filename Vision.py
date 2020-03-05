import numpy as np
from Shooter import pygame

def cross_product(p1, p2):
    return p1[0] * p2[1] - p2[0] * p1[1]


def perp( a ) :
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b


def intersect(p1, p2, p3, p4):

    d1 = direction(p3, p4, p1)
    d2 = direction(p3, p4, p2)
    d3 = direction(p1, p2, p3)
    d4 = direction(p1, p2, p4)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    elif d1 == 0 and on_segment(p3, p4, p1):
        return True
    elif d2 == 0 and on_segment(p3, p4, p2):
        return True
    elif d3 == 0 and on_segment(p1, p2, p3):
        return True
    elif d4 == 0 and on_segment(p1, p2, p4):
        return True
    else:
        return False


def direction(p1, p2, p3):
    return cross_product([p3[0] - p1[0], p3[1] - p1[1]], [p2[0] - p1[0], p2[1] - p1[1]])


def on_segment(p1, p2, p):
    return min(p1[0], p2[0]) <= p[0] <= max(p1[0], p2[0]) and min(p1[1], p2[1]) <= p[1] <= max(p1[1], p2[1])


def seg_intersect(a1,a2, b1,b2) :
    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = perp(da)
    denom = np.dot(dap, db)
    num = np.dot(dap, dp)
    return (num / denom.astype(float))*db + b1


def rotate(x1, y1, x2, y2, angle):

    qx = x1 + np.cos(angle) * (x2 - x1) - np.sin(angle) * (y2 - y1)
    qy = y1 + np.sin(angle) * (x2 - x1) + np.cos(angle) * (y2 - y1)

    return int(qx), int(qy)


def sight(player_pos, player_direction, map_coords, win):
    sight_x = [0, 800, 800, 800, 0, -800, -800, -800]
    sight_y = [-800, -800, 0, 800, 800, 800, 0, -800]

    sight_x = [x + player_pos[0] for x in sight_x]
    sight_y = [x  +player_pos[1] for x in sight_y]
    sight_list = [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]

    for i in range(8):
        x1 = player_pos[0]
        y1 = player_pos[1]
        x2, y2 = rotate(x1, y1, sight_x[i], sight_y[i], player_direction)
        #pygame.draw.line(win, (250, 250, 250), (x1, y1), (x2, y2), 1)
        '''
        if i == 0:
        pygame.draw.line(win, (250, 250, 250), (x1, y1), (x2, y2), 1)
        else:
            pygame.draw.line(win, (200-20*i, 200-20*i, 200-20*i), (x1, y1), (x2, y2), 1)
        '''
        for k in range(len(map_coords)):
            if max([x1, x2]) < map_coords[k][0] and max([x1, x2]) < map_coords[k][2]:
                continue
            elif min([x1, x2]) > map_coords[k][0] and min([x1, x2]) > map_coords[k][2]:
                continue
            elif max([y1, y2]) < map_coords[k][1] and max([y1, y2]) < map_coords[k][3]:
                continue
            elif min([y1, y2]) > map_coords[k][1] and min([y1, y2]) > map_coords[k][3]:
                continue
            elif intersect([x1, y1], [x2, y2], [map_coords[k][0], map_coords[k][1]], [map_coords[k][2], map_coords[k][3]]):
                p1 = np.array([x1, y1])
                p2 = np.array([x2, y2])
                p3 = np.array([map_coords[k][0], map_coords[k][1]])
                p4 = np.array([map_coords[k][2], map_coords[k][3]])
                in_point = seg_intersect(p1, p2, p3, p4)
                #pygame.draw.circle(win, (0,0,0), (int(in_point[0]), int(in_point[1])), 4)
                dist = 0.0025*np.sqrt((x1-in_point[0])**2 + (y1-in_point[1])**2)
                if dist < sight_list[i]:
                    sight_list[i] = dist

    return sight_list

def check_sight(player_pos, player_rot, enemy_pos, map_coords, dist_players, win):
    visual = True
    x2 = enemy_pos[0]
    y2 = enemy_pos[1]

    x1 = player_pos[0]
    y1 = player_pos[1]
    #x2, y2 = rotate(x1, y1, sight_x, sight_y, bullet_direction)

    #pygame.draw.line(win, (200, 200, 200), (x1, y1), (x2, y2), 1)
    # pygame.draw.line(win, (200, 200, 200), (10, 10), (500, 500), 1)
    for k in range(len(map_coords)):
        if max([x1, x2]) < map_coords[k][0] and max([x1, x2]) < map_coords[k][2]:
            continue
        elif min([x1, x2]) > map_coords[k][0] and min([x1, x2]) > map_coords[k][2]:
            continue
        elif max([y1, y2]) < map_coords[k][1] and max([y1, y2]) < map_coords[k][3]:
            continue
        elif min([y1, y2]) > map_coords[k][1] and min([y1, y2]) > map_coords[k][3]:
            continue
        elif intersect([x1, y1], [x2, y2], [map_coords[k][0], map_coords[k][1]], [map_coords[k][2], map_coords[k][3]]):
            p1 = np.array([x1, y1])
            p2 = np.array([x2, y2])
            p3 = np.array([map_coords[k][0], map_coords[k][1]])
            p4 = np.array([map_coords[k][2], map_coords[k][3]])
            in_point = seg_intersect(p1, p2, p3, p4)
            # pygame.draw.circle(win, (0,0,0), (int(in_point[0]), int(in_point[1])), 4)
            dist = np.sqrt((x1 - in_point[0]) ** 2 + (y1 - in_point[1]) ** 2)
            if dist <= dist_players:
                visual = False

    return visual

def bullet_colission(bullet_pos, bullet_direction, map_coords, win):

    colission = False
    sight_x = bullet_pos[0]
    sight_y = -100 + bullet_pos[1]

    x1_ = bullet_pos[0]
    y1_ = bullet_pos[1]

    x1, y1 = rotate(x1_, y1_, x1_, y1_+15, bullet_direction)
    x2, y2 = rotate(x1_, y1_, sight_x, sight_y, bullet_direction)

    #pygame.draw.line(win, (200, 200, 200), (x1, y1), (x2, y2), 1)
    #pygame.draw.line(win, (200, 200, 200), (10, 10), (500, 500), 1)
    for k in range(len(map_coords)):
        if max([x1, x2]) < map_coords[k][0] and max([x1, x2]) < map_coords[k][2]:
            continue
        elif min([x1, x2]) > map_coords[k][0] and min([x1, x2]) > map_coords[k][2]:
            continue
        elif max([y1, y2]) < map_coords[k][1] and max([y1, y2]) < map_coords[k][3]:
            continue
        elif min([y1, y2]) > map_coords[k][1] and min([y1, y2]) > map_coords[k][3]:
            continue
        elif intersect([x1, y1], [x2, y2], [map_coords[k][0], map_coords[k][1]], [map_coords[k][2], map_coords[k][3]]):
            p1 = np.array([x1, y1])
            p2 = np.array([x2, y2])
            p3 = np.array([map_coords[k][0], map_coords[k][1]])
            p4 = np.array([map_coords[k][2], map_coords[k][3]])
            in_point = seg_intersect(p1, p2, p3, p4)
            # pygame.draw.circle(win, (0,0,0), (int(in_point[0]), int(in_point[1])), 4)
            dist = 0.0025*np.sqrt((x1-in_point[0])**2 + (y1-in_point[1])**2)
            if dist <= 0.030:
                colission = True

    return colission
