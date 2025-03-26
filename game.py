from hand import *
from cards import *
from settings import *
from system import *
import ctypes, pygame, sys

# Maintain resolution regardless of Windows scaling settings
ctypes.windll.user32.SetProcessDPIAware()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set Screen Resolution
        pygame.display.set_caption(TITLE_STRING)                # Set Window resolution
        self.game_active = False
        self.clock = pygame.time.Clock()
        self.get_player_name_state = False
        self.curr_player_index = 0
        self.player_names = ["",""]
        self.system = Hand()
        self.chk_card_state = False
        
    def run(self):
        while self.game_active:
            self.screen.fill(BG_COLOR)
            pygame.display.update()

    def chk_card(self):
        while self.chk_card_state is True:
            self.screen.fill(BG_COLOR)
            # Render Text
            player_card_font = pygame.font.Font(GAME_FONT, 100)
            player_card_txt = player_card_font.render(f"Player {self.curr_player_index + 1}, Remember Your Cards", True, (255, 255, 255))
            player_card_rect = player_card_txt.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            self.screen.blit(player_card_txt, player_card_rect)
            # Render Player's Card
            curr_player = self.system.player_list[self.curr_player_index]
            for card in curr_player.cards:
                self.screen.blit(card.card_surf, card.position)
            # Render Play Text
            play_font = pygame.font.Font(GAME_FONT, 100)
            play_text = play_font.render(f"PLAY", True, (255, 255, 255))
            play_rect = play_text.get_rect(center=(WIDTH - 100, HEIGHT - 50))
            self.screen.blit(play_text, play_rect)
            # Check for Event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.curr_player_index < 1:
                            self.curr_player_index += 1
                            self.chk_card()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_rect.collidepoint(event.pos):
                        print("Start Playing")
                        self.chk_card_state = False
                        self.game_active = True
                        self.run()
            pygame.display.update()        

    def get_player_name(self):
        input_font = pygame.font.Font(GAME_FONT, 60)
        # prompt_font = pygame.font.Font(GAME_FONT, 40)
        input_boxes = [pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 50, 400, 60),
                       pygame.Rect(WIDTH//2 - 200, HEIGHT//2 + 50, 400, 60)]
        while self.get_player_name_state: # self.get_player_name_state is set to True after press "PLAY"
            self.screen.fill(BG_COLOR)

            # Render Text
            title_font = pygame.font.Font(GAME_FONT, 100) # Setup Title Font
            title_text = title_font.render("Enter Player's Name", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            self.screen.blit(title_text, title_rect)
            # Render input boxes
            for i, box in enumerate(input_boxes):
                color = (255, 255, 255) if i == self.curr_player_index else (200, 200, 200)
                pygame.draw.rect(self.screen, color, box, 2)
                text_surface = input_font.render(self.player_names[i], True, (255, 255, 255))
                self.screen.blit(text_surface, (box.x + 5, box.y + 5))
            # Render Play Text
            play_font = pygame.font.Font(GAME_FONT, 75)
            play_text = play_font.render("[Press Enter to Play]", True, (255, 255, 255))
            play_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 100))
            self.screen.blit(play_text, play_rect)
            # Check for Event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if clicked on input boxes
                    for i, box in enumerate(input_boxes):
                        if box.collidepoint(event.pos) is True:
                            self.curr_player_index = i

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: # If "Enter" is pressed
                        self.get_player_name_state = False
                        # self.game_active = True
                        print("Game Start")
                        self.chk_card_state = True
                        self.curr_player_index = 0
                        self.system.dealer.deal_card_for_each_player()
                        self.chk_card()
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_names[self.curr_player_index] = self.player_names[self.curr_player_index][:-1]
                    else:
                        # Limit name length to 15 characters
                        if len(self.player_names[self.curr_player_index]) < 15:
                            self.player_names[self.curr_player_index] += event.unicode

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
                            self.get_player_name_state = True
                            self.get_player_name()
                        elif quit_rect.collidepoint(mouse_pos):
                            pygame.quit()
                            sys.exit()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.show_menu()