from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from flappyq import get_random_gates, get_desired_state, check, levels, getGoalBlochs

FPS = 30
SCREENWIDTH  = 576
SCREENHEIGHT = 512
# amount by which base can maximum shift to left
PIPEGAPSIZE  = 200 # gap between upper and lower part of pipe
PIPEHEIGHT   = 320
BASEY        = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES, HITMASKS = {}, {}

# define the RGB value for white,
#  green, blue colour .
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        # amount by which base can maximum shift to left
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
    # cat
    (
        'assets/sprites/cat-upflap1.png',
        'assets/sprites/cat-midflap1.png',
        'assets/sprites/cat-downflap2.png',
    )
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-night-wide.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)

# list of quantum pipes
QUANTUM_PIPES_LIST = (
    'assets/sprites/pipe-purple.png',
)

try:
    xrange
except NameError:
    xrange = range


def main():
    global SCREEN, FPSCLOCK, LEVEL
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    LEVEL = 1
    pygame.display.set_caption('Flappy Q')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/IntroPageCat.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base-wide.png').convert_alpha()
    # boundary sprite
    IMAGES['boundary'] = pygame.image.load('assets/sprites/boundary.png').convert_alpha()
    # level 1 screen
    IMAGES['level1'] = pygame.image.load('assets/sprites/select.png').convert_alpha()
    # level 2 screen
    IMAGES['level2'] = pygame.image.load('assets/sprites/restart2.png').convert_alpha()


    while True:
        print("level: {}".format(LEVEL))
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        catPlayer = 3
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[3][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[3][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[3][2]).convert_alpha(),
            #pygame.image.load(PLAYERS_LIST[3][3]).convert_alpha(),
            #pygame.image.load(PLAYERS_LIST[3][4]).convert_alpha(),
            #pygame.image.load(PLAYERS_LIST[3][5]).convert_alpha(),
        )

        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        IMAGES['quantum_pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(QUANTUM_PIPES_LIST[0]).convert_alpha(), 180),
                pygame.image.load(QUANTUM_PIPES_LIST[0]).convert_alpha(),
        )


        # hismask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )


        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
            #getHitmask(IMAGES['player'][3]),
            #getHitmask(IMAGES['player'][4]),
            #getHitmask(IMAGES['player'][5]),
        )

        movementInfo = showWelcomeAnimation()

        crashInfo = mainGame(movementInfo)
        LEVEL = showGameOverScreen(crashInfo)


