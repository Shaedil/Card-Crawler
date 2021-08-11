import random
# from cmu 112 course notes
from cmu_112_graphics import *


class Card(object):
    def __init__(self, width, height, suit, number):
        # width is a numeric value
        self.width = width
        # height is a numeric value
        self.height = height
        # suit is a list of strings containing the suit names
        self.suit = suit
        # number is the list of possible numbers on cards
        self.number = number


class MapCard(Card):
    def __init__(self):
        # these cards are visible at the top of screen
        super().__init__(75, 100, ['hearts', 'spades', 'diamonds', 'clubs'],
                         [[i] for i in range(1, 14)])

    def drawMapCard(self, app, canvas, col, row):
        canvas.create_rectangle(app.marginHorizontal + col * app.mapCardWidth,
                        app.marginVertical + (row * app.mapCardHeight),
                        app.marginHorizontal + (col + 1) * app.mapCardWidth,
                        app.marginVertical + ((row + 1) * app.mapCardHeight),
                        fill='maroon')


class PlayerCard(Card):
    def __init__(self):
        # these cards are visible at the bottom of screen
        super().__init__(175, 200, ['sword', 'coin', 'shield', 'heal'],
                         [[j] for j in range(1, 14)])

    def getRandomCard(self):
        # return a random card from the list of cards
        cardNum = random.choice(self.number)
        cardSuit = random.choice(self.suit)
        return [cardSuit, cardNum]


class Map(object):
    def __init__(self, app):
        self.app = app
        # init an empty map grid so we can place cards onto it
        self.width = 5
        self.height = 5
        self.mapGrid = [[0] * self.height for i in range(self.width)]
        self.direction = [(0,-1),(0,1),(1,0),(-1,0)]  # N, S, E, W

    # based on the Aldous-Broder algorithm with some extra rules added.
    # https://weblog.jamisbuck.org/2011/1/17/maze-generation-aldous-broder-algorithm
    def aldousBroder(self):
        # best place to start is near the middle of the grid
        x, y = 2, 3
        remaining = random.randint(15, 20)
        while remaining > 0:            
            for direction in random.sample(self.direction, len(self.direction)):
                nx, ny = x + direction[0], y + direction[1]
                if (nx >= 0 and ny >= 0 and nx < self.width and ny < self.height):
                    if self.mapGrid[nx][ny] == 0:
                        self.mapGrid[nx][ny] = 1
                        remaining -= 1
                    else:
                        x, y = nx, ny
                    break

    def getPathNeighbors(self, row, col):
        neighbors = []
        if col != 0 and self.mapGrid[row][col - 1] == 1:
            neighbors.append([row, col - 1])
        if col != self.width - 1 and self.mapGrid[row][col + 1] == 1:
            neighbors.append([row, col + 1])
        if row != 0 and self.mapGrid[row - 1][col] == 1:
            neighbors.append([row - 1, col])
        if row != self.height - 1 and self.mapGrid[row + 1][col] == 1:
            neighbors.append([row + 1, col])
        return neighbors

    def getAllNeighbors(self, row, col):
        neighbors = []
        if col != 0:
            neighbors.append([row, col - 1])
        if col != self.width - 1:
            neighbors.append([row, col + 1])
        if row != 0:
            neighbors.append([row - 1, col])
        if row != self.height - 1:
            neighbors.append([row + 1, col])
        return neighbors

    def removeRandomMapCard(self):
        i = 0
        while i < 5:
            randX, randY = random.randint(1,3), random.randint(1,3)
            if self.mapGrid[randX][randY] == 1:
                self.mapGrid[randX][randY] = 0
            i += 1

    def buildBridgeFromIslandMapCard(self):
        for row in range(len(self.mapGrid)):
            for col in range(len(self.mapGrid[row])):
                # if there are no neighbors of current cell, then make a new
                # cell
                if len(self.getPathNeighbors(row, col)) <= 1:
                    # assign a random neighoring point to it
                    newPoint = random.choice(self.getAllNeighbors(row, col))
                    row = newPoint[0]
                    col = newPoint[1]
                    self.mapGrid[row][col] = 1

    def assignRoomTypes(self):
        for row in range(len(self.mapGrid)):
            for col in range(len(self.mapGrid[row])):
                if self.mapGrid[row][col] == 1:
                    self.mapGrid[row][col] = random.choice([1, 2, 3])
        # randomly assign treasure room in row[-1] and row[-2]
        self.mapGrid[random.choice([-1, -2])][random.randint(0,4)] = 4

    def makeMap(self):
        self.aldousBroder()
        self.removeRandomMapCard()
        self.buildBridgeFromIslandMapCard()
        self.buildBridgeFromIslandMapCard()
        self.assignRoomTypes()

    def draw(self, canvas):
        # draw the map
        for row in range(len(self.mapGrid)):
            for col in range(len(self.mapGrid[row])):
                if self.mapGrid[row][col] in [1, 2, 3, 4]:
                    MapCard().drawMapCard(self.app, canvas, col, row)


