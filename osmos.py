#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:     demonstrate physics in a fun absorption game
#
# Author:      Abdul
#
# Created:     06/08/2012
# Copyright:   (c) Abdul 2012
#-------------------------------------------------------------------------------

# essential declarations
from pygame import *
from random import *
from sys import *
from math import *
import pygame, sys, random, math

WHITE =255,255,255 # background
BLUE = 0,0,255
RED = 255,0,0
GREEN = 0,255,0
YELLOW = 255,255,0
PURPLE = 255,0,255
BLACK = 0,0,0
NUM_COLOURS = 7

background = image.load('space.jpg')
anyKey = image.load('hit_a_key.png')
gameOverImg = image.load('game_over.png')
winImg = image.load('win.png')
instructions = image.load('instructions.png')

WIDTH = 800
HEIGHT = 600
FPS = 50

init()
mainClock = time.Clock()
screen = display.set_mode((WIDTH, HEIGHT))
display.set_caption('Osmos')
font = font.SysFont(None, 48)
game = True
main = True
mouseForce = 0
friction = 5
screen.blit(background, (0,0))
display.flip()
player = {'x':400, 'y':300, 'xVel': 0, 'yVel':0, 'rad':10}
mouse = {'x':0, 'y':0}
rad = 50
mass = 1000
dx = 0
dy = 0
density = 2
playerDragCoef = 0.5
PI = 3.14
mousePressed = False
inanimates = []


def getAngle(dx, dy):
    angle = 0
    if dx == 0:
        angle = 0
    else:
        relatedAcuteAngle = abs(degrees (atan (dy / dx)))
    if dx > 0 and dy > 0: # (x,y)
        angle = relatedAcuteAngle
    if dx > 0 and dy < 0: # (x,-y)
        angle = - relatedAcuteAngle
    if dx < 0 and dy > 0: # (-x,y)
        angle = - relatedAcuteAngle - 180
    if dx < 0 and dy < 0: # (-x,-y)
        angle = relatedAcuteAngle + 180
    return angle

def circleCollide(x1,y1,r1,x2,y2,r2):
    d = sqrt((y2-y1) * (y2-y1) + (x2-x1) * (x2-x1))
    if d < r1 + r2:
        return True
    return False

def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: # pressing escape quits
                    quit()
                return

def ejectMatter(player, inanimates, angle):
    areaOriginal = PI * player['rad'] ** 2
    areaChange = 0.003 * areaOriginal
    areaPlayer = areaOriginal - areaChange

    # conservation of momentum - X
    inanimatesVelX = (areaOriginal * player['xVel'] - (areaOriginal - areaChange) * (player['xVel'] + 2 * cos(radians(angle)))) / areaChange

    # conservation of momentum - Y
    inanimatesVelY = (areaOriginal * player['yVel'] - (areaOriginal - areaChange) * (player['yVel'] + 2 * sin(radians(angle)))) / areaChange

    player['xVel'] += 4 * cos(radians(angle))
    player['yVel'] += 4 * sin(radians(angle))

    inanimates.append(
        {'x':player['x'] + player['rad'] * 1.5  * cos(radians(angle + 180)) + sqrt(areaChange / PI) * 1.5 * cos(radians(angle)),
        'y':player['y'] + player['rad'] * 1.5 * sin(radians(angle + 180)) + sqrt(areaChange / PI) * 1.5 * sin(radians(angle)),
        'xVel': inanimatesVelX,
        'yVel': inanimatesVelY,
        'rad': sqrt(areaChange / PI)})
    player['rad'] -= sqrt(areaChange / PI)
    return (player, inanimates)

def spawny(HEIGHT):
    listOfRanges = randint(100, HEIGHT / 2 - 100), randint(HEIGHT / 2 + 100, HEIGHT - 100)
    spawn = listOfRanges[randint(0,1)]
    return spawn

def spawnx(WIDTH):
    listOfRanges = (randint(100, WIDTH / 2 - 100), randint(WIDTH / 2 + 100, WIDTH - 100))
    spawn = listOfRanges[randint(0,1)]
    return spawn

def mergeMatter(player, inanimates, level):
    level = True
    for i in inanimates: # had to make sure area changes, and radius changes with respect to area
        if circleCollide(player['x'], player['y'], player['rad'], i['x'], i['y'], i['rad']):
            distance = sqrt((player['y']-i['y']) ** 2 + (player['x']-i['x']) ** 2)
            overlap = player['rad'] + i['rad'] - distance
            areaChange = 10*PI
            changeSpeed = True
            pAreai = player['rad'] ** 2 * PI
            iAreai = i['rad'] ** 2 * PI

            if iAreai > areaChange:
                if player['rad'] >= i['rad']:
                    player['rad'] += sqrt(areaChange / PI)
                    i['rad'] -= sqrt(areaChange / PI)
            else:
                if player['rad'] >= i['rad']:
                    player['rad'] += sqrt(iAreai / PI)
                    i['rad'] -= sqrt(iAreai / PI)


            if pAreai > areaChange:
                if player['rad'] < i['rad']:
                    changeSpeed = False
                    player['rad'] -= sqrt(areaChange / PI)
                    i['rad'] += sqrt(areaChange / PI)
            else:
                if player['rad'] < i['rad']:
                    changeSpeed = False
                    player['rad'] -= sqrt(pAreai / PI)
                    i['rad'] += sqrt(pAreai / PI)


            pAreaf = player['rad'] ** 2 * PI
            iAreaf = i['rad'] ** 2 * PI

            # change in velocity - momentum applies
            if player['rad'] > 0:
                player['xVel'] = pAreai * player['xVel'] / pAreaf
                player['yVel'] = pAreai * player['yVel'] / pAreaf
            else:
                player['xVel'] = 0
                player['yVel'] = 0
            if i['rad'] > 0:
                i['xVel'] = iAreai * i['xVel'] / iAreaf
                i['yVel'] = iAreai * i['yVel'] / iAreaf
            else:
                i['xVel'] = 0
                i['yVel'] = 0

            if i['rad'] <= 0:
                inanimates.remove(i)
            if player['rad'] <= 0:
                level = True
    return (player, inanimates, level)


