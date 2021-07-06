# Imports
import random
import abc
import time
import sys
import math as m #for MCTS
# from fractions import Fraction as fr #maybe it will be useful later.

TIME_GIVEN=1.0 #makes it easier to change the time amount
# How Arguments Work
# python3 Monster.py quiteMode AIplayerType seed
# quiteMode - 0 or 1
# AIplayerType - 0, 1, 2, 3, 4 for random, grab and duck, rollouts, MCTS, perform comparison on 20 games each
# vsType 0 or 1, 0 for opponents random, 1 for opnents doing grab and duck
# seed - any text, optional

# Right Number of Arguments
numArgs = len(sys.argv[1:])
if numArgs < 2:
    print("Wrong number of arguments.") #maybe make it so this lets you input it on run time instead of quitting? Would be useful for running in IDLE
    exit()

# AI selection
AIselection = sys.argv[2]
#enemy selection
vsType = sys.argv[3]
    
# Quite mode?
if sys.argv[1] == '1':
    qMode = True
else:
    qMode = False
    
# Set Seeds
if numArgs >= 4:
    seed=sys.argv[4]
else:
    seed=""

if seed=="":
    random.seed()
else:
    random.seed(seed)

class Deck():
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

class Player(metaclass=abc.ABCMeta):          # This is an abstract base class.
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

class YieldPlayer(Player):
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
        
