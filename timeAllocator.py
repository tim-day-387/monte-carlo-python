# Class for timeAllocator
class timeAllocator:
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
