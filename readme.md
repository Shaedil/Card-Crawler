<!-- ┌─────────────┐ -->
<!-- │Term Project │ -->
<!-- └─────────────┘ -->
<!-- ┌──────────────┐ -->
<!-- │D&D Card Game │ -->
<!-- └──────────────┘ -->
# 15-112 Term Project - Card Crawler

## Project Description

Card Crawler is an original card-based dungeon crawler game created by me. The goal of the game is to find the hidden treasure in the dungeon by traversing through the rooms that are represented by playing cards. Certain rooms grant certain abilities to the player. For instance, landing on hearts allows the player to rest. Landing on diamonds however, immediately puts the player into combat. In combat, the player has a number of special cards that allow the player to heal, fight, get more cards, and defend. The enemy will attack, defend, and heal when possible.

## Structural Plan

- one function to create the overworld map.
  - generating a legal maze
  - difficulty level controlled by probability of spawning rest cards
- one class to control the player and movement throughout the map
- one class to control Player cards: `heal, shield, coin, sword`
- one function to create the room map, based on the 4 preset suits of card: `hearts, spades, diamonds, clubs`
  - `hearts`: do nothing/rest = hide all map cards and rearrange them but you get to draw two new cards
  - `spades`: trick choice: discard entire hand for new cards, choose a map card to reveal, move one map card to another place of choosing.
  - `diamonds`: enemy with health denoted by card number
  - `clubs`: treasure/exit
- one function in Player class for displaying player cards
- one function in Map class for displaying map cards
- one class for enemy and enemy ai (shielding/attacking/healing/coining)

## Algorithmic Plan

- Trickiest parts of the project (in order of high complexity to low complexity)
  - Implementing legal maze generation
    - Approach: Krimskal's algorithm or random assignment of rooms
  - Implementing enemy AI
    - Approach: analysis of player's actions
  - Implementing reactive ui elements
    - Approach: mousePressed w/ object detection (standard)

## Version Control Plan

- I will be using GitHub for my versioning control

![](screenshot.png)

## TP2 Update

- Use Aldous-Broder maze generation algorithm instead of Krimskal's algorithm.
- Use keys instead of mouse clicks to control elements.

## TP3 Update

- Improve enemy AI through more states
- Improve player navigation through map
- Add all tricks to the game
- Add end screen
- Add BFS powered hint engine
- Improve UI colorscheme

## How To Play

**There are two states to the game that you can be in: in the map or in battle.**

**In the map**, you must use arrow keys to move your player around the cards and
explore the dungeon.

When you encounter a spades card, you must press one of three number keys to activate an ability of a trick

When you encounter a hearts card, you must press 'y' or 'n' to confirm your choice of healing.

When you encounter a clubs card, you will have found the treasure and you win.

When you encounter a diamonds card, you will be put into a battle, with one enemy of a random amount of health.

While you are in the map, you can press 'h' to get a hint as to where the treasure might be.

A reminder that you cannot use your combat cards outside of battle.

**In battle**, you have the choice of picking any type of card to play against the enemy.

To do so, you must press either of these keys on your keyboard to play either of your combat cards:

| Keys | Card Descriptions                                |
| ---- | ------------------------------------------------ |
| `a`  | Use your sword card to attack the enemy          |
| `h`  | Use your heal card to gain HP up to your max HP  |
| `s`  | Use your shield card to gain HP above max HP     |
| `c`  | Use your coin card to get (1-3) cards            |
| `.`  | Wait a turn to get 1 random card.                |

The goal of the game is to find the treasure, be aware that you may die or win suddenly.

I have coded up a short console log for the player to read in order to understand what exactly is happening and who is doing what.

PS: YOU WILL NEED PYGAME FOR THIS TO RUN

PSS: press 'm' to enable the music ;)

Good luck!
