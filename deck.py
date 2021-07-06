# General Imports
import random

# Class for deck
class deck():
    def __init__(self,exceptFor=None):
        self.deck = []
        self.shuffle(exceptFor)
                
    def __str__(self):
        # Print the list without the brackets
        return str(self.deck).strip('[]')
    
    def shuffle(self,exceptFor=None): 
        self.deck = []
        if exceptFor is None:                 # if not given any exceptions
            skipCards=set()                   # make the set of cards to skip empty.
        else:
            skipCards=set(exceptFor)          # if it's not a set, make it one. 
        for suit in ['U','F','Z','T']:
            for i in range(15):
                card=(suit,i)                 # turn this into a card, to compare with the set.
                if card not in skipCards:     # if skipCards is empty, then don't skip anything.
                    self.deck.append(card)
        random.shuffle(self.deck)
        
    def getCard(self):
        return self.deck.pop()
