from settings import *
from cards import *
from player import *
from community_card import *
import pygame
import random
from itertools import combinations

class Dealer:
    def __init__(self, players, comm_card):
        self.comm_card = comm_card
        self.player_list = players
        self.num_player = len(self.player_list)
        self.deck = self.generate_deck()
        random.shuffle(self.deck)

    def generate_deck(self):
        fresh_deck = []
        for cv in cardvalues:
            for cs in cardsuits:
                fresh_deck.append(Card(cv, cs))
        return fresh_deck
    def deal_card_for_each_player(self):
        for i in range(2):  # Deal 2 cards to each player
            for player in self.player_list:
                player.cards.append(self.deck.pop())
                # Set card positions for Player 1 and Player 2
                if player == self.player_list[0]:
                    if i == 0:
                        player.cards[-1].position = (P1_C1[0], P1_C1[1])
                    elif i == 1:
                        player.cards[-1].position = (P1_C2[0], P1_C2[1])
                elif player == self.player_list[1]:
                    if i == 0:
                        player.cards[-1].position = (P2_C1[0] - 300, P2_C1[1])
                    elif i == 1:
                        player.cards[-1].position = (P2_C2[0] - 300, P2_C2[1])
    def deal_flop(self):
        for _ in range(3):
            self.comm_card.community_cards.append(self.deck[-1])
            self.deck.pop(-1)
            self.comm_card.community_cards[-1].position = (WIDTH//3 + 300*_, HEIGHT//3 - 100)
    def deal_turn(self):
        self.comm_card.community_cards.append(self.deck[-1])
        self.deck.pop(-1)
        self.comm_card.community_cards[-1].position = (WIDTH//3 + 150, HEIGHT//3 + 200)
    def deal_river(self):
        self.comm_card.community_cards.append(self.deck[-1])
        self.deck.pop(-1)
        self.comm_card.community_cards[-1].position = (WIDTH//3 + 450, HEIGHT//3 + 200)
######################################################################
    def evaluate_winner(self):
        def hand_rank(hand):
            ranks = sorted([card.value for card in hand], reverse=True)
            suits = [card.suit for card in hand]
            is_flush = len(set(suits)) == 1
            is_straight = ranks == list(range(ranks[0], ranks[0] - 5, -1)) or ranks == [14, 5, 4, 3, 2]
            
            if is_straight and is_flush:
                return (8, ranks)
            if is_flush:
                return (5, ranks)
            if is_straight:
                return (4, ranks)
            
            rank_counts = {rank: ranks.count(rank) for rank in ranks}
            counts = sorted(rank_counts.values(), reverse=True)
            
            if counts == [4, 1]:
                return (7, ranks)
            if counts == [3, 2]:
                return (6, ranks)
            if counts == [3, 1, 1]:
                return (3, ranks)
            if counts == [2, 2, 1]:
                return (2, ranks)
            if counts == [2, 1, 1, 1]:
                return (1, ranks)
            
            return (0, ranks)
        
        best_hand = None
        best_rank = (-1, [])
        
        for player in self.players:
            combined_hand = player.cards + self.comm_card.community_cards
            for hand in combinations(combined_hand, 5):
                rank = hand_rank(hand)
                if rank > best_rank:
                    best_rank = rank
                    best_hand = player
        
        return best_hand
######################################################################