class Game:  # Main class
    def __init__(self, players,yieldMode=False,quietMode=qMode):
        self.deck = Deck()
        self.players = players
        self.played_cards = []  # List of already played cards in this hand
        self.yieldM=yieldMode   # should I yield? Only use with "yieldPlayers", which are used for AI. Very important this is False otherwise
        self.quiet=quietMode    # setting this to true makes it not print anything.
        self.HAND_SIZE = 18
        self.ZOMBIE_ARMY = 12
        self.ZOMBIE_ARMY_PENALTY = 20
        self.WIN_SCORE = 200
        
    def slp(self,*args,**kwargs): # "sleepy print" helper function, acts exactly like print if quiet mode is off, does nothing if it is on.
        if self.quiet:
            return
        else:
            print(*args,**kwargs)
            
    def deal(self):
        self.deck.shuffle()
        self.played_cards = []
        for i in range(self.HAND_SIZE):
            for p in self.players:
                p.hand.append(self.deck.getCard())
    
    def dealSpecial(self,knownHand,playedCards,currentTrick):
        # deals out a virtual set of cards to players, except for the player about to play,
        # who gets the knownHand. Assumes first player goes first this trick.
        # Also allows dealing out mid trick
        exclude=set(knownHand) |set(playedCards)|set(currentTrick)
        # union all cards we know aren't in other players hands, or in the deck
        self.deck.shuffle(exceptFor=exclude)
        # shuffle a deck without cards we know shouldn't be there.
        
        # Now, make sure the hand sizes are known.
        handSizes=[len(knownHand)]*3
        # start with assuming that all players have the same hand size, will be fixed in next step.
        if len(currentTrick)>=1:
            # if we are the second or third player, then the first player has one fewer card.
            handSizes[0]-=1 # make the hand size for that player one smaller.
        if len(currentTrick)==2:
            # if we are the third player, then remove one from the second player as well.
            # If we're the first player, neither if statement happens
            handSizes[1]-=1
        # Deal the hands.
        for pIndex in range(3):
            if pIndex == len(currentTrick): # if this is our known hand,
                self.players[1].hand=knownHand.copy() #player 2 always gets it
                # then give that player the known hand and keep going.
                continue # we copy to make sure it doesn't mess with something it's not supposed to
            playerHand=[] # otherwise, get ready to fill a hand, then give it to them
            while len(playerHand) < handSizes[pIndex]:
                playerHand.append(self.deck.getCard())
            self.players[(pIndex-len(currentTrick)+4)%3].hand=playerHand.copy() # make it a copy just in case. The shift is so that it will deal the leader of the current trick first, always.

    def scoreTrick(self, trick):
        # Score the trick and add the score to the winning player
        # Get the suit led
        suit = trick[0][0]
        value = trick[0][1]
        winner = 0
        score = 0
        # Determine who won (trick position not player!)
        for i in range(len(trick)-1):
            if trick[i+1][0] == suit and trick[i+1][1] > value:
                winner = i+1
                value = trick[i+1][1]
        # Determine the score
        # Separate the suit and value tuples
        suits_list = list(zip(*trick))[0]
        if suits_list.count('T') == 0:
            # No Trolls, go ahead and score the unicorns
            score += suits_list.count('U') * 3
        score += suits_list.count('F') * 2
        n_zomb = suits_list.count('Z')
        score -= n_zomb
        return winner, score, n_zomb  # Index of winning card
    
    def playHand(self,leader=0,trick=[]):
        # splitting off the playing a hand code from the rest.
        # Trick is given here so starting mid trick is possible
        while len(self.players[(leader+len(trick))%3].hand) > 0: # while the next player to play can play
            # Form the trick, get a card from each player. Score the trick.
            startAt=len(trick) #make sure the fact the length of the trick changing is not the problem
            for i in range(startAt,len(self.players)):
                # for every loop after the first, this is the same as the old code
                p_idx = (leader + i) % len(self.players)
                if self.yieldM: # if in yield mode...
                    # first, get the legal cards
                    legalCards=self.players[p_idx].playCard(trick,self) 
                    # then yield to let the game master choose a card.
                    chosenCard = yield (False,p_idx,legalCards,trick,self.played_cards)
                    # this player would know these things, so use that to decide.
                    # it is not a terminal state, here's the player, the cards allowed to play,
                    # what's been played in this trick, and what in this hand.
                    self.players[p_idx].removeCard(chosenCard)
                    # make sure that this card is not in the hand for later
                    trick.append(chosenCard)
                else: # if not using yield players, just ask them directly
                    trick.append(self.players[p_idx].playCard(trick,self))
                    # yes, we send the whole game over
            self.slp(self.players[leader].name, "led:", trick)
            win_idx, score, n_zomb = self.scoreTrick(trick)

            # Convert winning trick index into new lead player index
            leader = (leader + win_idx) % len(self.players)
            self.slp(self.players[leader].name, "won trick", score, "points")
            

            # Check for zombie army
            self.players[leader].zombie_count += n_zomb
            if self.players[leader].zombie_count >= self.ZOMBIE_ARMY:
                # Uh-oh here comes the Zombie army!
                self.players[leader].zombie_count = -self.ZOMBIE_ARMY
                # make sure they can't do it again
                self.slp("***** ZOMBIE ARMY *****")
                # Subtract 20 points from each opponent
                for i in range(len(self.players)-1):
                    self.players[(leader+1+i) % len(self.players)].score -= self.ZOMBIE_ARMY_PENALTY
            
            # Update score & check if won
            self.players[leader].score += score
            if self.players[leader].score >= self.WIN_SCORE:
                self.slp(self.players[leader].name, "won with", self.players[leader].score, "points")
                yield (True,True,leader)
                # is this terminal,did someone win, if so who? is what this should be read as.
            
            # Keep track of the cards played
            self.played_cards.extend(trick)
            trick=[] # now clear the trick, for the next loop.
        
        # Score the kitty (undealt cards)
        self.slp(self.deck)
        win_idx, score, n_zomb = self.scoreTrick(self.deck.deck)
        self.slp(self.players[leader].name, "gets", score, "points from the kitty")
        self.players[leader].score += score
        # Check for zombie army
        if self.players[leader].zombie_count >= self.ZOMBIE_ARMY:
            self.slp("***** ZOMBIE ARMY *****")
            # Subtract 20 points from each opponent
            for i in range(len(self.players)-1):
                self.players[(leader+1+i) % len(self.players)].score -= self.ZOMBIE_ARMY_PENALTY
        # Check for winner
        if self.players[leader].score >= self.WIN_SCORE:
            self.slp(self.players[leader].name, "won with", self.players[leader].score, "points!")
            yield (True, True,leader) # yes, the hand ends, yes there's a winner, and it is leader
        else:
            # otherwise, another hand is needed.
            yield (True, False, leader,
                   # The hand is over, but a winner is not decided. Play next hand.
                   self.players[0].score,self.players[1].score,self.players[2].score)
            # return everyone's score.
            
    def play(self): # don't use if yield players are in play!
        lead_player = 0
        while True:  # Keep looping on hands until we have a winner
            self.deal()
            thisHand=self.playHand(leader=lead_player) #make  new generator each loop.
            try: # have to do it this way since its a generator now
                result=next(thisHand) 
            except StopIteration:
                print("Didn't stop successfully.")
            if result[1]==True: # if the hand had someone win,
                return (self.players[result[2]].name,self.players[0].score,self.players[1].score,self.players[2].score) #return who won, then everyone's score.
            # otherwise...
            self.slp("\n* Deal a new hand! *\n")
            # reset the zombie count
            for p in self.players:
                p.zombie_count = 0
            # reset the played cards so they represet this hand
            self.played_cards=[]
            lead_player=result[2] # get the leader of the last hand
            
