import asyncio
import platform
import pygame
from cards import Deck
from gamelogic import PokerGame
from ui import PokerUI
from data import DataLogger

FPS = 60
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

async def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Poker Game")
    clock = pygame.time.Clock()

    # Create game objects
    deck = Deck()
    logger = DataLogger()
    game = PokerGame(deck, logger)
    ui = PokerUI(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            ui.handle_event(event, game, logger)

        # Update game state
        game.update()

        # Draw UI
        screen.fill((0, 128, 0))  # Green background
        ui.draw(game)
        pygame.display.flip()

        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())