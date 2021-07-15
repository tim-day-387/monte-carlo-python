# General Imports
import random
import abc
import time
import sys
import math as m
from multiprocessing import Pool

# File Imports
from player import player
from yieldPlayer import yieldPlayer
from randomPlayer import randomPlayer
from rolloutPlayer import rolloutPlayer
from grabAndDuckPlayer import grabAndDuckPlayer
from mctsPlayer import mctsPlayer
from randomGrabAndDuckPlayer import randomGrabAndDuckPlayer
from deck import deck
from game import game

# Play one game
def playGame(selectedAI):
    result = 0
    playerAI = selectedAI[0]
    enemyAI = selectedAI[1]

    # Decide enemyAI
    if enemyAI == 0:
        enemyPlayer=randomPlayer
    else:
        enemyPlayer=grabAndDuckPlayer

    # Create games and play them
    players = []
    players.append(enemyPlayer("Foo"))

    # Decide playerAI type
    if playerAI == 0:
        players.append(grabAndDuckPlayer("AI"))
    elif playerAI == 1:
        players.append(rolloutPlayer("AI", 0.01))
    elif playerAI == 2:
        players.append(randomGrabAndDuckPlayer("AI", 0.1))
    else:
        players.append(mctsPlayer("AI", 0.01))
            
    players.append(enemyPlayer("Bar"))
    theGame = game(players)

    # Record result if playerAI wins
    if theGame.play()[0] == "AI":
        result += 1

    return result
    
# Return results of a set of games
def playGames(numGames, playerAI, enemyAI):
    results = 0
    selectedAI = [playerAI, enemyAI];

    # Start Timer
    timeElapsed = time.perf_counter()
    
    # Create list of AI selections for multiprocessing
    selectionList = []
    for _ in range(numGames):
        selectionList.append(selectedAI)

    # Perform multiprocessing
    totalProcs = min(numGames*2, 256)
    pool = Pool(processes = totalProcs)
    outputs = pool.map(playGame, selectionList)
    results = sum(outputs)

    # End Timer
    timeElapsed = time.perf_counter() - timeElapsed
    
    # Decide playerAI type
    if playerAI == 0:
        print("** Grab And Duck **")
    elif playerAI == 1:
        print("**** Rollouts *****")
    elif playerAI == 2:
        print("**** Random G&D ***")
    else:
        print("****** MCTS *******")

    # Return results
    print("AI win rate: ", 100*(results/numGames),"% or",results,"over",numGames)
    print("Time: ", timeElapsed)
          
# Produce all reports for numGames
def playAll(numGames):
    for playerAI in range(0,4):
        for enemyAI in range(0,2):
            playGames(numGames, playerAI, enemyAI)

# Set Seeds
numArgs = len(sys.argv[1:])
if numArgs != 0:
    random.seed(sys.argv[1])
else:
    random.seed("bababooey")
            
# Produce report
playAll(20)

