# General Imports
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import random

# File Imports
from player import player
from grabAndDuckPlayer import grabAndDuckPlayer
from game import game

# Class for mlPlayer
class mlPlayer(player):
    # Constructor
    def __init__(self, name):
        # Inherit
        super().__init__(name)

        # Create model
        self.model = mlPlayer.recursiveTrain(0)

    # Play a set number of games and record the results
    @staticmethod
    def playGames(playerType, numGames):
        # Create the games and play them, while writing results to csv
        for n in range(0,numGames):
            players = []
            players.append(grabAndDuckPlayer("Foo"))
            players.append(playerType("AI"))        
            players.append(grabAndDuckPlayer("Bar"))
            theGame = game(players)
            theGame.play(True)
            
    # Try to predict a card that is in the hand
    def metaPredict(self):
        card_idx = -1
        hand = self.hand.copy()
        
        for i in range(0, 10):
            # Generate sample
            sample = [[hash(tuple(hand)), True]]

            # Make prediction and convert to string
            cardString = self.model.predict(sample)[0]

            # Extract card from string
            if len(cardString) == 8:
                suit = cardString[2:3]
                num = int(cardString[6:7])
            else:
                suit = cardString[2:3]
                num = int(cardString[6:8])
                
            card = (suit, num)
        
            for i in range(0, len(hand)):
                if((hand[i][0] == card[0]) & (hand[i][1] == card[1])):
                    card_idx = i
                    break

            if(card_idx != -1):
                break
            else:
                random.shuffle(hand)
            
        if(card_idx == -1):
            card_idx = 0
            
        return card_idx
    
    # Train the model using epochs
    @staticmethod
    def recursiveTrain(numEpochs):
        # Set filenames
        filename = "data.csv"

        # Create file
        fp = open(filename, 'w')
        fp.close()

        # Initial epoch
        return mlPlayer.train(grabAndDuckPlayer)
    
    # Train the model
    @staticmethod
    def train(player):
        # Play games
        mlPlayer.playGames(player, 100)

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
        val_pred = model.predict(Xv)
        print("Model accuracy:")
        print(accuracy_score(yv, val_pred)) 

        return model
        
    # Decide which card to play
    def playCardAlt(self, trick, game):
        # Check if trick is empty
        if len(trick) != 0:
            card_idx = self.metaPredict()
            
            return self.hand.pop(card_idx)
        
        # If the trick is empty or if we can't follow suit, return anything
        return self.hand.pop()
    
    # Decide which card to play
    def playCard(self, trick, game):
        # Check if trick is empty
        if len(trick) != 0:
            results = [0]*len(self.hand);
            card_idx = None;

            # Get suit
            suit = trick[0][0]
            
            # Get the results for each card
            for i in range(0, len(self.hand)):
                # Generate sample
                cardTuple = self.hand[i]
                hand = self.hand.copy()
                played = game.played_cards.copy()
                sample = game.getFeatures(cardTuple, hand, played, False)
                           
                # Make prediction and convert to string
                results[i] = self.model.predict([sample])[0]

                # Find winning card of matching suit, or play any losing card
                for i in range(0, len(self.hand)):
                    if(self.hand[i][0] == suit):
                        card_idx = i
                        if(results[i] == 1):
                            return self.hand.pop(card_idx)
                
        # If the trick is empty or if we can't follow suit, return anything
        return self.hand.pop()
