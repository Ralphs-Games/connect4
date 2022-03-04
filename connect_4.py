###################################################
# Connect-4 (aka The Captain's Mistress)
# The Captain's Mistress is supposedly the game
# that so engrossed Captain Cook during his long
# voyages that his crew gave it that name
###################################################
# 3/3/22, 10:20 PM

'''
to do:

check disk drop speed...

alternate player that goes first
_keep stats on # wins per player

_quit() -> sys.exit()

_fix full board draw checking
_fix ai drops into full column
_? fix ai moves when no 3iar or 4iar ?
AI for single player mode (in process)
    _add 2iar strategy code
    look for gaps? XX.X

_2d array (but can't hold class instances)
_screen <= screen
_Screen update from 1d array
Screen update from 2d array ??
_2 player mode (easier)
_victory ck
_replay?

robot arm??

'''

import pygame
import time
import random
import sys
import os
import numpy as np

# must come before pygame.init():
os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()

display_width = 1920
display_height = 1080

screen = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption("Connect 4")

# why isn't this working?
#gameIcon = pygame.image.load('images/nfl-league-logo-100x100.png').convert_alpha()
#gameIcon = pygame.image.load('images/connect_four_icon2.png').convert_alpha()
#gameIcon = pygame.image.load('./images/connect_four_icon.png').convert_alpha()
#pygame.display.set_icon(gameIcon)

clock = pygame.time.Clock()

random.seed()  # uses system time as a seed

#random.randint(a, b)   #Return a random integer N such that a <= N <= b

### display setup & colors ###
black = (0,0,0)
white = (255,255,255)
brightgreen = (0,255,0)
lightblue = (0,255,255)
pink = (255,0,255)

# bright colors:
#blue   = (0,0,255)
#red    = (235,0,0)
#yellow = (240,240,0)

# not so bright colors:
blue   = (40,40,220)
red    = (230,0,0)
yellow = (240,240,0)
green  = (0,200,0)

### board setup ###
boardRows = 6
boardCols = 7

squareSize = 150
squareBorder = 5
# use if no border desired:
#squareSize = 155
#squareBorder = 0
circleRadius = 50

boardStartX = 420
boardStartY = 130

### game play variables ###
numPlayers = 2  # 1 for human vs. computer, 2 for human vs. human
turnPlayer = 1  # 1 or 2. Computer is player 1 if single player mode
winner     = 0  # 1 or 2, winning player
playCount  = 0  # a play is one round, i.e. computer and human each taking a turn
playColumn = 3  # ai always picks this on first move
leftRight  = 0  # for random ai movement

# can be changed at game start:
colorPlayer1 = red
colorPlayer2 = yellow

# stats? num victories by each player/computer?
winsPlayer1 = 0
winsPlayer2 = 0

dropSound = pygame.mixer.Sound('./sounds/sfx_sounds_impact6.wav')
honk3Sound = pygame.mixer.Sound('./sounds/honk3.wav')

# debug:
debugHilite = False


#---------------------------
# Functions:

def drawRect(rect_x, rect_y, rect_w, rect_h, color):
    pygame.draw.rect(screen, color, [rect_x, rect_y, rect_w, rect_h])

def drawCirle(x, y, radius, color, width=0):   # x,y is center. If width > 1, is line thickness, else filled. 
    pygame.draw.circle(screen, color, (x, y), radius, width)   # circle(surface, color, center, radius) 


## no longer using this, see boardSquare class
#def drawSquare(x, y, size, color, disc, hilite):
#    drawRect(x, y, size, size, color)
#    drawCirle(x + squareSize/2, y + squareSize/2, circleRadius+2, black)   # draw hole in square
#    drawCirle(x + squareSize/2, y + squareSize/2, circleRadius, disc)        # fill if disc present
#    drawCirle(x + squareSize/2, y + squareSize/2, circleRadius-3, black, 2)
#    drawCirle(x + squareSize/2, y + squareSize/2, circleRadius-8, black, 2)
#    if hilite == True:
#        drawCirle(x + squareSize/2, y + squareSize/2, circleRadius+10, brightgreen, 8)   # drawCircleHiLite

## might need this later... unused currently
## draws at x,y; is this useful?? use isover instead to update class? then drawSquare?
#def drawDisc(x, y, color):
#    drawCirle(x, y, circleRadius, color)
#    drawCirle(x, y, circleRadius-3, black, 2)
#    drawCirle(x, y, circleRadius-8, black, 2)

## might need this later...
#def drawCircleHiLite(x, y):
#    drawCirle(x + squareSize/2, y + squareSize/2, circleRadius+10, brightgreen, 8)

# debug: (misc stuff)
# misc debug stuff I'm no longer using below...

# debug:
# print 2d array of class instances (this doesn't work!!)
#for i in range(boardRows*boardCols):
#    print(squaresArray(i,))

# debug:
# print 2d array values
#for i in range(boardRows):
#    for j in range(boardCols):
#        print(squares2dArray[i,j])
##        k = i // boardCols
##        l = i %  boardCols

#           debug:
#            drawDisc(pos[0], pos[1], green)
#           debug:
#            print('mouse_x =',pos[0],' mouse_y =',pos[1])

#keys = pygame.key.get_pressed()
#if keys[pygame.K_y]:

#squaresArray[38].disc = 'red'

                    # debug:
                    #for i in range (len(squaresArray)):
                    #    squaresArray[i].hilite = False
                    #    if squaresArray[i].isOver(pos):
                    #        squaresArray[i].hilite = True


# create class for board squares
class boardSquare():
    def __init__(self, x, y, disc=black, hilite=False, color=blue, size=squareSize):
        self.x = x
        self.y = y
        self.disc = disc
        self.hilite = hilite
        self.color = color
        self.size = size

    # call this method to draw the square on the screen: squaresArray[i].draw()
    def draw(self):
        drawRect(self.x, self.y, self.size, self.size, self.color)
        drawCirle(self.x + squareSize/2, self.y + squareSize/2, circleRadius+2, black)   # draw hole in square
        drawCirle(self.x + squareSize/2, self.y + squareSize/2, circleRadius, self.disc)   # fill if disc present
        drawCirle(self.x + squareSize/2, self.y + squareSize/2, circleRadius-3, black, 2)
        drawCirle(self.x + squareSize/2, self.y + squareSize/2, circleRadius-8, black, 2)
        if self.hilite == True:
            drawCirle(self.x + squareSize/2, self.y + squareSize/2, circleRadius+10, brightgreen, 8)   # draw Circle HiLite

    # pos is the mouse position or a tuple of (x,y) coordinates
    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.size:
            if pos[1] > self.y and pos[1] < self.y + self.size:
                drawCirle(self.x + squareSize/2, self.y + squareSize/2, circleRadius+10, brightgreen, 8)   # draw Circle HiLite
                return True
        drawCirle(self.x + squareSize/2, self.y + squareSize/2, circleRadius+10, self.color, 8)   # erase Circle HiLite
        return False


# create array for boardSquare class instances
squaresArray = []

def initSquaresArray():

    print("initSquaresArray")
    # debug:
    #print("")
    #print("squaresArray debug")
    #print("i,j,  x,  y")

    # initialize array of class boardSquare
    for i in range(boardRows):
        for j in range(boardCols):
            squaresArray.append(boardSquare((boardStartX + squareSize*j + squareBorder*j), (boardStartY + squareSize*i + squareBorder*i), black, False))
            #debug:
            #print(i,j,(boardStartX + squareSize*j + squareBorder*j), (boardStartY + squareSize*i + squareBorder*i))

    ## debug:
    ## this works best!
    #print("")
    #print("print squaresArray i,j direct")
    #print("  x,  y, disc, hilite")
    #for i in range(boardRows):
    #    for j in range(boardCols):
    #        print(squaresArray[i*boardCols + j].x,squaresArray[i*boardCols + j].y,squaresArray[i*boardCols+j].disc, squaresArray[i*boardCols+j].hilite)


