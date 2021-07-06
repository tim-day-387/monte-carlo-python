# Imports
from player import player

# Class for randomPlayer
class randomPlayer(player):  # Inherit from Player
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick,game):
        # added the game itself, since the AI needs that, even if it isn't used here.
        # print("-", self.name+"("+str(self.score)+")(Z"+str(self.zombie_count)+")", "sees", trick)
        # comment out for quiet mode
        if len(trick) != 0:
            # Figure out what was led and follow it if we can
            suit = trick[0][0]
            # print(self.name, ":", suit, "was led")
            # Get the first occurence of a matching suit in our hand
            # This 'next' thing below is a "generator expression"
            card_idx = next((i for i,c in enumerate(self.hand) if c[0]==suit), None)
            if card_idx != None:
                return self.hand.pop(card_idx)
        # If the trick is empty or if we can't follow suit, return anything
        return self.hand.pop()
# block of helper keys for grab and duck
# each one places prefered cards at the end of the list,for pop.
