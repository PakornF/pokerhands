import pygame
from visualize import PokerVisualizer as Visualizer

class PokerUI:
    def __init__(self, screen):
        self.screen = screen
        self.visualizer = Visualizer('game_data.csv')
        self.font = pygame.font.SysFont("arial", 24)
        self.card_font = pygame.font.SysFont("arial", 30, bold=True)
        self.button_font = pygame.font.SysFont("arial", 20, bold=True)
        self.screen_width = 800
        self.screen_height = 600
        self.button_rects = {
            "fold": pygame.Rect(50, self.screen_height - 80, 120, 50),
            "call": pygame.Rect(200, self.screen_height - 80, 120, 50),
            "raise": pygame.Rect(350, self.screen_height - 80, 120, 50),
            "show_data": pygame.Rect(self.screen_width - 170, self.screen_height - 80, 150, 50)
        }
        self.button_colors = {
            "fold": (200, 50, 50),  # Red
            "call": (50, 150, 50),  # Green
            "raise": (50, 50, 200),  # Blue
            "show_data": (150, 150, 150)  # Gray
        }
        self.button_hover = {key: False for key in self.button_rects}

        # Image displaying
        self.show_data_image = False
        self.data_image = []
        self.current_image_index = 0
        self.image_file_name = ['game_duration_distribution.png', 
                                'player_card_distribution.png', 
                                'win_ratio.png']
        self.close_button_rect = None
        self.previous_button_rect = None
        self.next_button_rect = None

    def draw_card(self, card, x, y, face_down=False):
        card_width, card_height = 80, 120
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, card_width, card_height), border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, card_width, card_height), 2, border_radius=10)
        
        if face_down:
            # Back
            text = self.card_font.render("?", True, (100, 100, 100))
            text_rect = text.get_rect(center=(x + card_width // 2, y + card_height // 2))
            self.screen.blit(text, text_rect)
        else:
            # Front
            suit_color = (200, 0, 0) if card.suit in ['♥', '♦'] else (0, 0, 0)
            rank_text = self.card_font.render(card.rank, True, suit_color)
            suit_text = self.card_font.render(card.suit, True, suit_color)
            rank_rect = rank_text.get_rect(center=(x + card_width // 2, y + card_height // 3))
            suit_rect = suit_text.get_rect(center=(x + card_width // 2, y + 2 * card_height // 3))
            self.screen.blit(rank_text, rank_rect)
            self.screen.blit(suit_text, suit_rect)

    def draw_button(self, action, rect, color):
        if self.button_hover[action]:
            hover_color = tuple(min(c + 30, 255) for c in color)
            pygame.draw.rect(self.screen, hover_color, rect, border_radius=10)
        else:
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2, border_radius=10)
        text = self.button_font.render(action.capitalize(), True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)

    def draw(self, game):
        # Background
        self.screen.fill((0, 100, 0))  # Green
        table_rect = pygame.Rect(20, 20, self.screen_width - 40, self.screen_height - 100)
        pygame.draw.rect(self.screen, (0, 80, 0), table_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 255, 255), table_rect, 5, border_radius=20)

        if not self.show_data_image:
            # Draw Player cards
            player_cards = game.players[0]['cards']
            for i, card in enumerate(player_cards):
                self.draw_card(card, self.screen_width // 2 - 100 + i * 100, self.screen_height - 200)

            # Draw Bot cards
            bot_cards = game.players[1]['cards']
            for i, card in enumerate(bot_cards):
                face_down = game.state != "showdown"
                self.draw_card(card if not face_down else None, self.screen_width // 2 - 100 + i * 100, 50, face_down=face_down)

            # Draw community cards
            community_cards = game.community_cards
            if not community_cards:
                # Preflop
                text = self.font.render("No Community Cards", True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(text, text_rect)
            else:
                for i, card in enumerate(community_cards):
                    self.draw_card(card, self.screen_width // 2 - len(community_cards) * 50 + i * 100, self.screen_height // 2 - 60)

            # Chips Info
            text = f"Your Chips: {game.players[0]['chips']}"
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (50, self.screen_height - 120))
            text = f"Bot Chips: {game.players[1]['chips']}"
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (50, 30))

            # Pot Info
            text = f"Pot: {game.pot}"
            text_surface = self.font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
            self.screen.blit(text_surface, text_rect)

            # Game State
            text = f"State: {game.state.capitalize()}"
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (self.screen_width - 150, 30))

            # End game message
            if game.state == "showdown":
                winner = game.players[0]['chips'] if game.players[0]['chips'] > game.players[1]['chips'] else game.players[1]['chips']
                winner_text = "You Win!" if winner == game.players[0]['chips'] else "Bot Wins!"
                text = self.font.render(f"{winner_text} Starting New Round...", True, (255, 255, 0))
                text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 120))
                self.screen.blit(text, text_rect)

            # Buttons
            for action, rect in self.button_rects.items():
                self.draw_button(action, rect, self.button_colors[action])
        else: # Show data image
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            if not self.data_image:
                for filename in self.image_file_name:
                    image = pygame.image.load(filename)
                    image = pygame.transform.scale(image, (self.screen_width - 100, self.screen_height - 100))
                    self.data_image.append(image)
            if self.data_image:
                image = self.data_image[self.current_image_index]
                image_rect = image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(image, image_rect)

                title = self.font.render(f"Data Visualization: {self.image_file_name[self.current_image_index]}", True, (255, 255, 255))
                title_rect = title.get_rect(center=(self.screen_width // 2, 50))
                self.screen.blit(title, title_rect)

            button_y = self.screen_height - 600
            button_width, button_height = 120, 50
            
            # Close button (center)
            self.close_button_rect = pygame.Rect(self.screen_width//2 - button_width//2, button_y, button_width, button_height)
            pygame.draw.rect(self.screen, (200, 50, 50), self.close_button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), self.close_button_rect, 2, border_radius=10)
            text = self.button_font.render("Close", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.close_button_rect.center)
            self.screen.blit(text, text_rect)
            
            # Previous button (left)
            self.prev_button_rect = pygame.Rect(self.screen_width//4 - button_width//2, button_y, button_width, button_height)
            prev_color = (100, 100, 200) if self.current_image_index > 0 else (100, 100, 100)
            pygame.draw.rect(self.screen, prev_color, self.prev_button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), self.prev_button_rect, 2, border_radius=10)
            text = self.button_font.render("Previous", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.prev_button_rect.center)
            self.screen.blit(text, text_rect)
            
            # Next button (right)
            self.next_button_rect = pygame.Rect(3*self.screen_width//4 - button_width//2, button_y, button_width, button_height)
            next_color = (100, 100, 200) if self.current_image_index < len(self.data_image)-1 else (100, 100, 100)
            pygame.draw.rect(self.screen, next_color, self.next_button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), self.next_button_rect, 2, border_radius=10)
            text = self.button_font.render("Next", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.next_button_rect.center)
            self.screen.blit(text, text_rect)

        # Always draw buttons (they'll be under the overlay when showing data)
        for action, rect in self.button_rects.items():
            self.draw_button(action, rect, self.button_colors[action])

    def handle_event(self, event, game, logger):
        if event.type == pygame.MOUSEMOTION:
            for action, rect in self.button_rects.items():
                self.button_hover[action] = rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.show_data_image:
                if self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                    self.show_data_image = False
                    self.data_image = []
                    self.current_image_index = 0
                elif self.prev_button_rect and self.prev_button_rect.collidepoint(event.pos) and self.current_image_index > 0:
                    self.current_image_index -= 1
                elif self.next_button_rect and self.next_button_rect.collidepoint(event.pos) and self.current_image_index < len(self.data_image) - 1:
                    self.current_image_index += 1
            else:
                for action, rect in self.button_rects.items():
                    if rect.collidepoint(event.pos):
                        if action == "show_data":
                            print(logger.get_csv())  # Show CSV
                            self.show_data_image = True
                            self.visualizer.plot_game_duration()
                            self.visualizer.plot_player_hands()
                            self.visualizer.plot_win_ratio()
                        elif game.state != "showdown":  # Prevent actions in showdown
                            game.player_action(action, 0 if action == "fold" else 50 if action == "call" else 150 if action == "raise" else None)