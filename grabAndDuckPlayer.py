# File Imports
from player import player

# Static Method
def trollKey(card):
    if card[0]=="T": # is this a troll?
        ret=1500 # ensures legal moves triumph if possible
        if card[1]>0: # ensures that ones that beat rank above those that don't
            ret+=100
        ret-=card[1] # prioritizes lowest possible
    elif card[0]=="Z":
        ret=1000+card[1]
    elif card[0]=="F":
        ret=500-card[1]
    else:
        ret=-card[1]
    return ret

# Static Method
def zombieKey(card):
    if card[0]=="Z":
        ret=1500 # ensures legal moves triumph if possible
        if card[1]<0: # ensures that ones that lose rank above those that don't
            ret+=100
        ret+=card[1] # prioritizes highest possible
    elif card[0]=="T":
        ret=1000-card[1]
    elif card[0]=="F":
        ret=500-card[1]
    else:
        ret=-card[1]
    return ret

# Static Method
def fairyKey(card):
    if card[0]=="F":
        ret=1500 # ensures legal moves triumph if possible
        if card[1]>0: # ensures that ones that beat rank above those that don't
            ret+=100
        ret-=card[1] # prioritizes lowest possible
    elif card[0]=="Z":
        ret=1000+card[1]
    elif card[0]=="T":
        ret=500-card[1]
    else:
        ret=-card[1]
    return ret

# Static Method
def unicornKey(card):
    if card[0]=="U":
        ret=1500 # ensures legal moves triumph if possible
        if card[1]>0: # ensures that ones that beat rank above those that don't
            ret+=100
        ret-=card[1] # prioritizes lowest possible
    elif card[0]=="T":
        ret=1000-card[1]
    elif card[0]=="Z":
        ret=500+card[1]
    else:
        ret=-card[1]
    return ret

# Class for grabAndDuckPlayer
class grabAndDuckPlayer(player):
    def __init__(self, name):
        super().__init__(name)
        
    def playCard(self, trick,game):
        # added the game itself, since the AI needs that, even if it isn't used here.
        if len(trick) != 0:
            # first, if we don't have a choice, just play it.
            if len(self.hand)==1:
                return self.hand.pop()
            # Figure out what was led
            suit = trick[0][0]
            # Next, determine the "threshold to win"
            threshold=trick[0][1]
            if len(trick)==2 and trick[1][0]==suit and trick[1][1]>threshold:
                # order is important here, 
                # the trick must have 2 entries to look at the second one.
                threshold=trick[1][1]
                # if that's the case, then the second player will win, so consider their
                # card instead
                # make a "psudo hand" with the threshold subtracted from each card.
                # this makes highest that loses -1,
                # and lowest that loses 1. These help with the key functions.
            pHand=[]
            for card in self.hand:
                pHand.append((card[0],card[1]-threshold))
                # now, sort our psudo hand based on the threshold and the suit played.
            if suit=="T":
                pHand.sort(key=trollKey)
            elif suit=="Z":
                pHand.sort(key=zombieKey)
            elif suit=="F":
                pHand.sort(key=fairyKey)
            else:
                pHand.sort(key=unicornKey)
                # now that it's sorted, we  it, then convert to normal card
            pCard=pHand.pop()
            card=(pCard[0],pCard[1]+threshold)
            # finally, remove the card and return it.
            self.hand.remove(card)
            return card
        else: # how to start the trick
            lowestTroll= 30 # this is an error value. If the "lowest troll" is 30, then I have none.
            lowestZombie= 30 # same idea for each of these
            highestFairy=-30
            highestUnicorn=-30
            # figure out each kind of card.
            for card in self.hand:
                if card[0]=="T": # if it's a troll
                    if card[1] < lowestTroll:
                        lowestTroll=card[1]
                elif card[0]=="Z": # if a zombie
                    if card[1] < lowestZombie:
                        lowestZombie=card[1]
                elif card[0]=="F":
                    if card[1] > highestFairy:
                        highestFairy=card[1]
                else:
                    if card[1] > highestUnicorn:
                        highestUnicorn=card[1]
                        # now, see if you have a troll, zombie, fairy, or only unicorns, in that order
            if lowestTroll < 30:
                card=("T",lowestTroll)
                self.hand.remove(card) # should never fail, since lowestTroll is not 30
                return card
            # next, zombies
            if lowestZombie < 30:
                card=("Z",lowestZombie)
                self.hand.remove(card) # should never fail, since lowestZombie is not 30
                return card
            # then fairies
            if highestFairy > -30:
                card=("F",highestFairy)
                self.hand.remove(card) # should never fail, since highestFairy is not -30
                return card
            # if we haven't returned by now, the hand must be all unicorns.
            card=("U",highestUnicorn)
            self.hand.remove(card)
            return card
