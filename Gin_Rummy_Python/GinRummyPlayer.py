from abc import ABC, abstractmethod
class GinRummyPlayer(ABC):
    @abstractmethod
    def startGame(playerNum, startingPlayerNum, cards):
        pass
    @abstractmethod
    def willDrawFaceUpCard(card):
        pass

    @abstractmethod
    def reportDraw(playerNum, drawnCard):
        pass

    @abstractmethod
    def getDiscard(self):
        pass

    @abstractmethod
    def reportDiscard(playerNum, discardedCard):
        pass

    @abstractmethod
    def getFinalMelds(self):
        pass

    @abstractmethod
    def reportFinalMelds(playerNum, melds):
        pass

    @abstractmethod
    def reportScores(scores):
        pass

    @abstractmethod
    def reportLayoff(playerNum, layoffCard, opponentMeld):
        pass

    @abstractmethod
    def reportFinalHand(playerNum, hand):
        pass
