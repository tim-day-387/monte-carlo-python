# General Imports
import abc

# Class for player
class player(metaclass=abc.ABCMeta):
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 0
        self.zombie_count = 0

    # If __str__ is not defined this will be used. Allows easy printing of list of players    
    def __repr__(self):        
        return str(self.name) + ": " + str(self.hand) + "\n"

    # A player shows legal cards instead of playing one, only works if yieldMode is true
    @abc.abstractmethod
    def playCard(self):
        pass
    
