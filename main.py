# General Imports
import random
import abc
import time
import sys
import math as m
from tabulate import tabulate
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
    
    # Return results
    return (100*(results/numGames), timeElapsed)
          
# Produce all reports for numGames
def playAll(numGames, model):
    # Define headers
    headers = ["Enemy", "MCTS", "Grab & Duck", "Rollouts", \
               "Random G&D", "ML", "ML Rollouts", "Random"]

    # Define Metrics
    totalTime = 0; 

    # Define list
    data = [[None]*8,[None]*8,[None]*8,[None]*8]
    data[0][0] = "Grab & Duck"
    data[1][0] = "Random G&D"
    data[2][0] = "ML"
    data[3][0] = "Random"
    
    # Play all games
    for playerAI in range(0,7):
        for enemyAI in [1, 3, 4, 6]:
            # Get results from game
            results = playGames(numGames, playerAI, enemyAI, model)

            # Get row
            if enemyAI == 1:
                row = 0
            elif enemyAI == 3:
                row = 1
            elif enemyAI == 4:
                row = 2
            elif enemyAI == 6:
                row = 3

            # Input data
            data[row][playerAI+1] = results[0]
            totalTime = totalTime + results[1]

    # Show table and results
    print(tabulate(data, headers))
    print("")
    print("Total time:")
    print(totalTime)
            
# Set Seeds
numArgs = len(sys.argv[1:])
if numArgs != 0:
    random.seed(sys.argv[1])
else:
    random.seed("bababooey")
            
# Produce report
#model =  trainModel.recursiveTrain(0, True, 1000)
#playAll(50, model)
# mlPlayer("Test")
# for i in range(0, 1000):
#      playGame([1, 1, None])
# print(playGames(1000000, 1, 1, None))

# model = trainModel.recursiveTrain(0, True, 1000, None)

# for i in range(0,100):
#     print(playGames(30, 4, 10, model))
#     model = trainModel.recursiveTrain(0, True, 100, model)
