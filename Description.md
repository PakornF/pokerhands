# Poker
A simple Plaver VS Bot Python-based poker game that determines the best hand among players. This project utilizes Pygame for the graphical interface and implements core poker logic to evaluate hand rankings.
# Project VERSION 1.0

![Poker Hands Image](screenshots/gameplay/Showdown.png)

## Installation

1. Clone the Repository:
```sh
git clone https://github.com/PakornF/pokerhands.git
cd pokerhands
```
2. Install Required Packages
```sh
pip install -r requirements.txt
```

## Gameplay Instruction
- Starting the Game: Type this in the terminal to launch the game window.
  ```sh
  game.py
  ```
- Player Actions: Use the on-screen buttons or keyboard inputs to perform actions.
- Winning: The game evaluates all hands and declares the winner at the end of each round.

## Project Structure
- cards.py: Contains classes and functions related to card representations.
- cfr.py: Implements the Counterfactual Regret Minimization(CFR) algorithm for strategy optimization.
- data.py: Manages data structures and utilities.
- game.py: Main game loop and event handling.
- gamelogic.py: Core logic for evaluating poker hands.
- ui.py: Handles the graphical user interface using Pygame.
- visualize.py: Functions for visualizing game data and statistics.
- game_data.csv: Dataset after collecting

## Contact
Created by PakornF. Feel free to reach out for any questions or collaborations.
