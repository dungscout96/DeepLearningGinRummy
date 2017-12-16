import Gin_Rummy_Python.GinRummyPlayer as GinRummyPlayer
import Gin_Rummy_Python.GinRummyUtil as GinRummyUtil
from Gin_Rummy_Python.Card import Card
import copy
import random
class SimpleGinRummyPlayer():
    def __init__(self):
        self.playerNum = 0
        self.startingPlayerNum = 0
        self.cards = []
        self.opponentKnocked = False
        self.faceUpCard = Card()
        self.drawnCard = Card()
        self.drawDiscardBitstrings = []

    def startGame(self, playerNum, startingPlayerNum, cards):
        self.playerNum = playerNum
        self.startingPlayerNum = startingPlayerNum
        self.cards.clear()
        for card in cards:
            self.cards.append(card)
        self.opponentKnocked = False
        self.drawDiscardBitstrings.clear()


    # Moment of decision: draw a face up card?
    def willDrawFaceUpCard(self,card):
        self.faceUpCard = card
        newCards = copy.copy(self.cards)
        newCards.append(card)
        for meld in GinRummyUtil.cardsToAllMelds(newCards):
            if card in meld:
                return True
        return False


    def reportDraw(self,playerNum, drawnCard):
        if (playerNum == self.playerNum):
            self.cards.append(drawnCard)
            self.drawnCard = drawnCard

    def getDiscard(self):
        minDeadwood = 10000000000000000
        candidateCards = []
        for card in self.cards:
            if (card == self.drawnCard and self.drawnCard == self.faceUpCard):
                continue
            drawDiscard = []
            drawDiscard.append(self.drawnCard)
            drawDiscard.append(card)
            if (GinRummyUtil.cardsToBitstring(drawDiscard) in self.drawDiscardBitstrings):
                continue
            remainingCards = copy.copy(self.cards)
            remainingCards.remove(card)
            bestMeldSets = GinRummyUtil.cardsToBestMeldSets(remainingCards)
            deadwood = GinRummyUtil.getDeadwoodPoints(None, None, None, remainingCards) if not bestMeldSets else GinRummyUtil.getDeadwoodPoints(bestMeldSets[0], remainingCards, None, None)
            if (deadwood <= minDeadwood):
                if (deadwood < minDeadwood):
                    minDeadwood = deadwood
                    candidateCards.clear()
                candidateCards.append(card)

        discard = candidateCards[random.randrange(0, (len(candidateCards)))]
        drawDiscard = []
        drawDiscard.append(self.drawnCard)
        drawDiscard.append(discard)
        self.drawDiscardBitstrings.append(GinRummyUtil.cardsToBitstring(drawDiscard))
        return discard

    def reportDiscard(self, playerNum, discardedCard):
        if (playerNum == self.playerNum):
            self.cards.remove(discardedCard)

    def getFinalMelds(self):
        bestMeldSets = GinRummyUtil.cardsToBestMeldSets(self.cards)
        #if (!opponentKnocked && (bestMeldSets.isEmpty() || GinRummyUtil.getDeadwoodPoints(bestMeldSets.get(0), cards) > GinRummyUtil.MAX_DEADWOOD))
        if (not self.opponentKnocked) and ((not bestMeldSets) or (GinRummyUtil.getDeadwoodPoints(bestMeldSets[0], self.cards, None, None) > GinRummyUtil.MAX_DEADWOOD)):
            return None
        return [] if (not bestMeldSets) else bestMeldSets[random.randrange(0,len(bestMeldSets))]

    def reportFinalMelds(self, playerNum, melds):
        if (playerNum != self.playerNum):
            self.opponentKnocked = True

    def reportScores(self, scores):
        return
    def reportLayoff(self, playerNum, layoffCard, opponentMeld):
        return

    def reportFinalHand(self, playerNum, hand):
        return

'''
player = SimpleGinRummyPlayer()
cards = Card.allCards
for c in cards:
    print(player.willDrawFaceUpCard(c))
print('here')
player = SimpleGinRummyPlayer()
cards2 = [Card.getCard(2,1),Card.getCard(11,0),Card.getCard(2,3), Card.getCard(3,0), Card.getCard(10,0), Card.getCard(1,0), Card.getCard(12,0), Card.getCard(3,2), Card.getCard(1,2), Card.getCard(3,3)]
player.cards = cards2
print(player.cards)
print(GinRummyUtil.cardsToBestMeldSets(cards2))
print('another')
print(player.getFinalMelds())
print(GinRummyUtil.getDeadwoodPoints(GinRummyUtil.cardsToBestMeldSets(cards2)[0], cards2, None, None))
    '''
