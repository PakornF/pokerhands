import itertools, os, pygame, random
from cards import *
from settings import *

# Audio
pygame.mixer.init()
audio_files = os.listdir(GAME_AUDIO_DIR)
wav_files = [file for file in audio_files if file.endswith('.wav')]
num_channels = len(wav_files)
pygame.mixer.set_num_channels(num_channels)
channels = [pygame.mixer.Channel(i) for i in range(num_channels)]


class Hand:
  def __init__(self):
    self.display_surface = pygame.display.get_surface()
    self.winner = None
    self.font = pygame.font.Font(GAME_FONT, 120)
    self.win_rotation_angle = random.uniform(-10, 10)
    self.p1 = Player()
    self.p2 = Player()
    self.flop = Flop()
    self.player_list = [self.p1, self.p2]
    self.num_players = len(self.player_list)
    self.dealer = Dealer(self.player_list, self.flop)
    self.pot = 0
    self.current_bet = 0
    self.current_player_index = 0
    self.game_phase = 'preflop'  # preflop, flop, turn, river
    self.actions_complete = False  # Track if player actions are complete

  def deal_initial_cards(self):
    # Deal 2 cards to each player
    for _ in range(2):
      for player in self.player_list:
        player.cards.append(self.dealer.deck.pop())
        # Set card positions for Player 1 and Player 2
        if player == self.p1:
          player.cards[-1].position = (P1_C1[0] + len(player.cards) * 80, P1_C1[1])
        elif player == self.p2:
          player.cards[-1].position = (P2_C1[0] - len(player.cards) * 80, P2_C1[1])

  def render_player_cards(self):
    for player in self.player_list:
      for card in player.cards:
        self.display_surface.blit(card.card_surf, card.position) # Draw Each Player's Card
  def render_community_cards(self):
    for card in self.flop.cards:
        self.display_surface.blit(card.card_surf, card.position) # Draw Community Card

  def render_winner(self):
        if self.dealer.determined_winner is not None:
            # Set the text and color based on the winner
            if self.dealer.determined_winner == "Player 1":
                text = "Player 1 Wins!"
                text_color = (115, 235, 0)  # Blue
            elif self.dealer.determined_winner == "Player 2":
                text = "Player 2 Wins!"
                text_color = (135, 206, 235)  # Green
            elif self.dealer.determined_winner == "Tie":
                text = "Split Pot!"
                text_color = (255, 192, 203)  # Pink

            coordinates = (520, 100)
            # Winner text
            text_surface = self.font.render(text, True, text_color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = coordinates
            rotated_surface = pygame.transform.rotate(text_surface, self.win_rotation_angle)
            rotated_rect = rotated_surface.get_rect(center=text_rect.center)
            self.display_surface.blit(rotated_surface, rotated_rect)

  def render_pot(self):
        pot_text = self.font.render(f"Pot: {self.pot}", True, (255, 255, 255))
        self.display_surface.blit(pot_text, (WIDTH // 2 - 100, 20))

  def render_actions(self):
        actions = ['Bet', 'Raise', 'Call', 'Fold']
        button_width = 220  # Width of each button
        button_height = 50  # Height of each button
        button_spacing = 30  # Spacing between buttons
        start_x = 20  # Starting X position for the first button
        start_y = HEIGHT - 100  # Y position for the buttons

        for i, action in enumerate(actions):
            # Calculate the position for each button
            button_x = start_x + i * (button_width + button_spacing)
            button_y = start_y

            # Render the button background (optional, for visual clarity)
            pygame.draw.rect(self.display_surface, (0, 0, 0), (button_x, button_y, button_width, button_height))

            # Render the action text
            action_text = self.font.render(action, True, (255, 255, 255))
            text_rect = action_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
            self.display_surface.blit(action_text, text_rect)
  def render_current_player_index(self):
     font = pygame.font.Font(GAME_FONT, 75)
     text = f"Player {self.current_player_index+1}'s Turn"
     curr_player_index = font.render(text, True, (255, 255, 255))
     self.display_surface.blit(curr_player_index, (WIDTH // 2 - 900, 20))

  def handle_action(self, action):
        current_player = self.player_list[self.current_player_index]
        if action == 'Bet':
            current_player.current_bet = 100  # Example bet amount
            self.pot += current_player.current_bet
            current_player.chips -= current_player.current_bet
        elif action == 'Raise':
            current_player.current_bet += 100  # Example raise amount
            self.pot += current_player.current_bet
            current_player.chips -= current_player.current_bet
        elif action == 'Call':
            self.pot += current_player.current_bet
            current_player.chips -= current_player.current_bet
        elif action == 'Fold':
            current_player.cards = []
            self.current_player_index = (self.current_player_index + 1) % len(self.player_list)
            return

        self.current_player_index = (self.current_player_index + 1) % len(self.player_list)
        self.actions_complete = True  # Mark actions as complete

  def update(self):
        self.dealer.update()
        self.render_player_cards()
        self.render_community_cards()
        self.render_winner()
        self.render_pot()
        self.render_current_player_index()
        self.render_actions()

        # Handle game phases
        if self.game_phase == 'preflop':
            if self.dealer.dealt_cards == (self.num_players * 2):
                self.game_phase = 'flop'
                self.actions_complete = False  # Reset actions for the flop phase

        elif self.game_phase == 'flop':
            if self.dealer.dealt_cards == (self.num_players * 2) + 3 and self.actions_complete:
                self.game_phase = 'turn'
                self.actions_complete = False  # Reset actions for the turn phase

        elif self.game_phase == 'turn':
            if self.dealer.dealt_cards == (self.num_players * 2) + 4 and self.actions_complete:
                self.game_phase = 'river'
                self.actions_complete = False  # Reset actions for the river phase

        elif self.game_phase == 'river':
            if self.dealer.dealt_cards == (self.num_players * 2) + 5 and self.actions_complete:
                self.game_phase = 'showdown'
                self.dealer.determined_winner = self.dealer.eval_winner([card.id for card in self.p1.cards] + [card.id for card in self.flop.cards] + [card.id for card in self.p2.cards])


class Dealer:
  def __init__(self, players, flop):
    self.determined_winner = None
    self.players_list = players # Array of player
    self.num_players = len(players)
    self.current_player_index = 0
    self.current_flop_index = 0
    self.printed_flop = False
    self.deck = self.generate_deck()
    random.shuffle(self.deck)
    self.animating_card = None
    self.can_deal = True
    self.can_deal_flop = False
    self.last_dealt_card_time = None
    self.last_dealt_flop_time = None
    self.dealt_cards = 0
    self.flop = flop # Array of Card
    self.audio_channel = 0

  def card_audio(self):
    random_wav = random.choice(wav_files)
    wav_file_path = os.path.join(GAME_AUDIO_DIR, random_wav)
    sound = pygame.mixer.Sound(wav_file_path)
    channels[self.audio_channel].play(sound)
    self.audio_channel += 1

  def generate_deck(self):
    fresh_deck = []
    for cv in cardvalues:
      for cs in cardsuits:
        fresh_deck.append(Card(cv, cs))
    return fresh_deck

  def cooldowns(self):
    current_time = pygame.time.get_ticks()
    if self.last_dealt_card_time and current_time - 200 > self.last_dealt_card_time:
      self.can_deal = True

    if self.last_dealt_flop_time and current_time - random.randint(120, 200) > self.last_dealt_flop_time:
      self.can_deal_flop = True

  def animate_hole_card(self, card):
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - self.last_dealt_card_time

    current_card = card
    animation_duration = 200

    if elapsed_time < animation_duration:
      x_orig, y_orig = current_card.orig_position
      x_final, y_final = current_card.position
      elapsed_ratio = elapsed_time / animation_duration
      x_change = x_orig + (x_final - x_orig) * elapsed_ratio
      y_change = y_orig + (y_final - y_orig) * elapsed_ratio
      current_card.start_position = (x_change, y_change)
    else:
      card.animation_complete = True

  def deal_hole_cards(self):
    if self.can_deal:
      current_player = self.players_list[self.current_player_index]
      current_player.cards.append(self.deck[-1])

      if self.current_player_index == 0:
        if len(current_player.cards) == 1:
          current_player.cards[0].position = (P1_C1[0], current_player.cards[0].card_y)
        elif len(current_player.cards) == 2:
          current_player.cards[1].position = (P1_C2[0], current_player.cards[1].card_y)
        self.animating_card = current_player.cards[-1]
      elif self.current_player_index == 1:
        if len(current_player.cards) == 1:
          current_player.cards[0].position = (
          (P2_C1[0] - current_player.cards[0].card_surf.get_width() - 80), current_player.cards[0].card_y)
        elif len(current_player.cards) == 2:
          current_player.cards[1].position = (
          (P2_C2[0] - current_player.cards[1].card_surf.get_width() - 20), current_player.cards[1].card_y)
        self.animating_card = current_player.cards[-1]

      if self.animating_card is not None:
        self.last_dealt_card_time = pygame.time.get_ticks()
        self.animate_hole_card(self.animating_card)

      self.card_audio()
      self.deck.pop(-1)
      self.current_player_index = (self.current_player_index + 1) % self.num_players
      self.can_deal = False

  def deal_flop(self):
     flop_x = self.players_list[0].cards[0].card_surf.get_width() * 2
     flop_y = HEIGHT // 2 - self.players_list[0].cards[0].card_surf.get_height() // 2
     for i in range(3):
        self.flop.cards.append(self.deck[-1])
        self.flop.cards[-1].position = (flop_x + i * (self.flop.cards[-1].card_surf.get_width() + 20), flop_y)
        self.deck.pop(-1)
  def deal_turn(self):
     turn_x = self.flop.cards[-1].position[0] - self.flop.cards[-1].card_surf.get_width() + 20
     turn_y = HEIGHT // 2 + self.players_list[0].cards[0].card_surf.get_height() // 2
     self.flop.cards.append(self.deck[-1])
     self.flop.cards[-1].position = (turn_x, turn_y)
     self.deck.pop(-1)
  def deal_river(self):
    river_x = self.flop.cards[-1].position[0] + self.flop.cards[-1].card_surf.get_width() + 20
    river_y = HEIGHT // 2 + self.players_list[0].cards[0].card_surf.get_height() // 2
    self.flop.cards.append(self.deck[-1])
    self.flop.cards[-1].position = (river_x, river_y)
    self.deck.pop(-1)

  def eval_hand(self, hand):
    values = sorted([c[0] for c in hand], reverse=True)
    suits = [c[1] for c in hand]
    straight = (values == list(range(values[0], values[0] - 5, -1)) or values == [14, 5, 4, 3, 2])
    flush = all(s == suits[0] for s in suits)

    if straight and flush: return 8, values[1]
    if flush: return 5, values
    if straight: return 4, values[1]

    trips = []
    pairs = []
    for v, group in itertools.groupby(values):
      count = sum(1 for _ in group)
      if count == 4:
        return 7, v, values
      elif count == 3:
        trips.append(v)
      elif count == 2:
        pairs.append(v)

    if trips: return (6 if pairs else 3), trips, pairs, values
    return len(pairs), pairs, values

  def eval_winner(self, hand_to_eval):
    eval_cards = [(value_dict[x[0]], x[1]) for x in hand_to_eval]
    if self.eval_hand(eval_cards[:5]) > self.eval_hand(eval_cards[5:]):
      print(f"P1 WIN: {self.eval_hand(eval_cards[:5])}")
      return "Player 1"
    elif self.eval_hand(eval_cards[:5]) < self.eval_hand(eval_cards[5:]):
      print(f"P2 WIN: {self.eval_hand(eval_cards[5:])}")
      return "Player 2"
    else:
      print("SPLIT")
      return "Tie"

  def print_hands(self):
    for i in range(len(self.players_list)):
      print(f"P{i + 1}: {[card.id for card in self.players_list[i].cards]}")
    print(f"FL: {[card.id for card in self.flop.cards]}")

  def update_dealt_card_count(self):
    total_card_count = 0
    for player in self.players_list:
      total_card_count += len(player.cards)
    total_card_count += len(self.flop.cards)
    return total_card_count

  def update(self):
    self.dealt_cards = self.update_dealt_card_count()
    self.cooldowns()

    if self.dealt_cards < (self.num_players * 2):
      self.deal_hole_cards()

    if self.animating_card:
      self.animate_hole_card(self.animating_card)

    if self.dealt_cards == (self.num_players * 2) and (
            not self.animating_card or self.animating_card.animation_complete):
      self.can_deal_flop = True
      self.deal_flop()

    if self.dealt_cards == (self.num_players * 2) + 3 and (
            not self.animating_card or self.animating_card.animation_complete):
      self.can_deal_flop = True
      self.deal_turn()

    if self.dealt_cards == (self.num_players * 2) + 4 and (
            not self.animating_card or self.animating_card.animation_complete):
      self.can_deal_flop = True
      self.deal_river()

    if not self.printed_flop and self.dealt_cards == (self.num_players * 2) + 5:
      self.print_hands()
      self.printed_flop = True

    if self.dealt_cards == ((self.num_players * 2) + 5) and self.determined_winner is None:
      eval_cards = [card_id.id for card_id in self.players_list[0].cards] + [card_id.id for card_id in
                                                                             self.flop.cards] + [card_id.id for card_id
                                                                                                 in self.players_list[
                                                                                                   1].cards]
      self.determined_winner = self.eval_winner(eval_cards)