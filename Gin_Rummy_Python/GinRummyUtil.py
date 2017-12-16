from Gin_Rummy_Python.Card import Card
import copy
from queue import Queue
from collections import deque

Card.initialize()

GOAL_SCORE = 100
GIN_BONUS = 20
UNDERCUT_BONUS = 10
MAX_DEADWOOD = 10
DEADWOOD_POINTS = []
for i in range(Card().NUM_RANKS):
    DEADWOOD_POINTS.append(0)
cardBitstrings = [0 for i in range(Card.NUM_CARDS)]
meldBitstrings = []
meldBitstringToCardsMap = dict()
for rank in range(Card.NUM_RANKS):
    DEADWOOD_POINTS[rank] = min(rank + 1, 10)

bitstring = 1
for i in range(Card.NUM_CARDS):
    cardBitstrings[i] = bitstring
    bitstring <<= 1

# meldBitstrings = []
# meldBitstringToCardsMap = new HashMap<Long, ArrayList<Card>>()

for suit in range(Card.NUM_SUITS):
    for runRankStart in range(Card.NUM_RANKS - 2):
        bitstringList = []
        cards = []
        c = Card.getCard(runRankStart, suit)
        cards.append(c)
        meldBitstring = cardBitstrings[c.getId()]
        c = Card.getCard(runRankStart + 1, suit)
        cards.append(c)
        meldBitstring |= cardBitstrings[c.getId()]
        for rank in range(runRankStart + 2, Card.NUM_RANKS):
            c = Card.getCard(rank, suit)
            cards.append(c)
            meldBitstring |= cardBitstrings[c.getId()]
            bitstringList.append(meldBitstring)
            meldBitstringToCardsMap[meldBitstring] = copy.copy(cards)
        meldBitstrings.append(bitstringList)

for rank in range(Card.NUM_RANKS):
    cards = []
    for suit in range(Card.NUM_SUITS):
        cards.append(Card.getCard(rank, suit))
    for suit in range(Card.NUM_SUITS + 1):
        cardSet = copy.copy(cards)
        if suit < Card.NUM_SUITS:
            cardSet.remove(Card.getCard(rank, suit))
        bitstringList = []
        meldBitstring = 0
        for card in cardSet:
            meldBitstring |= cardBitstrings[card.getId()]
        bitstringList.append(meldBitstring)
        meldBitstringToCardsMap[meldBitstring] = cardSet
        meldBitstrings.append(bitstringList)


def bitstringToCards(bitstring):
    cards = []
    bitstring = int(bitstring)
    for i in range(Card.NUM_CARDS):
        if bitstring % 2 == 1:
            cards.append(Card.allCards[i])
        bitstring = int(bitstring / 2)
        #print(bitstring)
    return cards


def cardsToBitstring(cards):
    bitstring = 0
    for card in cards:
        bitstring |= cardBitstrings[card.getId()]
    return bitstring


def cardsToAllMeldBitstrings(cards):
    bitstringList = []
    cardsBitstring = cardsToBitstring(cards)
    for meldBitstringList in meldBitstrings:
        for meldBitstring in meldBitstringList:
            if (meldBitstring & cardsBitstring) == meldBitstring:
                bitstringList.append(meldBitstring)
            else:
                break
    return bitstringList


def cardsToAllMelds(cards):
    meldList = []
    for meldBitstring in cardsToAllMeldBitstrings(cards):
        meldList.append(bitstringToCards(meldBitstring))
    return meldList