# re-initialize array of class boardSquare
def clearSquaresArray():

    print("clearSquaresArray")
    for i in range(boardRows):
        for j in range(boardCols):
            squaresArray[i*boardCols + j].disc = black
            squaresArray[i*boardCols + j].hilite = False
    # debug:
    #print("")
    #print("print squaresArray i,j direct")
    #print("  x,  y, disc, hilite")
    #for i in range(boardRows):
    #    for j in range(boardCols):
    #        print(squaresArray[i*boardCols + j].x,squaresArray[i*boardCols + j].y,squaresArray[i*boardCols+j].disc, squaresArray[i*boardCols+j].hilite)

def clearSquaresHilite():

    print("clearSquaresArray")
    for i in range(boardRows):
        for j in range(boardCols):
            squaresArray[i*boardCols + j].hilite = False


# create 2D array for board squares
squares2dArray = np.zeros((6,7), dtype=int)

def update2dArray():

    ## debug:
    #print("")
    #print(squares2dArray)  # before update
    #print("")

    for i in range(boardRows):
        for j in range(boardCols):
            #arr = np.append(arr, 7)
    #        squaresArray = np.append(squaresArray, boardSquare((boardStartX + squareSize*j + squareBorder*j), (boardStartY + squareSize*i + squareBorder*i)))
            if squaresArray[i*boardCols + j].disc == black:
                squares2dArray[i,j] = 0
            elif squaresArray[i*boardCols + j].disc == colorPlayer1:  # colorPlayer1 red
                squares2dArray[i,j] = -1
            elif squaresArray[i*boardCols + j].disc == colorPlayer2:  # colorPlayer2 yellow
                squares2dArray[i,j] = 1
            #debug:
            #print(i,j,(boardStartX + squareSize*j + squareBorder*j), (boardStartY + squareSize*i + squareBorder*i))

    # debug:
    #update2dArray()
    print("update2dArray()")
    print(squares2dArray)   # after update
    #print("")


def redrawWindow():
    # draw game playing surface, including squares with disc & hilite if set
    screen.fill(black)
    for i in range(boardRows*boardCols):
        squaresArray[i].draw()
        #def drawSquare(x, y, size, color, disc):
        #drawSquare(squaresArray[i].x, squaresArray[i].y, squaresArray[i].size, squaresArray[i].color, squaresArray[i].disc, squaresArray[i].hilite)

    textmsg = "Connect 4"
    font = pygame.font.SysFont('comicsansms', 70)  # comicsansms arial
    text = font.render(textmsg,1,white)
    screen.blit(text, (30,10))

    textmsg = "'The Captain's Mistress'"
    font = pygame.font.SysFont('comicsansms', 30)  # comicsansms arial
    text = font.render(textmsg,1,white)
    screen.blit(text, (30,110))

    font = pygame.font.SysFont('comicsansms', 30)  # comicsansms arial

    textmsg = "Player #1 Score:"
    text = font.render(textmsg,1,colorPlayer1)
    screen.blit(text, (1560,40))
#    screen.blit(text, (30,150))
#    print("winsPlayer1 =",winsPlayer1)
    textmsg = str(winsPlayer1)
    text = font.render(textmsg,1,colorPlayer1)
    screen.blit(text, (1820,40))
#    screen.blit(text, (50,150))

    #randNumLabel = myFont.render("You have rolled:", 1, black)
    #diceDisplay = myFont.render(str(diceRoll), 1, black)

    textmsg = "Player #2 Score:"
    text = font.render(textmsg,1,colorPlayer2)
    screen.blit(text, (1560,80))
#    screen.blit(text, (30,200))
#    print("winsPlayer2 =",winsPlayer2)
    textmsg = str(winsPlayer2)
    text = font.render(textmsg,1,colorPlayer2)
    screen.blit(text, (1820,80))
#    screen.blit(text, (50,200))

    #update2dArray()
    pygame.display.update()



