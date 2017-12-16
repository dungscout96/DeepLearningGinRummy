import random
import csv as csvmodule
import sys
sys.path.append('../')
import copy
import Gin_Rummy_Python.Card as Card
import Gin_Rummy_Python.GinRummyUtil as GinRummyUtil
import Gin_Rummy_Python.DataCollector as DataCollector
from Gin_Rummy_Python.Card import Card
from Gin_Rummy_Python.SimpleGinRummyPlayer import SimpleGinRummyPlayer
from Gin_Rummy_Python.SimpleGinRummyPlayer2 import SimpleGinRummyPlayer2

# 11/26/2017 - 9:18 p.m.: edit turn and csv sizes and indices for new implementation of neural network
Card.initialize()
HAND_SIZE = 10
playVerbose = True
players = [SimpleGinRummyPlayer(), SimpleGinRummyPlayer2()]
roundNumber = []
currentHand = []
cardDrawnFaceup = []
cardDrawnFacedown = []
discardedCard= []
oppDrawnCard = []
oppDiscardedCard = []
cardsRevealed = []
toCSV1 = True
#collector = DataCollector()
#csvRecords = [] #collector.csvRecords

# 11/29: new feature set: current hand, opponent draw, opponents discards, revealed cards, hand outcome
csvFileX = open('csvP_trashX.csv', 'w', newline='')
out = csvmodule.writer(csvFileX)
csvFileY = open('csvP_trashY.csv', 'w', newline='')
outY = csvmodule.writer(csvFileY)

def setPlayVerbose(verbose):
    playVerbose = verbose