class RandomPlayer(Player):  # Inherit from Player
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
    

class GrabAndDuckPlayer(Player):
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

# helper function to make an imaginary version of the game to play out.
# Creates with all the information the AI (player 2 in turn order) should know.
# Returns the random state and a generator to use for the AI to play with.
def makeVirtualGameCopy(currGame,thisTrick):
    # make a virtual game with 3 players with set names (to aid in debug)
    alice=YieldPlayer("alice")
    me =YieldPlayer("me")
    bob =YieldPlayer("bob")
    virPlayers=[alice,me,bob]
    # make the scores and zombie_count match
    for i in range(3):
        virPlayers[i].score=currGame.players[i].score
        virPlayers[i].zombie_count=currGame.players[i].zombie_count
    # get my hand and played cards 
    myHand=currGame.players[1].hand
    playedCards=currGame.played_cards
    # now, make the game.
    newGame=Game(virPlayers,yieldMode=True,quietMode=True)
    # deal the cards
    newGame.dealSpecial(myHand,playedCards,thisTrick)
    # Randomly deal the unknown cards, while keeping the known cards with me.
    #for i in range(3):
    #    print("player",i,"'s hand:",newGame.players[i].hand)
    # save alice and bob's starting hands
    aliceHand=frozenset(newGame.players[0].hand)
    bobHand=frozenset(newGame.players[2].hand)
    # figure out the leader
    lead=(4-len(thisTrick))%3
    # if the currentTrick is empty, we (1) are the leader. if there are two cards, bob must have lead.
    # create the generator
    gen = newGame.playHand(leader=lead,trick=thisTrick.copy()) # we copy the trick just in case
    return (gen,aliceHand,bobHand)

#For question 6, a time allocator as our (mandated) "extra credit"
class TimeAllocator:
    def __init__(self,initialTime,priorityMul=1.0):
        self.iniTime=initialTime
        self.curTime=initialTime
        self.prio=priorityMul
    def reset(self):
        self.curTime=self.iniTime
    def getAllowedTime(self,handSize,legalSize): #How much time should I be allowed? Legal Size is how many legal cards there are.
        if handSize==2: #if there's only 2 cards in hand, just give all the hand.
            return self.curTime
        if self.curTime <= 0.0 : #if we have no time left
            return 0
        #otherwise, we need to compute the ratio
        ratio=(handSize*legalSize)/(handSize*(legalSize+(handSize-1)*(2*handSize-1)/6)-1) #how much time should this get, vs how many are left, in the worst case? 
        #explanation in the writeup
        if ratio*self.prio >= 0.99: #if we'd give almost all the time
            pass #ignore the priority
        else:
            ratio*=self.prio #otherwise, apply it.
        return self.curTime*ratio
    def removeSpent(self,spentTime):
        self.curTime-=spentTime

