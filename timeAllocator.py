# Class for timeAllocator
class timeAllocator:
    # Constructor
    def __init__(self, initialTime, priorityMul = 1.0):
        self.iniTime = initialTime
        self.curTime = initialTime
        self.prio = priorityMul

    # Reset the given time
    def reset(self):
        self.curTime = self.iniTime

    # How much time should I be allowed?
    def getAllowedTime(self, handSize, legalSize):
        # If there's only 2 cards in hand, just give all the hand.
        if handSize == 2: 
            return self.curTime

        # If we have no time left, return nothing
        if self.curTime <= 0.0 : 
            return 0
        
        # Otherwise, compute the ratio (how much time this get v. how many left in worst case?) 
        ratio = (handSize*legalSize)/(handSize*(legalSize+(handSize-1)*(2*handSize-1)/6)-1) 

        # If we'd give almost all the time, ignore priority
        if ratio*self.prio >= 0.99: 
            pass 
        else:
            ratio*=self.prio

        # Return the remaining time
        return self.curTime*ratio

    # Remove the spent time
    def removeSpent(self,spentTime):
        self.curTime-=spentTime