def play(startingPlayer):
    # csvGameRecords = []
    csvTurnRecords = []
    scores = [0 for i in range(2)]
    hands = []
    hands.append([])
    hands.append([])

    while scores[0] < GinRummyUtil.GOAL_SCORE and scores[1] < GinRummyUtil.GOAL_SCORE:
        currentPlayer = startingPlayer
        opponent = 1 if currentPlayer == 0 else 0
        prevScores = copy.copy(scores)

        deck = Card.getShuffle(random.randrange(sys.maxsize))
        # deck = Card.getShuffle(1)
        # print(deck)
        hands[0].clear()
        hands[1].clear()
        # deal cards to players
        for i in range(2 * HAND_SIZE):
            hands[i % 2].append(deck.pop())
        for i in range(2):
            handArr = hands[i]
            players[i].startGame(i, startingPlayer, handArr)
            if playVerbose:
                print("Player {} is dealt {}.\n".format(i, hands[i]))
        if playVerbose:
            print("Player {} starts.\n".format(startingPlayer))
        discards = []  # new  Stack<Card>()
        discards.append(deck.pop())
        if playVerbose:
            print("The initial face up card is {}.\n".format(discards[-1]))
        firstFaceUpCard = discards[-1] #https://stackoverflow.com/questions/4085417/how-to-check-the-last-element-of-a-python-list discards.peek()
        turnsTaken = 0
        knockMelds = None

        revealedCards = []  # ArrayList<Card>()
        revealedCards.append(firstFaceUpCard)
        oppDraw = []
        oppDiscard = []
        if currentPlayer == 0:
            currentCards = copy.copy(hands[currentPlayer])
            revealedCards.extend(currentCards)

        # while there still card in the deck of card, play
        while len(deck) > 2:
            # print('len deck {}'.format(len(deck)))
            if toCSV1:
                turn = []  # new ArrayList<Object>()
                turn.append(currentPlayer) #  turn[0]
                #turn.append(turnsTaken + 1)
                unmeldedCards = copy.copy(hands[currentPlayer])

                turn.append(copy.copy(hands[currentPlayer])) # turn[1]

                bestMelds = GinRummyUtil.cardsToBestMeldSets(unmeldedCards)
                if bestMelds: #!bestMelds.isEmpty()
                    melds = bestMelds[0]
                    for meld in melds:
                        for card in meld:
                            unmeldedCards.remove(card)
                    melds.append(unmeldedCards)

                drawFaceUp = False
                faceUpCard = discards[-1]
                if not (turnsTaken == 3 and faceUpCard == firstFaceUpCard): # only for the beginning of the hand
                    drawFaceUp = players[currentPlayer].willDrawFaceUpCard(faceUpCard)
                    # print("drawFaceUp {}".format(drawFaceUp))
                    if not drawFaceUp and faceUpCard == firstFaceUpCard and turnsTaken < 2:
                        if playVerbose:
                            print("Player {} declines {}.\n".format(currentPlayer, firstFaceUpCard))
                        turn.append(None) # draw face up
                        turn.append(None) # discard
                        if (currentPlayer == 0):
                            turn.append(copy.deepcopy(revealedCards))

                if not ((not drawFaceUp) and turnsTaken < 2 and faceUpCard == firstFaceUpCard):
                    drawCard = discards.pop() if drawFaceUp else deck.pop()
                    for i in range(2):
                        players[i].reportDraw(currentPlayer, drawCard if i == currentPlayer or drawFaceUp else None)
                    if playVerbose:
                        print("Player {} draws {}.\n".format(currentPlayer, drawCard))
                    hands[currentPlayer].append(drawCard)

                    if (drawFaceUp):
                        turn.append(drawCard)
                        if currentPlayer == 1:
                            oppDraw.append(drawCard)
                    else:
                        turn.append(None)
                    if (currentPlayer == 0):
                        revealedCards.append(drawCard)
                    discardCard = players[currentPlayer].getDiscard()
                    if (not (discardCard in hands[currentPlayer])) or discardCard == faceUpCard:
                        if playVerbose:
                            print("Player {} discards {} illegally and forfeits.\n".format(currentPlayer, discardCard))
                        return opponent
                    hands[currentPlayer].remove(discardCard)
                    for i in range(2):
                        players[i].reportDiscard(currentPlayer, discardCard)
                    if playVerbose:
                        print("Player {} discards {}.\n".format(currentPlayer, discardCard))
                    discards.append(discardCard)
                    if currentPlayer == 1:
                        oppDiscard.append(discardCard)
                    turn.append(discardCard)
                    if (currentPlayer == 1):
                        revealedCards.append(discardCard)

                    if (playVerbose):
                        if (not bestMelds): #if bestMelds.isEmpty()
                            print("Player {} has {} with {} deadwood.\n".format(currentPlayer, unmeldedCards,
                                  GinRummyUtil.getDeadwoodPoints(None, None, None, unmeldedCards)))
                        else:
                            melds = bestMelds[0]
                            for meld in melds:
                                for card in meld:
                                    unmeldedCards.remove(card)
                            melds.append(unmeldedCards)
                            print("Player {} has {} with {} deadwood.\n".format(currentPlayer, melds,
                                  GinRummyUtil.getDeadwoodPoints(None, None, None, unmeldedCards)))

                    # only player, not opponent receive extra info
                    if (currentPlayer == 0):
                        turn.append(copy.deepcopy(revealedCards))
                        turn.append(copy.deepcopy(oppDraw))
                        turn.append(copy.deepcopy(oppDiscard))

                    csvTurnRecords.append(turn)

                    knockMelds = players[currentPlayer].getFinalMelds()
                    # print("knockMelds {}".format(knockMelds))
                    if (knockMelds != None):
                        break
                turnsTaken = turnsTaken + 1
                currentPlayer = 1 if currentPlayer == 0 else 0
                opponent = 1 if currentPlayer == 0 else 0

        if (knockMelds != None):
            handBitstring = GinRummyUtil.cardsToBitstring(hands[currentPlayer])
            # print("handBitstring {}".format(handBitstring))
            unmelded = handBitstring
            for meld in knockMelds:
                # print("meld {}".format(meld))
                meldBitstring = GinRummyUtil.cardsToBitstring(meld)
                # print("meldBitstring {}".format(meldBitstring))
                if (not (meldBitstring in GinRummyUtil.getAllMeldBitstrings())) or ((meldBitstring & unmelded) != meldBitstring):  # TODO
                    if playVerbose:
                        print("Player {} melds {} illegally and forfeits.\n".format(currentPlayer, knockMelds))
                    print("not here 1")
                    return opponent
                unmelded = unmelded & ~meldBitstring
            #print("current hand {}".format(hands[currentPlayer]))
            knockingDeadwood = GinRummyUtil.getDeadwoodPoints(knockMelds, hands[currentPlayer], None, None)
            # print("knowckingDeadwood {}".format(knockingDeadwood))
            if (knockingDeadwood > GinRummyUtil.MAX_DEADWOOD):
                if (playVerbose):
                    print("Player {} melds {} with greater than {} deadwood and forfeits.\n".format(currentPlayer, knockMelds,
                          knockingDeadwood))
                print("not here 2")
                return opponent

            meldsCopy = []
            for i in range(2):
                # meldsCopy =   < <Card>>()
                for meld in knockMelds:
                    meldsCopy.append(copy.copy(meld))
                meldsCopy.append(GinRummyUtil.bitstringToCards(unmelded))
                # print("meldsCopy {}".format(meldsCopy))
                players[i].reportFinalMelds(currentPlayer, meldsCopy)

            if playVerbose:
                if (knockingDeadwood > 0):
                    print("Player {} melds {} with {} deadwood from {}.\n".format(currentPlayer, knockMelds, knockingDeadwood,
                          GinRummyUtil.bitstringToCards(unmelded)))
                else:
                    print("Player {} goes gin with melds {}.\n".format(currentPlayer, knockMelds))

            opponentMelds = players[opponent].getFinalMelds()
            # print("opponentMelds {}".format(opponentMelds))
            opponentHandBitstring = GinRummyUtil.cardsToBitstring(hands[opponent])
            # print("opponentHandBitstring {}".format(opponentHandBitstring))
            opponentUnmelded = opponentHandBitstring
            for meld in opponentMelds:
                meldBitstring = GinRummyUtil.cardsToBitstring(meld)
                if not (meldBitstring in GinRummyUtil.getAllMeldBitstrings()) or ((meldBitstring & opponentUnmelded) != meldBitstring):
                    if (playVerbose):
                        print("Player {} melds {} illegally and forfeits.\n".format(opponent, opponentMelds))
                    print("not here 3")
                    return currentPlayer
                opponentUnmelded = opponentUnmelded & ~meldBitstring
            unmeldedCards = GinRummyUtil.bitstringToCards(opponentUnmelded)
            # print("unmeldedCards {}".format(unmeldedCards))
            if (knockingDeadwood > 0):
                cardWasLaidOff = True
                while True:
                    cardWasLaidOff = False
                    layOffCard = None
                    layOffMeld = None
                    for card in unmeldedCards:
                        for meld in knockMelds:
                            newMeld = copy.deepcopy(meld)
                            newMeld.append(card)
                            newMeldBitstring = GinRummyUtil.cardsToBitstring(newMeld)
                            if (newMeldBitstring in GinRummyUtil.getAllMeldBitstrings()):
                                layOffCard = card
                                layOffMeld = meld
                                break
                        if (layOffCard != None):
                            if (playVerbose):
                                print("Player {} lays off {} on {}.\n".format(opponent, layOffCard, layOffMeld))
                            for player in range(2):
                                players[player].reportLayoff(opponent, layOffCard, layOffMeld)
                            unmeldedCards.remove(layOffCard)
                            layOffMeld.append(layOffCard)
                            cardWasLaidOff = True
                            break
                    if (not cardWasLaidOff):
                        break

            opponentDeadwood = 0
            for card in unmeldedCards:
                opponentDeadwood += GinRummyUtil.getDeadwoodPoints(None, None,card, None)
            # print("opponentDeadwood {}".format(opponentDeadwood))
            if (playVerbose):
                print("Player {} has {} deadwood with {}\n".format(opponent, opponentDeadwood, unmeldedCards))
            if (playVerbose):
                print("Player {} melds {}.\n".format(opponent, opponentMelds))

            for i in range(2):
                meldsCopy = []
                for meld in opponentMelds:
                    meldsCopy.append(copy.copy(meld))
                meldsCopy.append(copy.copy(unmeldedCards))
                players[i].reportFinalMelds(opponent, meldsCopy)

            if (knockingDeadwood == 0):
                scores[currentPlayer] += GinRummyUtil.GIN_BONUS + opponentDeadwood
                if (playVerbose):
                    print("Player {} scores the gin bonus of {} plus opponent deadwood {} for {} total points.\n".format(
                          currentPlayer, GinRummyUtil.GIN_BONUS, opponentDeadwood,
                          GinRummyUtil.GIN_BONUS + opponentDeadwood))
            elif (knockingDeadwood < opponentDeadwood):
                scores[currentPlayer] += opponentDeadwood - knockingDeadwood
                if (playVerbose):
                    print("Player {} scores the deadwood difference of {}.\n".format(currentPlayer,
                          opponentDeadwood - knockingDeadwood))
            else:
                scores[opponent] += GinRummyUtil.UNDERCUT_BONUS + knockingDeadwood - opponentDeadwood
                if (playVerbose):
                    print(
                        "Player {} undercuts and scores the undercut bonus of {} plus deadwood difference of {} for {} total points.\n".format(
                        opponent, GinRummyUtil.UNDERCUT_BONUS, knockingDeadwood - opponentDeadwood,
                        GinRummyUtil.UNDERCUT_BONUS + knockingDeadwood - opponentDeadwood))
            startingPlayer = 1 if startingPlayer == 0 else 0
        else:  # If the round ends due to a two card draw pile with no knocking, the round is cancelled.
            if (playVerbose):
                print("The draw pile was reduced to two cards without knocking, so the hand is cancelled.")

        for i in range(2):
            for j in range(2):
                players[i].reportFinalHand(j, hands[j])

        if (playVerbose):
            print("Player\tScore\n0\t%d\n1\t%d\n", scores[0], scores[1])
        for i in range(2):
            players[i].reportScores(copy.deepcopy(scores))

        if (toCSV1):
            # add hand outcome
            for i in range(len(csvTurnRecords)):
                turn = csvTurnRecords[i]
                turnPlayer = turn[0]
                turnOpponent = 1 - turnPlayer
                handOutcome = scores[turnPlayer] - prevScores[turnPlayer] - scores[turnOpponent] + prevScores[
                    turnOpponent]
                turn.append(handOutcome)

            # write to csv file
            for turn in csvTurnRecords:
                csv = turn # redundancy just so that don't have to modify code below
                #matrix = [[0 for c in range(65)] for r in range(4)] #All info of the turn
                matrix = [[0 for c in range(52)] for r in range(4)] #All info of the turn
                handOutcome = 0
                if (csv[0] == 0):
                    for i in range(len(csv)):
                        if i != 0 and i != 2 and i != 3: # disregard [0] (player), [1] (turn), revealed cards, and opp draw face up
                            if (i == 7):
                                handOutcome = csv[i]
                            #elif (i != 6): # { // if not numeric values: draw card, discard card, revealed cards, opp draw, opp discard
                            else: # { // if not numeric values: draw card, discard card, revealed cards, opp draw, opp discard
                                rankOffset = 0# // indicate to which set of the 13 rank the info belong
                                #// suit order: club, heart, space, diamond
                                # if (i == 2): # if player's hand
                                if (i == 1): # if current hand
                                    rankOffset = 0
                                elif i == 5:
                                    rankOffset = 1 * 13
                                elif i == 6:
                                    rankOffset = 2 * 13
                                elif i == 4:
                                    print(csv[i])
                                    rankOffset = 3 * 13
                                for card in csv[i]:
                                    suit = card.getSuit()
                                    rank = card.getRank()
                                    matrix[suit][rank + rankOffset] = 1
                    for r in range(len(matrix)):
                        out.writerow(matrix[r])
                    outY.writerow([handOutcome])

            #csvGameRecords.extend(copy.deepcopy(csvTurnRecords))
            #DataCollector.csvRecords.extend(csvGameRecords)
            csvTurnRecords.clear()
    #if playVerbose:
        #print("Player {} wins.\n".format(0 if scores[0] > scores[1] else 1))
    # winOutcome = [1 if scores[0] > scores[1] else 0, 0 if scores[0] > scores[1] else 1]
    # for turn in csvGameRecords:
    #     turnPlayer = turn[0]
    #     turn.append(winOutcome[turnPlayer])
    # DataCollector.csvRecords.extend(copy.deepcopy(csvGameRecords))
    # csvGameRecords.clear()
    return 0 if scores[0] >= GinRummyUtil.GOAL_SCORE else 1