class Button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    #Call this method to draw the button on the screen
    def draw(self,screen,outline=None):
        if outline:
            pygame.draw.rect(screen, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(screen, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text != '':
            font = pygame.font.SysFont('arial', 40)
            text = font.render(self.text, 1, black)
            screen.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    #pos is the mouse position or a tuple of (x,y) coordinates
    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

class ButtonCir():
    def __init__(self, color, x, y, radius, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.radius = radius
        self.text = text

    #call this method to draw the button on the screen
    def draw(self,screen,outline=None):
        if outline:
            pygame.draw.circle(screen, outline, (self.x, self.y), self.radius+2)   # circle(surface, color, center, radius) 
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)   # circle(surface, color, center, radius) 
        
        if self.text != '':
            font = pygame.font.SysFont('arial', 40)
            text = font.render(self.text, 1, black)
            screen.blit(text,(self.x-11,self.y-22))
            #screen.blit(text, (self.x + (self.radius/2 - text.get_width()/2), self.y + (self.radius/2 - text.get_height()/2)))

    #pos is the mouse position or a tuple of (x,y) coordinates
    def isOver(self, pos):
        if pos[0] > self.x - self.radius and pos[0] < self.x + self.radius:
            if pos[1] > self.y - self.radius and pos[1] < self.y + self.radius:
                return True
            
        return False


instructions = ["*** Instructions ***"
,""
,"The Captain's Mistress"
,""
,"The Captain's Mistress is supposedly the game that so engrossed Captain Cook"
,"during his long voyages that his crew gave it the name that has stuck to this day."
,"Modern day copies such as Connect 4 are simply rehashed versions of this game."
,""
,"Connect 4 is a two-player connection board game in which the players choose a color"
,"and then take turns dropping colored discs into a seven-column, six-row vertical grid."
,"The pieces fall straight down, occupying the lowest available space within the column."
,"The objective of the game is to be the first to form a horizontal, vertical,"
,"or diagonal line of four of one's own discs."
,""
,"You may also play against the computer as a single player."
,"The computer always moves first."
,""
,"Position the mouse at the top square of the column you want to choose"
,"and then click to drop a piece down it."]


def displayInstructions():
    pygame.event.clear()  # This will clear any pending events (keys held down or released) from the previous run
    run_di = True

    yesButton = Button((255,255,0), 740,804,40,40,'Y')

    while run_di:

        screen.fill(black)
        font = pygame.font.SysFont('arial', 40)  # comicsansms arial

        for i in range(len(instructions)):
            text = font.render(instructions[i],1,white)
            screen.blit(text, (340,40*i+10))

        text = "Are you ready to play?"
        text = font.render(text,1,white)
        screen.blit(text, (340,800))
    
        yesButton.draw(screen,(0,0,0))  #surface, outline
        pygame.display.update()

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                run_di = False
                pygame.quit()
                sys.exit()
    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    print("instructions Done")
                    #instructionsDone = 1
                    run_di = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if yesButton.isOver(pos):
                    print("instructions Done")
                    #instructionsDone = 1
                    run_di = False
    
            if event.type == pygame.MOUSEMOTION:
                if yesButton.isOver(pos):
                    yesButton.color = (0,255,0)
                else:
                    yesButton.color = (255,255,0)


def game_setup():

    pygame.event.clear()
    run_setup = True

    instructionsDone = 0
    numPlayersDone = 0
    discColorDone = 0

    # reset game variables:
    global numPlayers
    numPlayers = 2  # 1 for human vs. computer, 2 for human vs. human
    global turnPlayer
    turnPlayer = 1  # 1 or 2. Computer is player 1 if single player mode
    print("game_setup: turnPlayer = ",turnPlayer)
    global winner
    winner = 0      # 1 or 2, winning player
    global playCount
    playCount = 0   # a play is one round, i.e., computer and human each taking a turn

    global colorPlayer1
    global colorPlayer2
    colorPlayer1 = red
    colorPlayer2 = yellow

    # ai left/right coin toss:
    global leftRight
    leftRight = random.randint(0,1)
    print("game_setup: leftRight =",leftRight)

    #yesButton = ButtonCir((255,255,0), 1200,70,25,'Y')
    #noButton  = ButtonCir((255,255,0), 1270,70,25,'N')
    yesButton = Button((255,255,0), 1180,50,40,40,'Y')
    noButton  = Button((255,255,0), 1250,50,40,40,'N')

    initSquaresArray()
    update2dArray()
    redrawWindow()
    #pygame.display.update()

    print("game_setup = while run_setup")

    while run_setup:

        #redrawWindow()
#        clock.tick(10)
        clock.tick(30)

#       "Do you need instructions?"
        if instructionsDone == 0:
            textmsg = "Do you need instructions?"
            font = pygame.font.SysFont('comicsansms', 40)  # comicsansms arial
            #font = pygame.font.SysFont('arial', 30)
            text = font.render(textmsg,1,white)
            screen.blit(text, ((display_width/2)-320,40))

            yesButton.draw(screen,(0,0,0))  #surface, outline
            noButton.draw(screen,(0,0,0))  #surface, outline
            pygame.display.update()

            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    run_setup = False
                    pygame.quit()
                    sys.exit()

                #if event.type == pygame.KEYDOWN:
                    #if event.key == pygame.K_LEFT:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_y]:  # supports upper & lower case
                    print("displayInstructions = yes")
                    displayInstructions()
                    instructionsDone = 1
                    redrawWindow()

                if keys[pygame.K_n]:  # supports upper & lower case
                    print("displayInstructions = no")
                    instructionsDone = 1
                    redrawWindow()
                    #run_setup = False

                pos = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if yesButton.isOver(pos):
                        print("displayInstructions = yes")
                        displayInstructions()
                        yesButton.color = (255,255,0)
                        instructionsDone = 1
                        redrawWindow()
                    if noButton.isOver(pos):
                        print("displayInstructions = no")
                        noButton.color = (255,255,0)
                        instructionsDone = 1
                        redrawWindow()
                        #run_setup = False

                if event.type == pygame.MOUSEMOTION:
                    if yesButton.isOver(pos):
                        yesButton.color = (0,255,0)
                    else:
                        yesButton.color = (255,255,0)
                    if noButton.isOver(pos):
                        noButton.color = (0,255,0)
                    else:
                        noButton.color = (255,255,0)

#       "Is this a two player game?"
        elif numPlayersDone == 0:
            textmsg = "Is this a two player game?"
            font = pygame.font.SysFont('comicsansms', 40)  # comicsansms arial
            #font = pygame.font.SysFont('arial', 30)
            text = font.render(textmsg,1,white)
            screen.blit(text, ((display_width/2)-320,40))

            #yesButton = ButtonCir((255,255,0), 1200,70,25,'Y')
            #noButton  = ButtonCir((255,255,0), 1270,70,25,'N')

            yesButton.draw(screen,(0,0,0))  #surface, outline
            noButton.draw(screen,(0,0,0))  #surface, outline
            pygame.display.update()
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_setup = False
                    pygame.quit()
                    sys.exit()

                keys = pygame.key.get_pressed()
                if keys[pygame.K_y]:  # supports upper & lower case
                    numPlayers = 2
                    numPlayersDone = 1
                    print("numPlayers = ",numPlayers)
                    redrawWindow()
#                    run_setup = False

                if keys[pygame.K_n]:  # supports upper & lower case
                    numPlayers = 1
                    numPlayersDone = 1
                    print("numPlayers = ",numPlayers)
                    redrawWindow()
#                    run_setup = False

                pos = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if yesButton.isOver(pos):
                        numPlayers = 2
                        numPlayersDone = 1
                        print("numPlayers = ",numPlayers)
                        redrawWindow()
#                        run_setup = False
                    if noButton.isOver(pos):
                        numPlayers = 1
                        numPlayersDone = 1
                        print("numPlayers = ",numPlayers)
                        redrawWindow()
#                        run_setup = False

                if event.type == pygame.MOUSEMOTION:
                    if yesButton.isOver(pos):
                        yesButton.color = (0,255,0)
                    else:
                        yesButton.color = (255,255,0)
                    if noButton.isOver(pos):
                        noButton.color = (0,255,0)
                    else:
                        noButton.color = (255,255,0)
                    pygame.display.update()

#       "What color disc do you want?"
        elif discColorDone == 0:
            textmsg = "What color discs, Player 2?"
            font = pygame.font.SysFont('comicsansms', 40)  # comicsansms arial
            #font = pygame.font.SysFont('arial', 30)
            text = font.render(textmsg,1,white)
            screen.blit(text, ((display_width/2)-350,40))

            #redButton = ButtonCir((255,0,0), 1200,70,25,'')
            #yelButton = ButtonCir((255,255,0), 1270,70,25,'')
            redButton = Button((255,0,0), 1180,50,40,40,'R')
            yelButton = Button((255,255,0), 1250,50,40,40,'Y')

            redButton.draw(screen,(0,0,0))  #surface, outline
            yelButton.draw(screen,(0,0,0))  #surface, outline
            pygame.display.update()
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_setup = False
                    pygame.quit()
                    sys.exit()

                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:  # supports upper & lower case
                    colorPlayer1 = yellow
                    colorPlayer2 = red
                    discColorDone = 1
                    print("colorPlayer2 =",colorPlayer2)  # debug
                    run_setup = False

                if keys[pygame.K_y]:  # supports upper & lower case
                    colorPlayer1 = red
                    colorPlayer2 = yellow
                    discColorDone = 1
                    print("colorPlayer2 =",colorPlayer2)  # debug
                    run_setup = False

                pos = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if redButton.isOver(pos):
                        colorPlayer1 = yellow
                        colorPlayer2 = red
                        discColorDone = 1
                        print("colorPlayer2 =",colorPlayer2)  # debug
                        run_setup = False
                    if yelButton.isOver(pos):
                        colorPlayer1 = red
                        colorPlayer2 = yellow
                        discColorDone = 1
                        print("colorPlayer2 =",colorPlayer2)  # debug
                        run_setup = False

                if event.type == pygame.MOUSEMOTION:
                    if redButton.isOver(pos):
                        redButton.color = (255,0,0)
                    else:
                        redButton.color = red
                    if yelButton.isOver(pos):
                        yelButton.color = (255,255,0)
                    else:
                        yelButton.color = yellow
                    pygame.display.update()

    print("intro exit: turnPlayer = ",turnPlayer)   # debug
    redrawWindow()
    game_loop()   # experimental... but it seems to work!

#def game_setup(): end


def dropDisc(column,color):
    print("dropDisc")
    global squaresArray
    run_dd = 1
    delay = 25

    while run_dd:

        clock.tick(5)   # experimental
        #pygame.time.delay(5000)

        if squares2dArray[1,column] == 0:
#            squaresArray[column].hilite = False
            squaresArray[column].disc = black
            squaresArray[column+7].disc = color
            squares2dArray[0,column] = 0
            redrawWindow()
            pygame.time.delay(delay)
        elif squares2dArray[1,column] != 0:
            run_dd = 0
        if squares2dArray[2,column] == 0:
            squaresArray[column+7].disc = black
            squaresArray[column+14].disc = color
            redrawWindow()
            pygame.time.delay(delay)
        elif squares2dArray[2,column] != 0:
            run_dd = 0
        if squares2dArray[3,column] == 0:
            squaresArray[column+14].disc = black
            squaresArray[column+21].disc = color
            redrawWindow()
            pygame.time.delay(delay)
        elif squares2dArray[3,column] != 0:
            run_dd = 0
        if squares2dArray[4,column] == 0:
            squaresArray[column+21].disc = black
            squaresArray[column+28].disc = color
            redrawWindow()
            pygame.time.delay(delay)
        elif squares2dArray[4,column] != 0:
            run_dd = 0
        if squares2dArray[5,column] == 0:
            squaresArray[column+28].disc = black
            squaresArray[column+35].disc = color
            redrawWindow()
            #pygame.time.delay(delay)
            run_dd = 0
        elif squares2dArray[5,column] != 0:
            run_dd = 0
    update2dArray()
    #print("dropDisc")
    #print(squares2dArray)
    dropSound.play()  #sfx_sounds_impact6.wav


def winnerCheck():

    print("winnerCheck")
    run_wc = True
    global winner
    numInRow = 0

    while run_wc:
        # check for board full draw
        winner = 2   # draw
        for i in range(boardRows):
            for j in range(boardCols):
                if squares2dArray[i,j] == 0:
                    winner = 0
                    run_wc = False
        # check rows
        numInRow = 0
        for i in range(boardRows):
            for j in range(4):
                numInRow = squares2dArray[i,j] + squares2dArray[i,j+1] + squares2dArray[i,j+2] + squares2dArray[i,j+3]
                if numInRow == 4:
                    winner = 1
                    print("winner = ",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[i*boardCols + j+1].hilite = True
                    squaresArray[i*boardCols + j+2].hilite = True
                    squaresArray[i*boardCols + j+3].hilite = True
                    run_wc = False
                elif numInRow == -4:
                    winner = -1
                    print("winner = ",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[i*boardCols + j+1].hilite = True
                    squaresArray[i*boardCols + j+2].hilite = True
                    squaresArray[i*boardCols + j+3].hilite = True
                    run_wc = False
        # check columns
        numInRow = 0
        for i in range(3):
            for j in range(boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j] + squares2dArray[i+2,j] + squares2dArray[i+3,j]
                if numInRow == 4:
                    winner = 1
                    print("winner = ",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[(i+1)*boardCols + j].hilite = True
                    squaresArray[(i+2)*boardCols + j].hilite = True
                    squaresArray[(i+3)*boardCols + j].hilite = True
                    run_wc = False
                elif numInRow == -4:
                    winner = -1
                    print("winner = ",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[(i+1)*boardCols + j].hilite = True
                    squaresArray[(i+2)*boardCols + j].hilite = True
                    squaresArray[(i+3)*boardCols + j].hilite = True
                    run_wc = False
        # check diagonals right
        numInRow = 0
        for i in range(3):
            for j in range(4):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j+1] + squares2dArray[i+2,j+2] + squares2dArray[i+3,j+3]
                if numInRow == 4:
                    winner = 1
                    print("winner = ",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[(i+1)*boardCols + j+1].hilite = True
                    squaresArray[(i+2)*boardCols + j+2].hilite = True
                    squaresArray[(i+3)*boardCols + j+3].hilite = True
                    run_wc = False
                elif numInRow == -4:
                    winner = -1
                    print("winner = ",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[(i+1)*boardCols + j+1].hilite = True
                    squaresArray[(i+2)*boardCols + j+2].hilite = True
                    squaresArray[(i+3)*boardCols + j+3].hilite = True
                    run_wc = False
        # check diagonals left
        numInRow = 0
        for i in range(3):
            for j in range(3,boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j-1] + squares2dArray[i+2,j-2] + squares2dArray[i+3,j-3]
                if numInRow == 4:
                    winner = 1
                    print("winner = ",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[(i+1)*boardCols + j-1].hilite = True
                    squaresArray[(i+2)*boardCols + j-2].hilite = True
                    squaresArray[(i+3)*boardCols + j-3].hilite = True
                    run_wc = False
                elif numInRow == -4:
                    winner = -1
                    print("winner = ",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[(i+1)*boardCols + j-1].hilite = True
                    squaresArray[(i+2)*boardCols + j-2].hilite = True
                    squaresArray[(i+3)*boardCols + j-3].hilite = True
                    run_wc = False

        print("winnerCheck end: winner = ",winner)
        run_wc = False
#def winnerCheck(): end


def endgame():

    clock.tick(3)
#    clock.tick(30)

    global winsPlayer1
    global winsPlayer2
    
    run_end = True
    yesButton = Button((255,255,0), 1180,50,40,40,'Y')
    noButton  = Button((255,255,0), 1250,50,40,40,'N')
#    yesButton = Button((255,255,0), 1750,50,40,40,'Y')
#    noButton  = Button((255,255,0), 1820,50,40,40,'N')
    redrawWindow()
    print("endgame winner = ",winner)

#    while run_end:

    font = pygame.font.SysFont('comicsansms', 50)  # comicsansms arial

    if winner == 1:
        winsPlayer2 = winsPlayer2 + 1
        textmsg = "Player #2 wins!!!"
        text = font.render(textmsg,1,colorPlayer2)
        screen.blit(text, ((display_width/2)-190,25))
    elif winner == -1:
        winsPlayer1 = winsPlayer1 + 1
        if numPlayers == 1:
            textmsg = "Computer wins!!!"
        elif numPlayers == 2:
            textmsg = "Player #1 wins!!!"
        text = font.render(textmsg,1,colorPlayer1)
        screen.blit(text, ((display_width/2)-190,25))
    elif winner == 2:
        textmsg = "It's a draw!!"
        text = font.render(textmsg,1,white)
        screen.blit(text, ((display_width/2)-190,25))

    pygame.display.update()
    pygame.time.wait(2000)

    redrawWindow()

    textmsg = "Play again?"
    text = font.render(textmsg,1,white)
    screen.blit(text, ((display_width/2)-190,25))
    pygame.display.update()

    while run_end:

        clock.tick(10)

#        redrawWindow()

#        textmsg = "Play again?"
#        text = font.render(textmsg,1,white)
#        screen.blit(text, ((display_width/2)-190,25))
#        #pygame.display.update()

        yesButton.draw(screen,(0,0,0))  #surface, outline
        noButton.draw(screen,(0,0,0))  #surface, outline
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_end = False
                pygame.quit()
                sys.exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_y]:  # supports upper & lower case
                run_end = False
                #initSquaresArray()
                clearSquaresArray()
                update2dArray()
                game_setup()
            if keys[pygame.K_n]:  # supports upper & lower case
                run_end = False
                pygame.quit()
                sys.exit()
            pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yesButton.isOver(pos):
                    run_end = False
                    #initSquaresArray()
                    clearSquaresArray()
                    update2dArray()
                    game_setup()
                if noButton.isOver(pos):
                    run_end = False
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEMOTION:
                if yesButton.isOver(pos):
                    yesButton.color = (0,255,0)
                else:
                    yesButton.color = (255,255,0)
                if noButton.isOver(pos):
                    noButton.color = (0,255,0)
                else:
                    noButton.color = (255,255,0)


def computer_ai():

    print("computer_ai")
    run_ai = True

    # ai algorithm/strategy:
    #
    # how to update to allow taking turns at who goes first?
    # 
    # 1. if ai gets first move: play 5,3 (always) playColumn = 3
    #
    # move tree:
    #
    # 2a. if user first move is 4,3: play 5,2 or 5,4 randomly (playColumn = 2 or 4)
    #   3a. if user 2nd move is 3,3: play 5,2 or 5,4, whichever is open (playColumn = 2 or 4)
    #   3b. if user 2nd move is 5,x: play 5,2 or 5,4 (if open), or else 5,1/5,5 to extend to 3iar (playColumn = 2/4 or 1/5)
    #           check to see what is open, from center outwards
    #
    # 2b. if user first move is 5,2 or 5,4 (or anything else): play 4,3 (playColumn = 3)
    #   3a. if user 2nd move is 3,3: play 5,2 or 5,4, whichever is open (playColumn = 2 or 4)
    #       4a. if user 3rd move is a 2iar (4,2/4,4): play to block at 3,2 or 3,4 (playColumn = 2 or 4)
    #       4b. if user 3rd move is a 4,x but not 2iar: play 5,1/5,5 to extend to 3iar (playColumn = 1 or 5)
    #       4c. if user 3rd move is a 5,x but not 2iar: play 4,2/4,4 on same side as opp (playColumn = 2 or 4)
    #
    #   3b. if user 2nd move is 5,x: play 3,3 (playColumn = 3)
    #       4d. if user 3rd move is 2,3: play 4,2/4,4, whichever is on side of 2iar or if none: left/right (playColumn = 2 or 4)
    # 
    # from here on use play algo:
    # move to next item if first not found, etc.
    # 
    # (not all of this has been implemented yet...)
    # 1. ck for ai 3iar to win by 4th
    # 2. ck user 3iar, 2iar, block. If 2iar, favor blocks that create 2/3iar for ai
    # 3. ck ai 2iar to make 3iar (two at a time if possible)(favor moves that block user)
    # 4. ck ai to make 2iar (two at a time if possible)(favor moves that block user)
    # 
    # ?? point system for moves:
    # 100 - to win
    # 50  - to block user 3iar
    # 15  - to make ai 3iar
    # 10  - to block user 2iar
    # 5   - to make ai 2iar
    # +5  - if can also make two at a time
    # +5  - if can also block user 2iar
    # 1   - move close to center


    # bring in game loop move code here for computer?

    global playColumn
    playColumn = 3
    global playCount
    print("playCount = ",playCount)   # debug
    global leftRight
    print("leftRight = ",leftRight)   # debug

    global debugHilite

    numInRow = 0

    # a = random.randint(0,1)

    while run_ai:

        if playCount == 0:
            playColumn = 3  # 5,3
            run_ai = False
        elif playCount == 1:
            if squares2dArray[4,3] == 1:   # (1a) play 2 or 4 ramdomly...
                if leftRight == 0:
                    playColumn = 2  # left
                elif leftRight == 1:
                    playColumn = 4  # right
                run_ai = False
            else:
                playColumn = 3      # (1b) ai takes the center stack
                run_ai = False
        elif playCount == 2:
            if squares2dArray[4,3] == 1 and squares2dArray[3,3] == 1:   # human in stack 2 deep
                if squares2dArray[5,2] == 0:   # (2a)
                    playColumn = 2
                    run_ai = False
                elif squares2dArray[5,4] == 0:  # (2a)
                    playColumn = 4
                    run_ai = False
                run_ai = False
            elif squares2dArray[4,3] == 1 and squares2dArray[3,3] == 0:   # human in stack 1 deep
                if squares2dArray[5,2] == 0:   # (2b)
                    playColumn = 2
                    run_ai = False
                elif squares2dArray[5,4] == 0:  # (2b)
                    playColumn = 4
                    run_ai = False
                elif squares2dArray[5,2] == 1:  # (2b)
                    playColumn = 5
                    run_ai = False
                elif squares2dArray[5,4] == 1:  # (2b)
                    playColumn = 1
                    run_ai = False
            elif squares2dArray[4,3] == -1 and squares2dArray[3,3] == 1:   # human on top in stack (3c)
                if squares2dArray[5,2] == 0:   # (2c)
                    playColumn = 2
                    run_ai = False
                elif squares2dArray[5,4] == 0:  # (2c)
                    playColumn = 4
                    run_ai = False
                run_ai = False
            elif squares2dArray[4,3] == -1 and squares2dArray[3,3] == 0:   # human in stack 1 deep
                playColumn = 3       # (2d) ai takes the center stack
                run_ai = False
        elif playCount == 3:
            if squares2dArray[4,3] == -1 and squares2dArray[3,3] == -1:   # ai in stack 3 deep 5/4/3,3
                if squares2dArray[2,3] == 1:   # (3d)
                    if squares2dArray[5,1] == 1 and squares2dArray[5,2] == 1:   # (3d)
                        playColumn = 2
                        run_ai = False
                    elif squares2dArray[5,4] == 1 and squares2dArray[5,5] == 1:   #  (3d)
                        playColumn = 4
                        run_ai = False
                    elif leftRight == 0:
                        playColumn = 2  # left (3d)
                    elif leftRight == 1:
                        playColumn = 4  # right (3d)
                    run_ai = False
                elif squares2dArray[2,3] == 0:  # (3e)
                    playColumn = 3    # FTW!!
                    run_ai = False
            elif squares2dArray[4,3] == -1 and squares2dArray[3,3] == 1:   # human on top in stack (3a/b/c)
                if squares2dArray[5,2] == 1 and squares2dArray[4,2] == 1:   # human 2iar (3a)
                    playColumn = 2
                    run_ai = False
                elif squares2dArray[5,4] == 1 and squares2dArray[4,4] == 1:   # human 2iar (3a)
                    playColumn = 4
                    run_ai = False
                elif squares2dArray[4,2] == 1 or squares2dArray[4,4] == 1:   # human on top in stack (3b)
                    if squares2dArray[5,2] == -1:  # (3b)
                        playColumn = 1
                        run_ai = False
                    elif squares2dArray[5,4] == -1:  # (3b)
                        playColumn = 5
                        run_ai = False
                elif squares2dArray[5,1] == 1:  # (3c)
                    playColumn = 2
                    run_ai = False
                elif squares2dArray[5,5] == 1:  # (3c)
                    playColumn = 4
                    run_ai = False

    # 1. ck for ai 3iar to win by 4th
    # 2. ck user 3iar, 2iar, block. If 2iar, favor blocks that create 2/3iar for ai
    # 3. ck ai 2iar to make 3iar (two at a time if possible) (favor moves that block user)
    # 4. ck ai to make 2iar (two at a time if possible) (favor moves that block user)
    # code is ordered in increasing priority, top to bottom, last one rules!

    # if debugHilite == 1:

# 2iar:
    # scan board, add up how many 2iar for both ai & human, use in algo
        # check rows
        numInRow = 0
        for i in range(boardRows):
            for j in range(6):
                numInRow = squares2dArray[i,j] + squares2dArray[i,j+1]
                if numInRow == -2:  # ai
                    print("numInRow = ",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[i*boardCols + j+1].hilite = debugHilite
                    if 0 <= (j - 1):
                        print("ai 2iar rows: j-1")  # debug
                        if squares2dArray[i,(j - 1)] == 0:  # open to make 3iar
                            if i == 5:
                                playColumn = j - 1
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j - 1)] != 0:  # support to make 3iar
                                    playColumn = j - 1
                                    run_ai = False
                    if (j + 2) < boardCols:
                        print("ai 2iar rows: j+2")  # debug
                        if squares2dArray[i,(j + 2)] == 0:  # open to make 3iar
                            if i == 5:
                                playColumn = j + 2
                                print("ai rows: playColumn = ",playColumn)  # debug
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j + 2)] != 0:  # support to make 3iar
                                    playColumn = j + 2
                                    print("ai rows: playColumn = ",playColumn)  # debug
                                    run_ai = False
#                    run_ai = False
                elif numInRow == 2:    # human
                    print("numInRow = ",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[i*boardCols + j+1].hilite = debugHilite
                    if 0 <= (j - 1):
                        print("ai 2iar rows: j-1")  # debug
                        if squares2dArray[i,(j - 1)] == 0:  # open to make 3iar
                            if i == 5:
                                playColumn = j - 1
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j - 1)] != 0:  # support to make 3iar
                                    playColumn = j - 1
                                    run_ai = False
                    if (j + 2) < boardCols:
                        print("ai 2iar rows: j+2")  # debug
                        if squares2dArray[i,(j + 2)] == 0:  # open to make 3iar
                            if i == 5:
                                playColumn = j + 2
                                print("ai rows: playColumn = ",playColumn)  # debug
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j + 2)] != 0:  # support to make 3iar
                                    playColumn = j + 2
                                    print("ai rows: playColumn = ",playColumn)  # debug
                                    run_ai = False
#                    run_ai = False
        # check columns
        numInRow = 0
        for i in range(5):
            for j in range(boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j]
                if numInRow == -2:  # ai
                    print("numInRow = ",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j].hilite = debugHilite
                    if 0 <= (i - 1):
                        print("ai 2iar cols: i-1")
                        if squares2dArray[i - 1,j] == 0:  # open to make 3iar
                            playColumn = j
                            print("ai 2iar rows: playColumn = ",playColumn)
                            run_ai = False
                elif numInRow == 2:    # human
                    print("numInRow = ",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j].hilite = debugHilite
                    if 0 <= (i - 1):
                        print("ai 2iar cols: i-1")
                        if squares2dArray[i - 1,j] == 0:  # open to make 3iar
                            playColumn = j
                            print("ai 2iar rows: playColumn = ",playColumn)
                            run_ai = False
#                    run_ai = False
        # check diagonals right
        numInRow = 0
        for i in range(5):
            for j in range(6):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j+1]
                if numInRow == -2:  # ai
                    print("numInRow = ",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j+1].hilite = debugHilite
                    if 0 <= (i - 1):
                        if 0 <= (j - 1):
                            print("ai 2iar diagonals right: j-1")  # debug
                            if squares2dArray[(i - 1),(j - 1)] == 0:  # open to make 3iar
                                if squares2dArray[i,(j - 1)] != 0:  # support to make 3iar
                                    playColumn = j - 1
                                    run_ai = False
                    if (i + 2) < boardRows:
                        if (j + 2) < boardCols:
                            print("ai 2iar diagonals right: j+2")  # debug
                            if squares2dArray[(i + 2),(j + 2)] == 0:  # open to make 3iar
                                if (i + 2) == 5:
                                    playColumn = j + 2
                                    print("ai 2iar 2iar diagonals: playColumn = ",playColumn)  # debug
                                    run_ai = False
                                elif (i + 2) < 5:
                                    if squares2dArray[(i + 3),(j + 2)] != 0:  # support to make 3iar
                                        playColumn = j + 2
                                        print("ai 2iar 2iar diagonals: playColumn = ",playColumn)  # debug
                                        run_ai = False
#                    run_ai = False
                elif numInRow == 2:    # human
                    print("numInRow = ",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j+1].hilite = debugHilite
                    if 0 <= (i - 1):
                        if 0 <= (j - 1):
                            print("ai 2iar diagonals right: j-1")  # debug
                            if squares2dArray[(i - 1),(j - 1)] == 0:  # open to make 3iar
                                if squares2dArray[i,(j - 1)] != 0:  # support to make 3iar
                                    playColumn = j - 1
                                    run_ai = False
                    if (i + 2) < boardRows:
                        if (j + 2) < boardCols:
                            print("ai 2iar diagonals right: j+2")  # debug
                            if squares2dArray[(i + 2),(j + 2)] == 0:  # open to make 3iar
                                if (i + 2) == 5:
                                    playColumn = j + 2
                                    print("ai 2iar diagonals: playColumn = ",playColumn)  # debug
                                    run_ai = False
                                elif (i + 2) < 5:
                                    if squares2dArray[(i + 3),(j + 2)] != 0:  # support to make 3iar
                                        playColumn = j + 2
                                        print("ai 2iar diagonals: playColumn = ",playColumn)  # debug
                                        run_ai = False
#                    run_ai = False
        # check diagonals left
        numInRow = 0
        for i in range(5):
            for j in range(1,boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j-1]
                if numInRow == -2:  # ai
                    print("numInRow = ",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j-1].hilite = debugHilite
                    if 0 <= (i - 1):
                        if (j + 1) < boardCols:
                            print("ai 2iar diagonals left: i-1")  # debug
                            if squares2dArray[(i - 1),(j + 1)] == 0:  # open to make 3iar
                                if squares2dArray[i,(j + 1)] != 0:  # support to make 3iar
                                    playColumn = j + 1
                                    run_ai = False
                    if (i + 2) < boardRows:
                        if 0 <= (j - 2):
                            print("ai 2iar diagonals right: j-2")  # debug
                            if squares2dArray[(i + 2),(j - 2)] == 0:  # open to make 3iar
                                if (i + 2) == 5:
                                    playColumn = j - 2
                                    print("ai 2iar diagonals left: playColumn = ",playColumn)  # debug
                                    run_ai = False
                                elif (i + 2) < 5:
                                    if squares2dArray[(i + 3),(j - 2)] != 0:  # support to make 3iar
                                        playColumn = j - 2
                                        print("ai 2iar diagonals left: playColumn = ",playColumn)  # debug
                                        run_ai = False
#                    run_ai = False
                elif numInRow == 2:    # human
                    danger = 3
                    print("numInRow = ",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j-1].hilite = debugHilite
                    if 0 <= (i - 1):
                        if (j + 1) < boardCols:
                            print("ai 2iar diagonals left: i-1")  # debug
                            if squares2dArray[(i - 1),(j + 1)] == 0:  # open to make 3iar
                                if squares2dArray[i,(j + 1)] != 0:  # support to make 3iar
                                    playColumn = j + 1
                                    run_ai = False
                    if (i + 2) < boardRows:
                        if 0 <= (j - 2):
                            print("ai 2iar diagonals right: j-2")  # debug
                            if squares2dArray[(i + 2),(j - 2)] == 0:  # open to make 3iar
                                if (i + 2) == 5:
                                    playColumn = j - 2
                                    print("ai 2iar diagonals left: playColumn = ",playColumn)  # debug
                                    run_ai = False
                                elif (i + 2) < 5:
                                    if squares2dArray[(i + 3),(j - 2)] != 0:  # support to make 3iar
                                        playColumn = j - 2
                                        print("ai 2iar diagonals left: playColumn = ",playColumn)  # debug
                                        run_ai = False
#                    run_ai = False

# 3iar:
    # scan board, add up how many 3iar for both ai & human, use in algo
        # check rows
        numInRow = 0
        for i in range(boardRows):
            for j in range(5):
                numInRow = squares2dArray[i,j] + squares2dArray[i,j+1] + squares2dArray[i,j+2]
                if numInRow == -3:   # ai
                    print("numInRow = ",numInRow)  # debug
                    # debug: hilite winning discs (remove this later)
                    #squaresArray[i*boardCols + j].hilite = True
                    #squaresArray[i*boardCols + j+1].hilite = True
                    #squaresArray[i*boardCols + j+2].hilite = True
                    if 0 <= (j - 1):
                        print("ai 3iar rows: j-1")  # debug
                        if squares2dArray[i,(j - 1)] == 0:  # open to make 4iar
                            squaresArray[i*boardCols + j].hilite = debugHilite
                            squaresArray[i*boardCols + j+1].hilite = debugHilite
                            squaresArray[i*boardCols + j+2].hilite = debugHilite
                            if i == 5:
                                playColumn = j - 1
                                print("ai 3iar rows: playColumn = ",playColumn)  # debug
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j - 1)] != 0:  # support to make 3iar
                                    playColumn = j - 1
                                    print("ai 3iar rows: playColumn = ",playColumn)  # debug
                                    run_ai = False
                    if (j + 3) < boardCols:
                        print("ai 3iar rows: j+3")  # debug
                        if squares2dArray[i,(j + 3)] == 0:  # open to make 4iar
                            squaresArray[i*boardCols + j].hilite = debugHilite
                            squaresArray[i*boardCols + j+1].hilite = debugHilite
                            squaresArray[i*boardCols + j+2].hilite = debugHilite
                            if i == 5:
                                playColumn = j + 3
                                print("ai 3iar rows: playColumn = ",playColumn)  # debug
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j + 3)] != 0:  # support to make 4iar
                                    playColumn = j + 3
                                    print("ai 3iar rows: playColumn = ",playColumn)  # debug
                                    run_ai = False
                elif numInRow == 3:  # human
                    print("numInRow = ",numInRow)
                    # debug: hilite winning discs (remove this later)
                    #squaresArray[i*boardCols + j].hilite = True
                    #squaresArray[i*boardCols + j+1].hilite = True
                    #squaresArray[i*boardCols + j+2].hilite = True
                    if 0 <= (j - 1):
                        print("ai 3iar rows: j-1")  # debug
                        if squares2dArray[i,(j - 1)] == 0:  # open to block 4iar
                            squaresArray[i*boardCols + j].hilite = debugHilite
                            squaresArray[i*boardCols + j+1].hilite = debugHilite
                            squaresArray[i*boardCols + j+2].hilite = debugHilite
                            if i == 5:
                                playColumn = j - 1
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j - 1)] != 0:  # support to block 4iar
                                    playColumn = j - 1
                                    run_ai = False
                    if (j + 3) < boardCols:
                        print("ai 3iar rows: j+3")
                        if squares2dArray[i,(j + 3)] == 0:  # open to block 4iar
                            squaresArray[i*boardCols + j].hilite = debugHilite
                            squaresArray[i*boardCols + j+1].hilite = debugHilite
                            squaresArray[i*boardCols + j+2].hilite = debugHilite
                            if i == 5:
                                playColumn = j + 3
                                print("ai 3iar colsrows: playColumn = ",playColumn)  # debug
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j + 3)] != 0:  # support to block 4iar
                                    playColumn = j + 3
                                    print("ai 3iar colsrows: playColumn = ",playColumn)  # debug
                                    run_ai = False
