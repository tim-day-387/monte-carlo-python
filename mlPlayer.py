# File Imports
from player import player

# Class for mlPlayer
class mlPlayer(player):
    # Constructor
    def __init__(self, name):
        # Inherit
        super().__init__(name)

        # Train model
        mlPlayer.train()

    # Train the model using epochs
    def train():
        # Set filenames
        filename = "data.csv"

        # Create file
        fp = open(filename, 'w')
        fp.close()
        
    # Decide which card to play
    def playCard(self, trick, game):
        # Check if trick is empty
        if len(trick) != 0:
            # Figure out what was led and follow it if we can
            suit = trick[0][0]
            
            # Get the first occurence of a matching suit in our hand
            card_idx = next((i for i,c in enumerate(self.hand) if c[0]==suit), None)

            # Play the card, if it exists
            if card_idx != None:
                return self.hand.pop(card_idx)
            
        # If the trick is empty or if we can't follow suit, return anything
        return self.hand.pop()
