# Sentence Match Memory Game (Python/Pygame)

This is a classic card-matching memory game, converted from a web-based version (HTML/CSS/JS) to a complete desktop application using Python and the Pygame library.

## Description

The objective of the game is to find all the matching pairs of cards. Instead of matching images, players match the two halves of a sentence. The game tracks the number of moves, and when all pairs are found, it presents a "Game Over" screen with an option to play again.

This project serves as a practical example of software porting, code structuring, and phased development for building a game from the ground up.

## Features

- **Classic Memory Gameplay:** Flip cards to find matching pairs.
- **Sentence Matching:** A unique twist where you match parts of sentences.
- **Move Counter:** Tracks the number of moves made during the game.
- **Game Over and Replay:** A clear end-state with a "Play Again" button for continuous play.
- **Clean, Centered UI:** The game board and elements are dynamically centered on the screen.

## Screenshot

*(You can add a screenshot of the game running here)*

![Game Screenshot](placeholder.png)

## Requirements

- Python 3.x
- Pygame

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-folder>
    ```

2.  **Install the required library (Pygame):**
    ```bash
    pip install pygame
    ```
    *Or, if you use a `requirements.txt` file: `pip install -r requirements.txt`*

## How to Run

To start the game, simply run the `game.py` script from your terminal:

```bash
python3 game.py
```

## Development Process

The development of this game followed a structured, phased approach:

1.  **Phase 0: Skeleton Setup:** Established the basic Pygame window and game loop.
2.  **Phase 1: Core Object:** Created the `Card` class with its own state and drawing logic.
3.  **Phase 2: Board Generation:** Implemented the dynamic creation and shuffling of the game board.
4.  **Phase 3: Gameplay Logic:** Added interactivity, click handling, pair matching, and the flip-back timer.
5.  **Phase 4: Final Touches:** Implemented the move counter, game-over state, and the "Play Again" functionality.