#                    run_ai = False
        # check columns
        numInRow = 0
        for i in range(4):
            for j in range(boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j] + squares2dArray[i+2,j]
                if numInRow == -3:  # ai
                    print("numInRow = ",numInRow)  # debug
                    # debug: hilite winning discs (remove this later)
                    #squaresArray[i*boardCols + j].hilite = True
                    #squaresArray[(i+1)*boardCols + j].hilite = True
                    #squaresArray[(i+2)*boardCols + j].hilite = True
                    if 0 <= (i - 1):
                        print("ai 3iar cols: i-1")
                        if squares2dArray[i - 1,j] == 0:  # open to make 4iar
                            squaresArray[i*boardCols + j].hilite = debugHilite
                            squaresArray[(i+1)*boardCols + j].hilite = debugHilite
                            squaresArray[(i+2)*boardCols + j].hilite = debugHilite
                            playColumn = j
                            print("ai 3iar cols: playColumn = ",playColumn)
                            run_ai = False
                elif numInRow == 3:    # human
                    print("numInRow = ",numInRow)  # debug
                    # debug: hilite winning discs (remove this later)
                    #squaresArray[i*boardCols + j].hilite = True
                    #squaresArray[(i+1)*boardCols + j].hilite = True
                    #squaresArray[(i+2)*boardCols + j].hilite = True
                    if 0 <= (i - 1):
                        print("ai 3iar cols: i-1")
                        if squares2dArray[i - 1,j] == 0:  # open to make 4iar
                            squaresArray[i*boardCols + j].hilite = debugHilite
                            squaresArray[(i+1)*boardCols + j].hilite = debugHilite
                            squaresArray[(i+2)*boardCols + j].hilite = debugHilite
                            playColumn = j
                            print("ai 3iar cols: playColumn = ",playColumn)
                            run_ai = False
