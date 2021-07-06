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
# AIplayerType - 0, 1, 2, 3, 4 for random, grab and duck, rollouts, mcts, perform comparison
# vsType 0 or 1, 0 for opponents random, 1 for grab and duck
# seed - any text, optional

# Right Number of Arguments
numArgs = len(sys.argv[1:])
if numArgs < 2:
    print("Wrong number of arguments.") 
    exit()

# AI and Enemy selection
AIselection = sys.argv[2]
vsType = sys.argv[3]

# Quite mode?
if sys.argv[1] == '1':
    qMode = True
else:
    qMode = False
    
# Set Seeds
if numArgs >= 4:
    random.seed(sys.argv[4])
else:
    random.seed()
    
# Select kind of player up against, by defining "EnemyPlayer" to mean one of two classes
if vsType == '0': 
    enemyPlayer=randomPlayer
elif vsType == '1':
    enemyPlayer=grabAndDuckPlayer
else:
    print("Bad player type! Must be 0 or 1")
    exit()
    # Code for Playing Games

# Determine what kind of results to return
if AIselection == '4':
    Games=20
    
#    MctsResults=0
#    for i in range(Games):
#        players = []
#        players.append(enemyPlayer("Foo"))
#        players.append(mctsPlayer("AI"))
#        players.append(enemyPlayer("Bar"))
#        theGame = game(players)
#
#        if theGame.play()[0] == "AI":
#            MctsResults+=1

    GDResults=0
    for i in range(Games):
        players = []
        players.append(enemyPlayer("Foo"))
        players.append(grabAndDuckPlayer("AI"))
        players.append(enemyPlayer("Bar"))
        theGame = game(players)

        if theGame.play()[0] == "AI":
            GDResults+=1

#    RResults=0
#    for i in range(Games):
#        players = []
#        players.append(enemyPlayer("Foo"))
#        players.append(rolloutPlayer("AI"))
#        players.append(enemyPlayer("Bar"))
#        theGame = game(players)
#
#        if theGame.play()[0] == "AI":
#            RResults+=1
            
#    print("MTCS AI win rate: ", 100*MctsResults/Games,"% or",MctsResults,"over",Games)
    print("Grab And Duck AI win rate: ", 100*GDResults/Games,"% or",GDResults,"over",Games)
#    print("Rollout AI win rate: ", 100*RResults/Games,"% or",RResults,"over",Games)
else:
    players = []
    players.append(enemyPlayer("Foo"))

    if AIselection == '0':
        players.append(randomPlayer("AI"))
    elif AIselection == '1':
        players.append(grabAndDuckPlayer("AI"))
    elif AIselection == '2':
        players.append(rolloutPlayer("AI"))
    else:
        players.append(mctsPlayer("AI"))
        
    players.append(enemyPlayer("Bar")) 
    theGame = game(players) 

    print(theGame.play())