class Player(object):
    def __init__(self, app, x, y, cards):
        # mapX and mapY are the coordinates of the player's starting position
        # on the map
        self.x = x
        self.y = y
        self.app = app
        # cards is a list of lists: [ [suit, num] ]
        self.cards = cards
        # health is randomized between 1 and 14 --> represents regular card
        # numbers
        health = random.randint(1, 14)
        # maxHealth will be used later to check against using healing cards to
        # buff HP above max amount.
        self.maxHealth = health
        self.health = health

    def move(self, dx, dy):
        # dx and dy are the distances the player will move in the x and y
        # directions, respectively
        # if move not illegal, move player
        self.x += dx
        self.y += dy
    
    def drawPlayerCards(self, canvas):
        # draw the player's cards centered at bottom of screen
        leftMargin = (self.app.width - len(self.cards) *
                      self.app.playerCardWidth) / 2
        for i in range(len(self.cards)):
            if self.cards[i][0] == 'heal':
                canvas.create_rectangle(leftMargin + i * self.app.playerCardWidth,
                                self.app.height - self.app.playerCardHeight,
                                leftMargin + (i + 1) * self.app.playerCardWidth,
                                self.app.height, fill='dark red')
            elif self.cards[i][0] == 'sword':
                canvas.create_rectangle(leftMargin + i * self.app.playerCardWidth,
                                self.app.height - self.app.playerCardHeight,
                                leftMargin + (i + 1) * self.app.playerCardWidth,
                                self.app.height, fill='gray')
            elif self.cards[i][0] == 'coin':
                canvas.create_rectangle(leftMargin + i * self.app.playerCardWidth,
                                self.app.height - self.app.playerCardHeight,
                                leftMargin + (i + 1) * self.app.playerCardWidth,
                                self.app.height, fill='orange')
            elif self.cards[i][0] == 'shield':
                canvas.create_rectangle(leftMargin + i * self.app.playerCardWidth,
                                self.app.height - self.app.playerCardHeight,
                                leftMargin + (i + 1) * self.app.playerCardWidth,
                                self.app.height, fill='light blue')
            else: return
            canvas.create_text(leftMargin + (i + 0.5) * self.app.playerCardWidth,
                               self.app.height - 2*(self.app.playerCardHeight/3),
                               anchor='n', text=str(self.cards[i][0]),
                               font=('Helvetica 15 bold'))

class Enemy(object):
    def __init__(self, health, cards):
        self.health = health
        self.cards = cards

    def attack(self):
        pass

    def shield(self):
        pass

    def heal(self):
        if 'heal' in self.cards:
            pass


def appStarted(app):
    app._root.resizable(False, False)
    app.timerDelay = 100
    app.marginHorizontal = 260
    app.marginVertical = 20
    app.mapCardWidth = 56
    app.mapCardHeight = 75
    app.playerCardWidth = 100
    app.playerCardHeight = 150
    app.map = Map(app)
    app.map.makeMap()
    userCards = []
    card = PlayerCard()
    for i in range(random.randint(3,6)):
        suit = card.getRandomCard()[0]
        num = card.getRandomCard()[1]
        userCards.append([suit, num])
    app.player = Player(app, 0, 0, userCards)
    app.starting = True
    app.battle = False


def mousePressed(app, event):
    # if the player clicks on a card, reveal the card
    if app.starting:
        pass
    else:
        pass


def keyPressed(app, event):
    if event.key == 'q':
        app.quit()
    if event.key == 'e':
        app.battle = True
        # debug: start a battle to show off the battle mechanics
        # battle mechanics not implemented yet


def timerFired(app):
    if app.battle:
        # if a battle is happening, run a function that inits a new battle
        userCards = []
        card = PlayerCard()
        for i in range(random.randint(3,6)):
            suit = card.getRandomCard()[0]
            num = card.getRandomCard()[1]
            userCards.append([suit, num])
        # debug: health for now is going to be random
        health = random.randint(1, 10)
        enemy = Enemy(health, userCards)
    else:
        pass


def redrawAll(app, canvas):
    app.map.draw(canvas)
    app.player.drawPlayerCards(canvas)


def main():
    runApp(width=800, height=600)


if __name__ == '__main__':
    main()
