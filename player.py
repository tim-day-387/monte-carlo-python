# Imports
import abc

# Class for player
class player(metaclass=abc.ABCMeta):          # This is an abstract base class.
    def __init__(self, name):
        self.name = name
        self.hand = []         # List of cards (tuples). I don't think this needs to be a class....
        self.score = 0
        self.zombie_count = 0
        
    def __repr__(self):        # If __str__ is not defined this will be used. Allows easy printing
        # of a list of these, e.g. "print(players)" below.
        return str(self.name) + ": " + str(self.hand) + "\n"
    
    @abc.abstractmethod
    def playCard(self):
        pass
# a player who shows legal cards instead of playing one.
# this only works if yieldMode is true
