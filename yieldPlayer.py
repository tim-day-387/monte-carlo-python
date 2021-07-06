# Imports
from player import player

# Class of yieldPlayer
class yieldPlayer(player):
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick,game): # added game itself, the AI needs that, even if isn't used here.
        if len(trick) != 0:
            # Figure out what was led and follow it if we can
            suit = trick[0][0]
            # get a list of all valid cards
            legalCards=[]
            for card in self.hand:
                if card[0]==suit:
                    legalCards.append(card)
            # if it has anything, reveal only the legal cards.
            if len(legalCards)>0:
                return legalCards
        # If the trick is empty or if we can't follow suit, reveal hand
        return self.hand

    # special function only used by this class.
    def removeCard(self,card):
        if card not in self.hand:
            print("Err!",card,"not in",self.hand)
        self.hand.remove(card) # there should be only 1
