# General Imports
import time
import math as m

# File Imports
from game import game
from player import player
from yieldPlayer import yieldPlayer
from timeAllocator import timeAllocator

TIME_GIVEN=1.0 #makes it easier to change the time amount

# Class for rolloutPlayer
class rolloutPlayer(player):
    def __init__(self, name,question6=False):
        super().__init__(name)
        if question6 == False: #if not using a time alocator
            self.allocator = False  #save that we're not using one
        else:
            self.allocator = timeAllocator(18,priorityMul=1.1) #priority mul says how much more time it should get than "fair" in worst case, so it muls over first moves more.

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

    # helper function to make an imaginary version of the game to play out.
    # Creates with all the information the AI (player 2 in turn order) should know.
    # Returns the random state and a generator to use for the AI to play with.
    @staticmethod
    def makeVirtualGameCopy(currGame,thisTrick):
        # make a virtual game with 3 players with set names (to aid in debug)
        alice=yieldPlayer("alice")
        me =yieldPlayer("me")
        bob =yieldPlayer("bob")
        virPlayers=[alice,me,bob]
        # make the scores and zombie_count match
        for i in range(3):
            virPlayers[i].score=currGame.players[i].score
            virPlayers[i].zombie_count=currGame.players[i].zombie_count
            # get my hand and played cards 
        myHand=currGame.players[1].hand
        playedCards=currGame.played_cards
        # now, make the game.
        newGame=game(virPlayers,yieldMode=True,quietMode=True)
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
