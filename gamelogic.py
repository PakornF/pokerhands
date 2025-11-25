import pygame
from cfr import CFR


class PokerGame:
    def __init__(self, deck, logger):
        self.deck = deck
        self.logger = logger

        # Two-player heads-up
        self.players = [
            {"cards": [], "chips": 1000, "bet": 0, "folded": False, "acted": False},
            {"cards": [], "chips": 1000, "bet": 0, "folded": False, "acted": False},
        ]
        self.community_cards = []
        self.pot = 0
        self.current_player = 0  # 0 = human, 1 = AI
        self.state = "preflop"   # preflop / flop / turn / river / showdown
        self.round_complete = False

        # CFR bot
        self.cfr = CFR()

        # Logging / timing
        self.game_start_time = pygame.time.get_ticks()
        self.showdown_timer = 0
        self.bets_history = []   # list of rounds; each round is list[(player_idx, action, amount)]
        self.current_bets = []   # bets for current street
        self.round_complete = False
        self.showdown_timer = 0

        self.last_winner = None
        # Start first hand
        self.deal_hole_cards()

    # ---------- Dealing helpers ----------

    def deal_hole_cards(self):
        self.game_start_time = pygame.time.get_ticks()
        self.community_cards = []
        self.pot = 0
        self.current_player = 0
        self.state = "preflop"
        self.round_complete = False
        self.bets_history = []
        self.current_bets = []
        for p in self.players:
            p["cards"] = [self.deck.draw(), self.deck.draw()]
            p["bet"] = 0
            p["folded"] = False
            p["acted"] = False

    def deal_community_cards(self, num):
        for _ in range(num):
            card = self.deck.draw()
            if card is not None:
                self.community_cards.append(card)
        # Save bets from the completed street
        if self.current_bets:
            self.bets_history.append(self.current_bets[:])
        self.current_bets = []
        for p in self.players:
            p["bet"] = 0
            p["acted"] = False

    # ---------- Utility helpers ----------

    def _max_bet(self):
        return max(p["bet"] for p in self.players)

    def _to_call_for(self, idx):
        return self._max_bet() - self.players[idx]["bet"]

    # ---------- Main update ----------

    def update(self):
        # Handle showdown auto-reset timer (2 seconds delay)
        if self.state == "showdown":
            now = pygame.time.get_ticks()
            if self.showdown_timer == 0:
                self.showdown_timer = now
            elif now - self.showdown_timer > 2000:
                self.reset_round()
                self.showdown_timer = 0
        else:
            self._advance_if_round_complete()

    def _advance_if_round_complete(self):
        if not self.round_complete:
            return

        # End of betting round -> move to next street or showdown
        if self.current_bets:
            self.bets_history.append(self.current_bets[:])
        self.current_bets = []

        for p in self.players:
            p["bet"] = 0
            p["acted"] = False

        if self.state == "preflop":
            self.deal_community_cards(3)
            self.state = "flop"
        elif self.state == "flop":
            self.deal_community_cards(1)
            self.state = "turn"
        elif self.state == "turn":
            self.deal_community_cards(1)
            self.state = "river"
        elif self.state == "river":
            self.determine_winner()
            self.state = "showdown"

        self.round_complete = False
        self.current_player = 0

    # ---------- Actions ----------

    def player_action(self, action, amount=0):
        player = self.players[self.current_player]

        if player["folded"]:
            return

        to_call = self._to_call_for(self.current_player)

        if action == "fold":
            # mark fold
            player["folded"] = True
            player["acted"] = True
            self.current_bets.append((self.current_player, "fold", 0))

            # immediately end the hand
            self.determine_winner()
            self.state = "showdown"
            self.round_complete = False  # no more betting this hand
            self.showdown_timer = 0      # let update() handle auto-reset
            return  # IMPORTANT: stop here, don't let AI act

        elif action == "call":
            pay = amount if amount > 0 else to_call
            pay = max(0, min(pay, player["chips"]))
            player["chips"] -= pay
            player["bet"] += pay
            self.pot += pay
            player["acted"] = True
            self.current_bets.append((self.current_player, "call", pay))

        elif action == "raise":
            pay = amount if amount > 0 else to_call + 100
            if pay <= to_call:
                pay = to_call + 100
            pay = max(0, min(pay, player["chips"]))
            player["chips"] -= pay
            player["bet"] += pay
            self.pot += pay
            player["acted"] = True
            self.current_bets.append((self.current_player, "raise", pay))
            for i, p in enumerate(self.players):
                if i != self.current_player and not p["folded"]:
                    p["acted"] = False

        # if not folded, continue normal flow
        self.current_player = (self.current_player + 1) % 2

        if all(p["acted"] or p["folded"] for p in self.players):
            self.round_complete = True

        if self.current_player == 1 and not self.round_complete:
            self.ai_action()

    def ai_action(self):
        ai_idx = 1
        ai = self.players[ai_idx]
        if ai["folded"]:
            return

        to_call = self._to_call_for(ai_idx)
        pot = self.pot
        street = self.state

        action, amount = self.cfr.get_action(
            ai["cards"],
            self.community_cards,
            pot=pot,
            to_call=to_call,
            street=street,
        )

        if action in ("call", "raise") and amount > ai["chips"]:
            amount = ai["chips"]

        self.player_action(action, amount)

    # ---------- Showdown / logging ----------

    def determine_winner(self):
        """Decide winner, award pot, build bets string, and log via DataLogger."""
        game_end_time = pygame.time.get_ticks()
        duration = (game_end_time - self.game_start_time) / 1000.0  # seconds

        # ----- Decide winner -----
        if self.players[0]["folded"] and not self.players[1]["folded"]:
            winner = 1
            self.players[1]["chips"] += self.pot
        elif self.players[1]["folded"] and not self.players[0]["folded"]:
            winner = 0
            self.players[0]["chips"] += self.pot
        else:
            # Showdown: let CFR compare full hands (hole + board)
            winner = self.cfr.evaluate_hands(
                self.players[0]["cards"] + self.community_cards,
                self.players[1]["cards"] + self.community_cards,
            )
            self.players[winner]["chips"] += self.pot

        # Optional: remember winner for UI
        if hasattr(self, "last_winner"):
            self.last_winner = winner

        # ----- Build bets string for CSV -----
        # Combine all completed rounds + any current bets (last street)
        rounds = self.bets_history + [self.current_bets]
        round_strs = []
        for i, round_bets in enumerate(rounds):
            if not round_bets:
                continue
            # round_bets is list of (player_idx, action, amount)
            moves = [f"P{p}:{act}{amt}" for (p, act, amt) in round_bets]
            round_strs.append(f"Round{i+1}:" + ",".join(moves))
        bets_str = ";".join(round_strs)

        # ----- Build game_data dict (NOW includes 'bets') -----
        game_data = {
            "duration": duration,
            "player0_cards": ",".join(str(c) for c in self.players[0]["cards"]),
            "player1_cards": ",".join(str(c) for c in self.players[1]["cards"]),
            "winner": winner,
            "community_cards": ",".join(str(c) for c in self.community_cards),
            "bets": bets_str,  # 👈 important
        }

        self.logger.log_game(game_data)

        # Reset pot and bet histories for the next hand
        self.pot = 0
        self.bets_history = []
        self.current_bets = []

    # ---------- New hand ----------

    def reset_round(self):
        self.deck.reset()
        self.deal_hole_cards()