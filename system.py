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
        self.pot = 0
        self.font = pygame.font.Font(GAME_FONT, 120)

    def render_player_card(self):
        for player in self.players:
            for card in player.cards:
                self.display_surface.blit(card.card_surf, card.position) # Draw Each Player's Card
    def render_community_card(self):
        for card in self.community_card:
            self.display_surface.blit(card.card_surf, card.position) # Draw Community Card