import sys
import random
import copy
import Gin_Rummy_Python.GinRummyUtil as GinRummyUtil
from Gin_Rummy_Python.Card import Card


class SimpleGinRummyPlayer2:
    playerNum = 0
    startingPlayerNum = 0
    cards = []
    # random = new Random()g
    opponentKnocked = False
    faceUpCard = Card()
    drawnCard = Card()
    drawDiscardBitstrings = []
    totalDiscarded = 0

    def startGame(self, playerNum, startingPlayerNum, cards):
        self.playerNum = playerNum
        self.startingPlayerNum = startingPlayerNum
        self.cards.clear()
        for card in cards:
            self.cards.append(card)
        self.opponentKnocked = False
        self.drawDiscardBitstrings.clear()
        self.totalDiscarded = 0

    def willDrawFaceUpCard(self, card):
        self.faceUpCard = card
        newCards = copy.deepcopy(self.cards)
        newCards.append(card)
        for meld in GinRummyUtil.cardsToAllMelds(newCards):
            if (card in meld):
                return True
        return False

    def reportDraw(self, playerNum, drawnCard):
        if (playerNum == self.playerNum):
            self.cards.append(drawnCard)
            self.drawnCard = drawnCard

    def getDiscard(self):
        minDeadwood = sys.maxsize
        candidateCards = []
        for card in self.cards:
            if (card == self.drawnCard and self.drawnCard == self.faceUpCard):
                continue
            drawDiscard = []
            drawDiscard.append(self.drawnCard)
            drawDiscard.append(card)
            if (GinRummyUtil.cardsToBitstring(drawDiscard) in self.drawDiscardBitstrings):
                continue

            remainingCards = copy.deepcopy(self.cards)
            remainingCards.remove(card)
            bestMeldSets = GinRummyUtil.cardsToBestMeldSets(remainingCards)
            deadwood = GinRummyUtil.getDeadwoodPoints(None, None, None, remainingCards) if (not bestMeldSets) \
                else GinRummyUtil.getDeadwoodPoints(bestMeldSets[0], remainingCards, None, None)
            if (deadwood <= minDeadwood):
                if (deadwood < minDeadwood):
                    minDeadwood = deadwood
                    candidateCards.clear()
                candidateCards.append(card)
        if (len(candidateCards) > 1):
            maxRank = candidateCards[0].rank
            maxCandidateCards = []
            for c in candidateCards:
                if (c.rank > maxRank):
                    maxCandidateCards.clear()
                    maxRank = c.rank
                if (c.rank == maxRank):
                    maxCandidateCards.append(c)
            candidateCards = maxCandidateCards
        discard = candidateCards[random.randrange(0, len(candidateCards))]
        drawDiscard = []
        drawDiscard.append(self.drawnCard)
        drawDiscard.append(discard)
        self.drawDiscardBitstrings.append(GinRummyUtil.cardsToBitstring(drawDiscard))
        return discard

    def reportDiscard(self, playerNum, discardedCard):
        self.totalDiscarded = self.totalDiscarded + 1
        if (playerNum == self.playerNum):
            self.cards.remove(discardedCard)

    def getFinalMelds(self):
        bestMeldSets = GinRummyUtil.cardsToBestMeldSets(self.cards)
        if (not self.opponentKnocked and (not bestMeldSets or GinRummyUtil.getDeadwoodPoints(bestMeldSets[0],
                                                                                             self.cards, None, None) > GinRummyUtil.MAX_DEADWOOD)):
            return None
        return [] if not bestMeldSets else bestMeldSets[random.randrange(0, len(bestMeldSets))]

    def reportFinalMelds(self, playerNum, melds):
        if (playerNum != self.playerNum):
            self.opponentKnocked = True

    def reportLayoff(self, playerNum, layoffCard, opponentMeld):
        return

    def reportScores(self, scores):
        return

    def reportFinalHand(self, playerNum, hand):
        return