class RolloutPlayer(Player):
    def __init__(self, name,question6=False):
        super().__init__(name)
        if question6 == False: #if not using a time alocator
            self.allocator = False  #save that we're not using one
        else:
            self.allocator = TimeAllocator(18,priorityMul=1.1) #priority mul says how much more time it should get than "fair" in worst case, so it muls over first moves more.

    def playCard(self, trick,game): # game is only used to make a virtual copy, does not hand look
        if len(self.hand)==0: #check if I'm being asked to play when I can't.
            raise Exception("My hand is empty, why are you asking for a card?")
        if self.allocator==False: #if we're not using the question 6 allocator,
            terminateBy=time.process_time()+TIME_GIVEN # set a timer for one TIME GIVEN
        else:
            if len(self.hand)==18: #if our hand is full
                self.allocator.reset() #reset our time allocator.
            startAt=time.process_time()
            terminateBy=startAt+18.0 #this is a temporary value, is corrected once we know how many cards are legal.
            
        legalCards=[] #on the first rollout, find what cards in the hand are legal, which are in lists of "number of times, total advantage"
        #if there is only one legal move, just play it and avoid computing. Advantage is me-first place, or if I am in first, me-second place. 
        #Set to +200 if I win on the hand, set to -200 if I lose on the hand, as winning or losing on the spot is way more important than next round.
        tryThis=0 #which index in the list should we start with this time?
        while time.process_time() < terminateBy: # loop until time has finished.
            temp = makeVirtualGameCopy(game,trick) #Note, this also returns the imagined hands of Alice and Bob, but we can get rid of those
            gameGen = temp[0] #Get the game generator object.
            del temp #get rid of temporary object. may remove if it causes problems
            if len(legalCards)==0: #if we don't know what cards are legal, find out.
                temp=next(gameGen) #get the first return from the game generator, which gives a lot more than just our hand
                if type(temp[2])==type(1): #if the next thing will throw an exception...
                    raise TypeError("Something is wrong with my first return!"+str(temp)) #this doesn't seem to happen, but it might
                if len(temp[2])==1: #if there's only one legal card, no point in doing anything else.
                    self.hand.remove(temp[2][0]) #make sure to actually remove the card.
                    return temp[2][0] #temp[2] is the legal card list, so get the only element and return
                #otherwise, format the legal card list.
                for card in temp[2]: #for each card...
                    legalCards.append([card,0,0]) #add the card, and that it has been tried zero times, and has had advantage of zero
                del temp
                
                #then, see if we need to update how much time we're allowed.
                if self.allocator!=False: #that is, we have an allocator
                    terminateBy=startAt+self.allocator.getAllowedTime(len(self.hand),len(legalCards)) #set up the real terminate time
                    if time.process_time() > terminateBy: #if we actually ran out of time, just return the first card.
                        self.hand.remove(legalCards[0][0]) #make sure we get the played card out of the hand
                        return legalCards[0][0]
                    
            else: #if we already know what cards are legal, just run the "next" without looking at the output.
                next(gameGen) #get it ready to accept the card.
            #Now that I know Legal Cards is full, we can try the card at index tryThis.
            output=gameGen.send(legalCards[tryThis][0]) #send card tryThis and collect the output.
            legalCards[tryThis][1]+=1 #increment how many times this was tried
            #then, play the hand out.
            while time.process_time() < terminateBy: #will break out if the hand is over before then.
                if output[0]==True: #if we are told the game is over...
                    if output[1]==True: #if someone won the game...
                        if output[2]==1: #is it us?
                            legalCards[tryThis][2]+=200 #if it is us, add 200 points to advantage!
                        else:
                            legalCards[tryThis][2]-=200 #If someone else won, we lost, so remove 200 points
                        #in either case, the game is over
                        break
                    #otherwise, we need to look at points scored.
                    adv=output[4] - max(output[3],output[5]) #take our score, and subtract the larger of the other players.
                    #then add it to the total advantage for this card.
                    legalCards[tryThis][2]+=adv
                    #finally, break.
                    break
                #otherwise, we're being asked to play a card.
                card=output[2][0] #This one picks the first legal card in the hand of whoever's turn it is. Mcts will have to care whose turn it is, but I don't.
                #also if you simulated everyone with grab and duck, they would need to know the trick from this output. but we don't have to.
                #finally, send that card in and collect the new output.
                output = gameGen.send(card)
            #now, the hand has come to an end.
            tryThis=(tryThis+1)%len(legalCards) #move to trying the next card in sequence, or back to the start.
        #okay, so we've collected as much data as we can in one second. Now comes decision time.
        legalCards.sort(key=lambda entry: entry[2]/entry[1]) #assume each one has been tried at least once, or this will set on fire.
        
        #if we are using an allocator, we need to update it with how much time was spent
        if self.allocator != False:
            self.allocator.removeSpent(time.process_time()-startAt)
        self.hand.remove(legalCards[-1][0]) #remove the card from hand
        return legalCards[-1][0] #return the card at the end of the legal cards list, and strip off how much it was tried.
                        