#                run_ai = False
        # check diagonals right
        numInRow = 0
        for i in range(4):
            for j in range(5):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j+1] + squares2dArray[i+2,j+2]
                if numInRow == -3:  # ai
                    print("numInRow = ",numInRow)  # debug
                    # debug: hilite winning discs (remove this later)
                    #squaresArray[i*boardCols + j].hilite = True
                    #squaresArray[(i+1)*boardCols + j+1].hilite = True
                    #squaresArray[(i+2)*boardCols + j+2].hilite = True
                    if 0 <= (i - 1):
                        if 0 <= (j - 1):
                            print("ai 3iar diagonals right: j-1")  # debug
                            if squares2dArray[(i - 1),(j - 1)] == 0:  # open to make 4iar
                                squaresArray[i*boardCols + j].hilite = debugHilite
                                squaresArray[(i+1)*boardCols + j+1].hilite = debugHilite
                                squaresArray[(i+2)*boardCols + j+2].hilite = debugHilite
                                if squares2dArray[i,(j - 1)] != 0:  # support to make 4iar
                                    playColumn = j - 1
                                    print("ai 3iar diagonals right: playColumn = ",playColumn)  # debug
                                    run_ai = False
                    if (i + 3) < boardRows:
                        if (j + 3) < boardCols:
                            print("ai 3iar diagonals right: j+3")  # debug
                            if squares2dArray[(i + 3),(j + 3)] == 0:  # open to make 4iar
                                squaresArray[i*boardCols + j].hilite = debugHilite
                                squaresArray[(i+1)*boardCols + j+1].hilite = debugHilite
                                squaresArray[(i+2)*boardCols + j+2].hilite = debugHilite
                                if (i + 3) == 5:
                                    playColumn = j + 3
                                    print("ai 3iar diagonals right: playColumn = ",playColumn)  # debug
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j + 3)] != 0:  # support to make 4iar
                                        playColumn = j + 3
                                        print("ai 3iar diagonals right: playColumn = ",playColumn)  # debug
                                        run_ai = False
