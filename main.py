from hand import *
from cards import *
from settings import *
import ctypes, pygame, sys

# Maintain resolution regardless of Windows scaling settings
ctypes.windll.user32.SetProcessDPIAware()

class Game:
    def __init__(self):
        # General setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set Screen Resolution
        pygame.display.set_caption(TITLE_STRING)                # Set Window resolution
        self.clock = pygame.time.Clock()                        # Setup clock
        self.hand = Hand()                                      # Create Poker Hand Manager
        self.mouse_down = False                                 # Initial State
        self.game_active = False                                # Track if the game is active or in the menu
        self.show_player_hand = 0                               # Track which player's hand to show (0: Player 1, 1: Player 2)
        self.in_preflop = False                                 # Track if the game is in the preflop phase (before drawing Flop)
        self.player_names = ["Player 1", "Player 2"]            # Default player names
        self.active_input = 0                                   # Track which player name is being edited (0 or 1)

    def get_player_names(self):
        input_font = pygame.font.Font(GAME_FONT, 60)
        prompt_font = pygame.font.Font(GAME_FONT, 40)
        active = True
        
        # Input boxes
        input_boxes = [
            pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 50, 400, 60),
            pygame.Rect(WIDTH//2 - 200, HEIGHT//2 + 50, 400, 60)
        ]
        
        while active:
            self.screen.fill(BG_COLOR)
            
            # Render title
            title_font = pygame.font.Font(GAME_FONT, 80)
            title_text = title_font.render("Enter Player Names", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            self.screen.blit(title_text, title_rect)
            
            # Render prompts
            p1_prompt = prompt_font.render("Player 1:", True, (255, 255, 255))
            p2_prompt = prompt_font.render("Player 2:", True, (255, 255, 255))
            self.screen.blit(p1_prompt, (WIDTH//2 - 300, HEIGHT//2 - 50))
            self.screen.blit(p2_prompt, (WIDTH//2 - 300, HEIGHT//2 + 50))
            
            # Render input boxes
            for i, box in enumerate(input_boxes):
                color = (255, 255, 255) if i == self.active_input else (200, 200, 200)
                pygame.draw.rect(self.screen, color, box, 2)
                text_surface = input_font.render(self.player_names[i], True, (255, 255, 255))
                self.screen.blit(text_surface, (box.x + 5, box.y + 5))
            
            # Render continue button
            continue_font = pygame.font.Font(GAME_FONT, 50)
            continue_text = continue_font.render("Continue", True, (255, 255, 255))
            continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
            pygame.draw.rect(self.screen, (0, 100, 0), continue_rect)
            self.screen.blit(continue_text, continue_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if clicked on input boxes
                    for i, box in enumerate(input_boxes):
                        if box.collidepoint(event.pos):
                            self.active_input = i
                    
                    # Check if clicked on continue button
                    if continue_rect.collidepoint(event.pos):
                        active = False
                        self.game_active = True
                        self.hand.deal_initial_cards()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        active = False
                        self.game_active = True
                        self.hand.deal_initial_cards()
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_names[self.active_input] = self.player_names[self.active_input][:-1]
                    else:
                        # Limit name length to 15 characters
                        if len(self.player_names[self.active_input]) < 15:
                            self.player_names[self.active_input] += event.unicode
            
            pygame.display.update()
            self.clock.tick(FPS)

    def show_menu(self):
        menu_font = pygame.font.Font(GAME_FONT, 120)            # Setup Font, Size
        title_font = pygame.font.Font(GAME_FONT, 150)           # Setup Font, Size
        while not self.game_active:
            self.screen.fill(BG_COLOR)                            # While game is not active, fill the Background with BG_COLOR

            # Render title
            title_text = title_font.render("Texas Hold'em", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            self.screen.blit(title_text, title_rect)

            # Render menu options
            play_text = menu_font.render("Play", True, (255, 255, 255))
            play_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(play_text, play_rect)

            quit_text = menu_font.render("Quit", True, (255, 255, 255))
            quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
            self.screen.blit(quit_text, quit_rect)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = pygame.mouse.get_pos()
                        if play_rect.collidepoint(mouse_pos):
                            self.get_player_names()  # Get player names before starting
                        elif quit_rect.collidepoint(mouse_pos):
                            pygame.quit()
                            sys.exit()

            pygame.display.update()
            self.clock.tick(FPS)

    def run(self):
        self.start_time = pygame.time.get_ticks()               # Track Start Time

        # Show the menu before starting the game
        self.show_menu()

        while True:
            # Handle quit operation
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.mouse_down = True

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        if self.mouse_down:
                            self.mouse_down = False
                            mouse_pos = pygame.mouse.get_pos()
                            self.handle_mouse_click(mouse_pos)

            # Time variables
            self.delta_time = (pygame.time.get_ticks() - self.start_time) / 1000
            self.start_time = pygame.time.get_ticks()
            pygame.display.update()
            self.screen.fill(BG_COLOR)
            self.render_player_hand()
            self.render_next_button()
            # Game Flow
            if not self.in_preflop: # Flop not yet drawn, render play button
                self.render_play_button()
            else:
                self.hand.update()
            self.clock.tick(FPS)

    def render_player_hand(self):
        if self.show_player_hand == 0:
            player = self.hand.p1
            player_name = self.player_names[0]
        else:
            player = self.hand.p2
            player_name = self.player_names[1]

        # Render player name
        name_font = pygame.font.Font(GAME_FONT, 40)
        name_text = name_font.render(player_name, True, (255, 255, 255))
        name_rect = name_text.get_rect(midtop=(WIDTH // 2, 20))
        self.screen.blit(name_text, name_rect)

        for card in player.cards:
            self.screen.blit(card.card_surf, card.position)

    def render_next_button(self):
        button_font = pygame.font.Font(GAME_FONT, 60)
        next_button_text = button_font.render("Next", True, (255, 255, 255))
        next_button_rect = next_button_text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        pygame.draw.rect(self.screen, (0, 0, 0), next_button_rect)
        self.screen.blit(next_button_text, next_button_rect)

    def render_play_button(self):
        button_font = pygame.font.Font(GAME_FONT, 60)
        play_button_text = button_font.render("Play", True, (255, 255, 255))
        play_button_rect = play_button_text.get_rect(center=(WIDTH // 2, HEIGHT - 200))
        pygame.draw.rect(self.screen, (0, 0, 0), play_button_rect)
        self.screen.blit(play_button_text, play_button_rect)

    def handle_mouse_click(self, mouse_pos):
        # Check if the click is within the "Next" button area
        if HEIGHT - 150 <= mouse_pos[1] <= HEIGHT - 50:
            if WIDTH // 2 - 50 <= mouse_pos[0] <= WIDTH // 2 + 50:
                self.show_player_hand = (self.show_player_hand + 1) % 2

        # Check if the click is within the "Play" button area
        if HEIGHT - 250 <= mouse_pos[1] <= HEIGHT - 150:
            if WIDTH // 2 - 50 <= mouse_pos[0] <= WIDTH // 2 + 50:
                self.in_preflop = True  # Transition to preflop phase

if __name__ == '__main__':
    game = Game()
    game.run()