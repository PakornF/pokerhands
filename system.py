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

    def bet(self, player, amount):
        if player.chips >= amount:
            player.chips -= amount
            player.current_bet += amount
            self.each_pot += amount
            self.overall_pot += amount
            return True
        return False
    def call(self, player, bet_amount):
        if player.chips >= 2*bet_amount:
            diff = bet_amount - player.current_bet
            player.chips -= diff
            player.current_bet += diff
            self.each_pot += diff
            self.overall_pot += diff
            return True
        return False