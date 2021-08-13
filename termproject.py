import random
import collections
import pygame
from os import path
# graphics library from cmu 112 course notes and all subsequent course notes
# 'builtin' functions provided by this library: appStarted, mousePressed,
# keyPressed, timerFired, redrawAll, and main
from cmu_112_graphics import *

# music is by "dwarf fortress" game 


class Color(object):
    # https://stackoverflow.com/questions/8924173/how-do-i-print-bold-text-in-python
    # https://ss64.com/nt/syntax-ansi.html
    # common foreground colors
    RED =       '\033[91m'
    GREEN =     '\033[92m'
    YELLOW =    '\033[93m'
    BLUE =      '\033[94m'
    PURPLE =    '\033[95m'
    CYAN =      '\033[96m'
    # default
    BOLD =      '\033[1m'
    UNDERLINE = '\033[4m'
    END =       '\033[0m'


class Card(object):
    def __init__(self, suit, number, width=175, height=200):
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
        super().__init__(['hearts', 'spades', 'diamonds', 'clubs'],
                         [[i] for i in range(1, 14)], 75, 100)

    def drawMapCard(self, app, canvas, col, row):
        # check if app.map.mapGrid[row][col] is > 10, if it is, it's face up
        # else: it's face down
        if (app.map.mapGrid[row][col] > 10):
            canvas.create_rectangle(app.marginHorizontal + col * app.mapCardWidth,
                            app.marginVertical + (row * app.mapCardHeight),
                            app.marginHorizontal + (col + 1) * app.mapCardWidth,
                            app.marginVertical + ((row + 1) * app.mapCardHeight),
                            fill='lightgray')
            canvas.create_text(app.marginHorizontal + col * app.mapCardWidth + app.mapCardWidth / 2,
                               app.marginVertical + (row * app.mapCardHeight) + app.mapCardHeight / 2,
                               text=f'{self.suit[(app.map.mapGrid[row][col]%10) - 1]}',
                               font='Helvetica 9 bold', fill='black')
        else:
            canvas.create_rectangle(app.marginHorizontal + col * app.mapCardWidth,
                            app.marginVertical + (row * app.mapCardHeight),
                            app.marginHorizontal + (col + 1) * app.mapCardWidth,
                            app.marginVertical + ((row + 1) * app.mapCardHeight),
                            fill='maroon')


class PlayerCard(Card):
    def __init__(self):
        # these cards are visible at the bottom of screen
        super().__init__(['sword', 'coin', 'shield', 'heal'],
                         [j for j in range(1, 14)])

    def getRandomCard(self):
        # return a random card from the list of cards
        cardNum = random.choice(self.number)
        cardSuit = random.choice(self.suit)
        return [cardSuit, cardNum]


class EnemyCard(Card):
    def __init__(self):
        # these cards are visible at the bottom of screen
        super().__init__(['sword', 'coin', 'shield', 'heal'],
                         [j for j in range(1, 10)])

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
        self.buildBridgeFromIslandMapCard()
        self.assignRoomTypes()

    def draw(self, canvas):
        # draw the map
        for row in range(len(self.mapGrid)):
            for col in range(len(self.mapGrid[row])):
                if self.mapGrid[row][col] % 10 in [1, 2, 3, 4]:
                    MapCard().drawMapCard(self.app, canvas, col, row)


class Hint(object):
    def __init__(self, app):
        self.app = app

    def getMinDistance(self, grid, playerPosition):
        # using bfs and queue to find the min distance from start point to
        # treasure
        # https://stackoverflow.com/questions/47896461/get-shortest-path-to-a-cell-in-a-2d-array-in-python
        # create a queue from playerPosition
        queue = collections.deque([[playerPosition]])
        # count currPosition as seen
        seen = set([playerPosition])
        while queue:
            # get the first element in queue, first in first out
            path = queue.popleft()
            x, y = path[-1]
            if grid[x][y] == 4:
                # if we reach treasure, return how far away it is
                return f"You are {len(path)} spaces away from the treasure!"
            # check all cardinal directions of current position
            for newX, newY in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                # if we are not heading out of bounds (in a wall) and we have
                # not seen this cell before, then add it to queue
                if (0 <= newX < self.app.map.width and 
                   0 <= newY < self.app.map.height and
                   grid[newY][newX] != 0 and (newX, newY) not in seen):
                    queue.append(path + [(newX, newY)])
                    seen.add((newX, newY))
        return 'The dungeon\'s magic is too powerful, you must land on a hearts or trick card to change the dungeon.'


