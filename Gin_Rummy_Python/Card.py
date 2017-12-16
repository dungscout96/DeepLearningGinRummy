import random
import csv
class Card:
    allCards = []
    rankNames = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]
    suitNames = ["C", "H", "S", "D"]
    isSuitRed = {False, True, False, True}
    NUM_RANKS = len(rankNames)
    NUM_SUITS = len(suitNames)
    NUM_CARDS = NUM_RANKS * NUM_SUITS
    strCardMap = dict() # new HashMap<String, Card>()
    strIdMap = dict() #new HashMap<String, Integer>()
    idStrMap = dict() #new HashMap<Integer, String>()


    def __init__(self, rank=0, suit=0):
        self.rank = rank
        self.suit = suit

    def getRank(self):
        return self.rank

    def getSuit(self):
        return self.suit

    def isRed(self):
        return self.suit % 2 == 1

    def getId(self, rank=-1, suit=-1):
        if rank==-1 or suit == -1:
            return self.suit * self.NUM_RANKS + self.rank
        else:
            return suit * self.NUM_RANKS + rank

    def __eq__(self, other):
        if other == None:
            return False
        else:
            return self.rank == other.rank and self.suit == other.suit

    def toString(self):
        return self.rankNames[self.rank] + self.suitNames[self.suit]

    def __str__(self):
        return self.rankNames[self.rank] + self.suitNames[self.suit]

    def __repr__(self):
        return self.__str__()

    @classmethod
    def initialize(self):
        self.allCards = [Card() for i in range(self.NUM_SUITS*self.NUM_RANKS)]
        i = 0
        for suit in range(self.NUM_SUITS):
            for rank in range(self.NUM_RANKS):
                c = Card(rank, suit)
                self.allCards[i] = c
                self.strCardMap[c.toString()] = c
                self.strIdMap[c.toString()] = c.getId()
                self.idStrMap[c.getId()] = c.toString()
                i = i + 1
    @classmethod
    def getCard(self, id):
        return self.allCards[id]


    @classmethod
    def getCard(self, rank, suit):
        return self.allCards[suit * self.NUM_RANKS + rank]

    #def getId(self, rank, suit):
        #return self.suit * self.NUM_RANKS + self.rank

    @classmethod
    def getShuffle(self,seed):
        deck = [] #new Stack<Card>()
        for i in range(self.NUM_CARDS):
            deck.append(Card.allCards[i])
        random.Random(seed).shuffle(deck)

        # # to read in card deck from csv file generated by Java code
        # deck = [] # deckString = None
        # with open('cards.csv', newline='') as csvfile:
        #     cardReader = csv.reader(csvfile)
        #     for row in cardReader:
        #         deckString = row
        # count = 0
        # for card in deckString:
        #     newstr = card.replace(" ","")
        #     r = self.rankNames.index(newstr[0])
        #     s = self.suitNames.index(newstr[1])
        #     deck.append(self.getCard(r,s))
        #     count = count + 1
        return deck

