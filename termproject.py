import math
import random
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


class PlayerCard(Card):
    def __init__(self):
        # these cards are visible at the bottom of screen
        super().__init__(175, 200, ['sword', 'coin', 'shield', 'heal'],
                         [[j] for j in range(1, 14)])
    
    def getRandomCard(self):
        # return a random card from the list of cards
        cardNum = random.choice(self.number)
        cardSuit = random.choice(self.suit)
        return {'Suit': cardSuit, 'Number': cardNum}

    def draw(self, canvas):
        # draw the card
        cardCenter = (self.width / 2, self.height / 2)
        cardPoints = [cardCenter]
        cardPoints.append((self.width / 2 + self.width * 0.25, self.height / 2 + self.height * 0.25))
        cardPoints.append((self.width / 2 + self.width * 0.25, self.height / 2 - self.height * 0.25))
        cardPoints.append((self.width / 2 - self.width * 0.25, self.height / 2 - self.height * 0.25))
        cardPoints.append((self.width / 2 - self.width * 0.25, self.height / 2 + self.height * 0.25))
        cardPoints.append(cardCenter)
        canvas.create_polygon(cardPoints, fill='white', outline='black')


class Map(object):
    def __init__(self, width, height, app):
        self.width = width
        self.height = height
        self.app = app
        # init an empty map grid so we can place cards onto it
        self.mapGrid = [[0, 0, 0, 0, 0] for i in range(5)]

    def makeMap(self):
        # take self.mapGrid and place 1s in a maze like way
        # use krimskal's algorithm later
        self.mapGrid = [[0, 1, 0, 0, 3],
                        [1, 2, 3, 1, 1],
                        [0, 1, 0, 3, 0],
                        [4, 2, 3, 2, 0],
                        [1, 0, 0, 1, 0]]

    def draw(self, canvas):
        # draw the map
        for row in range(len(self.mapGrid)):
            for col in range(len(self.mapGrid[row])):
                if self.mapGrid[row][col] in [1, 2, 3, 4]:
                    canvas.create_rectangle(self.app.marginHorizontal + 
                    col * 56, self.app.marginVertical + (row * 75),
                    self.app.marginHorizontal + (col + 1) * 56,
                    self.app.marginVertical + ((row + 1) * 75), fill='maroon')


class Player(object):
    def __init__(self, x, y, startingCards):
        # mapX and mapY are the coordinates of the player's starting position
        # on the map
        self.x = x
        self.y = y
        self.startingCards = startingCards
        # health is randomized between 1 and 14 --> represents regular card
        # numbers
        health = random.randint(1, 14)
        self.maxHealth = health
        self.health = health
        self.cards = {'heal': self.startingCards[0],
                      'shield': self.startingCards[1],
                      'coin': self.startingCards[2],
                      'sword': self.startingCards[3]}

    def move(self, dx, dy):
        # dx and dy are the distances the player will move in the x and y
        # directions, respectively
        # if move not illegal, move player
        self.x += dx
        self.y += dy
    
    def drawPlayerCards(self, canvas):
        # draw the player's cards
        pass


def appStarted(app):
    app._root.resizable(False, False)
    app.timerDelay = 100
    app.marginHorizontal = 260
    app.marginVertical = 20
    mapWidth = app.width
    mapHeight = app.height
    app.map = Map(mapWidth, mapHeight, app)
    app.map.makeMap()
    app.player = Player(0, 0, [PlayerCard(), PlayerCard(),
                               PlayerCard(), PlayerCard()])


def mousePressed(app, event):
    pass


def keyPressed(app, event):
    if event.key == 'q':
        app.quit()


def timerFired(app):
    pass


def redrawAll(app, canvas):
    app.map.draw(canvas)


def main():
    runApp(width=800, height=600)


if __name__ == '__main__':
    main()
