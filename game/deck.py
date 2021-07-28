# General Imports
import random

# Class for deck
class deck():
    # Constructor
    def __init__(self,exceptFor=None):
        # Create deck
        self.deck = []

        # Populate
        self.newDeck()
        
        # Shuffle deck
        self.shuffle(exceptFor)

    # Print the list without the brackets
    def __str__(self):
        return str(self.deck).strip('[]')

    # Shuffle the deck - minus excluded cards
    def shuffle(self,exceptFor=None):
        # Create a new deck
        self.newDeck();
        
        # Check if cards should be exclude
        if exceptFor is None:
            random.shuffle(self.deck)
        else:
            skipCards=set(exceptFor)

            # Exclude cards
            self.deck = list(set(self.deck).difference(skipCards))

            # Shuffle cards
            random.shuffle(self.deck)
            
        return

    # Reset deck
    def newDeck(self):
        # Create deck
        self.deck = []

        # Populate
        for suit in ['U','F','Z','T']:
            for i in range(15):
                card=(suit,i)  
                self.deck.append(card)

    # Take a card from the deck
    def getCard(self):
        return self.deck.pop()