def cardsToAllMaximalMeldSets(cards):
    maximalMeldSets = []
    meldBitstrings = cardsToAllMeldBitstrings(cards)
    closed = []  # new HashSet<HashSet<Integer>>()
    queue = Queue()  # new LinkedList<HashSet<Integer>>()
    allIndices = set()  # new HashSet<Integer>()
    for i in range(len(meldBitstrings)):
        meldIndexSet = set()  # new HashSet<Integer>()
        meldIndexSet.add(i)
        allIndices.add(i)
        queue.put(meldIndexSet)
    while not queue.empty():
        meldIndexSet = queue.get()  # queue.poll()
        #print("meldIndexSet {}".format(meldIndexSet))
        #print("closed {}".format(closed))
        if (meldIndexSet in closed):
            #print("hit here")
            continue
        meldSetBitstring = 0
        for meldIndex in meldIndexSet:
            meldSetBitstring |= meldBitstrings[meldIndex]
        closed.append(meldIndexSet)
        #print("closed {}".format(closed))
        isMaximal = True
        for i in range(len(meldBitstrings)):
            if (i in meldIndexSet):
                continue
            meldBitstring = meldBitstrings[i]
            if ((meldSetBitstring & meldBitstring) == 0):  # &
                isMaximal = False
                newMeldIndexSet = copy.copy(meldIndexSet)
                newMeldIndexSet.add(i)
                queue.put(newMeldIndexSet)
                #print("queue after {}".format(queue))
        if isMaximal:
            cardSets = []
            for meldIndex in meldIndexSet:
                meldBitstring = meldBitstrings[meldIndex]
                #print(meldBitstring)
                cardSets.append(bitstringToCards(meldBitstring))
            maximalMeldSets.append(cardSets)
    return maximalMeldSets


def getDeadwoodPoints(melds=None, hand=None, card=None, cards=None):
    if melds!=None and hand!=None:
        melded = []
        for meld in melds:
            for card in meld:
                melded.append(card)
        deadwoodPoints = 0
        for card in hand:
            if not (card in melded):
                deadwoodPoints += DEADWOOD_POINTS[card.rank]
        return deadwoodPoints
    elif card != None:
        return DEADWOOD_POINTS[card.rank]
    elif cards != None:
        deadwood = 0
        for c in cards:
            deadwood += DEADWOOD_POINTS[c.rank]
        return deadwood



'''
def getDeadwoodPoints(card):
    return DEADWOOD_POINTS[card.rank]


def getDeadwoodPoints(cards):
    deadwood = 0
    for card in cards:
        deadwood += DEADWOOD_POINTS[card.rank]
    return deadwood
'''

def cardsToBestMeldSets(cards):
    minDeadwoodPoints = 100000000
    maximalMeldSets = cardsToAllMaximalMeldSets(cards)
    bestMeldSets = []
    for melds in maximalMeldSets:
        deadwoodPoints = getDeadwoodPoints(melds, cards, None, None)
        if deadwoodPoints <= minDeadwoodPoints:
            if deadwoodPoints < minDeadwoodPoints:
                minDeadwoodPoints = deadwoodPoints
                bestMeldSets.clear()
            bestMeldSets.append(melds)
    return bestMeldSets


def getAllMeldBitstrings():
    return meldBitstringToCardsMap.keys()

'''
cardNames = "AD AS AH AC 2C 3C 4C 4H 4D 4S"
cardNameArr = cardNames.split(" ")
cards = []
for cardName in cardNameArr:
    cards.append(Card.strCardMap.get(cardName))
print("Hand: " + str(cards))
print("Bitstring representation as long: " + str(cardsToBitstring(cards)))
print("All melds:")
for meld in cardsToAllMelds(cards):
    print(meld)
print("Maximal meld sets:")
for meldSet in cardsToAllMaximalMeldSets(cards):
    print(meldSet)
print("Best meld sets:")
for meldSet in cardsToBestMeldSets(cards):
    print(str(getDeadwoodPoints(meldSet, cards, None, None)) + ":" + meldSet)

cards = Card.allCards
print(cards)
print(cardsToBitstring(cards))
print(meldBitstrings)
print(cardsToAllMeldBitstrings(cards))
print(cardsToAllMaximalMeldSets(cards[0:10]))
print(cardsToBestMeldSets(cards[0:10]))
cards = [Card.getCard(8,0), Card.getCard(8,2), Card.getCard(8, 3)]
print(cardsToBitstring(cards))

'''
