# General Imports
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import random

# File Imports
from player import *
from game import game

# Class for trainModel
class trainModel():
    # Play a set number of games and record the results
    @staticmethod
    def playInitial(numGames):
        # Create the games and play them, while writing results to csv
        for n in range(0,numGames):
            players = []
            players.append(grabAndDuckPlayer.grabAndDuckPlayer("Foo"))
            players.append(grabAndDuckPlayer.grabAndDuckPlayer("AI"))        
            players.append(grabAndDuckPlayer.grabAndDuckPlayer("Bar"))
            theGame = game.game(players)
            theGame.play(True)
            
    # Train the model using epochs
    @staticmethod
    def recursiveTrain(numEpochs, verbose, size):
        # Set filenames
        filename = "./data.csv"

        # Create file
        fp = open(filename, 'w')
        fp.close()

        # Initial epoch
        model = trainModel.train(verbose, size)

        # Return completed model
        return model
    
    # Train the model
    @staticmethod
    def train(verbose, size):
        # Play games
        trainModel.playInitial(size)

        # Load data
        dataset = read_csv("./data.csv", header=None)

        # Create validation dataset
        array = dataset.values                                  
        X = array[:,0:-1]
        y = array[:,-1]                                         
        Xt, Xv, yt, yv = train_test_split(X, y, test_size = 0.20, random_state = 1)

        # Train model
        model = RandomForestClassifier(n_estimators = 10)
        model.fit(Xt, yt)

        # Validate
        if(verbose):
            val_pred = model.predict(Xv)
            print("Model accuracy:")
            print(accuracy_score(yv, val_pred)) 

        return model