#                    run_ai = False
                elif numInRow == 3:    # human
                    print("numInRow = ",numInRow)  # debug
                    # debug: hilite winning discs (remove this later)
                    #squaresArray[i*boardCols + j].hilite = True
                    #squaresArray[(i+1)*boardCols + j+1].hilite = True
                    #squaresArray[(i+2)*boardCols + j+2].hilite = True
                    if 0 <= (i - 1):
                        if 0 <= (j - 1):
                            print("ai 3iar diagonals right: j-1")  # debug
                            if squares2dArray[(i - 1),(j - 1)] == 0:  # open to make 4iar
                                squaresArray[i*boardCols + j].hilite = debugHilite
                                squaresArray[(i+1)*boardCols + j+1].hilite = debugHilite
                                squaresArray[(i+2)*boardCols + j+2].hilite = debugHilite
                                if squares2dArray[i,(j - 1)] != 0:  # support to make 4iar
                                    playColumn = j - 1
                                    print("ai 3iar diagonals right: playColumn = ",playColumn)  # debug
                                    run_ai = False
                    if (i + 3) < boardRows:
                        if (j + 3) < boardCols:
                            print("ai 3iar diagonals right: j+3")  # debug
                            if squares2dArray[(i + 3),(j + 3)] == 0:  # open to make 4iar
                                squaresArray[i*boardCols + j].hilite = debugHilite
                                squaresArray[(i+1)*boardCols + j+1].hilite = debugHilite
                                squaresArray[(i+2)*boardCols + j+2].hilite = debugHilite
                                if (i + 3) == 5:
                                    playColumn = j + 3
                                    print("ai 3iar diagonals right: playColumn = ",playColumn)  # debug
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j + 3)] != 0:  # support to make 4iar
                                        playColumn = j + 3
                                        print("ai 3iar diagonals right: playColumn = ",playColumn)  # debug
                                        run_ai = False