def showWelcomeAnimation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerShmVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):

                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame(movementInfo):
    quantumGateStatus = True # set dynamically based on a new measurement
    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe(quantumGateStatus)
    newPipe2 = getRandomPipe(quantumGateStatus)

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on flap
    playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
    playerMaxVelY =  10   # max vel along Y, max descend speed
    playerMinVelY =  -8   # min vel along Y, max ascend speed
    playerAccY    =   1   # players downward accleration
    playerRot     =  45   # player's rotation
    playerVelRot  =   3   # angular speed
    playerRotThr  =  20   # rotation threshold
    playerFlapAcc =  -9   # players speed on flapping
    playerFlapped = False # True when player flaps

    # LEVEL = 1
    q = QuantumRegister(levels[LEVEL]['qubits'])  # |0>
    c = ClassicalRegister(levels[LEVEL]['qubits'])
    circuit = QuantumCircuit(q, c)

    desired_state = get_desired_state(LEVEL)
    print("Desired state is: " + desired_state)
    # goal_blochs = getGoalBlochs(desired_state)
    # goal_blochs.savefig("desierd_sphere.png")

    # cblochs = getGoalBlochs(''.zfill(levels[LEVEL]['qubits']))
    # cblochs.savefig("current_sphere.png")

    rgates = get_random_gates(LEVEL)

    # define gate labels
    firstGateLabel = rgates[0][0].__name__ + str(rgates[0][1])
    secondGateLabel = rgates[1][0].__name__ + str(rgates[1][1])
    cstate = ''.zfill(levels[LEVEL]['qubits'])
    circuit_str = ''
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True


        # check for crash here
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperPipes, lowerPipes)
        if crashTest[0]:
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }

        # check for score
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:

                # NOTE: adding a check here for gate choice
                if 'quantum' in pipe.keys() and pipe['quantum'] == True:
                    gateno = checkGateChoice(upperPipes[0], lowerPipes[0], playery)

                    gate = rgates[gateno][0]
                    target = rgates[gateno][1]
                    gate(circuit, q[target - 1])
                    print("Applying gate: " + gate.__name__ + " on " + str(target))
                    p, cstate = check(desired_state, circuit, q, c)
                    print("Probabilaty for desired state is: " + str(p))
                    print("Current state: |" + cstate + ">")
                    circuit_str += gate.__name__ + str(target) + ' > '

                    # cblochs = getGoalBlochs(cstate)
                    # cblochs.savefig("current_sphere.png")

                    if p > 0.99:
                        return { 'score': p }

                    # Get new gates
                    rgates = get_random_gates(LEVEL)
                    firstGateLabel = rgates[0][0].__name__ + str(rgates[0][1])
                    secondGateLabel = rgates[1][0].__name__ + str(rgates[1][1])


                score += 1


        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # rotate the player
        if playerRot > -90:
            playerRot -= playerVelRot

        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe(quantumGateStatus)
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            if 'quantum' in uPipe.keys() and uPipe['quantum'] == True:
                SCREEN.blit(IMAGES['quantum_pipe'][0], (uPipe['x'], uPipe['y']))
                SCREEN.blit(IMAGES['quantum_pipe'][1], (lPipe['x'], lPipe['y']))

                # gate label text is written here
                font = pygame.font.Font('freesansbold.ttf', 32)

                upperText = font.render(firstGateLabel, True, white)
                lowerText = font.render(secondGateLabel, True, white)
                if ((uPipe['x'] == upperPipes[0]['x'] and playerx < uPipe['x']) or \
                    ('quantum' in upperPipes[1].keys() and upperPipes[1]['quantum'] == True and \
                    'quantum' in upperPipes[0].keys() and upperPipes[0]['quantum'] == False and \
                    playerx < upperPipes[1]['x'])): # compare against player x pos as well
                    SCREEN.blit(upperText, (uPipe['x'] + 10, uPipe['y'] + 250)) # upper pipe label
                    SCREEN.blit(lowerText, (lPipe['x'] + 10, lPipe['y'] + 25)) # lower pipe label
                    # boundary line gets drawn here
                    SCREEN.blit(IMAGES['boundary'], (uPipe['x'], uPipe['y'] + 420)) # draw boundary
            else:
                SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
                SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        # print score so player overlaps the score
        showScore(score)
        showState(cstate, desired_state, circuit_str)


        # Player rotation has a threshold
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot

        playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
        SCREEN.blit(playerSurface, (playerx, playery))

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def checkGateChoice(uPipe, lPipe, pHeight):
    """ checks the player's gate choice by looking at the height within the pipegap """
    # print("player height: {}".format(pHeight))
    # print("upper pipe: {}".format(uPipe['y']))
    # print("lower pipe: {}".format(lPipe['y']))
    if (uPipe['y'] + PIPEHEIGHT + (PIPEGAPSIZE / 2) > pHeight):
        print('top gate')
        return 0
    else:
        print('bottom gate')
        return 1


def showGameOverScreen(crashInfo):
    """crashes the player down ans shows gameover image"""
    score = crashInfo['score']
    print(crashInfo)
    if score >= .99 and 'groundCrash' not in crashInfo.keys():
        if LEVEL == 1:
            SCREEN.blit(IMAGES['level1'], (0,0))
        elif LEVEL == 2:
            SCREEN.blit(IMAGES['level2'], (0,0))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    return 2

    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return 1

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # rotate only when it's a pipe crash
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        SCREEN.blit(playerSurface, (playerx,playery))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe(quantumGateStatus):
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 25 # gap between pipes on the ground
    qStatus = random.choice([True, False])
    return [
        {'x': pipeX, 'y': gapY - pipeHeight, 'quantum': qStatus},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE, 'quantum': qStatus}, # lower pipe
    ]


def showState(current_state, desired_state, circuit_str):
    font = pygame.font.Font('freesansbold.ttf', 22)
    Xoffset = (SCREENWIDTH - 50 ) / 2

    text = font.render('|%s> current' % current_state, True, (20, 20, 20))
    SCREEN.blit(text, (Xoffset, SCREENHEIGHT * 0.90))

    text = font.render('|%s> desired' % desired_state, True, (20, 20, 20))
    SCREEN.blit(text, (Xoffset, SCREENHEIGHT * 0.85))

    text = font.render(circuit_str, True, (20, 20, 20))
    SCREEN.blit(text, (5, SCREENHEIGHT * 0.95))

def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        #SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

if __name__ == '__main__':
    main()