while main:
    game = False
    lvl = True
    gameOver = False
    player = {'x':400, 'y':300, 'xVel': 0, 'yVel':0, 'rad':15}
    screen.blit(background, (0,0))
    screen.blit(anyKey, (0,0))
    display.flip()
    waitForPlayerToPressKey()

    screen.blit(background, (0,0))
    screen.blit(instructions, (0,30))
    display.flip()
    waitForPlayerToPressKey()

    # initial inanimate objects
    inanimates = [
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': 5},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': 10},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': 15},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': 10},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': 5},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': randint(1,10)},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': randint(1,11)},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': randint(1,12)},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': randint(1,13)},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': randint(1,14)},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': randint(1,15)},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': randint(1,16)},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': randint(1,17)},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': randint(1,18)},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': randint(1,19)},
        {'x':spawnx(WIDTH), 'y':spawny(HEIGHT), 'xVel': randint(20,80), 'yVel': randint(20,50), 'rad': randint(1,20)}]
#===========================================================================================================================#
    while lvl:


        mousePressed = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEMOTION:
                mouse['x'] = event.pos[0]
                mouse['y'] = event.pos[1]
##            if event.type == MOUSEBUTTONDOWN:
##                mousePressed = True
            if event.type == MOUSEBUTTONUP:
                mousePressed = True



        dxMouse = mouse['x'] - player['x']
        dyMouse = mouse['y'] - player['y']
        angleMovement = getAngle(dxMouse,dyMouse) + 180


# ----------------------------- velocity change ------------------------------ #
        # X-Direction Player
##        netForcex =  mouseForce * cos(radians(angle))
##        accelx = netForcex / mass

        if player['x'] + player['rad'] > WIDTH:
            player['xVel'] = -abs(player['xVel'])
        if player['x'] - player['rad'] < 0:
            player['xVel'] = abs(player['xVel'])
        player['x'] += 0.1 * player['xVel']


        # Y-Direction Player
##        netForcey = mouseForce * sin(radians(angle))
##        accely = netForcey / mass


        if player['y'] + player['rad'] > HEIGHT:
            player['yVel'] = -abs(player['yVel'])
        if player['y'] - player['rad'] < 0:
            player['yVel'] = abs(player['yVel'])
        player['y'] += 0.1 * player['yVel']

        # X-Direction Inanimates
        for i in inanimates:
            if i['x'] + i['rad'] > WIDTH:
                i['xVel'] = -abs(i['xVel'])
            if i['x'] - i['rad'] < 0:
                i['xVel'] = abs(i['xVel'])
            i['x'] +=  0.01 * i['xVel']

        # Y-Direction inanimates
        for i in inanimates:
            if i['y'] + i['rad'] > HEIGHT:
                i['yVel'] = -abs(i['yVel'])
            if i['y'] - i['rad'] < 0:
                i['yVel'] = abs(i['yVel'])
            i['y'] +=  0.01 * i['yVel']


        if mousePressed:
            new = ejectMatter(player, inanimates, angleMovement)
            player = new[0]
            inanimates = new[1]

        temp = mergeMatter(player, inanimates, game)
        player = temp[0]
        inanimates = temp[1]
        lvl = temp[2]
        for i in inanimates:
            temp = mergeMatter(i, inanimates, game)
            inanimates = temp[1]


        screen.blit(background, (0,0))
        if player['rad'] < 0:
            player['rad'] = 0
        if player['rad'] <= 0:
            gameOver = True
            time.delay(1000)
            break
        if len(inanimates) == 0:
            win = True
            time.delay(1000)
            break
        try:
            draw.circle(screen, GREEN, (round(player['x']), round(player['y'])), round(player['rad']))
        except OverflowError:
            pass
        for i in inanimates:
            if i['rad'] > player['rad']:
                try:
                    draw.circle(screen, RED, (round(i['x']), round(i['y'])), round(i['rad']))
                except OverflowError:
                    pass
            else:
                try:
                    draw.circle(screen, BLUE, (round(i['x']), round(i['y'])), round(i['rad']))
                except OverflowError:
                    pass
        display.flip()
##        print(player['xVel'], player['yVel'])
        time.delay(20)

    if gameOver:
        screen.blit(gameOverImg, (0,0))
        display.flip()
        time.delay(3000)
    else:
        screen.blit(winImg, (0,0))
        display.flip()
        time.delay(3000)
