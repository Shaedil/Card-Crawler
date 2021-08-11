import random
# from cmu 112 course notes
from cmu_112_graphics import *


# https://stackoverflow.com/questions/8924173/how-do-i-print-bold-text-in-python
# https://ss64.com/nt/syntax-ansi.html
class Color(object):
    # common foreground colors
    RED =       '\033[91m'
    GREEN =     '\033[92m'
    YELLOW =    '\033[93m'
    BLUE =      '\033[94m'
    PURPLE =    '\033[95m'
    CYAN =      '\033[96m'
    DARKCYAN =  '\033[36m'
    # common background colors
    BG_RED =    '\033[101m'
    BG_GREEN =  '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE =   '\033[104m'
    BG_PURPLE = '\033[105m'
    BG_CYAN =   '\033[106m'
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
            print("You don't have a sword card. You can't attack.")
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
            print("You don't have a heal card. You can't heal.")
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
            print("You don't have a shield card. You can't shield.")
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
            print("You don't have a coin card. You can't use it.")
            return 0
        else:
            self.app.isPlayerTurn = not self.app.isPlayerTurn
            return cards

    def useCard(self, card):
        self.cards.pop(self.cards.index(card))

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
            print("You don't have a sword card. You can't attack.")
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
            print("You don't have a shield card. You can't shield.")
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
    
    def enemyTurn(self):
        if self.enemy.health > 0 and self.player.health > 0:
            # TODO: replace below line of code with probabilistic choice based
            # on player's health
            # if enemy still has cards left:
            if len(self.enemy.cards) > 0:
                card = random.choice(self.enemy.cards)
            else:
                card = self.enemyCard.getRandomCard()
                self.enemy.cards.append([card[0], card[1]])
                self.enemy.health -= 1
            if card[0] == 'sword':
                attack = self.enemy.attack()
                self.player.health -= attack
                print(f'Enemy attacked for {attack} points')
            elif card[0] == 'heal':
                heal = self.enemy.heal()
                self.enemy.health += heal
                if self.enemy.health > self.enemy.maxHealth:
                    self.enemy.health = self.enemy.maxHealth
                print(f'Enemy healed for {heal} points')
            elif card[0] == 'shield':
                shield = self.enemy.shield()
                self.enemy.health += shield
                print(f'Enemy shielded for {shield} points')
            elif card[0] == 'coin':
                for i in range(self.enemy.coin()):
                    suit = self.enemyCard.getRandomCard()[0]
                    num = self.enemyCard.getRandomCard()[1]
                    self.enemy.cards.append([suit, num])
            else:
                print(f"Enemy card '{card[0]}' not recognized.")
        elif self.enemy.health <= 0:
            print("Enemy is dead.")
            self.app.inBattle = False
            self.app.isPlayerTurn = True
        elif self.player.health <= 0:
            print("Player is dead.")
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
                # return True
            elif event.key == 'h':
                self.player.health += self.player.heal()
                if self.player.health > self.player.maxHealth:
                    self.player.health = self.player.maxHealth
                # return True
            elif event.key == 's':
                self.player.health += self.player.shield()
                # return True
            elif event.key == 'c':
                for i in range(self.player.coin()):
                    suit = self.playerCard.getRandomCard()[0]
                    num = self.playerCard.getRandomCard()[1]
                    self.player.cards.append([suit, num])
                # return True
            # else:
                # return False
        elif self.enemy.health <= 0:
            print("Enemy is dead.")
            self.app.inBattle = False
            self.app.isPlayerTurn = True
        return


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
    app.battle = None
    app.enemy = None
    app.inBattle = False
    app.isPlayerTurn = True
    app.isGameOver = False

def mousePressed(app, event):
    # if the player clicks on a card, reveal the card
    pass

def keyPressed(app, event):
    if event.key == 'q':
        app.quit()
    if event.key == 'r':
        appStarted(app)
    if app.isGameOver:
        print("Game Over")
        # TODO: show end screen here
    if event.key == 'e':
        app.inBattle = not app.inBattle
        userCards = []
        card = EnemyCard()
        for i in range(5):
            suit = card.getRandomCard()[0]
            num = card.getRandomCard()[1]
            userCards.append([suit, num])
        # TODO: health for now is going to be random
        health = random.randint(1, 10)
        enemyCard = ['hearts', health]
        app.enemy = Enemy(app, enemyCard, userCards)
        app.battle = Battle(app, app.player, app.enemy)
        # TODO: start a battle to show off the battle mechanics
        # battle mechanics not implemented yet
    if app.inBattle and event.key in ['a','h','c','s', '.']:
        app.battle.playerTurn(event)
        app.isPlayerTurn = False


def timerFired(app):
    if app.isGameOver == False:
        if app.player.health <= 0:
            print("Player is dead.")
            app.inBattle = False
            app.isPlayerTurn = True
            app.isGameOver = True
        if app.inBattle and not app.isPlayerTurn:
            app.battle.enemyTurn()
            app.isPlayerTurn = True
    else:
        print('play again?')
        app.quit()
    

def redrawAll(app, canvas):
    if app.inBattle:
        app.battle.draw(canvas)
    else:
        app.map.draw(canvas)
    app.player.drawPlayerCards(canvas)


def main():
    runApp(width=800, height=600)


if __name__ == '__main__':
    main()
