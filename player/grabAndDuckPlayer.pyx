# General Imports
import cython

# File Imports
import player

# Class for grabAndDuckPlayer
class grabAndDuckPlayer(player.player):
    # Constructor
    def __init__(self, name):
        super().__init__(name)
        
    # Determines card priority
    @staticmethod
    def trollKey(card):
        if card[0]=="T":
            # Ensures legal moves triumph if possible
            ret=1500

            # Ensures that ones that beat rank above those that don't
            if card[1]>0: 
                ret+=100

            # Prioritizes lowest possible
            ret-=card[1] 
        elif card[0]=="Z":
            ret=1000+card[1]
        elif card[0]=="F":
            ret=500-card[1]
        else:
            ret=-card[1]
        return ret

    # Determines card priority
    @staticmethod
    def zombieKey(card):
        if card[0]=="Z":
            # Ensures legal moves triumph if possible
            ret=1500

            # Ensures that ones that lose rank above those that don't
            if card[1]<0: 
                ret+=100

            # Prioritizes highest possible
            ret+=card[1] 
        elif card[0]=="T":
            ret=1000-card[1]
        elif card[0]=="F":
            ret=500-card[1]
        else:
            ret=-card[1]
        return ret

    # Determines card priority
    @staticmethod
    def fairyKey(card):
        if card[0]=="F":
            # Ensures legal moves triumph if possible
            ret=1500

            # Ensures that ones that beat rank above those that don't
            if card[1]>0: 
                ret+=100

            # Prioritizes lowest possible
            ret-=card[1] 
        elif card[0]=="Z":
            ret=1000+card[1]
        elif card[0]=="T":
            ret=500-card[1]
        else:
            ret=-card[1]
        return ret

    # Determines card priority
    @staticmethod
    def unicornKey(card):
        if card[0]=="U":
            # Ensures legal moves triumph if possible
            ret=1500

            # Ensures that ones that beat rank above those that don't
            if card[1]>0: 
                ret+=100

            # Prioritizes lowest possible
            ret-=card[1] 
        elif card[0]=="T":
            ret=1000-card[1]
        elif card[0]=="Z":
            ret=500+card[1]
        else:
            ret=-card[1]
        return ret

    # Decide what card to play
    def playCard(self, trick, game):
        # Check if starting trick
        if len(trick) != 0:
            # If one card, play it.
            if len(self.hand) == 1:
                return self.hand.pop()
            
            # Figure out what was led
            suit = trick[0][0]
            
            # Determine the "threshold to win"
            threshold = trick[0][1]

            # Check if trick is long enough, suit matches, and threshold is met
            if len(trick) == 2 and trick[1][0] == suit and trick[1][1] > threshold:
                # Second player will win, so consider their card instead
                threshold=trick[1][1]

            
            # Make a "psudo hand" with the threshold subtracted from each card
            pHand=[]
            for card in self.hand:
                pHand.append((card[0],card[1]-threshold))

            # Sort psudo hand based on the threshold and the suit played
            if suit=="T":
                pHand.sort(key = grabAndDuckPlayer.trollKey)
            elif suit=="Z":
                pHand.sort(key = grabAndDuckPlayer.zombieKey)
            elif suit=="F":
                pHand.sort(key = grabAndDuckPlayer.fairyKey)
            else:
                pHand.sort(key = grabAndDuckPlayer.unicornKey)
                
            # Get the top card and revert it to a normal card
            pCard = pHand.pop()
            card = (pCard[0],pCard[1]+threshold)

            # Remove the card and return it.
            self.hand.remove(card)
            return card
        else:
            # Set error values
            lowestTroll= 30 
            lowestZombie= 30 
            highestFairy=-30
            highestUnicorn=-30

            # Figure out lower kind of each card
            for card in self.hand:
                if card[0]=="T": 
                    if card[1] < lowestTroll:
                        lowestTroll=card[1]
                elif card[0]=="Z": 
                    if card[1] < lowestZombie:
                        lowestZombie=card[1]
                elif card[0]=="F":
                    if card[1] > highestFairy:
                        highestFairy=card[1]
                else:
                    if card[1] > highestUnicorn:
                        highestUnicorn=card[1]

            # Check if you have a troll, zombie, fairy, or only unicorns
            if lowestTroll < 30:
                card = ("T", lowestTroll)
                self.hand.remove(card) 
                return card
            elif lowestZombie < 30:
                card = ("Z", lowestZombie)
                self.hand.remove(card) 
                return card
            elif highestFairy > -30:
                card = ("F", highestFairy)
                self.hand.remove(card) 
                return card
            else:
                card = ("U", highestUnicorn)
                self.hand.remove(card)
                return card
