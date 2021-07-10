# General Imports
import time
import math as m

# File Imports
from game import game
from player import player
from yieldPlayer import yieldPlayer
from timeAllocator import timeAllocator

TIME_GIVEN=0.01 #makes it easier to change the time amount

# helper function to make an imaginary version of the game to play out.
# Creates with all the information the AI (player 2 in turn order) should know.
# Returns the random state and a generator to use for the AI to play with.
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

# Class for mctsPlayer
class mctsPlayer(player):
    def __init__(self, name,question6=False):
        super().__init__(name)
        if question6 == False: #if not using a time alocator
            self.allocator = False  #save that we're not using one
        else:
            self.allocator = timeAllocator(18,priorityMul=1.1) #priority mul says how much more time it should get than "fair" in worst case, so it muls over first moves more.
        self.explore=800 #the explore parameter, it's 800 since a win is +200, and a loss is -200, rather than a win being 1 and a loss being 0. Might be the wrong call.
        self.barfMode=False #do I go print out where the deepest node with 10 observations is, or keep quiet?
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