def match(player1Name, player2Name, numGames):
    if (toCSV1):
        header = []
        header.append("hand")
        header.append("draw face up")
        header.append("draw face down")
        header.append("discard")
        header.append("revealed")
        header.append("opp draw card")
        header.append("opp discard card")
        header.append("hand outcome")
        header.append("win outcome")
    numP1Wins = 0
    for i in range(numGames):
        numP1Wins = numP1Wins + play(i % 2)
        print("done " + str(i) + " game")
    print("Games Won: {}:{}, {}:{}.".format(player1Name, numGames - numP1Wins, player2Name, numP1Wins))
    # print(len(DataCollector.csvRecords))
    # DataCollector.toCSVByCards()

    '''
	filename = "match-" + numGames + "-" + player1Name + "-" + player2Name + ".txt"
	PrintWriter writer =  Pr Writer(filename, "UTF-8")
	writer.pr f("Match %s vs. %s (%d games) ... ", player1Name, player2Name, numGames)
	writer.flush()
	@SuppressWarnings("unchecked")
	Class<GinRummyPlayer> playerClass1 = (Class<GinRummyPlayer>) Class.forName(player1Name)
	players[0] = playerClass1.Instance()
	@SuppressWarnings("unchecked")
	Class<GinRummyPlayer> playerClass2 = (Class<GinRummyPlayer>) Class.forName(player2Name)
	players[1] = playerClass2.Instance()
	long startMs = System.currentTimeMillis()
	numP1Wins = 0
	for (  i = 0 i < numGames i++)
	numP1Wins += play(i % 2)
	System.out.pr ln("done " + i + " game")

	long totalMs = System.currentTimeMillis() - startMs
	writer.pr f("%d games played in %d ms.\n", numGames, totalMs)
	writer.pr f("Games Won: %s:%d, %s:%d.\n", player1Name, numGames - numP1Wins, player2Name, numP1Wins)
	System.out.pr f("%d games played in %d ms.\n", numGames, totalMs)
	System.out.pr f("Games Won: %s:%d, %s:%d.\n", player1Name, numGames - numP1Wins, player2Name, numP1Wins)
	writer.close()

	if (toCSV1)
		collector.toCSVByCards()



getComputerName()

// From: http://stackoverflow.com/questions/7883542/getting-the-computer-name-in-java
Map< ,  > env = System.getenv()
if (env.containsKey("COMPUTERNAME"))
return env.get("COMPUTERNAME")
elif (env.containsKey("HOSTNAME"))
return env.get("HOSTNAME")
else
hostname = "Unknown"
try

InetAddress addr
addr = InetAddress.getLocalHost()
hostname = addr.getHostName()

catch (UnknownHostException ex)

System.err.pr ln("Hostname can not be resolved")

return hostname



def main():
	playerNames = ["SimpleGinRummyPlayer", "SimpleGinRummyPlayer2"]
	computerName = getComputerName()
Scanner in =  Scanner(computerName)
computerNum = Integer.parseInt(in.findInLine(Pattern.compile("[1-9][0-9]*")))
in.close()
System.out.pr ln(computerNum)
minComputerNum = 1
index = computerNum - minComputerNum
index = 0 // TODO: comment out to use computer names
index1 = 0, index2 = 0
for (  i = 0 i < playerNames.length && index >= 0 i++)
for (  j = i + 1 j < playerNames.length && index >= 0 j++)
if (index == 0)
index1 = i
index2 = j

index--

numMatch = 10000
//  numMatch = 1
).match(playerNames[index1], playerNames[index2], numMatch)

'''


playVerbose = False
match("SimpleGinRummyPlayer", "SimpleGinRummyPlayer2", 40)

csvFileX.close()
csvFileY.close()