#                    run_ai = False
        # check diagonals left
        numInRow = 0
        for i in range(4):
            for j in range(2,boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j-1] + squares2dArray[i+2,j-2]
                if numInRow == -3:  # ai
                    print("numInRow = ",numInRow)  # debug
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j-1].hilite = debugHilite
                    squaresArray[(i+2)*boardCols + j-2].hilite = debugHilite
                    if 0 <= (i - 1):
                        if (j + 1) < boardCols:
                            print("ai 3iar diagonals left: i-1")  # debug
                            if squares2dArray[(i - 1),(j + 1)] == 0:  # open to make 4iar
                                if squares2dArray[i,(j + 1)] != 0:  # support to make 4iar
                                    playColumn = j + 1
                                    print("ai 3iar diagonals left: playColumn = ",playColumn)  # debug
                                    run_ai = False
                    if (i + 3) < boardRows:
                        if 0 <= (j - 3):
                            print("ai 3iar diagonals left: j-3")  # debug
                            if squares2dArray[(i + 3),(j - 3)] == 0:  # open to make 4iar
                                if (i + 3) == 5:
                                    playColumn = j - 3
                                    print("ai 3iar diagonals left: playColumn = ",playColumn)  # debug
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j - 3)] != 0:  # support to make 4iar
                                        playColumn = j - 3
                                        print("ai 3iar diagonals left: playColumn = ",playColumn)  # debug
                                        run_ai = False
#                    run_ai = False
                elif numInRow == 3:    # human
                    print("numInRow = ",numInRow)  # debug
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j-1].hilite = debugHilite
                    squaresArray[(i+2)*boardCols + j-2].hilite = debugHilite
                    if 0 <= (i - 1):
                        if (j + 1) < boardCols:
                            print("ai 3iar diagonals left: i-1")  # debug
                            if squares2dArray[(i - 1),(j + 1)] == 0:  # open to make 4iar
                                if squares2dArray[i,(j + 1)] != 0:  # support to make 4iar
                                    playColumn = j + 1
                                    print("ai 3iar diagonals left: playColumn = ",playColumn)  # debug
                                    run_ai = False
                    if (i + 3) < boardRows:
                        if 0 <= (j - 3):
                            print("ai 3iar diagonals left: j-3")  # debug
                            if squares2dArray[(i + 3),(j - 3)] == 0:  # open to make 4iar
                                if (i + 3) == 5:
                                    playColumn = j - 3
                                    print("ai 3iar diagonals left: playColumn = ",playColumn)  # debug
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j - 3)] != 0:  # support to make 4iar
                                        playColumn = j - 3
                                        print("ai 3iar diagonals left: playColumn = ",playColumn)  # debug
                                        run_ai = False
#                    run_ai = False

