import random
import pandas as pd
import csv as csvmodule
import sys
sys.path.append('../')
import numpy as np
from keras.models import model_from_json
from keras import optimizers
import copy
import Gin_Rummy_Python.Card as Card
import Gin_Rummy_Python.GinRummyUtil as GinRummyUtil
from Gin_Rummy_Python.Card import Card
from Gin_Rummy_Python.SimpleGinRummyPlayer import SimpleGinRummyPlayer
from Gin_Rummy_Python.SimpleGinRummyPlayer2 import SimpleGinRummyPlayer2
import CNN.project2 as TrainingModule

# 11/27/2018: modify playing code to implement explicit feature model
HAND_SIZE = 10
playVerbose = True
playVerboseNetwork = True
players = [SimpleGinRummyPlayer(), SimpleGinRummyPlayer2()]
cardsRevealed = []
toCSV = True
#playRecordFile = open('GameWonRecord.csv', 'w', newline='')
#outRecord = csvmodule.writer(playRecordFile)
csvFileX = None #open('csvP_X.csv', 'w', newline='')
out = None #csvmodule.writer(csvFileX)
csvFileY = None #open('csvP_Y.csv', 'w', newline='')
outY = None #csvmodule.writer(csvFileY)
network = None
#collector = DataCollector()
#csvRecords = [] #collector.csvRecords


