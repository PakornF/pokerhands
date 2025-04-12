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
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set Screen Resolution
        pygame.display.set_caption(TITLE_STRING)                # Set Window resolution
        self.game_active = False
        self.get_player_name_state = False
        self.curr_player_index = 0
        # self.player_names = ["",""]
        self.system = Hand()
        self.chk_card_state = False
        self.preflop = False
        self.flop = False
        self.turn = False

    def run(self):
        act_font = pygame.font.Font(GAME_FONT, 80)
        for i in range(len(self.system.player_list)):
            if self.system.player_list[i].small_blind == True:
                self.curr_player_index = i
        while self.game_active is True:
            while self.preflop is True:
                self.screen.fill(BG_COLOR)
                # Render Player Turn
                turn_txt = act_font.render(f"{self.system.player_list[self.curr_player_index].name}'s Turn", True, (255, 255, 255))
                turn_rect = turn_txt.get_rect(center=(240, HEIGHT//2))
                self.screen.blit(turn_txt, turn_rect)
                # Render Action Button
                call_txt = act_font.render("Call", True, (255, 255, 255))
                bet_txt = act_font.render("Bet", True, (255, 255, 255))
                raise_txt = act_font.render("Raise", True, (255, 255, 255))
                fold_txt = act_font.render("Fold", True, (255, 255, 255))
                all_in_txt = act_font.render("All in", True, (255, 255, 255))
                check_txt = act_font.render("Check", True, (255, 255, 255))

                call_rect = call_txt.get_rect(center=(400, HEIGHT-50))
                bet_rect = bet_txt.get_rect(center=(650, HEIGHT-50))
                raise_rect = raise_txt.get_rect(center=(900, HEIGHT-50))
                fold_rect = fold_txt.get_rect(center=(1150, HEIGHT-50))
                all_in_rect = all_in_txt.get_rect(center=(1400, HEIGHT-50))
                check_rect = check_txt.get_rect(center=(1650, HEIGHT-50))

                self.screen.blit(call_txt, call_rect)
                self.screen.blit(bet_txt, bet_rect)
                self.screen.blit(raise_txt, raise_rect)
                self.screen.blit(fold_txt, fold_rect)
                self.screen.blit(all_in_txt, all_in_rect)
                self.screen.blit(check_txt, check_rect)
                # Render Community Pot
                pot_txt = act_font.render(f"Pot: {self.system.pot}", True, (255, 255, 255))
                pot_rect = pot_txt.get_rect(center=(WIDTH // 2, 100))
                self.screen.blit(pot_txt, pot_rect)
                # Render Player's Pot
                for i in range(len(self.system.player_list)):
                    player_pot_txt = act_font.render(f"{self.system.player_list[i].name}'s Pot: {self.system.player_list[i].chips}", True, (255, 255, 255))
                    player_pot_rect = player_pot_txt.get_rect(center=(WIDTH*(2*i+1)//4, 100))
                    self.screen.blit(player_pot_txt, player_pot_rect)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if call_rect.collidepoint(event.pos):
                            print(f"Call is pressed")
                        elif bet_rect.collidepoint(event.pos):
                            current_player = self.system.player_list[self.curr_player_index]
                            self.system.bet(current_player, 100)
                        elif raise_rect.collidepoint(event.pos):
                            print(f"Raise is pressed")
                        elif fold_rect.collidepoint(event.pos):
                            print(f"Fold is pressed")
                        elif all_in_rect.collidepoint(event.pos):
                            print(f"All in is pressed")
                        elif check_rect.collidepoint(event.pos):
                            print(f"Check is pressed")
                
                pygame.display.update()
    def chk_card(self):
        while self.chk_card_state is True:
            self.screen.fill(BG_COLOR)
            # Render Text
            player_card_font = pygame.font.Font(GAME_FONT, 100)
            player_card_txt = player_card_font.render(f"{self.system.player_list[self.curr_player_index].name}, Remember Your Cards", True, (255, 255, 255))
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
                        if self.curr_player_index <= 1:
                            self.curr_player_index = (self.curr_player_index + 1) % 2
                            self.chk_card()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_rect.collidepoint(event.pos):
                        self.chk_card_state = False
                        print("Start Playing")
                        self.game_active = True
                        self.preflop = True
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
                text_surface = input_font.render(self.system.player_list[i].name, True, (255, 255, 255))
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
                        print("Game Start")
                        self.chk_card_state = True
                        self.curr_player_index = 0
                        self.system.dealer.deal_card_for_each_player()
                        self.chk_card()
                    elif event.key == pygame.K_BACKSPACE:
                        self.system.player_list[self.curr_player_index].name = self.system.player_list[self.curr_player_index].name[:-1]
                    else:
                        # Limit name length to 15 characters
                        if len(self.system.player_list[self.curr_player_index].name) < 15:
                            self.system.player_list[self.curr_player_index].name += event.unicode

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