class Player(object):
    def __init__(self, app, x, y, cards):
        # mapX and mapY are the coordinates of the player's starting position
        # on the map
        self.app = app
        self.x = x
        self.y = y
        self.app.map.mapGrid[self.x][self.y] += 10
        # reveal whatever card is below x, y in MapGrid
        # cards is a list of lists: [ [suit, num] ]
        self.cards = cards
        # health is randomized between 1 and 14 --> represents regular card
        # numbers
        health = random.randint(5, 14)
        # maxHealth will be used later to check against using healing cards to
        # buff HP above max amount.
        self.maxHealth = health
        self.health = health

    def move(self, dx, dy):
        # dx and dy are the distances the player will move in the x and y
        # directions, respectively
        if (self.x + dx >= 0 and self.x + dx < self.app.map.width and
            self.y + dy >= 0 and self.y + dy < self.app.map.height and
            self.app.map.mapGrid[self.x + dx][self.y + dy] % 10 != 0):
            self.x += dx
            self.y += dy
            self.activateMapCard(self.x, self.y)
            self.app.map.mapGrid[self.x][self.y] += 10

    def revealCard(self, event):
        for i in range(len(self.app.map.mapGrid)):
            for j in range(len(self.app.map.mapGrid[i])):
                if (event.x > (self.app.marginHorizontal + j * self.app.mapCardWidth) and 
                event.x < (self.app.marginHorizontal + (j + 1) * self.app.mapCardWidth) and 
                event.y > (self.app.marginVertical + i * self.app.mapCardHeight) and 
                event.y < (self.app.marginVertical + (i + 1) * self.app.mapCardHeight)):
                    if self.app.map.mapGrid[i][j] == 0 or self.app.map.mapGrid[i][j] > 10:
                        print(Color.RED + 'Please choose another card, you\'ve already picked this card or you picked a wall :|' + Color.RED)
                        return
                    self.app.map.mapGrid[i][j] += 10
                    self.app.inTrickCard = False
                    self.app.revealingCard = False
                    return

    def activateTrick(self, event):
        # activate the trick card that is selected
        if event.key == '1':
            # discard entire hand for new cards
            newCards = []
            card = PlayerCard()
            for i in range(len(self.cards)):
                suit = card.getRandomCard()[0]
                num = card.getRandomCard()[1]
                newCards.append([suit, num])
            self.cards = newCards
            # hide all cards on the map by modding them by 10
            for row in range(len(self.app.map.mapGrid)):
                for col in range(len(self.app.map.mapGrid[row])):
                    if self.app.map.mapGrid[row][col] % 10 in [1, 2, 3, 4]:
                        self.app.map.mapGrid[row][col] %= 10
            # now shuffle the map cards
            random.shuffle(self.app.map.mapGrid)
            self.app.inTrickCard = False
        elif event.key == '2':
            # choose a map card to reveal
            # use coords? use mousePressed?
            print(Color.GREEN + 'Please click on a card to reveal' + Color.END)
            self.app.inTrickCard = True
            self.app.revealingCard = True
        elif event.key == '3':
            # discards a random card to disarm trap and use normally
            print(Color.GREEN + 'You\'ve successfully disarmed the trap!' + Color.END)
            if len(self.cards) != 0:
                card = random.choice(self.cards)
                self.cards.pop(self.cards.index(card))
            self.app.inTrickCard = False
        else:
            print("Invalid key")
    
    def activateRest(self, event):
        if event.key == 'y':
            newCards = []
            card = PlayerCard()
            for i in range(2):
                suit = card.getRandomCard()[0]
                num = card.getRandomCard()[1]
                newCards.append([suit, num])
            self.cards += newCards
            # hide all cards on the map by modding them by 10
            for row in range(len(self.app.map.mapGrid)):
                for col in range(len(self.app.map.mapGrid[row])):
                    if self.app.map.mapGrid[row][col] % 10 in [1, 2, 3, 4]:
                        self.app.map.mapGrid[row][col] %= 10
            # now shuffle the map cards
            random.shuffle(self.app.map.mapGrid)
            self.app.inRest = False
        else:
            print(Color.YELLOW + "Bravely, you head on without rest" + Color.END)
            self.app.inRest = False
    
    def activateMapCard(self, row, col):
        if self.app.map.mapGrid[row][col] == 1:
            # hearts - do nothing/rest
            print(Color.YELLOW + 'Do you want to rest? You can draw two new cards if you do, but the map will be shuffled' + Color.END)
            print(Color.PURPLE + "Press 'y' or 'n' to confirm or deny" + Color.END)
            self.app.inRest = True
        if self.app.map.mapGrid[row][col] == 2:
            # spades - trick choice
            print(Color.PURPLE + 'You\'ve landed on a trap card, pick a trick using your keys:' + Color.END)
            print(Color.CYAN + '1. ' + Color.YELLOW + 'Discard entire hand for the same amount of new cards' + Color.END)
            print(Color.CYAN + '2. ' + Color.YELLOW + 'Choose a map card to reveal' + Color.END)
            print(Color.CYAN + '3. ' + Color.YELLOW + 'Disarm trick for a random card in your deck' + Color.END)
            self.app.inTrickCard = True
        if self.app.map.mapGrid[row][col] == 3:
            # diamonds - enemy with health equal to card num
            cards = []
            card = EnemyCard()
            for i in range(5):
                suit = card.getRandomCard()[0]
                num = card.getRandomCard()[1]
                cards.append([suit, num])
            health = random.randint(3, 14)
            enemyHealth = ['hearts', health]
            self.app.enemy = Enemy(self.app, enemyHealth, cards)
            self.app.battle = Battle(self.app, self, self.app.enemy)
            self.app.inBattle = True
        if self.app.map.mapGrid[row][col] % 10 == 4:
            # clubs - win state
            self.app.gameOverStatus = "You win!"
            self.app.isGameOver = True

    def attack(self):
        found = 0
        damage = 0
        for card in self.cards:
            if 'sword' in card[0]:
                found += 1
                damage = card[1]
                self.useCard(card)
                break
        if not found:
            print(Color.RED + "You don't have a sword card. You can't attack." + Color.END)
            return 0
        else:
            self.app.isPlayerTurn = not self.app.isPlayerTurn
            return damage
        
    def heal(self):
        found = 0
        health = 0
        for card in self.cards:
            if 'heal' in card[0]:
                found += 1
                health = card[1]
                self.useCard(card)
                break
        if not found:
            print(Color.RED + "You don't have a heal card. You can't heal." + Color.END)
            return 0
        else:
            self.app.isPlayerTurn = not self.app.isPlayerTurn
            return health

    def shield(self):
        found = 0
        shield = 0
        for card in self.cards:
            if 'shield' in card[0]:
                found += 1
                shield = card[1]
                self.useCard(card)
                break
        if not found:
            print(Color.RED + "You don't have a shield card. You can't shield." + Color.END)
            return 0
        else:
            self.app.isPlayerTurn = not self.app.isPlayerTurn
            return shield

    def coin(self):
        found = 0
        cards = 0
        for card in self.cards:
            if 'coin' in card[0]:
                found += 1
                cards = (card[1] // 5) + 1
                self.useCard(card)
                break
        if not found:
            print(Color.RED + "You don't have a coin card. You can't use it." + Color.END)
            return 0
        else:
            self.app.isPlayerTurn = not self.app.isPlayerTurn
            return cards

    def useCard(self, card):
        self.cards.pop(self.cards.index(card))

    def drawCurrentPlayerLocation(self, canvas):
        canvas.create_rectangle(self.app.marginHorizontal + self.y * self.app.mapCardWidth,
                        self.app.marginVertical + (self.x * self.app.mapCardHeight),
                        self.app.marginHorizontal + (self.y + 1) * self.app.mapCardWidth,
                        self.app.marginVertical + ((self.x + 1) * self.app.mapCardHeight),
                        fill='lightgray', outline='#EC701D', width=3)
        canvas.create_text(self.app.marginHorizontal + self.y * self.app.mapCardWidth + self.app.mapCardWidth / 2,
                           self.app.marginVertical + (self.x * self.app.mapCardHeight) + self.app.mapCardHeight / 2,
                           text=f'{MapCard().suit[(self.app.map.mapGrid[self.x][self.y]%10) - 1]}',
                           font='Helvetica 9 bold', fill='black')

    def drawPlayerCards(self, canvas):
        # draw the player's cards centered at bottom of screen
        leftMargin = (self.app.width - len(self.cards) * self.app.playerCardWidth) / 2
        for i in range(len(self.cards)):
            if self.cards[i][0] == 'heal':
                canvas.create_rectangle(leftMargin + i * self.app.playerCardWidth,
                                self.app.height - self.app.playerCardHeight,
                                leftMargin + (i + 1) * self.app.playerCardWidth,
                                self.app.height, fill='#D1E296')
            elif self.cards[i][0] == 'sword':
                canvas.create_rectangle(leftMargin + i * self.app.playerCardWidth,
                                self.app.height - self.app.playerCardHeight,
                                leftMargin + (i + 1) * self.app.playerCardWidth,
                                self.app.height, fill='#AF3636')
            elif self.cards[i][0] == 'coin':
                canvas.create_rectangle(leftMargin + i * self.app.playerCardWidth,
                                self.app.height - self.app.playerCardHeight,
                                leftMargin + (i + 1) * self.app.playerCardWidth,
                                self.app.height, fill='#E9C06E')
            elif self.cards[i][0] == 'shield':
                canvas.create_rectangle(leftMargin + i * self.app.playerCardWidth,
                                self.app.height - self.app.playerCardHeight,
                                leftMargin + (i + 1) * self.app.playerCardWidth,
                                self.app.height, fill='#2E6B69')
            else: return
            canvas.create_text(leftMargin + (i + 0.5) * self.app.playerCardWidth,
                               self.app.height - 2*(self.app.playerCardHeight/3),
                               anchor='n', text=f'{str(self.cards[i][0])} {self.cards[i][1]}',
                               font=('Helvetica 15 bold'))


class Enemy(object):
    def __init__(self, app, selfCard, cards):
        self.app = app
        self.cards = cards
        self.selfCard = selfCard
        self.maxHealth = selfCard[1]
        self.health = self.maxHealth
    
    def attack(self):
        found = 0
        damage = 0
        for card in self.cards:
            if 'sword' in card[0]:
                found += 1
                damage = card[1]
                self.useCard(card)
                break
        if not found:
            print(Color.GREEN + "Enemy is confused and could not attack" + Color.END)
            return 0
        else:
            self.app.isPlayerTurn = not self.app.isPlayerTurn
            return damage

    def shield(self):
        found = 0
        shield = 0
        for card in self.cards:
            if 'shield' in card[0]:
                found += 1
                shield = card[1]
                self.useCard(card)
                break
        if not found:
            print(Color.GREEN + "Enemy is confused and could not shield." + Color.END)
            return 0
        else:
            self.app.isPlayerTurn = not self.app.isPlayerTurn
            return shield

    def heal(self):
        found = 0
        health = 0
        for card in self.cards:
            if 'heal' in card[0]:
                found += 1
                health = card[1]
                self.useCard(card)
                break
        if not found:
            print("You don't have a heal card. You can't heal.")
            return 0
        else:
            self.app.isPlayerTurn = not self.app.isPlayerTurn
            return health

    def coin(self):
        found = 0
        cards = 0
        for card in self.cards:
            if 'coin' in card[0]:
                found += 1
                cards = (card[1] // 5) + 1
                self.useCard(card)
                break
        if not found:
            print("You don't have a coin card. You can't use it.")
            return 0
        else:
            self.app.isPlayerTurn = not self.app.isPlayerTurn
            return cards

    def useCard(self, card):
        self.cards.pop(self.cards.index(card))


class Battle(object):
    def __init__(self, app, player, enemy):
        self.player = player
        self.enemy = enemy
        self.app = app
        self.enemyCard = EnemyCard()
        self.playerCard = PlayerCard()

    def draw(self, canvas):
        # clear screen of map
        canvas.create_rectangle(self.app.marginHorizontal, self.app.marginVertical,
                                self.app.marginHorizontal + 5 * self.app.mapCardWidth,
                                self.app.marginVertical + 5 * self.app.mapCardHeight,
                                fill='white')
        # draw enemy below
        canvas.create_oval(self.app.marginHorizontal + 2 * self.app.mapCardWidth,
                           self.app.marginVertical + 3.25 * self.app.mapCardHeight,
                           self.app.marginHorizontal + 3 * self.app.mapCardWidth,
                           self.app.marginVertical + 4 * self.app.mapCardHeight,
                           fill='red')
        canvas.create_text(self.app.marginHorizontal + 2.5 * self.app.mapCardWidth,
                           self.app.marginVertical + 4 * self.app.mapCardHeight,
                           anchor='n', text=f'Enemy Health: {self.enemy.health}',
                           font='Helvetica 14 bold')
        # draw player below
        canvas.create_oval(self.app.marginHorizontal + 2 * self.app.mapCardWidth,
                           self.app.marginVertical + 1 * self.app.mapCardHeight,
                           self.app.marginHorizontal + 3 * self.app.mapCardWidth,
                           self.app.marginVertical + 1.75 * self.app.mapCardHeight,
                           fill='blue')
        canvas.create_text(self.app.marginHorizontal + 2.5 * self.app.mapCardWidth,
                           self.app.marginVertical + 1.75 * self.app.mapCardHeight,
                           anchor='n', text=f'Your Health: {self.player.health}',
                           font='Helvetica 14 bold')

    def probabilisticChoice(self):
        # if enemy is lower than 50% HP, pick heal or shield card if no heal
        enemyRatio = self.enemy.health / self.enemy.maxHealth
        playerRatio = self.player.health / self.player.maxHealth
        if enemyRatio < 0.50:
            # heal
            if playerRatio >= 0.50:
                found = 0
                for i in range(len(self.enemy.cards)):
                    if 'heal' in self.enemy.cards[i][0]:
                        found += 1
                        return self.enemy.cards[i]
                if not found:
                    for i in range(len(self.enemy.cards)):
                        if 'shield' in self.enemy.cards[i][0]:
                            found += 1
                            return self.enemy.cards[i]
                if not found:
                    for i in range(len(self.enemy.cards)):
                        if 'coin' in self.enemy.cards[i][0]:
                            return self.enemy.cards[i]
            else:
                # attack
                found = 0
                for i in range(len(self.enemy.cards)):
                    if ('sword' in self.enemy.cards[i][0] and 
                        self.enemy.cards[i][1] in list(range(self.player.health-2, self.player.health+2))):
                        found += 1
                        return self.enemy.cards[i]
                if not found:
                    for i in range(len(self.enemy.cards)):
                        if 'heal' in self.enemy.cards[i][0]:
                            found += 1
                            return self.enemy.cards[i]
                if not found:
                    for i in range(len(self.enemy.cards)):
                        if 'shield' in self.enemy.cards[i][0]:
                            found += 1
                            return self.enemy.cards[i]
                if not found:
                    for i in range(len(self.enemy.cards)):
                        if 'coin' in self.enemy.cards[i][0]:
                                return self.enemy.cards[i]
            return random.choice(self.enemy.cards)
        else:
            # get a random card
            if len(self.enemy.cards) < 4:
                for i in range(len(self.enemy.cards)):
                    if 'coin' in self.enemy.cards[i][0]:
                        return self.enemy.cards[i]
            found = 0
            for i in range(len(self.enemy.cards)):
                if ('sword' in self.enemy.cards[i][0] and self.enemy.cards[i][1] in list(range(self.player.health-2, self.player.health+2))):
                    found += 1
                    return self.enemy.cards[i]
            if not found:
                for i in range(len(self.enemy.cards)):
                    if 'shield' in self.enemy.cards[i][0]:
                        found += 1
                        return self.enemy.cards[i]
            if not found:
                for i in range(len(self.enemy.cards)):
                    if 'heal' in self.enemy.cards[i][0]:
                        found += 1
                        return self.enemy.cards[i]
            return random.choice(self.enemy.cards)
    
    def enemyTurn(self):
        if self.enemy.health > 0 and self.player.health > 0:
            # if enemy still has cards left:
            if len(self.enemy.cards) > 0:
                card = self.probabilisticChoice()
            else:
                card = self.enemyCard.getRandomCard()
                self.enemy.cards.append([card[0], card[1]])
            print(Color.CYAN + f'Enemy picked card: {Color.UNDERLINE + card[0]} {card[1]}' + Color.END)
            if card[0] == 'sword':
                attack = self.enemy.attack()
                self.player.health -= attack
                print(Color.CYAN + f'Enemy attacked for {Color.RED + str(attack) + Color.CYAN} points' + Color.END)
            elif card[0] == 'heal':
                heal = self.enemy.heal()
                self.enemy.health += heal
                if self.enemy.health > self.enemy.maxHealth:
                    self.enemy.health = self.enemy.maxHealth
                print(Color.CYAN + f'Enemy healed for {Color.RED + str(heal) + Color.CYAN} points' + Color.END)
            elif card[0] == 'shield':
                shield = self.enemy.shield()
                self.enemy.health += shield
                print(Color.CYAN + f'Enemy shielded for {Color.RED + str(shield) + Color.CYAN} points' + Color.END)
            elif card[0] == 'coin':
                for i in range(self.enemy.coin()):
                    suit = self.enemyCard.getRandomCard()[0]
                    num = self.enemyCard.getRandomCard()[1]
                    self.enemy.cards.append([suit, num])
                print(Color.CYAN + f'Enemy bought cards!' + Color.END)
            else:
                print(Color.RED + f"Enemy card '{card[0]}' not recognized." + Color.END)
        elif self.enemy.health <= 0:
            print(Color.GREEN + "Enemy is dead." + Color.END)
            self.app.inBattle = False
            self.app.isPlayerTurn = True
        elif self.player.health <= 0:
            print(Color.RED + "Player is dead." + Color.END)
            self.app.inBattle = False
            self.app.isPlayerTurn = True
            self.app.isGameOver = True
        return

    def playerTurn(self, event):
        if self.player.health > 0 and self.enemy.health > 0:
            if len(self.player.cards) <= 0 or event.key == '.':
                card = self.playerCard.getRandomCard()
                self.player.cards.append([card[0], card[1]])
                self.player.health -= 1
            if event.key == 'a':
                self.enemy.health -= self.player.attack()
            elif event.key == 'h':
                self.player.health += self.player.heal()
                if self.player.health > self.player.maxHealth:
                    self.player.health = self.player.maxHealth
            elif event.key == 's':
                self.player.health += self.player.shield()
            elif event.key == 'c':
                for i in range(self.player.coin()):
                    suit = self.playerCard.getRandomCard()[0]
                    num = self.playerCard.getRandomCard()[1]
                    self.player.cards.append([suit, num])
        elif self.enemy.health <= 0:
            print("Enemy is dead.")
            self.app.inBattle = False
            self.app.isPlayerTurn = True
        return


def appStarted(app):
    app._root.resizable(False, False)
    pygame.mixer.init()
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
    startingPositionsList = []
    for i in range(app.map.width):
        if app.map.mapGrid[0][i] != 0:
            startingPositionsList.append([0, i])
    if not startingPositionsList:
        for i in range(app.map.width):
            if app.map.mapGrid[1][i] != 0:
                startingPositionsList.append([1, i])
    initPosition = random.choice(startingPositionsList)
    # initPosition should be hearts always
    app.map.mapGrid[initPosition[0]][initPosition[1]] = 1
    app.player = Player(app, initPosition[0], initPosition[1], userCards)
    app.starting = True
    app.battle = None
    app.enemy = None
    app.inBattle = False
    app.isPlayerTurn = True
    app.isGameOver = False
    app.gameOverStatus = None
    app.inTrickCard = False
    app.revealingCard = False
    app.inRest = False
    app.enableMusic = True

def mousePressed(app, event):
    # if the player clicks on a card, reveal the card
    if app.inTrickCard and app.revealingCard:
        app.player.revealCard(event) 

def keyPressed(app, event):
    if event.key == 'q':
        app.quit()
    if event.key == 'r':
        appStarted(app)
        playMusic(app)
    if not app.isGameOver and not app.inBattle:
        if event.key == 'm':
            app.enableMusic = not app.enableMusic
            print(f"Music: {app.enableMusic}")
            playMusic(app)
        if app.inTrickCard:
            if event.key in ['1','2','3']:
                app.player.activateTrick(event)
        elif app.inRest:
            if event.key in ['y', 'n']:
                app.player.activateRest(event)
        else:
            if event.key == 'h':
                print(Hint(app).getMinDistance(app.map.mapGrid, (app.player.x, app.player.y)))
            if event.key == 'Up':
                app.player.move(-1, 0)
            elif event.key == 'Down':
                app.player.move(1, 0)
            elif event.key == 'Left':
                app.player.move(0, -1)
            elif event.key == 'Right':
                app.player.move(0, 1)
    if app.inBattle and event.key in ['a','h','c','s','.']:
        app.battle.playerTurn(event)
        app.isPlayerTurn = False



def playMusic(app):
    if (app.enableMusic == True and app.isGameOver == False):
        if path.exists("song.mp3"):
            pygame.mixer.music.load("song.mp3")
            pygame.mixer.music.play(-1)  # repeat indefinitely
        else:
            print(Color.RED + Color.BOLD + 'Error 404: tetris.mid Not Found' +
                Color.END)
            print(Color.RED + Color.BOLD +
                'Please Load Floppy Disk Containing song.mp3' + Color.END)
            print(Color.YELLOW + 
                'p.s. put tetris.mid in the same folder as termproject.py' + Color.END)
    else:
        stopMusic()


def stopMusic():
    pygame.mixer.music.stop()
    pygame.display.quit()


def timerFired(app):
    if app.isGameOver == False:
        if app.player.health <= 0:
            print("Player is dead.")
            app.inBattle = False
            app.isPlayerTurn = True
            app.isGameOver = True
            app.gameOverStatus = "You died."
        if app.inBattle and not app.isPlayerTurn:
            app.battle.enemyTurn()
            app.isPlayerTurn = True
    else:
        stopMusic()

def drawEndScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill='black')
    canvas.create_text(app.width/2, app.height/2, text=f"Game Over, {app.gameOverStatus}", font="Arial 26 bold", fill='white', anchor='s')
    canvas.create_text(app.width/2, app.height/2, text="Press 'r' to restart or 'q' to quit", font="Arial 26 bold", fill='white', anchor='n')

def redrawAll(app, canvas):
    if not app.isGameOver:
        if app.inBattle:
            app.battle.draw(canvas)
        else:
            app.map.draw(canvas)
            app.player.drawCurrentPlayerLocation(canvas)
        app.player.drawPlayerCards(canvas)
    else:
        drawEndScreen(app, canvas)


def main():
    runApp(width=800, height=600)


if __name__ == '__main__':
    main()