# TODO why not drawFaceUp ever?

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
        turnRecords = []
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
                print("Player {} is dealt {}.".format(i, hands[i]))
        if playVerbose:
            print("Player {} starts.".format(startingPlayer))
        discards = []  # new  Stack<Card>()
        discards.append(deck.pop())
        if playVerbose:
            print("The initial face up card is {}.".format(discards[-1]))
        firstFaceUpCard = discards[-1] #https://stackoverflow.com/questions/4085417/how-to-check-the-last-element-of-a-python-list discards.peek()
        turnsTaken = 0
        knockMelds = None

        # turn data
        revealedCards = []
        opponentDrawnCards = []
        opponentDiscardedCards = []

        revealedCards.append(firstFaceUpCard)
        if currentPlayer == 0:
            currentCards = copy.copy(hands[currentPlayer])
            revealedCards.extend(currentCards)

        # while there still card in the deck of card
        while len(deck) > 2:
            for i in range(2):
                if playVerbose:
                    print("Player {}'s hand {}.".format(i, hands[i]))
            turn = []
            unmeldedCards = copy.copy(hands[currentPlayer])
            turn.append(copy.copy(hands[currentPlayer]))

            bestMelds = GinRummyUtil.cardsToBestMeldSets(unmeldedCards)
            playerMelds = []
            if bestMelds: #!bestMelds.isEmpty()
                melds = bestMelds[0]
                for meld in melds:
                    playerMelds.extend(meld)
                    for card in meld:
                        unmeldedCards.remove(card)
                melds.append(unmeldedCards)

            drawFaceUp = False
            faceUpCard = discards[-1]


            #########################################################################################################################
            # prepare info for player draw decision
            # include, in order: current hand, opponent drawn cards, player discards, opponent discards
            if (currentPlayer == 0):
                decisionData = [] # temporary holder before write out to matrix. Will be cleared immediately after written to matrix
                decisionData.append(hands[currentPlayer])
                decisionData.append(opponentDrawnCards)
                decisionData.append(opponentDiscardedCards)
                decisionData.append(revealedCards)
                # decisionData.append(playerMelds)
                # decisionData.append(unmeldedCards)
                # decisionData.append(opponentDiscardedCards)
                # decisionData.append(faceUpCard)
                ##########################################################################################################################

                #<####################################################################################################
                # TODO implement the decline option for the first 2 turns
                # Continue with turn if not initial declined option
                #<
                #if not ((not drawFaceUp) and turnsTaken < 2 and faceUpCard == firstFaceUpCard):
                    # deciding whether draw face up (discards.pop()) or draw face down (deck.pop())
                    # draw whichever gives higher predicted hand result
                # 1 if draw face up
                # 1.1 append the face up card to the player hand for testing
                drawFaceUpPoint = 0
                drawFaceDownPoint = 0

                decisionData[0].append(discards[-1]) # assume that the player draw face up
                discardIfDrawFaceUp = None
                maxHandOutcomeIfDrawFaceUp = -1000000
                # 1.2 try different possible discards and get the highest expected score
                cards = copy.copy(decisionData[0]) # so that can freely remove and append on decisionData[0]
                for card in cards:
                    decisionData[0].remove(card)
                    hand = arrayToData(decisionData)
                    # if playVerboseNetwork:
                    #     print("removed card {}".format(card))
                    predictedHandOutcome = network.predict(hand)[0][0]
                    # if playVerboseNetwork:
                    #     print("estimated handoutcome of draw face up card {} with {} discard: {}".format(discards[-1], card, predictedHandOutcome))
                    if predictedHandOutcome > maxHandOutcomeIfDrawFaceUp:
                        maxHandOutcomeIfDrawFaceUp = predictedHandOutcome
                        discardIfDrawFaceUp = card
                    decisionData[0].append(card)
                # print("drawFaceUpPoint {}".format(drawFaceUpPoint))
                # if playVerboseNetwork:
                #     print("max draw face up card {}: {} with {} discard".format(discards[-1], maxHandOutcomeIfDrawFaceUp, discardIfDrawFaceUp))
                # 1.3 remove the face up card. Don't make decision yet till check draw face down
                decisionData[0].remove(discards[-1])
                # hand should still have just 10 cards
                if len(decisionData[0]) > 10 or len(hands[currentPlayer]) > 10:
                    print("more cards in hand than allowed")
                    exit(1)

                # 2: get average point of drawing a face down card
                drawFaceDownPoint = 0
                # 2.1 for each face down card
                for card in deck:
                    # 2.1.1 get the max score if drawing this card by checking point of each possible discard
                    decisionData[0].append(card)
                    cards = copy.copy(decisionData[0])
                    maxHandOutcomeThisFaceDown = -100000000
                    for c in cards:
                        decisionData[0].remove(c)
                        handData = arrayToData(decisionData)
                        predictedHandOutcome = network.predict(handData)[0][0]
                        if maxHandOutcomeThisFaceDown < predictedHandOutcome:
                            maxHandOutcomeThisFaceDown = predictedHandOutcome
                        decisionData[0].append(c)
                    # 2.1.2 add the max score for drawing this card to drawFaceDownPoint
                    drawFaceDownPoint += maxHandOutcomeThisFaceDown
                    # print("pointOfCurrentCard {}".format(pointOfCurrentCard))
                    # 2.1.3 remove this card out of hand
                    decisionData[0].remove(card)
                # hand should still have just 10 cards
                if len(decisionData[0]) > 10 or len(hands[currentPlayer]) > 10:
                    print("more cards in hand than allowed")
                    exit(1)
                drawFaceDownPoint /= len(deck)
                # if playVerboseNetwork:
                #     print("predicted outcome draw face down: {}".format(drawFaceDownPoint))

                drawCard = None
                drawFaceUp = False
                if maxHandOutcomeIfDrawFaceUp >= drawFaceDownPoint:
                    drawCard = discards.pop()
                    drawFaceUp = True
                else:
                    drawCard = deck.pop()
                    revealedCards.append(drawCard)

                if playVerbose:
                    print("Player {} draws {}.\n".format(currentPlayer, drawCard))

                if playVerboseNetwork:
                    if drawFaceUp:
                        print("Conv net draws face-up {}.\n".format(drawCard))
                    else:
                        print("Conv net draws face-down {}.\n".format(drawCard))

                for i in range(2):
                    players[i].reportDraw(currentPlayer, drawCard if i == currentPlayer or drawFaceUp else None)

                hands[currentPlayer].append(drawCard)

                # deciding which card to discard
                discardCard = None
                if drawFaceUp:
                    discardCard = discardIfDrawFaceUp
                else:
                    bestCardToRemove = None
                    maxPoint = -10000000
                    for card in hands[currentPlayer]:
                        decisionData[0].remove(card)
                        handIfDiscardThisCard = arrayToData(decisionData)
                        predictedPoint = network.predict(handIfDiscardThisCard)
                        predictedPoint = predictedPoint[0][0]
                        # print("predictedPoint {}".format(predictedPoint))
                        if predictedPoint > maxPoint:
                            maxPoint = predictedPoint
                            bestCardToRemove = card
                        decisionData[0].append(card)
                    discardCard = bestCardToRemove
                    # if (not (bestCardToRemove in hands[currentPlayer])) or bestCardToRemove == faceUpCard:
                    #     if playVerbose:
                    #         print("Player {} discards {} illegally and forfeits.\n".format(currentPlayer, discardCard))
                    #     return opponent
                    # if playVerboseNetwork:
                    #     print("predicted maxPoint of discard after a draw-face-down: {}".format(maxPoint))
                hands[currentPlayer].remove(discardCard)

                # report the discarded card to both players
                for i in range(2):
                    players[i].reportDiscard(currentPlayer, discardCard)

                # add to discard pile of possible drawing
                discards.append(discardCard)

                if playVerbose:
                    print("Player {} discards {}.\n".format(currentPlayer, discardCard))

                if playVerboseNetwork:
                    print("Conv net discards {}.\n".format(discardCard))


                # CHECK FOR KNOCK
                knockMelds = players[currentPlayer].getFinalMelds()
                # print("knockMelds {}".format(knockMelds))
                if (knockMelds != None):
                    break # player knocked, end of round
                #>

                # RECORD TURN DATA
                turn.append(copy.deepcopy(hands[currentPlayer]))
                turn.append(copy.deepcopy(opponentDrawnCards))
                turn.append(copy.deepcopy(opponentDiscardedCards))
                turn.append(copy.deepcopy(revealedCards))
                turnRecords.append(copy.deepcopy(turn))
                turn.clear()
            else: # Use old implementation for opponent
                # ####< Old implementation ####
                # offer draw face - up iff not 3rd turn with first face up card (decline automatically in that case)
                if not (turnsTaken == 3 and faceUpCard == firstFaceUpCard):
                    # Moment of decision: draw a face up card?
                    drawFaceUp = players[currentPlayer].willDrawFaceUpCard(faceUpCard)
                    # print("drawFaceUp {}".format(drawFaceUp))
                if not drawFaceUp and faceUpCard == firstFaceUpCard and turnsTaken < 2:
                    if playVerbose:
                        print("Player {} declines {}.\n".format(currentPlayer, firstFaceUpCard))
                drawCard = discards.pop() if drawFaceUp else deck.pop()
                for i in range(2):
                    players[i].reportDraw(currentPlayer, drawCard if i == currentPlayer or drawFaceUp else None)
                if playVerbose:
                    print("Player {} draws {}.\n".format(currentPlayer, drawCard))
                hands[currentPlayer].append(drawCard)

                if drawFaceUp:
                    opponentDrawnCards.append(drawCard)

                discardCard = players[currentPlayer].getDiscard()
                if (not (discardCard in hands[currentPlayer])) or discardCard == faceUpCard:
                    if playVerbose:
                        print("Player {} discards {} illegally and forfeits.\n".format(currentPlayer, discardCard))
                    return opponent
                hands[currentPlayer].remove(discardCard)
                opponentDiscardedCards.append(discardCard)
                revealedCards.append(discardCard)

                for i in range(2):
                    players[i].reportDiscard(currentPlayer, discardCard)
                if playVerbose:
                    print("Player {} discards {}.\n".format(currentPlayer, discardCard))
                discards.append(discardCard)

                # if (playVerbose):
                #     if (not bestMelds): #if bestMelds.isEmpty()
                #         print("Player {} has {} with {} deadwood.\n".format(currentPlayer, unmeldedCards,
                #               GinRummyUtil.getDeadwoodPoints(None, None, None, unmeldedCards)))
                #     else:
                #         melds = bestMelds[0]
                #         for meld in melds:
                #             for card in meld:
                #                 unmeldedCards.remove(card)
                #         melds.append(unmeldedCards)
                #         print("Player {} has {} with {} deadwood.\n".format(currentPlayer, melds,
                #               GinRummyUtil.getDeadwoodPoints(None, None, None, unmeldedCards)))
                # only player, not opponent receive revealed cards info
                # if (currentPlayer == 0):
                #     turn.append(copy.deepcopy(revealedCards))
                # csvTurnRecords.append(turn)

                knockMelds = players[currentPlayer].getFinalMelds()
                if (knockMelds != None):
                    break
            #>#########################################################################################

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

        # print("scores1 {}, scores2 {}".format(scores[0],scores[1]))

        # FINAL REPORT
        for i in range(2):
            for j in range(2):
                players[i].reportFinalHand(j, hands[j])

        if (playVerbose):
            print("Player\tScore\n0\t{}\n1\t{}\n".format(scores[0], scores[1]))
        for i in range(2):
            players[i].reportScores(copy.deepcopy(scores))

        if toCSV:
            #WRITE TURN DATA TO FILE
            # write turn data and their according hand outcome to csv file, for training
            for turn in turnRecords:
                matrix = arrayToMatrix(turn)
                for r in range(len(matrix)):
                    out.writerow(matrix[r])
                handOutcome = scores[0] - prevScores[0] - scores[1] + prevScores[1]
                outY.writerow([handOutcome])
        turnRecords.clear()

    #if playVerbose:
        #print("Player {} wins.\n".format(0 if scores[0] > scores[1] else 1))
    # winOutcome = [1 if scores[0] > scores[1] else 0, 0 if scores[0] > scores[1] else 1]
    # for turn in csvGameRecords:
    #     turnPlayer = turn[0]
    #     turn.append(winOutcome[turnPlayer])
    # DataCollector.csvRecords.extend(copy.deepcopy(csvGameRecords))
    # csvGameRecords.clear()
    return 0 if scores[0] >= GinRummyUtil.GOAL_SCORE else 1