#    # check for full columns here...
#    # then what?
#        # temporary...
#        print("ai check for full columns...")  # debug
#        print("playColumn = ",playColumn)   # debug
#        print(squares2dArray)
#        if squares2dArray[0,playColumn] != 0:  # column is full
#            if leftRight == 0:  # left
##            if playColumn == 0:
#                for i in range(boardCols):
#                    if squares2dArray[0,i] == 0:  # column is empty
#                        playColumn = i
#                        run_ai = False
#                    else:
##                        winner = 2   # draw
#                        run_ai = False
#                        winnerCheck()
#            elif leftRight == 1:  # right
##            elif playColumn == 6:
#                for i in range(boardCols-1,-1):
#                    if squares2dArray[0,i] == 0:  # column is empty
#                        playColumn = i
#                        run_ai = False
#                    else:
#                        winner = 2   # draw
#                        run_ai = False
#                        winnerCheck()
#
##            if leftRight == 0:  # left
##                if squares2dArray[0,playColumn - 1] == 0:  # column is empty
##                    playColumn = playColumn - 1
##                elif squares2dArray[0,playColumn + 1] == 0:  # column is empty
##                    playColumn = playColumn + 1
##            elif leftRight == 1:  # right
##                if squares2dArray[0,playColumn + 1] == 0:  # column is empty
##                    playColumn = playColumn + 1
##                elif squares2dArray[0,playColumn - 1] == 0:  # column is empty
##                    playColumn = playColumn - 1

        redrawWindow()
        print("ai exit: playColumn = ",playColumn)   # debug
        run_ai = False

#def computer_ai(): end


def fullColunnCheck():

    global playColumn

    # check for full columns here...
    # then what?
    # temporary...
    print("ai check for full columns...")  # debug
    print("playColumn = ",playColumn)   # debug
    print(squares2dArray)
    if squares2dArray[0,playColumn] != 0:  # column is full
        if leftRight == 0:  # left
            for i in range(boardCols):
                if 0 <= (playColumn - i):
                    if squares2dArray[0,playColumn - i] == 0:  # column is empty
                        playColumn = playColumn - i
                elif (playColumn + i) < boardCols:
                    if squares2dArray[0,playColumn + i] == 0:  # column is empty
                        playColumn = playColumn + i
        elif leftRight == 1:  # right
            for i in range(boardCols):
                if (playColumn + i) < boardCols:
                    if squares2dArray[0,playColumn + i] == 0:  # column is empty
                        playColumn = playColumn + i
                elif 0 <= (playColumn - i):
                    if squares2dArray[0,playColumn - i] == 0:  # column is empty
                        playColumn = playColumn - i


#        if leftRight == 0:  # left
##        if playColumn == 0:
#            for i in range(boardCols):
#                if squares2dArray[0,i] == 0:  # column is empty
#                    playColumn = i
##                    run_ai = False
#                else:
##                    winner = 2   # draw
##                    run_ai = False
#                    winnerCheck()
#        elif leftRight == 1:  # right
##        elif playColumn == 6:
#            for i in range(boardCols-1,-1):
#                if squares2dArray[0,i] == 0:  # column is empty
#                    playColumn = i
##                    run_ai = False
#                else:
##                    winner = 2   # draw
##                    run_ai = False
#                    winnerCheck()

#            if leftRight == 0:  # left
#                if squares2dArray[0,playColumn - 1] == 0:  # column is empty
#                    playColumn = playColumn - 1
#                elif squares2dArray[0,playColumn + 1] == 0:  # column is empty
#                    playColumn = playColumn + 1
#            elif leftRight == 1:  # right
#                if squares2dArray[0,playColumn + 1] == 0:  # column is empty
#                    playColumn = playColumn + 1
#                elif squares2dArray[0,playColumn - 1] == 0:  # column is empty
#                    playColumn = playColumn - 1

#        redrawWindow()
    print("fullColunnCheck exit: playColumn = ",playColumn)   # debug


def game_loop():

    print("")
    print("game_loop = while run_game")
    print("")
    pygame.event.clear()

    redrawWindow()

    global numPlayers
    global turnPlayer
#    turnPlayer = 1  # 1 or 2. Computer is player 1 if single player mode
    global winner
#    winner = 0      # 1 or 2, winning player
    global playColumn
#    playColumn = 3
    global playCount
#    playCount = 0   # a play is one round, i.e. computer and human each taking a turn

    # debug:
    #turnPlayer = 2
    print("numPlayers = ",numPlayers)
    print("turnPlayer = ",turnPlayer)
    print("winner = ",winner)

    run_game = True

    while run_game:

        #redrawWindow()
        #print("while run_game =",run_game)   # debug
        #print("turnPlayer = ",turnPlayer)   # debug
        #clock.tick(5)   # debug
        clock.tick(30)

    # is it computer's turn?
        if numPlayers == 1 and turnPlayer == 1:
            textmsg = "Computer's Turn"
            font = pygame.font.SysFont('comicsansms', 40)  # comicsansms arial
            text = font.render(textmsg,1,colorPlayer1)   # red  brightgreen  blue  lightblue
            screen.blit(text, ((display_width/2)-155,40))
            pygame.display.update()
            pygame.time.wait(1200)
            computer_ai()
            fullColunnCheck()
        # change to support color choice:
            #colorPlayer1
            squaresArray[playColumn].disc = colorPlayer1
            print("squaresArray",playColumn,".disc =",colorPlayer1)   # debug
            redrawWindow()
            dropDisc(playColumn,squaresArray[playColumn].disc)
            # check for victory here...
            winnerCheck()
            redrawWindow()
            if winner != 0:
                run_game = False
                endgame()    # declare winner & play again?
            # switch players if no winner:
            turnPlayer = 2

    # is it human's turn?
        if turnPlayer == 2 or numPlayers == 2:
            if turnPlayer == 1:
                textmsg = "Player #1's Turn"
                text = font.render(textmsg,1,colorPlayer1)
            elif turnPlayer == 2:
                textmsg = "Player #2's Turn"
                text = font.render(textmsg,1,colorPlayer2)
            font = pygame.font.SysFont('comicsansms', 40)  # comicsansms arial
            #font = pygame.font.SysFont('arial', 40)  # comicsansms arial
            screen.blit(text, ((display_width/2)-160,40))

            #text = font.render(textmsg,1,white)
            #screen.blit(text, ((display_width)-400,40))
            pygame.display.update()
 
            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    run_game = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    for i in range (7):
                        squaresArray[i].hilite = False
                        if squaresArray[i].isOver(pos):
                            squaresArray[i].hilite = True
 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range (7):
                        if squaresArray[i].isOver(pos):
                            playColumn = i
                            print("playColumn = ",playColumn)   # debug
                            #print(squares2dArray)   # debug
                        # error checking here....
                            if squares2dArray[0,playColumn] != 0:
                            #if squaresArray[i].disc != black:    #'black': fails, don't use colors as a string
                                print("game_loop")   # debug
                                print("turnPlayer =",turnPlayer)   # debug
                                print(squares2dArray)   # debug
                                honk3Sound.play()
                                print("squaresArray",i,".disc =",squaresArray[i].disc)   # debug
                            elif squaresArray[i].disc == black:
                                if turnPlayer == 1:
                                    squaresArray[i].disc = colorPlayer1
                                    print("squaresArray",i,".disc =",colorPlayer1)   # debug
                                elif turnPlayer == 2:
                                    squaresArray[i].disc = colorPlayer2
                                    print("squaresArray",i,".disc =",colorPlayer2)   # debug
                                redrawWindow()
                                #update2dArray()
                                print("game_loop")   # debug
                                print("turnPlayer =",turnPlayer)   # debug
                                print(squares2dArray)   # debug
                                playCount = playCount + 1
                                squaresArray[i].hilite = False   # experimental
                                dropDisc(playColumn,squaresArray[i].disc)
                            # check for victory here...
                                winnerCheck()
                                redrawWindow()
                                if winner != 0:
                                    # declare winner & play again?
                                    run_game = False
                                    endgame()
                                # switch players if no winner:
                                elif winner == 0:
                                    if turnPlayer == 1:
                                        turnPlayer = 2
                                    else:
                                        turnPlayer = 1

#def game_loop(): end


game_setup()
game_loop()  # called from game_setup, do I need this?

pygame.quit()
#quit()
sys.exit()

