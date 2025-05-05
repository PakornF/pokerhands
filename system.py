from settings import *
from cards import *
from player import *
from community_card import *
from dealer import *
import pygame
import random

class Hand:
    def __init__(self):
        self.p1 = Player()
        self.p2 = Player()
        self.player_list = [self.p1, self.p2]
        self.num_player = len(self.player_list)
        self.community_card = Community_Cards()
        self.dealer = Dealer(self.player_list, self.community_card)

        self.display_surface = pygame.display.get_surface()
        self.overall_pot = 0
        self.each_pot = 0
        self.font = pygame.font.Font(GAME_FONT, 120)

        self.big_small_blind()
    
    def big_small_blind(self):
        self.p1.big_blind = True
        self.p2.small_blind = True

    def post_bet(self, player, amount):
        if player.chips >= amount:
            player.chips -= amount
            player.current_bet += amount
            self.each_pot += amount
            self.overall_pot += amount
            return True
        return False
    def post_call(self, player, bet_amount):
        if player.chips >= bet_amount:
            diff = bet_amount - player.current_bet
            player.chips -= diff
            player.current_bet += diff
            self.each_pot += diff
            self.overall_pot += diff
            return True
        else:
            player.chips -= player.chips
            player.current_bet += player.chips
            self.each_pot += player.chips
            self.overall_pot += player.chips
        return False
    def raise_bet(self, player, amount):
        minimum_raise = round(1.5 * amount)
        if player.chips >= minimum_raise:
            player.chips -= minimum_raise
            player.current_bet += minimum_raise
            self.overall_pot += minimum_raise
            self.each_pot += minimum_raise
            return True
        return False

    def fold(self, player):
        """
        Handles player folding:
        1. Clears their cards
        2. Marks them as folded
        3. Awards pot to the other player
        4. Returns True if successful
        """
        if len(player.cards) > 0:  # Only allow folding if player has cards
            # Mark player as folded
            player.folded = True
            player.cards = []

            # Find the non-folding opponent
            opponent = next(p for p in self.player_list if p != player and not hasattr(p, 'folded'))

            if opponent:
                # Award the pot to the opponent
                opponent.chips += self.overall_pot
                self.overall_pot = 0
                self.each_pot = 0

                # Reset for new hand
                self.reset_hand_state()
                return True
        return False

    def reset_hand_state(self):
        """Resets all players' betting states for a new hand"""
        for player in self.player_list:
            player.current_bet = 0
            if hasattr(player, 'folded'):
                del player.folded  # Remove folded status

    def all_in(self, player):
        all_in_amount = player.chips  # Store the amount before modifying
        player.chips = 0  # Set chips to 0 first
        player.current_bet += all_in_amount
        self.overall_pot += all_in_amount
        self.each_pot += all_in_amount
        return True