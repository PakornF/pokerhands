import pygame
from cfr import CFR

class PokerGame:
    def __init__(self, deck, logger):
        self.deck = deck
        self.logger = logger
        self.players = [{'cards': [], 'chips': 1000, 'bet': 0, 'folded': False, 'acted': False} for _ in range(2)]
        self.community_cards = []
        self.pot = 0
        self.current_player = 0
        self.cfr = CFR()
        self.state = "preflop"
        self.game_start_time = pygame.time.get_ticks()
        self.bets_history = []
        self.current_bets = []
        self.round_complete = False
        self.showdown_timer = 0
        self.deal_hole_cards()

    def deal_hole_cards(self):
        self.game_start_time = pygame.time.get_ticks()
        self.current_bets = []
        for player in self.players:
            player['cards'] = [self.deck.draw(), self.deck.draw()]
            player['acted'] = False
        self.state = "preflop"
        self.round_complete = False

    def deal_community_cards(self, num):
        for _ in range(num):
            self.community_cards.append(self.deck.draw())
        self.bets_history.append(self.current_bets[:])
        self.current_bets = []
        for player in self.players:
            player['acted'] = False

    def update(self):
        if self.state == "showdown":
            current_time = pygame.time.get_ticks()
            if self.showdown_timer == 0:
                self.showdown_timer = current_time
            elif current_time - self.showdown_timer > 2000:  # 2 seconds
                self.reset_round() # reset round after showdown
                self.showdown_timer = 0
        elif self.round_complete:
            if self.state == "preflop":
                self.deal_community_cards(3)
                self.state = "flop"
                self.round_complete = False
            elif self.state == "flop":
                self.deal_community_cards(1)
                self.state = "turn"
                self.round_complete = False
            elif self.state == "turn":
                self.deal_community_cards(1)
                self.state = "river"
                self.round_complete = False
            elif self.state == "river":
                self.determine_winner()
                self.state = "showdown"
                self.round_complete = False

    def player_action(self, action, amount=0):
        player = self.players[self.current_player]
        if action == "fold":
            player['folded'] = True
            player['acted'] = True
        elif action == "call":
            player['bet'] += amount
            player['chips'] -= amount
            self.pot += amount
            self.current_bets.append((self.current_player, action, amount))
            player['acted'] = True
        elif action == "raise":
            player['bet'] += amount
            player['chips'] -= amount
            self.pot += amount
            self.current_bets.append((self.current_player, action, amount))
            player['acted'] = True
            for p in self.players: # Reset action if raised
                if p != player:
                    p['acted'] = False
        self.current_player = (self.current_player + 1) % 2

        if all(player['acted'] or player['folded'] for player in self.players):
            self.round_complete = True
        if self.current_player == 1 and not self.round_complete:
            self.ai_action()

    def ai_action(self):
        ai = self.players[1]
        action, amount = self.cfr.get_action(self.players[1]['cards'], self.community_cards)
        self.player_action(action, amount)

    def determine_winner(self):
        game_end_time = pygame.time.get_ticks()
        duration = (game_end_time - self.game_start_time) / 1000.0  # วินาที
        winner = None
        if self.players[0]['folded']:
            winner = 1
            self.players[1]['chips'] += self.pot
        elif self.players[1]['folded']:
            winner = 0
            self.players[0]['chips'] += self.pot
        else:
            winner = self.cfr.evaluate_hands(
                self.players[0]['cards'] + self.community_cards,
                self.players[1]['cards'] + self.community_cards
            )
            self.players[winner]['chips'] += self.pot

        game_data = {
            'duration': duration,
            'player0_cards': ','.join(str(card) for card in self.players[0]['cards']),
            'player1_cards': ','.join(str(card) for card in self.players[1]['cards']),
            'winner': winner,
            'community_cards': ','.join(str(card) for card in self.community_cards),
            'bets': ';'.join([f"Round{i+1}:{','.join([f'P{p}:{a}:{amt}' for p, a, amt in round_bets])}" for i, round_bets in enumerate(self.bets_history + [self.current_bets])])
        }
        self.logger.log_game(game_data)

        self.pot = 0
        self.bets_history = []
        self.current_bets = []

    def reset_round(self):
        self.deck.reset()
        self.community_cards = []
        self.pot = 0
        self.current_player = 0
        for player in self.players:
            player['cards'] = []
            player['bet'] = 0
            player['folded'] = False
            player['acted'] = False
        self.state = "preflop"
        self.round_complete = False
        self.deal_hole_cards()