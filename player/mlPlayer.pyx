# General Imports
import cython

# File Imports
import player

# Class for mlPlayer
class mlPlayer(player.player):
    # Constructor
    def __init__(self, name, model):
        # Inherit
        super().__init__(name)

        # Create model
        self.model = model

    # Decide which card to play
    def playCard(self, trick, game):
        # Check if trick is empty
        if len(trick) != 0:
            results = [0]*len(self.hand)
            card_idx = None
            maxScore = 0

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
                        if(results[i] >= maxScore):
                            maxScore = results[i]
                            card_idx = i

                # Return best card, if we have one
                if(card_idx != None):
                    return self.hand.pop(card_idx)
                
        # If the trick is empty or if we can't follow suit, return anything
        return self.hand.pop()
