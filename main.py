# General Imports
import random
import abc
import time
import sys
import math as m
from multiprocessing import Pool

# File Imports
from player import *
from game import game
from game import deck
from trainModel import trainModel

# Play one game
def playGame(selectedAI):
    result = 0
    playerAI = selectedAI[0]
    enemyAI = selectedAI[1]
    model = selectedAI[2]

    # Decide enemyAI
    if enemyAI == 0:
        enemyPlayer = randomPlayer.randomPlayer
    else:
        enemyPlayer = grabAndDuckPlayer.grabAndDuckPlayer

    # Create games and play them
    players = []
    players.append(enemyPlayer("Foo"))

    # Decide playerAI type
    if playerAI == 0:
        players.append(grabAndDuckPlayer.grabAndDuckPlayer("AI"))
    elif playerAI == 1:
        players.append(rolloutPlayer.rolloutPlayer("AI", 0.01))
    elif playerAI == 2:
        players.append(randomGrabAndDuckPlayer.randomGrabAndDuckPlayer("AI", 0.1))
    elif playerAI == 3:
        players.append(mlPlayer.mlPlayer("AI", model))
    else:
        players.append(mctsPlayer.mctsPlayer("AI", 0.01))
            
    players.append(enemyPlayer("Bar"))
    theGame = game.game(players)

    # Record result if playerAI wins
    if theGame.play(False)[0] == "AI":
        result += 1

    return result
    
# Return results of a set of games
def playGames(numGames, playerAI, enemyAI, model):
    results = 0
    selectedAI = [playerAI, enemyAI, model];

    # Start Timer
    timeElapsed = time.perf_counter()
    
    # Create list of AI selections for multiprocessing
    selectionList = []
    for _ in range(numGames):
        selectionList.append(selectedAI)

    # Perform multiprocessing
    totalProcs = min(numGames*2, 4)
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
    elif playerAI == 3:
        print("******* ML ********")
    else:
        print("****** MCTS *******")

    # Return results
    print("AI win rate: ", 100*(results/numGames),"% or",results,"over",numGames)
    print("Time: ", timeElapsed)
          
# Produce all reports for numGames
def playAll(numGames, model):
    for playerAI in range(0,4):
        for enemyAI in range(0,2):
            playGames(numGames, playerAI, enemyAI, model)

# Set Seeds
numArgs = len(sys.argv[1:])
if numArgs != 0:
    random.seed(sys.argv[1])
else:
    random.seed("bababooey")
            
# Produce report
model = trainModel.recursiveTrain(0, True, 1000)
playGames(50, 3, 1, model)
# playAll(1, model)
# mlPlayer("Test")
# for i in range(0, 100):
#      playGame([3, 1, model])
