# General Imports
import random
import csv

# File Imports
from deck import deck
from yieldPlayer import yieldPlayer

# Class for game
class game:
    def __init__(self, players, yieldMode = False, quietMode = True):
        self.deck = deck()
        self.players = players
        self.played_cards = []  
        self.yieldM = yieldMode   
        self.quiet = quietMode
        self.cardsPlayed = 0
        self.trickData = []
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

    # Deal cards to the players in the game
    def deal(self):
        # Shuffle cards and reset played cards
        self.deck.shuffle()
        self.played_cards = []

        # Take cards from shuffled deck and give them to players
        for i in range(self.HAND_SIZE):
            for p in self.players:
                p.hand.append(self.deck.getCard())

    # Sleepy print helper function, prints if quiet mode is off, does nothing if on
    def slp(self,*args,**kwargs): 
        if self.quiet:
            return
        else:
            print(*args,**kwargs)

    # Deals out virtual set of cards to players, player about to play gets the knownHand.
    # Assumes first player goes first this trick.
    def dealSpecial(self, knownHand, playedCards, currentTrick):
        # Shuffle deck without excluded cards
        exclude = set(knownHand) | set(playedCards) | set(currentTrick)
        self.deck.shuffle(exceptFor = exclude)
        
        # Number of cards in players' hands
        handSizes=[len(knownHand)]*3

        # If we are the second or third player, then the first player has one fewer card.
        if len(currentTrick) >= 1:
            handSizes[0] -= 1

        # If we are the third player, the second player has one fewer card as well.
        if len(currentTrick) == 2:
            handSizes[1] -= 1

        # Deal the hands.
        for playerIndex in range(3):
            # Check if this is the known hand
            if playerIndex == len(currentTrick):
                # Give the hand to player 2
                self.players[1].hand = knownHand.copy() 
                continue
            else:
                # Otherwise, populate hand for other player
                playerHand=[] 
                while len(playerHand) < handSizes[playerIndex]:
                    playerHand.append(self.deck.getCard())

                # Copy hand; the shift makes the leader of the current trick first
                self.players[(playerIndex-len(currentTrick)+4)%3].hand = playerHand.copy() 

    # Score the trick and add the score to the winning player
    def scoreTrick(self, trick):
        suit = trick[0][0]
        value = trick[0][1]
        winner = 0
        score = 0

        # Determine who won (trick position not player!)
        for i in range(len(trick)-1):
            if trick[i+1][0] == suit and trick[i+1][1] > value:
                # Determine the score
                winner = i+1
                value = trick[i+1][1]

        # Separate the suit and value tuples
        suits_list = list(zip(*trick))[0]

        # If no trolls, score unicorns
        if suits_list.count('T') == 0:    
            score += suits_list.count('U') * 3

        # Score faires
        score += suits_list.count('F') * 2

        # Remove score from Zombies
        n_zomb = suits_list.count('Z')
        score -= n_zomb
        
        return winner, score, n_zomb

    # Play a hand of the card game Monster (can start mid-trick)
    def playHand(self, leader = 0, trick = []):
        # While the next player to play can play, form trick, get card from players, score trick.
        while len(self.players[(leader+len(trick))%3].hand) > 0: 
            # Fixed the length of the trick
            startAt = len(trick)

            # Have each player play cards
            for i in range(startAt,len(self.players)):
                # for every loop after the first, this is the same as the old code
                p_idx = (leader + i) % len(self.players)

                # Check if in yieldMode
                if self.yieldM:
                    # If yes, get the legal cards
                    legalCards = self.players[p_idx].playCard(trick,self) 

                    # Yield to let game master choose card, using the information the player knows
                    chosenCard = yield (False, p_idx, legalCards, trick, self.played_cards)

                    # Remove chosen card
                    self.players[p_idx].removeCard(chosenCard)

                    # Append to trick
                    trick.append(chosenCard)
                else:
                    # If not using yield players, ping player directly (sends whole game over)
                    hand = self.players[p_idx].hand.copy()
                    card = self.players[p_idx].playCard(trick,self)
                    trick.append(card)

                    # Record hand and cards played
                    if p_idx == 2:
                        self.trickData.insert(self.cardsPlayed, [hand, card, -1])
                        self.cardsPlayed += 1

            # Show who lead the trick
            self.slp(self.players[leader].name, "led:", trick)

            # Get score of trick
            win_idx, score, n_zomb = self.scoreTrick(trick)

            # Convert winning trick index into new lead player index
            leader = (leader + win_idx) % len(self.players)

            # Show who won and by how much
            self.slp(self.players[leader].name, "won trick", score, "points")
            
            # Check for zombie army and apply the effects of the army
            self.players[leader].zombie_count += n_zomb
            if self.players[leader].zombie_count >= self.ZOMBIE_ARMY:
                # Remove the zombies from zombie count
                self.players[leader].zombie_count = -self.ZOMBIE_ARMY

                # Show that a zombie army happened
                self.slp("***** ZOMBIE ARMY *****")
                
                # Subtract 20 points from each opponent
                for i in range(len(self.players)-1):
                    self.players[(leader+1+i) % len(self.players)].score -= self.ZOMBIE_ARMY_PENALTY
                    
            # Update score & check if won
            self.players[leader].score += score
            if self.players[leader].score >= self.WIN_SCORE:
                # Show who won
                self.slp(self.players[leader].name, "won with", self.players[leader].score, "points")

                # Did someone win, if so who?
                yield (True, True, leader)
            
            # Keep track of the cards played, and clear trick
            self.played_cards.extend(trick)
            trick=[]
            
        # Show the deck
        self.slp(self.deck)

        # Score the kitty (undealt cards)
        win_idx, score, n_zomb = self.scoreTrick(self.deck.deck)

        # Show how many points the leader gets from the kitty
        self.slp(self.players[leader].name, "gets", score, "points from the kitty")

        # Adjust score accordingly
        self.players[leader].score += score
        
        # Check for zombie army
        if self.players[leader].zombie_count >= self.ZOMBIE_ARMY:
            # Show that a zombie army happened
            self.slp("***** ZOMBIE ARMY *****")
            
            # Subtract 20 points from each opponent
            for i in range(len(self.players)-1):
                self.players[(leader+1+i) % len(self.players)].score -= self.ZOMBIE_ARMY_PENALTY

        # Check for winner
        if self.players[leader].score >= self.WIN_SCORE:
            # Show the winner
            self.slp(self.players[leader].name, "won with", self.players[leader].score, "points!")

            # Yes, the hand ends, yes there's a winner, and it is leader
            yield (True, True, leader)
        else:
            # Otherwise, another hand is needed.
            yield (True, False, leader, self.players[0].score,
                   self.players[1].score, self.players[2].score)

    # Play a hand of the card game Monster (can start mid-trick, can't use yield players)
    def play(self, writeFeatures):
        lead_player = 0

        # Keep looping hands until we have winner
        while True:
            # Deal cards
            self.deal()

            # Make new generator each loop
            thisHand = self.playHand(leader=lead_player)

            # Get the result of hand from generator
            try: 
                result = next(thisHand)
            except StopIteration:
                print("Didn't stop successfully.")

            # If the hand had someone win, return who won, everyone's score.    
            if result[1] == True:
                # Find if the AI won
                if self.players[result[2]].name == "AI":
                    win = True
                else:
                    win = False

                # Population trick data
                for i in range(0, len(self.trickData)):
                    self.trickData[i][2] = win;

                # Writing to csv file
                filename = 'data.csv'
                with open(filename, 'a') as csvfile: 
                    csvwriter = csv.writer(csvfile) 
                    csvwriter.writerows(self.trickData)
                
                # Return information 
                return (self.players[result[2]].name, self.players[0].score,
                        self.players[1].score, self.players[2].score)
            else:
                # Otherwise, play more hands (and show this)
                self.slp("\n* Deal a new hand! *\n")

                # Reset the zombie count
                for p in self.players:
                    p.zombie_count = 0

                # Reset the played cards so they represet this hand
                self.played_cards=[]

                # Get leader of the last hand
                lead_player=result[2] 