class MctsPlayer(Player):
    def __init__(self, name,question6=False):
        super().__init__(name)
        if question6 == False: #if not using a time alocator
            self.allocator = False  #save that we're not using one
        else:
            self.allocator = TimeAllocator(18,priorityMul=1.1) #priority mul says how much more time it should get than "fair" in worst case, so it muls over first moves more.
        self.explore=800 #the explore parameter, it's 800 since a win is +200, and a loss is -200, rather than a win being 1 and a loss being 0. Might be the wrong call.
        self.barfMode=True #do I go print out where the deepest node with 10 observations is, or keep quiet?
    #helpers
    def ucb(self,totalScore,parentSimulations,thisSimulation):
        mean=totalScore/thisSimulation
        return mean+self.explore*m.sqrt(m.log(parentSimulations)/thisSimulation)
    def joinToTrick(self,optionsList,currentTrick): #makes the list of cards into a list of tuples of the trick after you play it.
        ret=[]
        for card in optionsList:
            trickCopy=currentTrick.copy()
            trickCopy.append(card)
            ret.append(tuple(trickCopy))
        return ret
    
    def chooseCard(self,optionList,currentTrick,remainingTree,parentSim): 
        #Takes the list of options, the tree from that point on (if it exists), and returns the trick after us (and adds to the tree)
        options=self.joinToTrick(optionList,currentTrick) #this way, it can see if it is on the tree, and if not, how.
        if len(options)==1: #if there's only one option, skip all this and jump right to the adding to tree and returning.
            choice=0
        else: #otherwise, you have to actually make a choice.
            #first, try to see if there's an unexplored option
            choice=-1
            for i in range(len(options)):
                if options[i] not in remainingTree: #if it's not in the tree, then it's new.
                    choice=i
                    break
            if choice ==-1: #if we didn't update our choice, then it means all of the choices have been expanded at least once. Find which to do.
                bestUCB=-m.inf #set the best we've seen to negative infinity, so that it's guarenteed to update at least once.
                for i in range(len(options)):
                    temp=remainingTree[options[i]] #doesn't error because we already checked that all of these are in the keys
                    thisUCB=self.ucb(temp[1],parentSim,temp[0]) #compute the UCB for the option, getting its score, the parent simulations, then its simulations.
                    if thisUCB > bestUCB: #is this better than the last one we saw?
                        bestUCB=thisUCB
                        choice=i #save the choice the best UCB seen
        #Now, we have the choice index. 
        futureTrick=options[choice] #save what the trick looks like
        if futureTrick in remainingTree: #if we've done this before, add 1 to the number of times we've been here.
            remainingTree[futureTrick][0]+=1
        else: #otherwise, add it here. 
            remainingTree[futureTrick]=[1,0,{}] #the empty dictionary is so that we know we've not explored any children.
        return futureTrick #to get the actual card, we get the -1 element
    
    def treeSeek(self, tree,threshold=10): #recursive method that finds where the deepest the tree is.
        if len(tree)==0: #if there's no deeper nodes, then it can at best be the level above.
            return -1
        deepest=-1 #assume this tree has no observations of more than threshold.
        for leaf in tree:
            if tree[leaf][0] < threshold: #if there aren't threshold observations of this node, there can't be less
                continue
            #otherwise, look deeper.
            fromThisLeaf= 1+ self.treeSeek(tree[leaf][-1],threshold) #the last entry is the subtree from here. If that one is -1, then this was the last with above, so 0 depth.
            if fromThisLeaf > deepest:
                deepest=fromThisLeaf
        #Now we know the furthest it goes.
        return deepest
    
    def treeUpdate(self,tree,result,path): #adds result to the advantage from the root down the tree.
        myTree=tree #don't mess with the actual tree, just being careful.
        for entry in path:
            myTree[entry][1]+=result #add this result to the total
            myTree=myTree.get(entry,[1,0,{}])[2] #move a layer deeper in the tree. On last step, will still give something, so this doesn't error, hopefully.
            

    def playCard(self, trick,game): # game is only used to make a virtual copy, does not hand look
        #if we have only one card, we have to play it.
        if len(self.hand)==1:
            return self.hand.pop()
        if self.allocator==False: #if we're not using the question 6 allocator,
            terminateBy=time.process_time()+TIME_GIVEN # set a timer for one TIME GIVEN
        else:
            if len(self.hand)==18: #if our hand is full
                self.allocator.reset() #reset our time allocator.
            startAt=time.process_time()
            terminateBy=startAt+18.0 #this is a temporary value, is corrected once we know how many cards are legal.
            
        tree={} # dictonary that stores each playable card as a key, and as values: the total number of simulations of this node, then the "advantage" as calculated last time, 
        #then a dict with the move information as keys, and same structure inside. the first "move" is the shuffle of Alice and Bob's hands,
        #but after that, all the moves are the state of the trick right after you play a card.
        #NOTE: due to jank, the first level of the tree are tuples as well, just with 1 element.
        rootSimulations=0 #how many times have you simulated the root of the tree?
        while time.process_time() < terminateBy: # loop until time has finished.
            moves=[] #needed, to update the tree at the end of the hand.
            rootSimulations+=1 #we're starting a new simulation
            myTree=tree #this moves in one level at a time, as we go.
            temp = makeVirtualGameCopy(game,trick) #now we need to keep the imagined hands of alice and bob
            gameGen = temp[0] #Get the game generator object.
            move1=(temp[1],temp[2]) #save Alice and bob's hands.
            del temp #get rid of temporary object. may remove if it causes problems
            #get the initial list of cards.
            output=next(gameGen) #look at everything
            initial=output[2]
            #print(output) #what cards do you see?
            if len(tree)==0: #check for first round stuff
                if len(initial)==1: #if there's only one legal card...
                    self.hand.remove(initial[0]) #remember to remove from hand before playing
                    return initial[0] #play the first card in the hand (that's legal)
                if self.allocator!=False: #if we need to update our terminate by with more information...
                    terminateBy=startAt+self.allocator.getAllowedTime(len(self.hand),len(initial)) #set up the real terminate time
                    if time.process_time() > terminateBy: #if we actually ran out of time, just return the first card.
                        self.hand.remove(initial[0]) #remember to remove from hand before playing
                        return initial[0] #play the first card in the hand (that's legal)
            #now, make my first move.
            #make the move, and save it in the tree and and moves list. We also set "output" to whatever happens after that card.
            move0=self.chooseCard(initial,[],myTree,rootSimulations) #since this is the root, we add nothing to the cards. Also, adds the move to the tree for us
            moves.append(move0) #get the card itself, rather than it in a tuple, as it is different here than normal
            myTree=myTree[move0][2] #move down the tree
            output=gameGen.send(move0[0])#get the card itself, rather than it in a tuple, as it is different here than normal
            #now add the "move1" to myTree, the moves list, and update myTree.
            moves.append(move1) #save what their hands are.
            if move1 in myTree:
                myTree[move1][0]+=1 #add 1 to the number of times we've seen this
                parentSimulation= myTree[move1][0] #Save how many times we've seen this shuffle.
                myTree=myTree[move1][2] #we've seen this shuffle before! Let's see what we've done before!
            else: 
                myTree[move1]=[1,0,{}] #otherwise, we're in a new place.
                parentSimulation=1 #We've only simulated this once
                myTree=myTree[move1][2] #now we go into that dictonary we made.
            #then, play the hand out.
            while time.process_time() < terminateBy: #will break out if the hand is over before then.
                if output[0]==True: #if we are told the game is over...
                    if output[1]==True: #if someone won the game...
                        if output[2]==1: #is it us?
                            adv=200 #if it is us, add 200 points to advantage!
                        else:
                            adv=-200 #If someone else won, we lost, so remove 200 points
                    else: #do advantage computation
                        adv=output[4] - max(output[3],output[5]) #take our score, and subtract the larger of the other players.
                    #then add it to the total advantage for the chain
                    self.treeUpdate(tree,adv,moves)
                    #finally, break.
                    break
                #otherwise, we're being asked to play a card.
                if output[1]==1: #is it one of our cards?
                    #then we use choose card to get our move (which is the result of the trick after we play.
                    moveN=self.chooseCard(output[2],output[3],myTree,parentSimulation)
                    parentSimulation=myTree[moveN][0] # get how many times the parent is simulated before going inward.
                    myTree=myTree[moveN][2] #now our tree is a layer in.
                    moves.append(moveN) #add this move.
                    card=moveN[-1] #the card we play is at the end of the trick after us, so get that
                else:
                    card=output[2][0] #othewise, just play the first legal card in that player's hand.
                #finally, send that card in and collect the new output.
                output = gameGen.send(card)
            #now, the hand has come to an end. No clean up here
        #okay, so we've collected as much data as we can in one second. Now comes decision time.
        #remember, it's the most seen card, not the highest outcome card.
        mostSeenAmount=0
        endCard=None #if this is still none, something is wrong.
        for card in iter(tree): #go through each card in the first level of the dictionary
            if tree[card][0] > mostSeenAmount: #if this card has been seen the most times so far
                mostSeenAmount=tree[card][0]
                endCard=card[0] #save our most tested card.
        #if we are using an allocator, we need to update it with how much time was spent
        if self.allocator != False:
            self.allocator.removeSpent(time.process_time()-startAt)
        #now, if we're told to tell about how deep we got, do it now.
        if self.barfMode==True:
            print("hand size:",len(self.hand),"deepest with at least 10 simulations,", end=" ") #make it so it's on one line
            if rootSimulations < 10:
                print("none, only",rootSimulations,"total. Level -2")
            else:
                print("level:", self.treeSeek(tree)-1) #the depth level needs to be subtracted by 1 to make is to looking 0 tricks ahead is level 0
        #remove that card from our hand.
        #print(endCard,self.hand,tree.keys())
        self.hand.remove(endCard)
        return endCard#return the card we decided on

        
