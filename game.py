# General Imports
import random

# File Imports
from deck import deck
from yieldPlayer import yieldPlayer

# Class for game
class game:  # Main class
    def __init__(self, players,yieldMode=False,quietMode=True):
        self.deck = deck()
        self.players = players
        self.played_cards = []  # List of already played cards in this hand
        self.yieldM=yieldMode   # Should I yield? Only use with "yieldPlayers"
        self.quiet=quietMode    # setting this to true makes it not print anything.
        self.HAND_SIZE = 18
        self.ZOMBIE_ARMY = 12
        self.ZOMBIE_ARMY_PENALTY = 20
        self.WIN_SCORE = 200
        
    # Helper function to make an imaginary version of the game
    def makeVirtualGameCopy(self, thisTrick):
        # Make virtual players
        virPlayers = [yieldPlayer("alice"), yieldPlayer("me"), yieldPlayer("bob")]
        
        # Get the scores and zombie_count
        for i in range(3):
            virPlayers[i].score = self.players[i].score
            virPlayers[i].zombie_count = self.players[i].zombie_count
            
        # Get hand and played cards 
        myHand = self.players[1].hand
        playedCards = self.played_cards

        # Make new game, deal cards
        newGame = game(virPlayers, yieldMode = True, quietMode = True)
        newGame.dealSpecial(myHand, playedCards, thisTrick)

        # Save alice and bob's starting hands
        aliceHand = frozenset(newGame.players[0].hand)
        bobHand = frozenset(newGame.players[2].hand)

        # Figure out the leader (currentTrick empty => we lead, two cards => bob leads)
        lead = (4-len(thisTrick))%3
        
        # Create generator
        gen = newGame.playHand(leader = lead, trick = thisTrick.copy()) 
        return (gen,aliceHand,bobHand)
    
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
