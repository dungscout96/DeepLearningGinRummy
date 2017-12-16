csvRecords = []

def toCSVByCards():
    import csv as csvmodule
    with open('csvP_X.csv', 'w', newline='') as csvfileX:
        out = csvmodule.writer(csvfileX)
        with open('csvP_Y.csv', 'w', newline='') as csvfileY:
            outY = csvmodule.writer(csvfileY)
            #for (int j = 0 j < 1 ++j) { // for 1 turn
            for j in range(len(csvRecords)):
                csv = csvRecords[j]
                matrix = [[0 for c in range(65)] for r in range(4)] #All info of the turn
                turn = 0
                winOutcome = 0
                gameOutcome = 0
                if (csv[0] == 0):
                    for i in range(len(csv)):
                        # //if (j == 0) {
                        # //out.print(csv.get(i) + ",")
                        # //} else {
                        # //if ((Integer) csv.get(0) == 0) { // only for current player
                        # // for each 13 columns: have cards, opponent has card, I discarded, Opp discarded, unknown (opp'shand or in deck)
                        #     /* index of turn record:
                        #     0: current player
                        #     1: turn
                        #     2: player's hand --> have card
                        #     3: card drawn face up --> have card
                        #     4: card drawn face down --> have card
                        #     5: discard card --> I discarded
                        #     6: revealed cards --> OUT
                        #     7: opp's draw card --> opp has card
                        #     8: opp's discard --> opp discard
                        #     9: hand outcome
                        #     10: win outcome
                        #      */
                        if (i == 9) :
                            handOutcome = csv[i]
                            #j//System.out.println("game outcome: " + gameOutcome)
                        elif (i != 6): # { // if not numeric values: draw card, discard card, revealed cards, opp draw, opp discard
                            rankOffset= 0# // indicate to which set of the 13 rank the info belong
                            #// suit order: club, heart, space, diamond
                            if (i == 2):
                                rankOffset = 0
                                cards = []
                                cards.extend(csv[i])
                                for c in range(len(cards)):
                                    card = cards[c]
                                    suit = card.getSuit()
                                    rank = card.getRank()
                                    matrix[suit][rank + rankOffset] = 1
                            elif (i == 3 or i == 4):
                                rankOffset = 0
                                if (csv[i] != None):
                                    card = csv[i]
                                    suit = card.getSuit()
                                    rank = card.getRank()
                                    matrix[suit][rank + rankOffset] = 1
                            elif (i == 5):# { // discard card --> I discard (2)
                                rankOffset = 2 * 13
                                if (csv[i] != None):
                                    card = csv[i]
                                    suit = card.getSuit()
                                    rank = card.getRank()
                                    matrix[suit][rank + rankOffset] = 1
                            elif (i == 7): #{ // opp draw card --> opp has card (1)
                                rankOffset = 1 * 13
                                if (csv[i] != None):
                                    card = csv[i]
                                    suit = card.getSuit()
                                    rank = card.getRank()
                                    matrix[suit][rank + rankOffset] = 1
                            elif (i == 8):# { // opp discard -- opp discard (3)
                                rankOffset = 3 * 13
                                if (csv[i] != None):
                                    card = csv[i]
                                    suit = card.getSuit()
                                    rank = card.getRank()
                                    matrix[suit][rank + rankOffset] = 1
                    # //if (j != 0) {
                    # //if ((Integer)csv.get(0) == 0) {
                    # // write to csv_X
                    # // Current format 4*13*5
                    # // Want to write in the order: 13 --> 4 --> 5
                    # int depth = 0
                    # int width = 0
                    # int height = 0
                    # int countCol = 0
                    # int countRow = 0
                    # int countDepth = 0
                    #
                    # while (depth < 5) {
                    #     int r = width
                    #     int c = height
                    #     while (r < (width+4)) {
                    #         while (c < (height+13)) {
                    #             if (depth == 4 && r == 3 && c == (height+12))
                    #                 out.print(matrix[r][c])
                    #             else {
                    #                 countCol++
                    #                 out.print(matrix[r][c] + ",")
                    #             }
                    #             c++
                    #         }
                    #         //System.out.println("Count Col: " + countCol) ==> should have observed the bug here when seeing that all the count col is the same! Because you were expecting it to increase every row.
                    #         c = height // What a bug! Took me 15 minutes!
                    #         countRow++
                    #         r++
                    #     }
                    #     //System.out.println("Count Row: " + countRow)
                    #     depth++
                    #     countDepth++
                    #     height = height+13
                    # }
                    # //System.out.println("Count Depth: " + countDepth)
                    for r in range(len(matrix)):
                        out.writerow(matrix[r])
                        # for c in range(len(matrix[0])):
                        #     if (c == matrix[0].length-1):
                        #         out.print(matrix[r][c])
                        #     else:
                        #         out.print(matrix[r][c] + ",")
                    #// write to csv_Y
                    # out.println()
                    outY.writerow([handOutcome])
            #out.close()
            #outY.close()

def cardToString(cards):
    result = ""
    deck = [0 for i in range(52)]
    if (cards != None):
        for card in cards:
            if (card != None):
                cardIndex = card.getId()
                deck[cardIndex] = 1
    result += str(deck)
    return removeSquareBracket(result)

def removeSquareBracket(string):
    result = ""
    for i in range(1, len(string)-1):
        result += string[i]
    return result
