# General Imports
import time
import math as m

# File Imports
from game import game
from player import player
from player import yieldPlayer
from timeAllocator import timeAllocator

# Class for mctsPlayer
class mctsPlayer(player.player):
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
        self.explore = 800 
        self.barfMode = False
        self.TIME_GIVEN = TIME_GIVEN
        
    # Perform a calculation
    def ucb(self, totalScore, parentSimulations, thisSimulation):
        mean = totalScore/thisSimulation
        return mean+self.explore*m.sqrt(m.log(parentSimulations)/thisSimulation)

    # Makes the list of cards into a list of tuples of the trick after you play it
    def joinToTrick(self, optionsList, currentTrick): 
        ret = []
        for card in optionsList:
            trickCopy = currentTrick.copy()
            trickCopy.append(card)
            ret.append(tuple(trickCopy))
        return ret

    # Takes the list of options, the tree from that point on (if it exists)
    # returns the trick after us (and adds to the tree)
    def chooseCard(self, optionList, currentTrick, remainingTree, parentSim): 
        # Use to see if it is on the tree, and if not, how
        options = self.joinToTrick(optionList, currentTrick) 

        # If there's only one option, add to tree and return, otherwise, make a choice
        if len(options) == 1: 
            choice = 0
        else: 
            choice = -1

            # See if there's an unexplored option
            for i in range(len(options)):
                # If it's not in the tree, it's new
                if options[i] not in remainingTree: 
                    choice = i
                    break
                
            # If didn't update our choice, all of the choices have been expanded at least once
            if choice == -1:
                # Set best we've seen to negative infinity, it'll update at least once.
                bestUCB = -m.inf

                # Try all options
                for i in range(len(options)):
                    # Save remaining tree of option
                    temp = remainingTree[options[i]]

                    # Compute the ucb for this option
                    thisUCB = self.ucb(temp[1],parentSim,temp[0])

                    # Is this better than the last one we saw?
                    if thisUCB > bestUCB: 
                        bestUCB = thisUCB
                        choice = i
                        
        # Save what the trick looks like 
        futureTrick = options[choice] 

        # Check if we've done this before
        if futureTrick in remainingTree:
            # Add 1 to the number of times we've been here
            remainingTree[futureTrick][0] += 1
        else:
            # Add it to remainingTree, otherwise
            remainingTree[futureTrick] = [1,0,{}]

        # To get the actual card, we get the -1 element
        return futureTrick 

    # Recursive method that finds where the deepest the tree is
    def treeSeek(self, tree, threshold = 10):
        # If there's no deeper nodes, then it can at best be the level above
        if len(tree) == 0: 
            return -1

        # Assume this tree has no observations of more than threshold.
        deepest = -1

        # Check every leaf in tree
        for leaf in tree:
            # If there aren't threshold observations of this node, there can't be less
            if tree[leaf][0] < threshold: 
                continue

            # The last entry is the subtree from here
            # If that one is -1, then this was the last with above, so 0 depth
            fromThisLeaf = 1 + self.treeSeek(tree[leaf][-1],threshold)

            # Get new deepest leaf
            if fromThisLeaf > deepest:
                deepest = fromThisLeaf
        
        return deepest

    # Adds result to the advantage from the root down the tree.
    def treeUpdate(self, tree, result, path):
        # Don't edit actual tree
        myTree = tree 

        # Cycle through each entry in path
        for entry in path:
            # Add this result to the total
            myTree[entry][1] += result

            # Move a layer deeper in the tree
            myTree = myTree.get(entry,[1,0,{}])[2] 

    # Decide what card to play
    def playCard(self, trick, game): 

        # If we have only one card, play it
        if len(self.hand) == 1:
            return self.hand.pop()

        # Check if using allocator
        if self.allocator == False:
            # Set a timer for one TIME GIVEN
            terminateBy = time.process_time()+self.TIME_GIVEN
        else:
            # If hand is full reset our time allocator
            if len(self.hand) == 18: 
                self.allocator.reset()

            # Set start and end times
            startAt = time.process_time()
            terminateBy = startAt+18.0 

        # Dictonary that stores each playable card as a key, with values:
        # the total number of simulations of this node, then the "advantage" as calculated
        # last time, then a dict with the move information as keys, and same structure inside
        # The first "move" is the shuffle of Alice and Bob's hands,
        # but after that, all the moves are the state of the trick right after you play a card.
        # NOTE: The first level of the tree are tuples as well, just with 1 element.
        tree = {} 

        # How many times have you simulated the root of the tree?
        rootSimulations = 0

        # Loop until time has finished.
        while time.process_time() < terminateBy: 
            # Save all moves, start new sim, save tree
            moves = []
            rootSimulations += 1
            myTree = tree 
            
            # Get the game generator object, save Alice and bob's hands, get rid of temporary object
            temp = game.makeVirtualGameCopy(trick)
            gameGen = temp[0] 
            move1 = (temp[1],temp[2]) 
            del temp
            
            # Get the initial list of cards.
            output = next(gameGen) 
            initial = output[2]

            # Check for first round
            if len(tree) == 0:
                # Check if there's only one legal card, and play it
                if len(initial) == 1: 
                    self.hand.remove(initial[0]) 
                    return initial[0]

                # Update our terminateBy with more information
                if self.allocator != False:
                    # Calculate terminateBy
                    terminateBy = startAt+self.allocator.getAllowedTime(len(self.hand),len(initial))

                    # If we ran out of time, return the first card
                    if time.process_time() > terminateBy: 
                        self.hand.remove(initial[0]) 
                        return initial[0]
                    
            # Make first move, save in tree + moves list
            move0 = self.chooseCard(initial,[],myTree,rootSimulations) 
            moves.append(move0)

            # Move down the tree, set "output" to what happens after card
            myTree = myTree[move0][2] 
            output = gameGen.send(move0[0])
            
            # Add the "move1" to myTree, the moves list, and update myTree
            moves.append(move1) 

            # Check if move is in tree
            if move1 in myTree:
                # Add 1 to the number of times we've seen this
                myTree[move1][0] += 1

                # Save how many times we've seen this shuffle
                parentSimulation = myTree[move1][0]

                # Save what we've done before in this shuffle
                myTree = myTree[move1][2] 
            else:
                # Otherwise, we're in a new place.
                myTree[move1] = [1,0,{}]

                # Only simulated this once
                parentSimulation = 1 

                # Go into that dictonary we made.
                myTree = myTree[move1][2]

            # Play the hand out
            while time.process_time() < terminateBy:
                # Is the game over?
                if output[0] == True:
                    # Has someone won the game?
                    if output[1] == True:
                        # Did we win?
                        if output[2] == 1:
                            # Add points to advantage
                            adv = 200 
                        else:
                            # Remove to advantage
                            adv = -200 
                    else:
                        # Otherwise, take our score, and subtract the larger of the other players
                        adv = output[4] - max(output[3], output[5])
                        
                    # Add it to the total advantage for the chain
                    self.treeUpdate(tree, adv, moves)

                    # Hand is over
                    break
                
                # Otherwise, play a card
                # Is it one of our cards?
                if output[1] == 1: 
                    # Use choose card to get our move (the result of the trick after we play)
                    moveN = self.chooseCard(output[2],output[3],myTree,parentSimulation)
                    parentSimulation = myTree[moveN][0] 
                    myTree = myTree[moveN][2] 
                    moves.append(moveN)

                    # The card we play is at the end of the trick after us, so get that
                    card = moveN[-1] 
                else:
                    # Othewise, just play the first legal card in that player's hand.
                    card = output[2][0]
                    
                # Send that card in and collect the new output.
                output = gameGen.send(card)
            
        
        # Find the most seen card
        mostSeenAmount = 0
        endCard = None
        for card in iter(tree): 
            if tree[card][0] > mostSeenAmount: 
                mostSeenAmount = tree[card][0]
                endCard = card[0]
                
        # If using allocator, update it with how much time was spent
        if self.allocator != False:
            self.allocator.removeSpent(time.process_time()-startAt)
            
        # If we need to tell about how deep we got, do it now
        if self.barfMode == True:
            # Print hand size and depth
            print("hand size:",len(self.hand),"deepest with at least 10 simulations,", end=" ")

            # Decide what to print based on number of rootSimulations
            if rootSimulations < 10:
                print("none, only",rootSimulations,"total. Level -2")
            else:
                print("level:", self.treeSeek(tree)-1) 
                
        # Remove that card from our hand.
        self.hand.remove(endCard)

        # Return card decided upon 
        return endCard
