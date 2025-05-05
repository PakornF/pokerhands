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
        self.act_font = pygame.font.Font(GAME_FONT, 80)    # Set Font

        self.game_active = False
        self.get_player_name_state = False
        self.chk_card_state = False
        self.setup = False
        self.preflop = False
        self.flop = False
        self.river = False
        self.turn = False
        self.final_state = False
        self.first_p_action = False

        self.curr_player_index = 0
        self.system = Hand()

    def render_call(self):
        call_txt = self.act_font.render("Call", True, (255, 255, 255))
        call_rect = call_txt.get_rect(center=(400, HEIGHT-50))
        self.screen.blit(call_txt, call_rect)
    def render_bet(self):
        bet_txt = self.act_font.render("Bet", True, (255, 255, 255))
        bet_rect = bet_txt.get_rect(center=(650, HEIGHT-50))
        self.screen.blit(bet_txt, bet_rect)
    def render_raise(self):
        raise_txt = self.act_font.render("Raise", True, (255, 255, 255))
        raise_rect = raise_txt.get_rect(center=(900, HEIGHT-50))
        self.screen.blit(raise_txt, raise_rect)
    def render_fold(self):
        fold_txt = self.act_font.render("Fold", True, (255, 255, 255))
        fold_rect = fold_txt.get_rect(center=(1150, HEIGHT-50))
        self.screen.blit(fold_txt, fold_rect)
    def render_allin(self):
        all_in_txt = self.act_font.render("All in", True, (255, 255, 255))
        all_in_rect = all_in_txt.get_rect(center=(1400, HEIGHT-50))
        self.screen.blit(all_in_txt, all_in_rect)
    def render_check(self):
        check_txt = self.act_font.render("Check", True, (255, 255, 255))
        check_rect = check_txt.get_rect(center=(1650, HEIGHT-50))
        self.screen.blit(check_txt, check_rect)
    def render_p_turn(self):
        turn_txt = self.act_font.render(f"{self.system.player_list[self.curr_player_index].name}'s Turn", True, (255, 255, 255))
        turn_rect = turn_txt.get_rect(center=(240, HEIGHT//2))
        self.screen.blit(turn_txt, turn_rect)
    def render_overall_pot(self):
        pot_txt = self.act_font.render(f"Overall Pot: {self.system.overall_pot}", True, (255, 255, 255))
        pot_rect = pot_txt.get_rect(center=(WIDTH // 2, 100))
        self.screen.blit(pot_txt, pot_rect)
    def render_each_round_pot(self):
        each_pot_txt = self.act_font.render(f"Pot: {self.system.each_pot}", True, (255, 255, 255))
        each_pot_rect = each_pot_txt.get_rect(center=(WIDTH // 2, 200))
        self.screen.blit(each_pot_txt, each_pot_rect)
    def render_p_chips(self):
        for i in range(len(self.system.player_list)):
            player_pot_txt = self.act_font.render(f"{self.system.player_list[i].name}'s Pot: {self.system.player_list[i].chips}", True, (255, 255, 255))
            player_pot_rect = player_pot_txt.get_rect(center=(WIDTH*(2*i+1)//4, 100))
            self.screen.blit(player_pot_txt, player_pot_rect)
    def render_p_curr_bet(self):
        for i in range(len(self.system.player_list)):
            p_curr_bet_txt = self.act_font.render(f"{self.system.player_list[i].name}'s Current Bet: {self.system.player_list[i].current_bet}", True, (255, 255, 255))
            p_curr_bet_rect = p_curr_bet_txt.get_rect(center=(WIDTH*(2*i+1)//4, 200))
            self.screen.blit(p_curr_bet_txt, p_curr_bet_rect)

    def run(self):
        # Track SB
        for i in range(len(self.system.player_list)):
            if self.system.player_list[i].small_blind == True:
                self.curr_player_index = i
        # Start
        while self.game_active is True:
            while self.setup is True and self.first_p_action is True:
                self.screen.fill(BG_COLOR)
                # Render Player Turn
                self.render_p_turn()
                # Render Community Pot
                self.render_overall_pot()
                self.render_each_round_pot()
                # Render Player's Pot
                self.render_p_chips()
                self.render_p_curr_bet()

                # Render Action Button
                post_bet_txt = self.act_font.render("Post Bet(SB)", True, (255, 255, 255))
                post_bet_rect = post_bet_txt.get_rect(center=(650, HEIGHT - 50))
                self.screen.blit(post_bet_txt, post_bet_rect)
                # Chk event
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.curr_player_index = (self.curr_player_index + 1) % 2
                            self.first_p_action = False
                            break
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if post_bet_rect.collidepoint(event.pos):
                            print("Post Bet(SB) is pressed")
                            self.system.post_bet(self.system.player_list[self.curr_player_index], 50)
                pygame.display.update()
            while self.setup is True and self.first_p_action is False:
                self.screen.fill(BG_COLOR)
                # Render Player Turn
                self.render_p_turn()
                # Render Community Pot
                self.render_overall_pot()
                self.render_each_round_pot()
                # Render Player's Pot
                self.render_p_chips()
                self.render_p_curr_bet()
                # Render Call
                post_bet_txt = self.act_font.render("Post Bet(BB)", True, (255, 255, 255))
                post_bet_rect = post_bet_txt.get_rect(center=(650, HEIGHT - 50))
                self.screen.blit(post_bet_txt, post_bet_rect)

                # Chk event
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.setup = False
                            self.flop = True
                            self.first_p_action = True
                            self.curr_player_index += 1
                            self.system.each_pot = 0
                            for player in self.system.player_list:
                                player.current_bet = 0
                            print("End Preflop")
                            self.system.dealer.deal_flop()
                            break
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if post_bet_rect.collidepoint(event.pos):
                            print("Post Call(BB) is pressed")
                            self.system.post_call(self.system.player_list[self.curr_player_index], 2*self.system.each_pot)
                pygame.display.update()
            while self.flop is True and self.first_p_action is True:
                self.screen.fill(BG_COLOR)
                # Render Game Info
                self.render_p_turn()
                self.render_overall_pot()
                self.render_each_round_pot()
                self.render_p_chips()
                self.render_p_curr_bet()
                # Render Action
                bet_txt = self.act_font.render("Bet", True, (255, 255, 255))
                bet_rect = bet_txt.get_rect(center=(650, HEIGHT - 50))
                self.screen.blit(bet_txt, bet_rect)
                fold_txt = self.act_font.render("Fold", True, (255, 255, 255))
                fold_rect = fold_txt.get_rect(center=(1150, HEIGHT - 50))
                self.screen.blit(fold_txt, fold_rect)
                all_in_txt = self.act_font.render("All in", True, (255, 255, 255))
                all_in_rect = all_in_txt.get_rect(center=(1400, HEIGHT - 50))
                self.screen.blit(all_in_txt, all_in_rect)
                chk_txt = self.act_font.render("Check", True, (255, 255, 255))
                chk_rect = chk_txt.get_rect(center=(1650, HEIGHT - 50))
                self.screen.blit(chk_txt, chk_rect)
                # Render Card
                for card in self.system.community_card.community_cards:
                    self.screen.blit(card.card_surf, card.position)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            print("1st -> 2nd")
                            self.first_p_action = False
                            self.curr_player_index = (self.curr_player_index+1) % 2
                            # break
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if bet_rect.collidepoint(event.pos):
                            self.system.post_bet(self.system.player_list[self.curr_player_index], 50)
                        elif fold_rect.collidepoint(event.pos):
                            self.system.fold(self.system.player_list[self.curr_player_index])
                        elif all_in_rect.collidepoint(event.pos):
                            self.system.all_in(self.system.player_list[self.curr_player_index])
                            self.curr_player_index = (self.curr_player_index+1) % 2
                pygame.display.update()
            while self.flop is True and self.first_p_action is False:
                self.screen.fill(BG_COLOR)
                # Render Game Info
                self.render_p_turn()
                self.render_overall_pot()
                self.render_each_round_pot()
                self.render_p_chips()
                self.render_p_curr_bet()
                # Render Action
                call_txt = self.act_font.render("Call", True, (255, 255, 255))
                call_rect = call_txt.get_rect(center=(400, HEIGHT - 50))
                self.screen.blit(call_txt, call_rect)
                all_in_txt = self.act_font.render("All in", True, (255, 255, 255))
                all_in_rect = all_in_txt.get_rect(center=(1400, HEIGHT - 50))
                self.screen.blit(all_in_txt, all_in_rect)
                raise_txt = self.act_font.render("Raise", True, (255, 255, 255))
                raise_rect = raise_txt.get_rect(center=(900, HEIGHT - 50))
                self.screen.blit(raise_txt, raise_rect)
                fold_txt = self.act_font.render("Fold", True, (255, 255, 255))
                fold_rect = fold_txt.get_rect(center=(1150, HEIGHT - 50))
                self.screen.blit(fold_txt, fold_rect)
                chk_txt = self.act_font.render("Check", True, (255, 255, 255))
                chk_rect = chk_txt.get_rect(center=(1650, HEIGHT - 50))
                self.screen.blit(chk_txt, chk_rect)
                for card in self.system.community_card.community_cards:
                    self.screen.blit(card.card_surf, card.position)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.curr_player_index = (self.curr_player_index+1) % 2
                            break
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if call_rect.collidepoint(event.pos):
                            self.system.post_call(self.system.player_list[self.curr_player_index], self.system.each_pot)
                            self.system.dealer.deal_turn()
                            self.flop = False
                            self.first_p_action = True
                            self.turn = True
                            self.system.each_pot = 0
                            self.curr_player_index = (self.curr_player_index + 1) % 2
                            for player in self.system.player_list:
                                player.current_bet = 0
                            print("End Flop")
                        elif fold_rect.collidepoint(event.pos):
                            self.system.fold(self.system.player_list[self.curr_player_index])
                        elif raise_rect.collidepoint(event.pos):
                            self.system.raise_bet(self.system.player_list[self.curr_player_index], self.system.player_list[(self.curr_player_index+1)%2].current_bet)
                        elif all_in_rect.collidepoint(event.pos):
                            self.system.all_in(self.system.player_list[self.curr_player_index])
                pygame.display.update()
            while self.turn is True and self.first_p_action is True:
                self.screen.fill(BG_COLOR)
                # Render Game Info
                self.render_p_turn()
                self.render_overall_pot()
                self.render_each_round_pot()
                self.render_p_chips()
                self.render_p_curr_bet()
                # Render Action
                bet_txt = self.act_font.render("Bet", True, (255, 255, 255))
                bet_rect = bet_txt.get_rect(center=(650, HEIGHT - 50))
                self.screen.blit(bet_txt, bet_rect)
                fold_txt = self.act_font.render("Fold", True, (255, 255, 255))
                fold_rect = fold_txt.get_rect(center=(1150, HEIGHT - 50))
                self.screen.blit(fold_txt, fold_rect)
                all_in_txt = self.act_font.render("All in", True, (255, 255, 255))
                all_in_rect = all_in_txt.get_rect(center=(1400, HEIGHT - 50))
                self.screen.blit(all_in_txt, all_in_rect)
                chk_txt = self.act_font.render("Check", True, (255, 255, 255))
                chk_rect = chk_txt.get_rect(center=(1650, HEIGHT - 50))
                self.screen.blit(chk_txt, chk_rect)
                # Render Card
                for card in self.system.community_card.community_cards:
                    self.screen.blit(card.card_surf, card.position)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            print("1st -> 2nd")
                            self.first_p_action = False
                            self.curr_player_index = (self.curr_player_index+1) % 2
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if bet_rect.collidepoint(event.pos):
                            self.system.post_bet(self.system.player_list[self.curr_player_index], 50)
                        elif fold_rect.collidepoint(event.pos):
                            self.system.fold(self.system.player_list[self.curr_player_index])
                        elif all_in_rect.collidepoint(event.pos):
                            self.system.all_in(self.system.player_list[self.curr_player_index])
                pygame.display.update()
            while self.turn is True and self.first_p_action is False:
                self.screen.fill(BG_COLOR)
                # Render Game Info
                self.render_p_turn()
                self.render_overall_pot()
                self.render_each_round_pot()
                self.render_p_chips()
                self.render_p_curr_bet()
                # Render Action
                call_txt = self.act_font.render("Call", True, (255, 255, 255))
                call_rect = call_txt.get_rect(center=(400, HEIGHT - 50))
                self.screen.blit(call_txt, call_rect)
                all_in_txt = self.act_font.render("All in", True, (255, 255, 255))
                all_in_rect = all_in_txt.get_rect(center=(1400, HEIGHT - 50))
                self.screen.blit(all_in_txt, all_in_rect)
                raise_txt = self.act_font.render("Raise", True, (255, 255, 255))
                raise_rect = raise_txt.get_rect(center=(900, HEIGHT - 50))
                self.screen.blit(raise_txt, raise_rect)
                fold_txt = self.act_font.render("Fold", True, (255, 255, 255))
                fold_rect = fold_txt.get_rect(center=(1150, HEIGHT - 50))
                self.screen.blit(fold_txt, fold_rect)
                chk_txt = self.act_font.render("Check", True, (255, 255, 255))
                chk_rect = chk_txt.get_rect(center=(1650, HEIGHT - 50))
                self.screen.blit(chk_txt, chk_rect)
                for card in self.system.community_card.community_cards:
                    self.screen.blit(card.card_surf, card.position)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.curr_player_index = (self.curr_player_index+1) % 2
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if call_rect.collidepoint(event.pos):
                            self.system.post_call(self.system.player_list[self.curr_player_index], self.system.each_pot)
                            self.system.dealer.deal_river()
                            self.turn = False
                            self.first_p_action = True
                            self.river = True
                            self.system.each_pot = 0
                            self.curr_player_index = (self.curr_player_index + 1) % 2
                            for player in self.system.player_list:
                                player.current_bet = 0
                            print("End Turn")
                        elif fold_rect.collidepoint(event.pos):
                            self.system.fold(self.system.player_list[self.curr_player_index])
                        elif raise_rect.collidepoint(event.pos):
                            self.system.raise_bet(self.system.player_list[self.curr_player_index], self.system.player_list[(self.curr_player_index+1)%2].current_bet)
                pygame.display.update()
            while self.river is True and self.first_p_action is True:
                self.screen.fill(BG_COLOR)
                # Render Game Info
                self.render_p_turn()
                self.render_overall_pot()
                self.render_each_round_pot()
                self.render_p_chips()
                self.render_p_curr_bet()
                # Render Action
                bet_txt = self.act_font.render("Bet", True, (255, 255, 255))
                bet_rect = bet_txt.get_rect(center=(650, HEIGHT - 50))
                self.screen.blit(bet_txt, bet_rect)
                fold_txt = self.act_font.render("Fold", True, (255, 255, 255))
                fold_rect = fold_txt.get_rect(center=(1150, HEIGHT - 50))
                self.screen.blit(fold_txt, fold_rect)
                all_in_txt = self.act_font.render("All in", True, (255, 255, 255))
                all_in_rect = all_in_txt.get_rect(center=(1400, HEIGHT - 50))
                self.screen.blit(all_in_txt, all_in_rect)
                chk_txt = self.act_font.render("Check", True, (255, 255, 255))
                chk_rect = chk_txt.get_rect(center=(1650, HEIGHT - 50))
                self.screen.blit(chk_txt, chk_rect)
                # Render Card
                for card in self.system.community_card.community_cards:
                    self.screen.blit(card.card_surf, card.position)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            print("1st -> 2nd")
                            self.first_p_action = False
                            self.curr_player_index = (self.curr_player_index+1) % 2
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if bet_rect.collidepoint(event.pos):
                            self.system.post_bet(self.system.player_list[self.curr_player_index], 50)
                        elif fold_rect.collidepoint(event.pos):
                            self.system.fold(self.system.player_list[self.curr_player_index])
                        elif all_in_rect.collidepoint(event.pos):
                            self.system.all_in(self.system.player_list[self.curr_player_index])
                pygame.display.update()
            while self.river is True and self.first_p_action is False:
                self.screen.fill(BG_COLOR)
                # Render Game Info
                self.render_p_turn()
                self.render_overall_pot()
                self.render_each_round_pot()
                self.render_p_chips()
                self.render_p_curr_bet()
                # Render Action
                call_txt = self.act_font.render("Call", True, (255, 255, 255))
                call_rect = call_txt.get_rect(center=(400, HEIGHT - 50))
                self.screen.blit(call_txt, call_rect)
                all_in_txt = self.act_font.render("All in", True, (255, 255, 255))
                all_in_rect = all_in_txt.get_rect(center=(1400, HEIGHT - 50))
                self.screen.blit(all_in_txt, all_in_rect)
                raise_txt = self.act_font.render("Raise", True, (255, 255, 255))
                raise_rect = raise_txt.get_rect(center=(900, HEIGHT - 50))
                self.screen.blit(raise_txt, raise_rect)
                fold_txt = self.act_font.render("Fold", True, (255, 255, 255))
                fold_rect = fold_txt.get_rect(center=(1150, HEIGHT - 50))
                self.screen.blit(fold_txt, fold_rect)
                chk_txt = self.act_font.render("Check", True, (255, 255, 255))
                chk_rect = chk_txt.get_rect(center=(1650, HEIGHT - 50))
                self.screen.blit(chk_txt, chk_rect)
                for card in self.system.community_card.community_cards:
                    self.screen.blit(card.card_surf, card.position)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.curr_player_index = (self.curr_player_index+1) % 2
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if call_rect.collidepoint(event.pos):
                            self.system.post_call(self.system.player_list[self.curr_player_index], self.system.each_pot)
                            self.system.dealer.deal_river()
                            self.river = False
                            self.first_p_action = True
                            self.final_state = True
                            self.system.each_pot = 0
                            self.curr_player_index = (self.curr_player_index + 1) % 2
                            for player in self.system.player_list:
                                player.current_bet = 0
                            print("End River")
                        elif fold_rect.collidepoint(event.pos):
                            self.system.fold(self.system.player_list[self.curr_player_index])
                        elif raise_rect.collidepoint(event.pos):
                            self.system.raise_bet(self.system.player_list[self.curr_player_index], self.system.player_list[(self.curr_player_index+1)%2].current_bet)
                pygame.display.update()
                break

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
                        self.setup = True
                        self.first_p_action = True
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