# General Imports
import random
import abc
import time
import sys
import math as m

# File Imports
from player import player
from yieldPlayer import yieldPlayer
from randomPlayer import randomPlayer
from rolloutPlayer import rolloutPlayer
from grabAndDuckPlayer import grabAndDuckPlayer
from mctsPlayer import mctsPlayer
from deck import deck
from game import game

# How Arguments Work
# python3 Monster.py quiteMode AIplayerType seed
# quiteMode - 0 or 1
# AIplayerType - 0, 1, 2, 3, 4 for random, grab and duck, rollouts, MCTS, perform comparison on 20 games each
# vsType 0 or 1, 0 for opponents random, 1 for opnents doing grab and duck
# seed - any text, optional

# Right Number of Arguments
numArgs = len(sys.argv[1:])
if numArgs < 2:
    print("Wrong number of arguments.") #maybe make it so this lets you input it on run time instead of quitting? Would be useful for running in IDLE
    exit()

# AI selection
AIselection = sys.argv[2]
#enemy selection
vsType = sys.argv[3]
    
# Quite mode?
if sys.argv[1] == '1':
    qMode = True
else:
    qMode = False
    
# Set Seeds
if numArgs >= 4:
    seed=sys.argv[4]
else:
    seed=""

if seed=="":
    random.seed()
else:
    random.seed(seed)
                    
#For question 6, a time allocator as our (mandated) "extra credit"
class TimeAllocator:
    def __init__(self,initialTime,priorityMul=1.0):
        self.iniTime=initialTime
        self.curTime=initialTime
        self.prio=priorityMul
    def reset(self):
        self.curTime=self.iniTime
    def getAllowedTime(self,handSize,legalSize): #How much time should I be allowed? Legal Size is how many legal cards there are.
        if handSize==2: #if there's only 2 cards in hand, just give all the hand.
            return self.curTime
        if self.curTime <= 0.0 : #if we have no time left
            return 0
        #otherwise, we need to compute the ratio
        ratio=(handSize*legalSize)/(handSize*(legalSize+(handSize-1)*(2*handSize-1)/6)-1) #how much time should this get, vs how many are left, in the worst case? 
        #explanation in the writeup
        if ratio*self.prio >= 0.99: #if we'd give almost all the time
            pass #ignore the priority
        else:
            ratio*=self.prio #otherwise, apply it.
        return self.curTime*ratio
    def removeSpent(self,spentTime):
        self.curTime-=spentTime
        
# Select kind of player up against, by defining "EnemyPlayer" to mean one of two classes
enemyPlayer=randomPlayer
if vsType == '0': 
    pass #no change here
elif vsType == '1':
    enemyPlayer=grabAndDuckPlayer
else:
    print("Bad player type! Must be 0 or 1")
    exit()
# Code for Playing Games
if AIselection == '5':
    Games=20 #only says to play 20 games, not 200

#    MctsResults=0
#    for i in range(Games):
#        playahs = []
#        playahs.append(enemyPlayer("Foo"))
#        playahs.append(mctsPlayer("AI"))
#        playahs.append(enemyPlayer("Bar"))
#        theGame = game(playahs)
#
#        if theGame.play()[0] == "AI":
#            MctsResults+=1

    GDResults=0
    for i in range(Games):
        playahs = []
        playahs.append(enemyPlayer("Foo"))
        playahs.append(grabAndDuckPlayer("AI"))
        playahs.append(enemyPlayer("Bar"))
        theGame = game(playahs)

        if theGame.play()[0] == "AI":
            GDResults+=1

    RResults=0
    for i in range(Games):
        playahs = []
        playahs.append(enemyPlayer("Foo"))
        playahs.append(rolloutPlayer("AI"))
        playahs.append(enemyPlayer("Bar"))
        theGame = game(playahs)

        if theGame.play()[0] == "AI":
            RResults+=1
            
#    print("MTCS AI win rate: ", 100*MctsResults/Games,"% or",MctsResults,"over",Games)
    print("Grab And Duck AI win rate: ", 100*GDResults/Games,"% or",GDResults,"over",Games)
    print("Rollout AI win rate: ", 100*RResults/Games,"% or",RResults,"over",Games)
else:
    playahs = []
    playahs.append(enemyPlayer("Foo"))

    if AIselection == '0':
        playahs.append(randomPlayer("AI"))
    elif AIselection == '1':
        playahs.append(grabAndDuckPlayer("AI"))
    elif AIselection == '2':
        playahs.append(rolloutPlayer("AI"))
    else:
        playahs.append(mctsPlayer("AI"))
    
    playahs.append(enemyPlayer("Bar")) 
    theGame = game(playahs) #potentially make it play more than one?

    print(theGame.play())