# Select kind of player up against, by defining "EnemyPlayer" to mean one of two classes
EnemyPlayer=RandomPlayer
if vsType == '0': 
    pass #no change here
elif vsType == '1':
    EnemyPlayer=GrabAndDuckPlayer
else:
    print("Bad player type! Must be 0 or 1")
    exit()
# Code for Playing Games
if AIselection == '5':
    Games=20 #only says to play 20 games, not 200

    MctsResults=0
    for i in range(Games):
        playahs = []
        playahs.append(EnemyPlayer("Foo"))
        playahs.append(MctsPlayer("AI"))
        playahs.append(EnemyPlayer("Bar"))
        theGame = Game(playahs)

        if theGame.play()[0] == "AI":
            MctsResults+=1

    GDResults=0
    for i in range(Games):
        playahs = []
        playahs.append(EnemyPlayer("Foo"))
        playahs.append(GrabAndDuckPlayer("AI"))
        playahs.append(EnemyPlayer("Bar"))
        theGame = Game(playahs)

        if theGame.play()[0] == "AI":
            GDResults+=1

    RResults=0
    for i in range(Games):
        playahs = []
        playahs.append(EnemyPlayer("Foo"))
        playahs.append(RolloutPlayer("AI"))
        playahs.append(EnemyPlayer("Bar"))
        theGame = Game(playahs)

        if theGame.play()[0] == "AI":
            RResults+=1
            
    print("MTCS AI win rate: ", 100*MctsResults/Games,"% or",MctsResults,"over",Games)
    print("Grab And Duck AI win rate: ", 100*GDResults/Games,"% or",GDResults,"over",Games)
    print("Rollout AI win rate: ", 100*RResults/Games,"% or",RResults,"over",Games)
else:
    playahs = []
    playahs.append(EnemyPlayer("Foo"))

    if AIselection == '0':
        playahs.append(RandomPlayer("AI"))
    elif AIselection == '1':
        playahs.append(GrabAndDuckPlayer("AI"))
    elif AIselection == '2':
        playahs.append(RolloutPlayer("AI"))
    else:
        playahs.append(MctsPlayer("AI"))
    
    playahs.append(EnemyPlayer("Bar")) 
    theGame = Game(playahs) #potentially make it play more than one?

    print(theGame.play())