def arrayToMatrix(array):
    # array order: 0 - Cards that I have, 1 - Cards that opponent drew,
    # 2 - Cards that I discarded, 3 - Cards that opponent discarded
    matrix = [[0 for c in range(65)] for r in range(4)] #All info of the turn
    for i in range(len(array)):
        for card in array[i]:
            rankOffSet = i
            suit = card.getSuit()
            rank = card.getRank() + rankOffSet*13
            matrix[suit][rank] = 1
    return matrix

def arrayToData(array):
    # array order: 0 - Cards that I have, 1 - Cards that opponent drew,
    # 2 - Cards that I discarded, 3 - Cards that opponent discarded
    matrix = [[0 for c in range(52)] for r in range(4)] #All info of the turn
    for i in range(len(array)):
        rankOffSet = i # decisionData is in the right order
        for card in array[i]:
            suit = card.getSuit()
            rank = card.getRank() + rankOffSet*13
            matrix[suit][rank] = 1
    X_test = np.asarray(matrix)
    X_test = X_test.reshape(1,4,52) # number of rows is number of rows of training set
    l = [] #
    array = np.split(X_test[0], 4, axis=1) # split the array vertically
    array_stack = np.stack(array, axis=0) # stack the split arrays --> add depth dimension
    l.append(array_stack)
    X_test = np.stack(tuple(l)) # stack all of the samples
    # print(np.shape(X_test))
    return X_test



def match(player1Name, player2Name, numGames):
    if (toCSV):
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
    #outRecord.writerow([player1Name, numGames - numP1Wins, player2Name, numP1Wins])
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


playVerbose = True
playVerboseNetwork = False
toCSV = False
for i in range(1):
    # LOAD THE NEURAL NET!
    # load json and create model
    json_file = open('../CNN/project2ModelKeras2.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    network = model_from_json(loaded_model_json)
    # load weights into new model
    network.load_weights("../CNN/project2ModelKeras2.h5")
    print("loaded model")
    network.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy'])

    # Initialize
    Card.initialize()
    players = [SimpleGinRummyPlayer(), SimpleGinRummyPlayer2()]
    if toCSV:
        csvFileX = open('../CNN/csvP_X.csv', 'w', newline='')
        out = csvmodule.writer(csvFileX)
        csvFileY = open('../CNN/csvP_Y.csv', 'w', newline='')
        outY = csvmodule.writer(csvFileY)

    # Play and collect data
    match("SimpleGinRummyPlayer", "SimpleGinRummyPlayer2", 1)
    if toCSV:
        csvFileX.close()
    # Train network again
    #TrainingModule.trainModel()

    #playRecordFile.close()


        csvFileY.close()


