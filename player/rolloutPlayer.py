# General Imports
import time
import math as m

# File Imports
from game import game
from game import timeAllocator
from player import player
from player import yieldPlayer

# Class for rolloutPlayer
class rolloutPlayer(player.player):
    # Constructor
    def __init__(self, name, TIME_GIVEN, timeAlloc = False):
        # Inherit
        super().__init__(name)

        # Do we use time allocator?
        if timeAlloc == False: 
            self.allocator = False  
        else:
            # priorityMul => how much more time given than "fair" in worst case
            self.allocator = timeAllocator(18,priorityMul=1.1)

        # Set remaining parameters
        self.TIME_GIVEN = TIME_GIVEN

    # Decide what card to play
    def playCard(self, trick, game):
        # Check if there are cards
        if len(self.hand) == 0: 
            raise Exception("My hand is empty, why are you asking for a card?")

        # Check if the allocator is being used
        if self.allocator == False:
            # Set a timer for one TIME GIVEN
            terminateBy=time.process_time()+self.TIME_GIVEN 
        else:
            # If hand is full reset our time allocator
            if len(self.hand)==18:
                self.allocator.reset()

            # Set start and end times
            startAt=time.process_time()
            terminateBy=startAt+18.0

        # Find what cards in the hand are legal    
        legalCards=[]

        # Which should we start with?
        tryThis=0

        # Loop until time has finished
        while time.process_time() < terminateBy:
            # Make copy of game
            temp = game.makeVirtualGameCopy(trick)

            # Get the game generator object.
            gameGen = temp[0]

            # Get rid of temp object
            del temp

            # If we don't know what cards are legal, find out
            if len(legalCards) == 0:
                # Get the first return from the game generator
                temp = next(gameGen)

                # Check if there is an error with the return
                if type(temp[2])==type(1): 
                    raise TypeError("Something is wrong with my first return!"+str(temp)) 

                # If one card, remove and return it
                if len(temp[2])==1: 
                    self.hand.remove(temp[2][0]) 
                    return temp[2][0]
                
                # Otherwise, format the legal card list.
                for card in temp[2]:
                    # Add card, record it has been tried zero times, has had advantage zero
                    legalCards.append([card,0,0]) 

                # Get rid of temp object
                del temp
                
                # Update how much time we're allowed.
                if self.allocator != False: 
                    # Set up the real terminate time
                    terminateBy = startAt+self.allocator.getAllowedTime(len(self.hand),
                                                                        len(legalCards))

                    # If we've run out of time, return first card
                    if time.process_time() > terminateBy: 
                        self.hand.remove(legalCards[0][0]) 
                        return legalCards[0][0]
                    
            else:
                # Get generator ready to accept the card.
                next(gameGen)

            # Legal Cards is full, try the card at tryThis, increment how many times it was tried
            output=gameGen.send(legalCards[tryThis][0])
            legalCards[tryThis][1]+=1
            
            # Play the hand out
            while time.process_time() < terminateBy:
                # Is the game over?
                if output[0] == True:
                    # Has someone won the game?
                    if output[1] == True:
                        # Did the player win?
                        if output[2]==1:
                            # Add to advantage
                            legalCards[tryThis][2]+=200 
                        else:
                            # Remove from advantage
                            legalCards[tryThis][2]-=200 

                        # End of game
                        break

                    # Otherwise, take our score, and subtract the larger of the other players.
                    adv = output[4] - max(output[3],output[5]) 

                    # Add it to the total advantage for this card.
                    legalCards[tryThis][2]+=adv

                    # End of game
                    break

                # Otherwise, play the first legal card in the hand of whoever's turn it is
                card=output[2][0] 
                
                # Send that card in and collect the new output.
                output = gameGen.send(card)

            # The hand has come to an end
            # Move to trying the next card in sequence, or back to the start.
            tryThis = (tryThis+1)%len(legalCards) 

        # We've collected as much data as we can in one second
        # Sort cards by advantage
        legalCards.sort(key=lambda entry: entry[2]/(entry[1]+1)) 
        
        # If using an allocator, update it with how much time was spent
        if self.allocator != False:
            self.allocator.removeSpent(time.process_time()-startAt)

        # Remove the card from hand
        self.hand.remove(legalCards[-1][0])

        # Return card at the end of the legal cards list, strip off how much it was tried
        return legalCards[-1][0] 

