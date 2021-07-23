# General Imports
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

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
        self.model = mlPlayer.train()

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
        
    # Train the model using epochs
    def train():
        # Set filenames
        filename = "data.csv"

        # Create file
        fp = open(filename, 'w')
        fp.close()

        # Play initial games
        mlPlayer.playGames(grabAndDuckPlayer, 6000)

        # Load data
        dataset = read_csv("./data.csv", names=["Deck","Win","Card"])

        # Create validation dataset
        array = dataset.values                                  
        X = array[:,0:-1]                                       
        y = array[:,-1]                                         
        Xt, Xv, yt, yv = train_test_split(X, y, test_size = 0.20, random_state = 1)

        # Train model
        model = RandomForestClassifier(n_estimators = 100)
        model.fit(Xt, yt)

        return model
        
    # Decide which card to play
    def playCard(self, trick, game):
        # Check if trick is empty
        if len(trick) != 0:
            # Generate sample
            sample = [[hash(tuple(self.hand.copy())), True]]

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
            
            card_idx = 0
            for i in range(0, len(self.hand)):
                if((self.hand[i][0] == card[0]) & (self.hand[i][1] == card[1])):
                    card_idx = i
                    break

            if card_idx == 0:
                print("Not found!")
            else:
                print("Found!")
            return self.hand.pop(card_idx)
        
        # If the trick is empty or if we can't follow suit, return anything
        return self.hand.pop()
