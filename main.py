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
    
# Return results of a set of games
def playGames(numGames, playerAI, enemyAI):
    Results=0

    # Decide enemyAI
    if enemyAI == 0:
        enemyPlayer=randomPlayer
    else:
        enemyPlayer=grabAndDuckPlayer

    # Create games and play them
    for i in range(numGames):
        players = []
        players.append(enemyPlayer("Foo"))

        # Decide playerAI type
        if playerAI == 0:
            players.append(grabAndDuckPlayer("AI"))
        elif playerAI == 1:
            players.append(rolloutPlayer("AI"))
        else:
            players.append(mctsPlayer("AI"))
            
        players.append(enemyPlayer("Bar"))
        theGame = game(players)

        # Record results if playerAI wins
        if theGame.play()[0] == "AI":
            Results+=1

    # Decide playerAI type
    if playerAI == 0:
        print("** Grab And Duck **")
    elif playerAI == 1:
        print("**** Rollouts *****")
    else:
        print("****** MCTS *******")

    # Return results
    print("AI win rate: ", 100*(Results/numGames),"% or",Results,"over",numGames)

# Produce all reports for numGames
def playAll(numGames):
    for enemyAI in range(0,2):
        for playerAI in range(0,1):
            playGames(numGames, playerAI, enemyAI)

# Set Seeds
numArgs = len(sys.argv[1:])
if numArgs != 0:
    random.seed(sys.argv[1])
else:
    random.seed("bababooey")
            
# Produce report
playAll(20)
