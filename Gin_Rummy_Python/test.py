from Gin_Rummy_Python.Card import Card
import copy

class Bank:
    id = 0
a = [1,2,3]
print(a[-1])
b = [[2,1], [3,4]]
c = {3,4,5}
print(3 in c)

print(True if a in b else False)
Card.initialize()
cards = Card.allCards
print(str(cards))
cards2 = []
for i in range(0,10):
    cards2.append(cards[i])
print(cards2)
cards3 = copy.copy(cards2)
print(cards3[9] in cards)

matrix = [[0 for c in range(65)] for r in range(4)] #All info of the turn
print(len(matrix))
print(len(matrix[0]))
print(matrix)
cards4 = [Card.getCard(11,1), Card.getCard(11,0), Card.getCard(0,0), Card.getCard(3,2), Card.getCard(0, 2), Card.getCard(4, 3), Card.getCard(1, 3), Card.getCard(10, 2), Card.getCard(11,2), Card.getCard(12,0)]
toberemoved = [Card.getCard(11,0), Card.getCard(11,1), Card.getCard(11,2)]
print(cards4)
print(toberemoved)
for card in toberemoved:
    cards4.remove(card)
print(cards4)

