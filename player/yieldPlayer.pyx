# General Imports
import cython

# File Imports
import player

# Class of yieldPlayer
class yieldPlayer(player.player):
    # Constructor
    def __init__(self, name):
        super().__init__(name)

    # Decide which cards can be played
    def playCard(self, trick, game): 
        # Check if trick is empty
        if len(trick) != 0:
            # Figure out what was led and follow it if we can
            suit = trick[0][0]

            # Create a list and populate it with all valid cards
            legalCards=[]
            for card in self.hand:
                if card[0] == suit:
                    legalCards.append(card)
                    
            # Reveal all legal cards, if they exist
            if len(legalCards)>0:
                return legalCards
        
        # If the trick is empty or if we can't follow suit, reveal hand
        return self.hand

    # Remove card from hand
    def removeCard(self, card):
        # Check if card in hard
        if card not in self.hand:
            # Show error
            print("Err!",card,"not in",self.hand)
        else:
            # Remove card from hand
            self.hand.remove(card)
