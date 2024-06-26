#===================================================
# Connect-4 (aka The Captain's Mistress)
# The Captain's Mistress is supposedly the game
# that so engrossed Captain Cook during his long
# voyages that his crew gave it that name
#===================================================
# 4/24/24, 11:00 PM

# The Rules of Connect 4:
# Players must connect 4 of the same colored discs in a row to win.
# Only one piece is played at a time.
# The game ends when there is a 4-in-a-row or a stalemate.
# Players take turns going first.

'''
Bug Tracker for Connect-4


4/22/24:
---> Need to check for 2iar with support for third, block if possible.

I won again, ai didn't see my 2iar to 3iar setup for a win on the diagonal.
---> block 2iar if possible, no other good moves. ai moved to col 3, for no reason.


7/27/23:
not taking a winning move, blocking me instead!!!
missed 4iar horiz with gap
##RH reorder, put ai last? or how to prioritize game winning move?
##RH set i = 5, j = 3, then run_ai = false?


4/24/23:
missed 4iar via diagonal with gap
missed 4iar via horizontal with gap

out of range error lines: 1031


(fixed?)
out of range error lines:
2246
692
2233
2091
2168


to do:

add highlight around buttons for color selection (or color change)

does run_ai = False exit the while loop as expected? or does it fall all the way through first?

_add gap check to make 3iar!!


add selection for beginner or advanced mode

AI for single player mode (in process)
    _add 2iar strategy code
    look for gaps? XX.X
    fix bad moves that give away the game!!
        setting up a 4iar by human
    eventually convert to score based moves?


_add click sound for mouse clicks
_don't ask again for instructions, #players, colors, etc., on replay

_alternate player that goes first (done)
_fix taking turns at the start of a new game (done, damn globals!)
_keep stats on # wins per player

_check disk drop speed... done, added delays

_fix full board draw checking
_fix ai drops into full column
_? fix ai moves when no 3iar or 4iar ?

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

avoidColumns = [0,0,0,0,0,0,0]
playColumns  = [0,0,0,0,0,0,0]

squareSize = 150
squareBorder = 5
# use if no border desired:
#squareSize = 155
#squareBorder = 0
circleRadius = 50

boardStartX = 420
boardStartY = 130

### game play variables ###
easyMode     = 0  # 1 for easy mode, 0 for normal (tougher) mode
numPlayers   = 2  # 1 for human vs. computer, 2 for human vs. human
whoGoesFirst = 1  # 1 (computer or player #1) or -1 (human or player #2). Alternates for now (per the rules), but should loser always go first? optional?
turnPlayer   = 1  # 1 or 2. Computer is player 1 if single player mode
winner       = 0  # 1 or 2, winning player
playCount    = 0  # a play is one round, i.e. computer and human each taking a turn
playColumn   = 3  # ai always picks this on first move
leftRight    = 0  # for random ai movement

# can be changed at game start:
colorPlayer1 = red
colorPlayer2 = yellow

# stats: num victories by each player/computer
winsPlayer1 = 0
winsPlayer2 = 0

# To play a sound: bulletSound.play()
dropSound = pygame.mixer.Sound('./sounds/sfx_sounds_impact6.wav')
honk3Sound = pygame.mixer.Sound('./sounds/honk3.wav')
click = pygame.mixer.Sound('./sounds/click.ogg')
alarmBellSound = pygame.mixer.Sound('./sounds/alarm-bell.wav')  # computer wins
shipsBellSound = pygame.mixer.Sound('./sounds/ships_bell.wav')
twoBellsSound = pygame.mixer.Sound('./sounds/ship-bell-two-chimes.wav')  # human wins

# music #
pygame.mixer.init()
pygame.mixer.music.set_volume(0.05)  # 0.03-0.05
music = pygame.mixer.music.load("sounds/sea_waves_13sec.wav")
pygame.mixer.music.play(-1) # -1 will ensure the song keeps looping

# debug:
debugHilite = False


#------------------------------------------------------
# Functions:

def drawRect(rect_x, rect_y, rect_w, rect_h, color):
    pygame.draw.rect(screen, color, [rect_x, rect_y, rect_w, rect_h])

def drawCirle(x, y, radius, color, width=0):   # x,y is center. If width > 1, is line thickness, else filled. 
    pygame.draw.circle(screen, color, (x, y), radius, width)   # circle(surface, color, center, radius) 


#------------------------------------------------------
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


#------------------------------------------------------
# create array for boardSquare class instances
squaresArray = []

def initSquaresArray():

    print("initSquaresArray")    # initialize array of class boardSquare
    for i in range(boardRows):
        for j in range(boardCols):
            squaresArray.append(boardSquare((boardStartX + squareSize*j + squareBorder*j), (boardStartY + squareSize*i + squareBorder*i), black, False))
            #debug:
            #print(i,j,(boardStartX + squareSize*j + squareBorder*j), (boardStartY + squareSize*i + squareBorder*i))
    # debug:
    ## this works best!
    #print("")
    #print("print squaresArray i,j direct")
    #print("  x,  y, disc, hilite")
    #for i in range(boardRows):
    #    for j in range(boardCols):
    #        print(squaresArray[i*boardCols + j].x,squaresArray[i*boardCols + j].y,squaresArray[i*boardCols+j].disc, squaresArray[i*boardCols+j].hilite)


#------------------------------------------------------
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

#------------------------------------------------------
def clearSquaresHilite():

    print("clearSquaresArray")
    for i in range(boardRows):
        for j in range(boardCols):
            squaresArray[i*boardCols + j].hilite = False


#------------------------------------------------------
squares2dArray = np.zeros((6,7), dtype=int)    # create 2D array for board squares

def update2dArray():
    #print("")
    #print(squares2dArray)  # before update

    for i in range(boardRows):
        for j in range(boardCols):
            #arr = np.append(arr, 7)
            #squaresArray = np.append(squaresArray, boardSquare((boardStartX + squareSize*j + squareBorder*j), (boardStartY + squareSize*i + squareBorder*i)))
            if squaresArray[i*boardCols + j].disc == black:
                squares2dArray[i,j] = 0
            elif squaresArray[i*boardCols + j].disc == colorPlayer1:  # colorPlayer1 red
                squares2dArray[i,j] = -1
            elif squaresArray[i*boardCols + j].disc == colorPlayer2:  # colorPlayer2 yellow
                squares2dArray[i,j] = 1
            #debug:
            #print(i,j,(boardStartX + squareSize*j + squareBorder*j), (boardStartY + squareSize*i + squareBorder*i))
    # debug:
    print("update2dArray()")
    print(squares2dArray)   # after update


#------------------------------------------------------
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
    #screen.blit(text, (30,150))
    #print("winsPlayer1 =",winsPlayer1)
    textmsg = str(winsPlayer1)
    text = font.render(textmsg,1,colorPlayer1)
    screen.blit(text, (1820,40))
    #screen.blit(text, (50,150))

    textmsg = "Player #2 Score:"
    text = font.render(textmsg,1,colorPlayer2)
    screen.blit(text, (1560,80))
    #screen.blit(text, (30,200))
    #print("winsPlayer2 =",winsPlayer2)
    textmsg = str(winsPlayer2)
    text = font.render(textmsg,1,colorPlayer2)
    screen.blit(text, (1820,80))
    #screen.blit(text, (50,200))

    #update2dArray()
    pygame.display.update()



#------------------------------------------------------
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

#------------------------------------------------------
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


#------------------------------------------------------
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
,"The computer always starts the first game. Players take turns going first afterwards."
,""
,"Position the mouse at the top square of the column you want to choose"
,"and then click to drop a piece down it."]


def displayInstructions():

    yesButton = Button((255,255,0), 740,804,40,40,'Y')

    pygame.event.clear()  # This will clear any pending events (keys held down or released) from the previous run
    run_di = True

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
                click.play()
                if yesButton.isOver(pos):
                    print("instructions Done")
                    #instructionsDone = 1
                    run_di = False
    
            if event.type == pygame.MOUSEMOTION:
                if yesButton.isOver(pos):
                    yesButton.color = (0,255,0)
                else:
                    yesButton.color = (255,255,0)


#------------------------------------------------------
def game_setup():

    # add selection for beginner or advanced mode

    print("")
    print("** Welcome to Connect-4 (aka The Captain's Mistress) **")
    print("")
    print("game_setup")

    # reset game variables:
    global easyMode
    global numPlayers
    global whoGoesFirst
    global turnPlayer
    global winner
    global playCount

    global colorPlayer1
    global colorPlayer2
    colorPlayer1 = red
    colorPlayer2 = yellow

    instructionsDone = 0
    winner = 0      # 1 or 2, winning player
    playCount = 0   # a play is one round, i.e., computer and human each taking a turn

    #  since replay added, do I need to do this?
    numPlayersDone = 0
    discColorDone = 0

    # RH is this correct here? since replay added, do I need to do this?
    #numPlayers = 2  # 1 for human vs. computer, 2 for human vs. human
    #if whoGoesFirst == 1:
    #    turnPlayer = 1  # Computer is player 1 if single player mode
    #elif whoGoesFirst == -1:
    #    turnPlayer = 2  # human

    turnPlayer   = 1    # Computer is player 1 if single player mode
    whoGoesFirst = 1    # The computer always starts the first game

    print("game_setup: turnPlayer =",turnPlayer)  # debug

    # ai left/right coin toss:
    global leftRight
    leftRight = random.randint(0,1)
    print("game_setup: leftRight =",leftRight)  # debug

    initSquaresArray()
    update2dArray()
    redrawWindow()
    #pygame.display.update()

    yesButton = Button((255,255,0), 1180,50,40,40,'Y')
    noButton  = Button((255,255,0), 1250,50,40,40,'N')
    redButton = Button((255,0,0),   1180,50,40,40,'R')
    yelButton = Button((255,255,0), 1250,50,40,40,'Y')

    pygame.event.clear()
    run_setup = True

    while run_setup:

        clock.tick(30)

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

                pos = pygame.mouse.get_pos()    # needed?
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click.play()
                    if yesButton.isOver(pos):
                        print("displayInstructions = yes")
                        displayInstructions()
                    elif noButton.isOver(pos):    # if
                        print("displayInstructions = no")
                    yesButton.color = (255,255,0)
                    noButton.color = (255,255,0)
                    instructionsDone = 1
                    redrawWindow()

                if event.type == pygame.MOUSEMOTION:
                    if yesButton.isOver(pos):
                        yesButton.color = (0,255,0)
                    else:
                        yesButton.color = (255,255,0)
                    if noButton.isOver(pos):
                        noButton.color = (0,255,0)
                    else:
                        noButton.color = (255,255,0)

        # "Is this a two player game?"
        elif numPlayersDone == 0:
            textmsg = "Is this a two player game?"
            font = pygame.font.SysFont('comicsansms', 40)  # comicsansms arial
            #font = pygame.font.SysFont('arial', 30)
            text = font.render(textmsg,1,white)
            screen.blit(text, ((display_width/2)-320,40))
            yesButton.draw(screen,(0,0,0))  #surface, outline
            noButton.draw(screen,(0,0,0))  #surface, outline
            pygame.display.update()
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_setup = False
                    pygame.quit()
                    sys.exit()

                #if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_y]:  # supports upper & lower case
                    numPlayers = 2
                    numPlayersDone = 1
                    print("numPlayers =",numPlayers)
                    redrawWindow()
                if keys[pygame.K_n]:  # supports upper & lower case
                    numPlayers = 1
                    numPlayersDone = 1
                    print("numPlayers =",numPlayers)
                    redrawWindow()

                pos = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click.play()
                    if yesButton.isOver(pos):
                        numPlayers = 2
                        numPlayersDone = 1
                        print("numPlayers =",numPlayers)
                        redrawWindow()
                    #run_setup = False
                    if noButton.isOver(pos):
                        numPlayers = 1
                        numPlayersDone = 1
                        print("numPlayers =",numPlayers)
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
                    pygame.display.update()

        # "What color disc do you want?"
        elif discColorDone == 0:
            textmsg = "What color discs, Player 2?"
            font = pygame.font.SysFont('comicsansms', 40)  # comicsansms arial
            #font = pygame.font.SysFont('arial', 30)
            text = font.render(textmsg,1,white)
            screen.blit(text, ((display_width/2)-350,40))
            #redButton = Button((255,0,0), 1180,50,40,40,'R')
            #yelButton = Button((255,255,0), 1250,50,40,40,'Y')

            ##RH do these conflict with each other? (above and below)

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
                    click.play()
                    pygame.time.delay(500)
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

                ##RH not working....   ?
                if event.type == pygame.MOUSEMOTION:
                    if redButton.isOver(pos):
                        redButton.color = (0,255,0)  ##RH not working....   ? (was 255, 0, 0)
                    else:
                        redButton.color = red
                    if yelButton.isOver(pos):
                        yelButton.color = (0,255,0)  ##RH not working....   ? (was 255, 255, 0)
                    else:
                        yelButton.color = yellow
                    pygame.display.update()

    print("game_setup exit: turnPlayer =",turnPlayer)   # debug
    #redrawWindow()   # done in game_loop
    game_loop()   # experimental... but it seems to work! why needed?

#def game_setup(): end


#------------------------------------------------------
def computer_ai():

    print("computer_ai")

    # code is ordered in increasing priority, top to bottom, last one rules! (still true? bad idea?)

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

    global easyMode
    global debugHilite
    global playCount
    global leftRight
    global playColumn
    global avoidColumns
    global playColumns

    playColumn = 3
    numInRow = 0
    avoidColumns = [0,0,0,0,0,0,0]   # init array
    playColumns  = [0,0,0,0,0,0,0]   # init array

    print("playCount =",playCount)   # debug
    print("leftRight =",leftRight)   # debug
    print("playColumn =",playColumn)  
    print("playColumns  =",playColumns)  
    print("avoidColumns =",avoidColumns)

    pygame.event.clear()
    run_ai = True

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
                run_ai = False    # needed?
            else:
                playColumn = 3      # (1b) ai takes the center stack
                run_ai = False    # needed?
            run_ai = False
        elif playCount == 2:
            if squares2dArray[4,3] == 1 and squares2dArray[3,3] == 1:   # human in stack 2 deep
                if squares2dArray[5,2] == 0:   # (2a)
                    playColumn = 2
                    run_ai = False    # needed?
                elif squares2dArray[5,4] == 0:  # (2a)
                    playColumn = 4
                    run_ai = False    # needed?
                run_ai = False
            elif squares2dArray[4,3] == 1 and squares2dArray[3,3] == 0:   # human in stack 1 deep
                if squares2dArray[5,2] == 0:   # (2b)
                    playColumn = 2
                    run_ai = False    # needed?
                elif squares2dArray[5,4] == 0:  # (2b)
                    playColumn = 4
                    run_ai = False    # needed?
                elif squares2dArray[5,2] == 1:  # (2b)
                    playColumn = 5
                    run_ai = False    # needed?
                elif squares2dArray[5,4] == 1:  # (2b)
                    playColumn = 1
                    run_ai = False    # needed?
                run_ai = False
            elif squares2dArray[4,3] == -1 and squares2dArray[3,3] == 1:   # human on top in stack (3c)
                if squares2dArray[5,2] == 0:   # (2c)
                    playColumn = 2
                    run_ai = False    # needed?
                elif squares2dArray[5,4] == 0:  # (2c)
                    playColumn = 4
                    run_ai = False    # needed?
                run_ai = False
            elif squares2dArray[4,3] == -1 and squares2dArray[3,3] == 0:   # ai in stack 1 deep
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
            elif squares2dArray[5,1] == 0:   # (2b)
                playColumn = 1
                run_ai = False    # needed?
            elif squares2dArray[5,5] == 0:  # (2b)
                playColumn = 5
                run_ai = False    # needed?
            run_ai = False

        # debug
        if playCount <= 3:
            print("# early moves, playCount =",playCount)  
            print("playColumn =",playColumn)  


        #------------------------------------------------------
        # if playCount > 3:

        # 1. ck for ai 3iar to win by 4th
        # 2. ck user 3iar, 2iar, block. If 2iar, favor blocks that create 2/3iar for ai
       ## 2a. ck for 'gap' moves in between 2 or more discs to make 3iar or 4iar
        # 3. ck ai 2iar to make 3iar (two at a time if possible) (favor moves that block user)
        # 4. ck ai to make 2iar (two at a time if possible) (favor moves that block user)
        # code is ordered in increasing priority, top to bottom, last one rules!
    
        # if debugHilite == 1:
        #boardRows = 6
        #boardCols = 7
        # if easyMode == 0:    # skip if easyMode turned on (1)
        '''
        print("")
        print("## gap check 3/4:")
        # scan board, add up how many 3/4 gap plays there are for both ai & human, use in algo
        # check rows
        numInRow = 0
        for i in range(boardRows):
            for j in range(4):    # stops after col 3
                numInRow = squares2dArray[i,j] + squares2dArray[i,j+1] + squares2dArray[i,j+2] + squares2dArray[i,j+3]
                ##RH reorder, put ai last? or how to prioritize game winning move?
                ##RH set i = 5, j = 3, then run_ai = false?
                # ai
                if numInRow == -3:   # ai
                    print("numInRow =",numInRow)
                    for k in range(4):
                        if squares2dArray[i,j + k] == 0:
                            if i == 5:
                                playColumn = j + k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                            elif squares2dArray[(i + 1),(j + k)] != 0:    # support to make 4iar
                                playColumn = j + k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                # human
                elif numInRow == 3:    # human
                    print("numInRow =",numInRow)
                    for k in range(4):
                        if squares2dArray[i,j + k] == 0:
                            if i == 5:
                                playColumn = j + k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                            elif squares2dArray[(i + 1),(j + k)] != 0:    # support to fill gap (block it)
                                playColumn = j + k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                            elif squares2dArray[(i + 1),(j + k)] == 0:    # avoid col?
                                if i <= 3:
                                    if squares2dArray[(i + 2),(j + k)] != 0:    # avoid col
                                        avoidColumns[j + k] = 1

        # check diagonals right, starting from top left corner
        numInRow = 0
        for i in range(3):
            for j in range(4):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j+1] + squares2dArray[i+2,j+2] + squares2dArray[i+3,j+3]    # add num in diagonal
                ##RH reorder, put ai last? or how to prioritize game winning move?
                ##RH set i = 5, j = 3, then run_ai = false?
                # ai
                if numInRow == -3:  # ai
                    print("numInRow =",numInRow) 
                    for k in range(4):
                        if squares2dArray[i + k,j + k] == 0:
                            if (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j + k)] != 0:    # support to make 4iar
                                playColumn = j + k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k) == 5:    # support to make 4iar
                                playColumn = j + k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                # human
                elif numInRow == 3:    # human
                    print("numInRow =",numInRow) 
                    for k in range(4):
                        if squares2dArray[i + k,j + k] == 0:
                            if (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j + k)] != 0:    # support to fill gap (block it)
                                playColumn = j + k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k) == 5:    # support to make 4iar
                                playColumn = j + k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j + k)] == 0:    # avoid col
                                avoidColumns[j + k] = 1

        # check diagonals left, starting from left side
        numInRow = 0
        for i in range(3):
            for j in range(3,boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j-1] + squares2dArray[i+2,j-2] + squares2dArray[i+3,j-3]    # add num in diagonal
                ##RH reorder, put ai last? or how to prioritize game winning move?
                ##RH set i = 5, j = 3, then run_ai = false?
                # ai
                if numInRow == -3:  # ai
                    print("numInRow =",numInRow) 
                    for k in range(4):
                        if squares2dArray[i + k,j - k] == 0:
                            if (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j - k)] != 0:    # support to make 4iar
                                playColumn = j - k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k) == 5:    # support to make 4iar
                                playColumn = j + k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                # human
                elif numInRow == 3:    # human
                    print("numInRow =",numInRow) 
                    for k in range(4):
                        if squares2dArray[i + k,j - k] == 0:
                            if (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j - k)] != 0:    # support to fill gap (block it)
                                playColumn = j - k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k) == 5:    # support to make 4iar
                                playColumn = j + k
                                print("ai 3/4 gap: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j - k)] == 0:    # avoid col
                                avoidColumns[j - k] = 1
        '''

        '''
        #------------------------------------------------------
        # if easyMode == 0:    # skip if easyMode turned on (1)

        print("")
        print("## check 3iar:")
        # scan board, add up how many 3iar for both ai & human, use in algo
        # check rows
        numInRow = 0
        for i in range(boardRows):
            for j in range(5):
                numInRow = squares2dArray[i,j] + squares2dArray[i,j+1] + squares2dArray[i,j+2]
                ##RH reorder, put ai last? or how to prioritize game winning move?
                ##RH set i = 5, j = 3, then run_ai = false?
                # ai
                if numInRow == -3:   # ai
                    print("numInRow =",numInRow)
                    if 0 <= (j - 1):
                        print("ai 3iar rows: j-1")
                        if squares2dArray[i,(j - 1)] == 0:  # open to make 4iar
                            if i == 5:
                                playColumn = j - 1
                                print("ai 3iar rows: playColumn =",playColumn)
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j - 1)] != 0:  # support to make 3iar
                                    playColumn = j - 1
                                    print("ai 3iar rows: playColumn =",playColumn)
                                    run_ai = False
                    if (j + 3) < boardCols:
                        print("ai 3iar rows: j+3")
                        if squares2dArray[i,(j + 3)] == 0:  # open to make 4iar
                            if i == 5:
                                playColumn = j + 3
                                print("ai 3iar rows: playColumn =",playColumn) 
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j + 3)] != 0:  # support to make 4iar
                                    playColumn = j + 3
                                    print("ai 3iar rows: playColumn =",playColumn) 
                                    run_ai = False
                # human
                elif numInRow == 3:  # human
                    print("numInRow =",numInRow)
                    if 0 <= (j - 1):
                        print("ai 3iar rows: j-1") 
                        if squares2dArray[i,(j - 1)] == 0:  # open to block 4iar
                            if i == 5:
                                playColumn = j - 1
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j - 1)] != 0:  # support to block 4iar
                                    playColumn = j - 1
                                    run_ai = False
                                elif squares2dArray[(i + 1),(j - 1)] == 0:  # avoid col
                                    avoidColumns[j - 1] = 1
                    if (j + 3) < boardCols:
                        print("ai 3iar rows: j+3")
                        if squares2dArray[i,(j + 3)] == 0:  # open to block 4iar
                            if i == 5:
                                playColumn = j + 3
                                print("ai 3iar colsrows: playColumn =",playColumn) 
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j + 3)] != 0:  # support to block 4iar
                                    playColumn = j + 3
                                    print("ai 3iar colsrows: playColumn =",playColumn) 
                                    run_ai = False
                                elif squares2dArray[(i + 1),(j + 3)] == 0:    # avoid col
                                    avoidColumns[j + 3] = 1
        # check columns
        numInRow = 0
        for i in range(4):
            for j in range(boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j] + squares2dArray[i+2,j]
                ##RH reorder, put ai last? or how to prioritize game winning move?
                ##RH set i = 5, j = 3, then run_ai = false?
                if numInRow == -3:  # ai
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        print("ai 3iar cols: i-1")
                        if squares2dArray[i - 1,j] == 0:  # open to make 4iar
                            playColumn = j
                            print("ai 3iar cols: playColumn =",playColumn)
                            run_ai = False
                elif numInRow == 3:    # human
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        print("ai 3iar cols: i-1")
                        if squares2dArray[i - 1,j] == 0:  # open to make 4iar
                            playColumn = j
                            print("ai 3iar cols: playColumn =",playColumn)
                            run_ai = False

        # check diagonals right, starting from top left corner
        numInRow = 0
        for i in range(4):
            for j in range(5):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j+1] + squares2dArray[i+2,j+2]    # add num in diagonal
                ##RH reorder, put ai last? or how to prioritize game winning move?
                ##RH set i = 5, j = 3, then run_ai = false?
                # ai
                if numInRow == -3:
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        if 0 <= (j - 1):
                            print("ai 3iar diagonals right: j-1") 
                            if squares2dArray[(i - 1),(j - 1)] == 0:  # open to make 4iar
                                if squares2dArray[i,(j - 1)] != 0:  # support to make 4iar
                                    playColumn = j - 1
                                    print("ai 3iar diagonals right: playColumn =",playColumn) 
                                    run_ai = False
                    if (i + 3) < boardRows:
                        if (j + 3) < boardCols:
                            print("ai 3iar diagonals right: j+3") 
                            if squares2dArray[(i + 3),(j + 3)] == 0:  # open to make 4iar
                                if (i + 3) == 5:
                                    playColumn = j + 3
                                    print("ai 3iar diagonals right: playColumn =",playColumn) 
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j + 3)] != 0:  # support to make 4iar
                                        playColumn = j + 3
                                        print("ai 3iar diagonals right: playColumn =",playColumn) 
                                        run_ai = False
                # human
                elif numInRow == 3:
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        if 0 <= (j - 1):
                            print("ai 3iar diagonals right: j-1") 
                            if squares2dArray[(i - 1),(j - 1)] == 0:  # open to make 4iar
                                if squares2dArray[i,(j - 1)] != 0:  # support to make 4iar
                                    playColumn = j - 1
                                    print("ai 3iar diagonals right: playColumn =",playColumn) 
                                    run_ai = False
                                elif squares2dArray[i,(j - 1)] == 0:    # avoid col
                                    avoidColumns[j - 1] = 1
                    if (i + 3) < boardRows:
                        if (j + 3) < boardCols:
                            print("ai 3iar diagonals right: j+3") 
                            if squares2dArray[(i + 3),(j + 3)] == 0:  # open to make 4iar
                                if (i + 3) == 5:
                                    playColumn = j + 3
                                    print("ai 3iar diagonals right: playColumn =",playColumn) 
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j + 3)] != 0:  # support to make 4iar
                                        playColumn = j + 3
                                        print("ai 3iar diagonals right: playColumn =",playColumn) 
                                        run_ai = False
                                    elif squares2dArray[(i + 4),(j + 3)] == 0:    # avoid col
                                        avoidColumns[j + 3] = 1

        # check diagonals left, starting from left side
        numInRow = 0
        for i in range(4):
            for j in range(2,boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j-1] + squares2dArray[i+2,j-2]
                ##RH reorder, put ai last? or how to prioritize game winning move?
                ##RH set i = 5, j = 3, then run_ai = false?
                # ai
                if numInRow == -3:  # ai
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        if (j + 1) < boardCols:
                            print("ai 3iar diagonals left: i-1") 
                            if squares2dArray[(i - 1),(j + 1)] == 0:  # open to make 4iar
                                if squares2dArray[i,(j + 1)] != 0:  # support to make 4iar
                                    playColumn = j + 1
                                    print("ai 3iar diagonals left: playColumn =",playColumn) 
                                    run_ai = False
                    if (i + 3) < boardRows:
                        if 0 <= (j - 3):
                            print("ai 3iar diagonals left: j-3") 
                            if squares2dArray[(i + 3),(j - 3)] == 0:  # open to make 4iar
                                if (i + 3) == 5:
                                    playColumn = j - 3
                                    print("ai 3iar diagonals left: playColumn =",playColumn) 
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j - 3)] != 0:  # support to make 4iar
                                        playColumn = j - 3
                                        print("ai 3iar diagonals left: playColumn =",playColumn) 
                                        run_ai = False
                # human
                elif numInRow == 3:    # human
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        if (j + 1) < boardCols:
                            print("ai 3iar diagonals left: i-1") 
                            if squares2dArray[(i - 1),(j + 1)] == 0:  # open to make 4iar
                                if squares2dArray[i,(j + 1)] != 0:  # support to make 4iar
                                    playColumn = j + 1
                                    print("ai 3iar diagonals left: playColumn =",playColumn) 
                                    run_ai = False
                                elif squares2dArray[i,(j + 1)] == 0:    # avoid col
                                    avoidColumns[j + 1] = 1
                    if (i + 3) < boardRows:
                        if 0 <= (j - 3):
                            print("ai 3iar diagonals left: j-3") 
                            if squares2dArray[(i + 3),(j - 3)] == 0:  # open to make 4iar
                                if (i + 3) == 5:
                                    playColumn = j - 3
                                    print("ai 3iar diagonals left: playColumn =",playColumn) 
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j - 3)] != 0:  # support to make 4iar
                                        playColumn = j - 3
                                        print("ai 3iar diagonals left: playColumn =",playColumn) 
                                        run_ai = False
                                    elif squares2dArray[(i + 4),(j - 3)] == 0:  # support to make 4iar
                                        avoidColumns[j - 3] = 1
        '''

        # debug
        #print("")
        #print("# avoidColumns =",avoidColumns)


        #------------------------------------------------------
        # if easyMode == 1:    # clear array if easyMode turned on (1)
        #avoidColumns = [0,0,0,0,0,0,0]    # init array

        # scan board, add up how many 2iar for both ai & human, use in algo
        print("")
        print("## check 2iar:")
        # check columns
        numInRow = 0
        for i in range(5):
            for j in range(boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j]
                # ai
                if numInRow == -2:  # ai
                    print("numInRow =",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j].hilite = debugHilite
                    if 0 <= (i - 1):
                        print("ai 2iar cols: i-1")
                        if squares2dArray[i - 1,j] == 0:  # open to make 3iar
                            if avoidColumns[j] == 0:
                                playColumn = j
                                playColumns[j] = 1
                                print("ai 2iar cols: playColumn =",playColumn)
                                run_ai = False
                # human
                elif numInRow == 2:    # human
                    print("numInRow =",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j].hilite = debugHilite
                    if 0 <= (i - 1):
                        print("ai 2iar cols: i-1")
                        if squares2dArray[i - 1,j] == 0:  # open to make 3iar
                            if avoidColumns[j] == 0:
                                playColumn = j
                                playColumns[j] = 1
                                print("ai 2iar cols: playColumn =",playColumn)
                                run_ai = False
        # check diagonals right
        numInRow = 0
        for i in range(5):
            for j in range(6):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j+1]
                if numInRow == -2:  # ai
                    print("numInRow =",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j+1].hilite = debugHilite
                    if 0 <= (i - 1):
                        if 0 <= (j - 1):
                            print("ai 2iar diagonals right: j-1") 
                            if squares2dArray[(i - 1),(j - 1)] == 0:  # open to make 3iar
                                if squares2dArray[i,(j - 1)] != 0:  # support to make 3iar
                                    if avoidColumns[j - 1] == 0:
                                        playColumn = j - 1
                                        playColumns[j - 1] = 1
                                        run_ai = False
                    if (i + 2) < boardRows:
                        if (j + 2) < boardCols:
                            print("ai 2iar diagonals right: j+2") 
                            if squares2dArray[(i + 2),(j + 2)] == 0:  # open to make 3iar
                                if (i + 2) == 5:
                                    if avoidColumns[j + 2] == 0:
                                        playColumn = j + 2
                                        playColumns[j + 2] = 1
                                        print("ai 2iar 2iar diagonals: playColumn =",playColumn) 
                                        run_ai = False
                                elif (i + 2) < 5:
                                    if squares2dArray[(i + 3),(j + 2)] != 0:  # support to make 3iar
                                        if avoidColumns[j + 2] == 0:
                                            playColumn = j + 2
                                            playColumns[j + 2] = 1
                                            print("ai 2iar 2iar diagonals: playColumn =",playColumn) 
                                            run_ai = False
                # human
                elif numInRow == 2:    # human
                    print("numInRow =",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j+1].hilite = debugHilite
                    if 0 <= (i - 1):
                        if 0 <= (j - 1):
                            print("ai 2iar diagonals right: j-1") 
                            if squares2dArray[(i - 1),(j - 1)] == 0:  # open to make 3iar
                                if squares2dArray[i,(j - 1)] != 0:  # support to make 3iar
                                    if avoidColumns[j - 1] == 0:
                                        playColumn = j - 1
                                        playColumns[j - 1] = 1
                                        run_ai = False
                    if (i + 2) < boardRows:
                        if (j + 2) < boardCols:
                            print("ai 2iar diagonals right: j+2") 
                            if squares2dArray[(i + 2),(j + 2)] == 0:  # open to make 3iar
                                if (i + 2) == 5:
                                    if avoidColumns[j + 2] == 0:
                                        playColumn = j + 2
                                        playColumns[j + 2] = 1
                                        print("ai 2iar diagonals: playColumn =",playColumn) 
                                        run_ai = False
                                elif (i + 2) < 5:
                                    if squares2dArray[(i + 3),(j + 2)] != 0:  # support to make 3iar
                                        if avoidColumns[j + 2] == 0:
                                            playColumn = j + 2
                                            playColumns[j + 2] = 1
                                            print("ai 2iar diagonals: playColumn =",playColumn) 
                                            run_ai = False
        # check diagonals left
        numInRow = 0
        for i in range(5):
            for j in range(1,boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j-1]
                # ai
                if numInRow == -2:  # ai
                    print("numInRow =",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j-1].hilite = debugHilite
                    if 0 <= (i - 1):
                        if (j + 1) < boardCols:
                            print("ai 2iar diagonals left: i-1") 
                            if squares2dArray[(i - 1),(j + 1)] == 0:  # open to make 3iar
                                if squares2dArray[i,(j + 1)] != 0:  # support to make 3iar
                                    if avoidColumns[j + 1] == 0:
                                        playColumn = j + 1
                                        playColumns[j + 1] = 1
                                        run_ai = False
                    if (i + 2) < boardRows:
                        if 0 <= (j - 2):
                            print("ai 2iar diagonals left: j-2") 
                            if squares2dArray[(i + 2),(j - 2)] == 0:  # open to make 3iar
                                if (i + 2) == 5:
                                    if avoidColumns[j - 2] == 0:
                                        playColumn = j - 2
                                        playColumns[j - 2] = 1
                                        print("ai 2iar diagonals left: playColumn =",playColumn) 
                                        run_ai = False
                                elif (i + 2) < 5:
                                    if squares2dArray[(i + 3),(j - 2)] != 0:  # support to make 3iar
                                        if avoidColumns[j - 2] == 0:
                                            playColumn = j - 2
                                            playColumns[j - 2] = 1
                                            print("ai 2iar diagonals left: playColumn =",playColumn) 
                                            run_ai = False
                # human
                elif numInRow == 2:    # human
                    #danger = 3
                    print("numInRow =",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[(i+1)*boardCols + j-1].hilite = debugHilite
                    if 0 <= (i - 1):
                        if (j + 1) < boardCols:
                            print("ai 2iar diagonals left: i-1") 
                            if squares2dArray[(i - 1),(j + 1)] == 0:  # open to make 3iar
                                if squares2dArray[i,(j + 1)] != 0:  # support to make 3iar
                                    if avoidColumns[j + 1] == 0:
                                        playColumn = j + 1
                                        playColumns[j + 1] = 1
                                    run_ai = False
                    if (i + 2) < boardRows:
                        if 0 <= (j - 2):
                            print("ai 2iar diagonals right: j-2") 
                            if squares2dArray[(i + 2),(j - 2)] == 0:  # open to make 3iar
                                if (i + 2) == 5:
                                        if avoidColumns[j - 2] == 0:
                                            playColumn = j - 2
                                            playColumns[j - 2] = 1
                                            print("ai 2iar diagonals left: playColumn =",playColumn) 
                                            run_ai = False
                                elif (i + 2) < 5:
                                    if squares2dArray[(i + 3),(j - 2)] != 0:  # support to make 3iar
                                        if avoidColumns[j - 2] == 0:
                                            playColumn = j - 2
                                            playColumns[j - 2] = 1
                                            print("ai 2iar diagonals left: playColumn =",playColumn) 
                                            run_ai = False
        # check rows
        numInRow = 0
        for i in range(boardRows):
            for j in range(6):
                numInRow = squares2dArray[i,j] + squares2dArray[i,j+1]
                # ai
                if numInRow == -2:  # ai
                    print("numInRow =",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[i*boardCols + j+1].hilite = debugHilite
                    if 0 <= (j - 1):
                        print("ai 2iar rows: j-1") 
                        if squares2dArray[i,(j - 1)] == 0:  # open to make 3iar
                            if i == 5:
                                if avoidColumns[j - 1] == 0:
                                    playColumn = j - 1
                                    playColumns[j - 1] = 1
                                    run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j - 1)] != 0:  # support to make 3iar
                                    if avoidColumns[j - 1] == 0:
                                        playColumn = j - 1
                                        playColumns[j - 1] = 1
                                        run_ai = False
                    if (j + 2) < boardCols:
                        print("ai 2iar rows: j+2") 
                        if squares2dArray[i,(j + 2)] == 0:  # open to make 3iar
                            if i == 5:
                                if avoidColumns[j + 2] == 0:
                                    playColumn = j + 2
                                    playColumns[j + 2] = 1
                                    print("ai 2iar rows: playColumn =",playColumn) 
                                    run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j + 2)] != 0:  # support to make 3iar
                                    if avoidColumns[j + 2] == 0:
                                        playColumn = j + 2
                                        playColumns[j + 2] = 1
                                        print("ai 2iar rows: playColumn =",playColumn) 
                                        run_ai = False
                # human
                elif numInRow == 2:    # human
                    print("numInRow =",numInRow)
                    # debug: hilite winning discs (remove this later)
                    squaresArray[i*boardCols + j].hilite = debugHilite
                    squaresArray[i*boardCols + j+1].hilite = debugHilite
                    if 0 <= (j - 1):
                        print("ai 2iar rows: j-1") 
                        if squares2dArray[i,(j - 1)] == 0:  # open to make 3iar
                            if i == 5:
                                if avoidColumns[j - 1] == 0:
                                    playColumn = j - 1
                                    playColumns[j - 1] = 1
                                    print("ai 2iar rows: playColumn =",playColumn) 
                                    run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j - 1)] != 0:  # support to make 3iar
                                    if avoidColumns[j - 1] == 0:
                                        playColumn = j - 1
                                        playColumns[j - 1] = 1
                                        print("ai 2iar rows: playColumn =",playColumn) 
                                        run_ai = False
                    if (j + 2) < boardCols:
                        print("hum 2iar rows: j+2") 
                        if squares2dArray[i,(j + 2)] == 0:  # open to make 3iar
                            if i == 5:
                                if avoidColumns[j + 2] == 0:
                                    playColumn = j + 2
                                    playColumns[j + 2] = 1
                                    print("hum 2iar rows: playColumn =",playColumn) 
                                    run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j + 2)] != 0:  # support to make 3iar
                                    if avoidColumns[j + 2] == 0:
                                        playColumn = j + 2
                                        playColumns[j + 2] = 1
                                        print("hum 2iar rows: playColumn =",playColumn) 
                                        run_ai = False
        # for check 2iar:
        print("")
        print("# playColumn =",playColumn) 
        print("# playColumns  =",playColumns) 
        print("# avoidColumns =",avoidColumns)


        # scan board, add up how many 2/3 gap plays there are for both ai & human, use in algo
        print("")
        print("## gap check 2/3 2iar")
        # check rows
        numInRow = 0
        for i in range(boardRows):
            for j in range(5):    # stops after col 4
                numInRow = squares2dArray[i,j] + squares2dArray[i,j+1] + squares2dArray[i,j+2]
                #print("numInRow =",numInRow)
                # ai
                if numInRow == -2 and squares2dArray[i,j+1] == 0:
                    print("numInRow =",numInRow)
                    k = 1
                    #for k in range(3):
                        #if squares2dArray[i,j + k] == 0:
                    if i == 5:
                        playColumn = j + k
                        playColumns[j + k] = 1
                        print("ai 2/3 gap: playColumn =",playColumn)
                        run_ai = False
                    elif squares2dArray[(i + 1),(j + k)] != 0:    # support to make 4iar
                        playColumn = j + k
                        playColumns[j + k] = 1
                        print("ai 2/3 gap: playColumn =",playColumn)
                        run_ai = False
                # human
                elif numInRow == 2 and squares2dArray[i,j+1] == 0:
                    print("numInRow =",numInRow)
                    k = 1
                    #for k in range(3):
                        #if squares2dArray[i,j + k] == 0:
                    if i == 5:
                        playColumn = j + k
                        playColumns[j + k] = 1
                        print("hum 2/3 gap: playColumn =",playColumn)
                        run_ai = False
                    elif squares2dArray[(i + 1),(j + k)] != 0:    # support to fill gap (block it)
                        playColumn = j + k
                        playColumns[j + k] = 1
                        print("hum 2/3 gap: playColumn =",playColumn)
                        run_ai = False
                    elif squares2dArray[(i + 1),(j + k)] == 0:    # avoid col
                        if i <= 3:
                            if squares2dArray[(i + 2),(j + k)] != 0:    # avoid col
                                avoidColumns[j + k] = 1
                                print("hum 2/3 gap avoidColumns =",avoidColumns)
        # for gap check 2/3 2iar:
        print("")
        print("# playColumn =",playColumn) 
        print("# playColumns  =",playColumns) 
        print("# avoidColumns =",avoidColumns)


        #------------------------------------------------------
        # if easyMode == 0:    # skip if easyMode turned on (1)

        # scan board, add up how many 3iar for both ai & human, use in algo
        ##RH why is there a second pass on all this?
        ##RH reorder, put ai last? or how to prioritize game winning move?
        ##RH set i = 5, j = 3, then run_ai = false?
        print("")
        print("## check 3iar: second pass")
        # check rows
        numInRow = 0
        for i in range(boardRows):
            for j in range(5):
                numInRow = squares2dArray[i,j] + squares2dArray[i,j+1] + squares2dArray[i,j+2]
                # ai
                if numInRow == -3:   # ai
                    print("numInRow =",numInRow)
                    if 0 <= (j - 1):
                        print("ai 3iar rows: j-1")
                        if squares2dArray[i,(j - 1)] == 0:  # open to make 4iar
                            if i == 5:
                                playColumn = j - 1
                                playColumns[j - 1] = 2
                                print("ai 3iar rows: playColumn =",playColumn)
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j - 1)] != 0:  # support to make 3iar
                                    playColumn = j - 1
                                    playColumns[j - 1] = 2
                                    print("ai 3iar rows: playColumn =",playColumn)
                                    run_ai = False
                    if (j + 3) < boardCols:
                        print("ai 3iar rows: j+3")
                        if squares2dArray[i,(j + 3)] == 0:  # open to make 4iar
                            if i == 5:
                                playColumn = j + 3
                                playColumns[j + 3] = 2
                                print("ai 3iar rows: playColumn =",playColumn) 
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j + 3)] != 0:  # support to make 4iar
                                    playColumn = j + 3
                                    playColumns[j + 3] = 2
                                    print("ai 3iar rows: playColumn =",playColumn) 
                                    run_ai = False
                # human
                elif numInRow == 3:  # human
                    print("numInRow =",numInRow)
                    if 0 <= (j - 1):
                        print("hum 3iar rows: j-1") 
                        if squares2dArray[i,(j - 1)] == 0:  # open to block 4iar
                            if i == 5:
                                playColumn = j - 1
                                playColumns[j - 1] = 2
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j - 1)] != 0:  # support to block 4iar
                                    playColumn = j - 1
                                    playColumns[j - 1] = 2
                                    print("hum 3iar rows: playColumn =",playColumn) 
                                    run_ai = False
                                elif squares2dArray[(i + 1),(j - 1)] == 0:  # avoid col
                                    avoidColumns[j - 1] = 1
                                    print("hum 3iar rows avoidColumns =",avoidColumns)
                    if (j + 3) < boardCols:
                        print("hum 3iar rows: j+3")
                        if squares2dArray[i,(j + 3)] == 0:  # open to block 4iar
                            if i == 5:
                                playColumn = j + 3
                                playColumns[j + 3] = 2
                                print("hum 3iar rows: playColumn =",playColumn) 
                                run_ai = False
                            elif i < boardRows - 1:
                                if squares2dArray[(i + 1),(j + 3)] != 0:  # support to block 4iar
                                    playColumn = j + 3
                                    playColumns[j + 3] = 2
                                    print("hum 3iar rows: playColumn =",playColumn) 
                                    run_ai = False
                                elif squares2dArray[(i + 1),(j + 3)] == 0:    # avoid col
                                    avoidColumns[j + 3] = 1
                                    print("hum 3iar rows avoidColumns =",avoidColumns)

        # check columns
        numInRow = 0
        for i in range(4):
            for j in range(boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j] + squares2dArray[i+2,j]
                # ai
                if numInRow == -3:
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        print("ai 3iar cols: i-1")
                        if squares2dArray[i - 1,j] == 0:  # open to make 4iar
                            playColumn = j
                            playColumns[j] = 2
                            print("ai 3iar cols: playColumn =",playColumn)
                            run_ai = False
                # human
                elif numInRow == 3:
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        print("hum 3iar cols: i-1")
                        if squares2dArray[i - 1,j] == 0:  # open to make 4iar
                            playColumn = j
                            playColumns[j] = 2
                            print("hum 3iar cols: playColumn =",playColumn)
                            run_ai = False

        # check diagonals right
        numInRow = 0
        for i in range(4):
            for j in range(5):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j+1] + squares2dArray[i+2,j+2]    # add num in diagonal
                # ai
                if numInRow == -3:
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        if 0 <= (j - 1):
                            print("ai 3iar diagonals right: j-1") 
                            if squares2dArray[(i - 1),(j - 1)] == 0:  # open to make 4iar
                                if squares2dArray[i,(j - 1)] != 0:  # support to make 4iar
                                    playColumn = j - 1
                                    playColumns[j - 1] = 2
                                    print("ai 3iar diagonals right: playColumn =",playColumn) 
                                    run_ai = False
                    if (i + 3) < boardRows:
                        if (j + 3) < boardCols:
                            print("ai 3iar diagonals right: j+3") 
                            if squares2dArray[(i + 3),(j + 3)] == 0:  # open to make 4iar
                                if (i + 3) == 5:
                                    playColumn = j + 3
                                    playColumns[j + 3] = 2
                                    print("ai 3iar diagonals right: playColumn =",playColumn) 
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j + 3)] != 0:  # support to make 4iar
                                        playColumn = j + 3
                                        playColumns[j + 3] = 2
                                        print("ai 3iar diagonals right: playColumn =",playColumn) 
                                        run_ai = False
                # human
                elif numInRow == 3:
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        if 0 <= (j - 1):
                            print("hum 3iar diagonals right: j-1") 
                            if squares2dArray[(i - 1),(j - 1)] == 0:  # open to block 4iar
                                if squares2dArray[i,(j - 1)] != 0:  # support to block 4iar
                                    playColumn = j - 1
                                    playColumns[j - 1] = 2
                                    print("hum 3iar diagonals right: playColumn =",playColumn) 
                                    run_ai = False
                                elif squares2dArray[i,(j - 1)] == 0:    # avoid col
                                    avoidColumns[j - 1] = 1
                                    print("hum 3iar diag right: avoidColumns =",avoidColumns)
                    if (i + 3) < boardRows:
                        if (j + 3) < boardCols:
                            print("hum 3iar diagonals right: j+3") 
                            if squares2dArray[(i + 3),(j + 3)] == 0:  # open to block 4iar
                                if (i + 3) == 5:
                                    playColumn = j + 3
                                    playColumns[j + 3] = 2
                                    print("hum 3iar diagonals right: playColumn =",playColumn) 
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j + 3)] != 0:  # support to block 4iar
                                        playColumn = j + 3
                                        playColumns[j + 3] = 2
                                        print("hum 3iar diagonals right: playColumn =",playColumn) 
                                        run_ai = False
                                    elif squares2dArray[(i + 4),(j + 3)] == 0:    # avoid col
                                        avoidColumns[j + 3] = 1
                                        print("hum 3iar diag right: avoidColumns =",avoidColumns)

        # check diagonals left
        numInRow = 0
        for i in range(4):
            for j in range(2,boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j-1] + squares2dArray[i+2,j-2]
                # ai
                if numInRow == -3:
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        if (j + 1) < boardCols:
                            print("ai 3iar diagonals left: i-1") 
                            if squares2dArray[(i - 1),(j + 1)] == 0:  # open to make 4iar
                                if squares2dArray[i,(j + 1)] != 0:  # support to make 4iar
                                    playColumn = j + 1
                                    playColumns[j + 1] = 2
                                    print("ai 3iar diagonals left: playColumn =",playColumn) 
                                    run_ai = False
                    if (i + 3) < boardRows:
                        if 0 <= (j - 3):
                            print("ai 3iar diagonals left: j-3") 
                            if squares2dArray[(i + 3),(j - 3)] == 0:  # open to make 4iar
                                if (i + 3) == 5:
                                    playColumn = j - 3
                                    playColumns[j - 3] = 2
                                    print("ai 3iar diagonals left: playColumn =",playColumn) 
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j - 3)] != 0:  # support to make 4iar
                                        playColumn = j - 3
                                        playColumns[j - 3] = 2
                                        print("ai 3iar diagonals left: playColumn =",playColumn) 
                                        run_ai = False
                # human
                elif numInRow == 3:
                    print("numInRow =",numInRow) 
                    if 0 <= (i - 1):
                        if (j + 1) < boardCols:
                            print("hum 3iar diagonals left: i-1") 
                            if squares2dArray[(i - 1),(j + 1)] == 0:  # open to make 4iar
                                if squares2dArray[i,(j + 1)] != 0:  # support to make 4iar
                                    playColumn = j + 1
                                    playColumns[j + 1] = 2
                                    print("hum 3iar diagonals left: playColumn =",playColumn) 
                                    run_ai = False
                                elif squares2dArray[i,(j + 1)] == 0:    # avoid col
                                    avoidColumns[j + 1] = 1
                                    print("hum 3iar diag left: avoidColumns =",avoidColumns)
                    if (i + 3) < boardRows:
                        if 0 <= (j - 3):
                            print("hum 3iar diagonals left: j-3") 
                            if squares2dArray[(i + 3),(j - 3)] == 0:  # open to make 4iar
                                if (i + 3) == 5:
                                    playColumn = j - 3
                                    playColumns[j - 3] = 2
                                    print("hum 3iar diagonals left: playColumn =",playColumn) 
                                    run_ai = False
                                elif (i + 3) < 5:
                                    if squares2dArray[(i + 4),(j - 3)] != 0:  # support to make 4iar
                                        playColumn = j - 3
                                        playColumns[j - 3] = 2
                                        print("hum 3iar diagonals left: playColumn =",playColumn) 
                                        run_ai = False
                                    elif squares2dArray[(i + 4),(j - 3)] == 0:  # support to make 4iar
                                        avoidColumns[j - 3] = 1
                                        print("hum 3iar diag left: avoidColumns =",avoidColumns)
        # for check 3iar:
        print("")
        print("# playColumn =",playColumn) 
        print("# playColumns  =",playColumns) 
        print("# avoidColumns =",avoidColumns)


        #------------------------------------------------------
        # if easyMode == 0:    # skip if easyMode turned on (1)

        # scan board, add up how many 3/4 gap plays there are for both ai & human, use in algo
        ##RH reorder, put ai last? or how to prioritize game winning move?
        ##RH set i = 5, j = 3, then run_ai = false?
        print("")
        print("## gap check 3/4: second pass")
        # check rows
        numInRow = 0
        for i in range(boardRows):
            for j in range(4):    # stops after col 3
                numInRow = squares2dArray[i,j] + squares2dArray[i,j+1] + squares2dArray[i,j+2] + squares2dArray[i,j+3]
                #print("numInRow =",numInRow)
                # ai
                if numInRow == -3:   # ai
                    print("numInRow =",numInRow)
                    for k in range(4):
                        if squares2dArray[i,j + k] == 0:
                            if i == 5:
                                playColumn = j + k
                                playColumns[j + k] = 2
                                print("ai 3/4 gap rows: playColumn =",playColumn)
                                run_ai = False
                            elif squares2dArray[(i + 1),(j + k)] != 0:    # support to make 4iar
                                playColumn = j + k
                                playColumns[j + k] = 2
                                print("ai 3/4 gap rows: playColumn =",playColumn)
                                run_ai = False
                # human
                elif numInRow == 3:    # human
                    print("numInRow =",numInRow)
                    for k in range(4):
                        if squares2dArray[i,j + k] == 0:
                            if i == 5:
                                playColumn = j + k
                                playColumns[j + k] = 2
                                print("hum 3/4 gap rows: playColumn =",playColumn)
                                run_ai = False
                            elif squares2dArray[(i + 1),(j + k)] != 0:    # support to fill gap (block it)
                                playColumn = j + k
                                playColumns[j + k] = 2
                                print("hum 3/4 gap rows: playColumn =",playColumn)
                                run_ai = False
                            elif squares2dArray[(i + 1),(j + k)] == 0:    # avoid col
                                if i <= 3:
                                    if squares2dArray[(i + 2),(j + k)] != 0:    # avoid col
                                        avoidColumns[j + k] = 1
                                        print("hum 3/4 gap rows: avoidColumns =",avoidColumns)

        # check diagonals right, starting from top left corner
        numInRow = 0
        for i in range(3):
            for j in range(4):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j+1] + squares2dArray[i+2,j+2] + squares2dArray[i+3,j+3]    # add num in diagonal
                #print("numInRow =",numInRow) 
                ##RH reorder? how to prioritize game winning move?
                ##RH set i = 5, j = 3, then run_ai = false??
                # ai
                if numInRow == -3:  # ai
                    print("numInRow =",numInRow) 
                    for k in range(4):
                        if squares2dArray[i + k,j + k] == 0:
                            if (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j + k)] != 0:    # support to make 4iar
                                playColumn = j + k
                                playColumns[j + k] = 2
                                print("ai 3/4 gap diags right: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k) == 5:    # support to make 4iar
                                playColumn = j + k
                                playColumns[j + k] = 2
                                print("ai 3/4 gap diags right: playColumn =",playColumn)
                                run_ai = False
                # human
                elif numInRow == 3:    # human
                    print("numInRow =",numInRow) 
                    for k in range(4):
                        if squares2dArray[i + k,j + k] == 0:
                            if (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j + k)] != 0:    # support to fill gap (block it)
                                playColumn = j + k
                                playColumns[j + k] = 2
                                print("hum 3/4 gap diags right: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k) == 5:    # support to make 4iar
                                playColumn = j + k
                                playColumns[j + k] = 2
                                print("hum 3/4 gap diags right: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j + k)] == 0:    # avoid col
                                avoidColumns[j + k] = 1
                                print("hum 3/4 gap diags right: avoidColumns =",avoidColumns)

        # check diagonals left, starting from left side
        numInRow = 0
        for i in range(3):
            for j in range(3,boardCols):
                numInRow = squares2dArray[i,j] + squares2dArray[i+1,j-1] + squares2dArray[i+2,j-2] + squares2dArray[i+3,j-3]    # add num in diagonal
                #print("numInRow =",numInRow) 
                ##RH reorder? how to prioritize game winning move?
                ##RH set i = 5, j = 3, then run_ai = false?
                # ai
                if numInRow == -3:  # ai
                    print("numInRow =",numInRow) 
                    for k in range(4):
                        if squares2dArray[i + k,j - k] == 0:
                            if (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j - k)] != 0:    # support to make 4iar
                                playColumn = j - k
                                playColumns[j - k] = 2
                                print("ai 3/4 gap diags left: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k) == 5:    # support to make 4iar
                                playColumn = j - k
                                playColumns[j - k] = 2
                                print("ai 3/4 gap diags left: playColumn =",playColumn)
                                run_ai = False
                # human
                elif numInRow == 3:    # human
                    print("numInRow =",numInRow) 
                    for k in range(4):
                        if squares2dArray[i + k,j - k] == 0:
                            if (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j - k)] != 0:    # support to fill gap (block it)
                                playColumn = j - k
                                playColumns[j - k] = 2
                                print("hum 3/4 gap diags left: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k) == 5:    # support to make 4iar
                                playColumn = j - k
                                playColumns[j - k] = 2
                                print("hum 3/4 gap diags left: playColumn =",playColumn)
                                run_ai = False
                            elif (i + k + 1) < 6 and squares2dArray[(i + k + 1),(j - k)] == 0:    # avoid col
                                avoidColumns[j - k] = 1
                                print("hum 3/4 gap diags left: avoidColumns =",avoidColumns)


        redrawWindow()    # RH why?
        print("")
        print("# ai exit: playColumn =",playColumn)
        print("# playColumns  =",playColumns) 
        print("# avoidColumns =",avoidColumns)

        #------------------------------------------------------
        ##RH what do to if playColumn == avoidColumn == 1?
        if avoidColumns[playColumn] == 1:
            # pick any open move (lowest priority)
            for i in range(boardCols):
                #if playColumns[i] == 1:
                if avoidColumns[i] == 0:
                    playColumn = i
            # pick another suggested open move (middle priority)
            for i in range(boardCols):
                if playColumns[i] == 1:
                    if avoidColumns[i] == 0:
                        playColumn = i
        # pick any urgent move (top priority)
        for i in range(boardCols):
            if playColumns[i] == 2:
                playColumn = i

        print("")
        print("# ai final: playColumn =",playColumn)
        print("# playColumns  =",playColumns) 
        print("# avoidColumns =",avoidColumns)
        run_ai = False

    # end computer_ai()


#------------------------------------------------------
def fullColumnCheck():

    # check for full column move, if full:
    # search for an open column
    # added avoidColumn array checking

    global playColumn
    global avoidColumns
    global boardCols

    print("")
    print("ai check for full columns...") 
    print("playColumn =",playColumn)  
    print(squares2dArray)

    if squares2dArray[0,playColumn] != 0:    # column is full
        print("** column is full, searching for an open column...")    # to see if I still need this function (I do)
        # debug
        print("# avoidColumns =",avoidColumns)
        if leftRight == 0:  # left
            for i in range(boardCols):
                if squares2dArray[0,i] == 0:    # column top is empty
                    if avoidColumns[i] == 0:
                        playColumn = i
                        break
            if squares2dArray[0,playColumn] != 0:    # column is still full
                for i in range(boardCols):
                    if squares2dArray[0,i] == 0:    # column top is empty
                        playColumn = i
                        break
        elif leftRight == 1:  # right
            for i in range(boardCols,0,-1):
                if squares2dArray[0,i-1] == 0:    # column top is empty
                    if avoidColumns[i-1] == 0:
                        playColumn = i -1
                        break
            if squares2dArray[0,playColumn] != 0:    # column is still full
                for i in range(boardCols,0,-1):
                    if squares2dArray[0,i-1] == 0:    # column top is empty
                        playColumn = i -1
                        break

    print("# fullColumnCheck exit: playColumn =",playColumn)   # debug
# end fullColumnCheck()


#------------------------------------------------------
def dropDisc(column,color):
    print("dropDisc")

    global squaresArray
    delay = 25

    pygame.event.clear()
    run_dd = 1

    while run_dd:

        clock.tick(5)   # experimental

        if squares2dArray[1,column] == 0:
            #squaresArray[column].hilite = False
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
    dropSound.play()  #sfx_sounds_impact6.wav
    # end dropDisc


#------------------------------------------------------
def winnerCheck():

    print("winnerCheck")

    global winner
    numInRow = 0

    pygame.event.clear()
    run_wc = True

    while run_wc:
        # check for board full draw
        winner = 2   # draw
        for i in range(boardRows):
            for j in range(boardCols):
                if squares2dArray[i,j] == 0:
                    winner = 0
                    #run_wc = False
        # check rows
        numInRow = 0
        for i in range(boardRows):
            for j in range(4):
                numInRow = squares2dArray[i,j] + squares2dArray[i,j+1] + squares2dArray[i,j+2] + squares2dArray[i,j+3]
                if numInRow == 4:
                    winner = 1
                    print("winner =",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[i*boardCols + j+1].hilite = True
                    squaresArray[i*boardCols + j+2].hilite = True
                    squaresArray[i*boardCols + j+3].hilite = True
                    run_wc = False
                elif numInRow == -4:
                    winner = -1
                    print("winner =",winner)
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
                    print("winner =",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[(i+1)*boardCols + j].hilite = True
                    squaresArray[(i+2)*boardCols + j].hilite = True
                    squaresArray[(i+3)*boardCols + j].hilite = True
                    run_wc = False
                elif numInRow == -4:
                    winner = -1
                    print("winner =",winner)
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
                    print("winner =",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[(i+1)*boardCols + j+1].hilite = True
                    squaresArray[(i+2)*boardCols + j+2].hilite = True
                    squaresArray[(i+3)*boardCols + j+3].hilite = True
                    run_wc = False
                elif numInRow == -4:
                    winner = -1
                    print("winner =",winner)
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
                    print("winner =",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[(i+1)*boardCols + j-1].hilite = True
                    squaresArray[(i+2)*boardCols + j-2].hilite = True
                    squaresArray[(i+3)*boardCols + j-3].hilite = True
                    run_wc = False
                elif numInRow == -4:
                    winner = -1
                    print("winner =",winner)
                    # hilite winning discs
                    clearSquaresHilite()
                    squaresArray[i*boardCols + j].hilite = True
                    squaresArray[(i+1)*boardCols + j-1].hilite = True
                    squaresArray[(i+2)*boardCols + j-2].hilite = True
                    squaresArray[(i+3)*boardCols + j-3].hilite = True
                    run_wc = False

        print("winnerCheck end: winner =",winner)
        run_wc = False

    # end winnerCheck()


#------------------------------------------------------
def endgame():

    global numPlayers
    global turnPlayer    # turnPlayer = 1  # 1 or 2. Computer is player 1 if single player mode
    global winner
    global playCount
    global winsPlayer1
    global winsPlayer2
    global whoGoesFirst

    print("endgame winner =",winner)
    print("endgame whoGoesFirst =",whoGoesFirst)
    whoGoesFirst = whoGoesFirst * -1   # alternate players
    print("endgame whoGoesFirst =",whoGoesFirst)

    playCount = 0   # a play is one round, i.e., computer and human each taking a turn

    redrawWindow()
    yesButton = Button((255,255,0), 1180,50,40,40,'Y')
    noButton  = Button((255,255,0), 1250,50,40,40,'N')

    font = pygame.font.SysFont('comicsansms', 50)  # comicsansms arial

    if winner == 1:
        winsPlayer2 = winsPlayer2 + 1
        print("")
        print("Player #2 wins!!!")
        textmsg ="Player #2 wins!!!"
        text = font.render(textmsg,1,colorPlayer2)
        screen.blit(text, ((display_width/2)-190,25))
        twoBellsSound.play()
        twoBellsSound.play()
    elif winner == -1:
        winsPlayer1 = winsPlayer1 + 1
        print("")
        if numPlayers == 1:
            print("Computer wins!!!")
            textmsg ="Computer wins!!!"
            alarmBellSound.play()
        elif numPlayers == 2:
            print("Player #1 wins!!!")
            textmsg ="Player #1 wins!!!"
            twoBellsSound.play()
            twoBellsSound.play()
        text = font.render(textmsg,1,colorPlayer1)
        screen.blit(text, ((display_width/2)-190,25))
    elif winner == 2:
        print("")
        print("It's a draw!!")
        textmsg ="It's a draw!!"
        text = font.render(textmsg,1,white)
        screen.blit(text, ((display_width/2)-190,25))

    winner = 0    # 1 or 2, winning player

    pygame.display.update()
    pygame.time.wait(2000)

    redrawWindow()
    print("Play again?")
    textmsg ="Play again?"
    text = font.render(textmsg,1,white)
    screen.blit(text, ((display_width/2)-190,25))
    pygame.display.update()

    pygame.event.clear()
    run_end = True

    while run_end:

        clock.tick(10)

        yesButton.draw(screen,(0,0,0))  #surface, outline
        noButton.draw(screen,(0,0,0))  #surface, outline
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("quit selected")
                run_end = False
                pygame.quit()
                sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_y]:  # supports upper & lower case
                print("yes selected")
                run_end = False
                if whoGoesFirst == 1:
                    turnPlayer = 1    # Computer is player 1 if single player mode
                elif whoGoesFirst == -1:
                    turnPlayer = 2    # human
                #initSquaresArray()
                clearSquaresArray()
                update2dArray()
                print("go to game_loop")
                game_loop()
            if keys[pygame.K_n]:  # supports upper & lower case
                print("no selected")
                run_end = False
                pygame.quit()
                sys.exit()

            pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click.play()
                if yesButton.isOver(pos):
                    print("yes selected")
                    run_end = False
                    if whoGoesFirst == 1:
                        turnPlayer = 1    # Computer is player 1 if single player mode
                    elif whoGoesFirst == -1:
                        turnPlayer = 2    # human
                    #initSquaresArray()
                    clearSquaresArray()
                    update2dArray()
                    print("go to game_loop")
                    game_loop()
                if noButton.isOver(pos):
                    print("no selected")
                    pygame.time.delay(500)
                    run_end = False
                    #run_game = False   # debug
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
    # end endgame()


#------------------------------------------------------
def game_loop():

    print("")
    print("** begin game_loop **")
    print("")

    global numPlayers
    global turnPlayer    # turnPlayer = 1  # 1 or 2. Computer is player 1 if single player mode
    global winner        # winner = 0      # 1 or 2, winning player
    global playColumn    # playColumn = 3
    global playCount     # playCount = 0   # a play is one round, i.e. computer and human each taking a turn

    # debug:
    #turnPlayer = 2
    print("numPlayers =",numPlayers)
    print("turnPlayer =",turnPlayer)
    print("winner =",winner)

    #print("** Computer's Turn **")

    font = pygame.font.SysFont('comicsansms', 40)

    shipsBellSound.play()
    redrawWindow()

    pygame.event.clear()
    run_game = True

    while run_game:

        #redrawWindow()
        #print("while run_game =",run_game)  
        #print("turnPlayer =",turnPlayer)  
        #clock.tick(5)   # debug
        clock.tick(30)

        # is it computer's turn?
        if numPlayers == 1 and turnPlayer == 1:
            print("")
            print("** Computer's Turn **")
            textmsg = "Computer's Turn"
            font = pygame.font.SysFont('comicsansms', 40)
            text = font.render(textmsg,1,colorPlayer1)
            screen.blit(text, ((display_width/2)-155,40))
            pygame.display.update()
            pygame.time.wait(1200)
            computer_ai()
            fullColumnCheck()
            squaresArray[playColumn].disc = colorPlayer1
            #print("squaresArray",playColumn,".disc =",colorPlayer1)  
            redrawWindow()
            dropDisc(playColumn,squaresArray[playColumn].disc)
            winnerCheck()
            redrawWindow()
            if winner != 0:
                run_game = False
                endgame()    # declare winner & play again?
            # switch players if no winner:
            print("")
            print("** Human Player's (#2) Turn **")
            #print("** Player #2's Turn **")
            turnPlayer = 2

        # is it human's turn?
        elif turnPlayer == 2 or numPlayers == 2:
            font = pygame.font.SysFont('comicsansms', 40)  # comicsansms arial
            if turnPlayer == 1:
                textmsg = "Player #1's Turn"
                text = font.render(textmsg,1,colorPlayer1)
            elif turnPlayer == 2:
                textmsg = "Player #2's Turn"
                text = font.render(textmsg,1,colorPlayer2)
            screen.blit(text, ((display_width/2)-160,40))
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
                    click.play()
                    for i in range (7):
                        if squaresArray[i].isOver(pos):
                            playColumn = i
                            print("playColumn =",playColumn)  
                            #print(squares2dArray)  
                            # error checking here....
                            if squares2dArray[0,playColumn] != 0:    # error
                                print("# error #")  
                                print("turnPlayer =",turnPlayer)  
                                print(squares2dArray)  
                                honk3Sound.play()
                                print("squaresArray",i,".disc =",squaresArray[i].disc)  
                            elif squaresArray[i].disc == black:
                                if turnPlayer == 1:
                                    squaresArray[i].disc = colorPlayer1
                                    #print("squaresArray",i,".disc =",colorPlayer1)  
                                elif turnPlayer == 2:
                                    squaresArray[i].disc = colorPlayer2
                                    #print("squaresArray",i,".disc =",colorPlayer2)  
                                redrawWindow()
                                #update2dArray()
                                #print("game_loop")  
                                print("turnPlayer =",turnPlayer)  
                                print(squares2dArray)  
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
                    #print("** Computer's Turn **")

    # end game_loop()


#------------------------------------------------------
game_setup()
game_loop()    # called from game_setup, do I need this?


pygame.quit()
sys.exit()

