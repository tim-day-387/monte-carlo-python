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
        enemyPlayer1 = mctsPlayer.mctsPlayer("Foo", 0.01)
        enemyPlayer2 = mctsPlayer.mctsPlayer("Bar", 0.01)
    elif enemyAI == 1:
        enemyPlayer1 = grabAndDuckPlayer.grabAndDuckPlayer("Foo")
        enemyPlayer2 = grabAndDuckPlayer.grabAndDuckPlayer("Bar")
    elif enemyAI == 2:
        enemyPlayer1 = rolloutPlayer.rolloutPlayer("Foo", 0.01)
        enemyPlayer2 = rolloutPlayer.rolloutPlayer("Bar", 0.01)
    elif enemyAI == 3:
        enemyPlayer1 = randomGrabAndDuckPlayer.randomGrabAndDuckPlayer("Foo", 0.1)
        enemyPlayer2 = randomGrabAndDuckPlayer.randomGrabAndDuckPlayer("Bar", 0.1)
    elif enemyAI == 4:
        enemyPlayer1 = mlPlayer.mlPlayer("Foo", model)
        enemyPlayer2 = mlPlayer.mlPlayer("Bar", model)
    elif enemyAI == 5:
        enemyPlayer1 = mlRolloutPlayer.mlRolloutPlayer("Foo", model, 0.01)
        enemyPlayer2 = mlRolloutPlayer.mlRolloutPlayer("Bar", model, 0.01)

    else:
        enemyPlayer1 = randomPlayer.randomPlayer("Foo")
        enemyPlayer2 = randomPlayer.randomPlayer("Bar")

    # Create games and play them
    players = []
    players.append(enemyPlayer1)

    # Decide playerAI type
    if playerAI == 0:
        players.append(mctsPlayer.mctsPlayer("AI", 0.01))
    elif playerAI == 1:
        players.append(grabAndDuckPlayer.grabAndDuckPlayer("AI"))
    elif playerAI == 2:
        players.append(rolloutPlayer.rolloutPlayer("AI", 0.01))
    elif playerAI == 3:
        players.append(randomGrabAndDuckPlayer.randomGrabAndDuckPlayer("AI", 0.1))
    elif playerAI == 4:
        players.append(mlPlayer.mlPlayer("AI", model))
    elif playerAI == 5:
        players.append(mlRolloutPlayer.mlRolloutPlayer("AI", model, 0.01))
    else:
        players.append(randomPlayer.randomPlayer("AI"))
            
    players.append(enemyPlayer2)
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
        print("****** MCTS *******")
    elif playerAI == 1:
        print("** Grab And Duck **")
    elif playerAI == 2:
        print("**** Rollouts *****")
    elif playerAI == 3:
        print("**** Random G&D ***")
    elif playerAI == 4:
        print("******* ML ********")
    elif playerAI == 5:
        print("*** ML Rollouts ***")
    else:
        print("***** Random ******")

    # Decide enemyAI type
    if enemyAI == 0:
        print("vs: MCTS")
    elif enemyAI == 1:
        print("vs: Grab And Duck")
    elif enemyAI == 2:
        print("vs: Rollouts")
    elif enemyAI == 3:
        print("vs: Random G&D")
    elif enemyAI == 4:
        print("vs: ML")
    elif enemyAI == 5:
        print("vs: ML Rollouts")
    else:
        print("vs: Random")

    # Return results
    print("AI win rate: ", 100*(results/numGames),"% or",results,"over",numGames)
    print("Time: ", timeElapsed)
          
# Produce all reports for numGames
def playAll(numGames, model):
    for playerAI in range(0,6):
        for enemyAI in [1, 3, 4, 6]:
            playGames(numGames, playerAI, enemyAI, model)

# Set Seeds
numArgs = len(sys.argv[1:])
if numArgs != 0:
    random.seed(sys.argv[1])
else:
    random.seed("bababooey")
            
# Produce report
model = trainModel.recursiveTrain(0, True, 1000)
playGames(50, 5, 1, model)
# playAll(50, model)
# mlPlayer("Test")
# for i in range(0, 100):
#      playGame([3, 1, model])

