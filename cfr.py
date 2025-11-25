import random
from itertools import combinations
from collections import defaultdict
from typing import Any, Dict, List, Tuple, Optional

ACTIONS = ("fold", "call", "raise")

_RANK_TO_INT: Dict[str, int] = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 11, "Q": 12, "K": 13, "A": 14,
}


def _card_rank(card: Any) -> int:
    return _RANK_TO_INT[str(card.rank)]


def _card_suit(card: Any) -> str:
    return str(card.suit)


def _is_straight(ranks: List[int]) -> Optional[int]:
    if len(ranks) < 5:
        return None
    rset = set(ranks)
    # wheel A-2-3-4-5
    if {14, 5, 4, 3, 2}.issubset(rset):
        return 5
    for hi in range(14, 5, -1):
        seq = {hi, hi - 1, hi - 2, hi - 3, hi - 4}
        if seq.issubset(rset):
            return hi
    return None


def evaluate_7card_hand(cards: List[Any]) -> Tuple[int, List[int]]:
    """
    Best 5-card poker hand from up to 7 cards.
    Returns (category, tiebreakers) where higher is better.

    Categories:
        8 straight flush
        7 four of a kind
        6 full house
        5 flush
        4 straight
        3 three of a kind
        2 two pair
        1 one pair
        0 high card
    """
    best = (-1, [])
    for combo in combinations(cards, 5):
        ranks = sorted((_card_rank(c) for c in combo), reverse=True)
        suits = [_card_suit(c) for c in combo]
        counts: Dict[int, int] = defaultdict(int)
        for r in ranks:
            counts[r] += 1
        items = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
        is_flush = len(set(suits)) == 1
        distinct = sorted(set(ranks), reverse=True)
        straight_hi = _is_straight(distinct)

        if straight_hi is not None and is_flush:
            score = (8, [straight_hi])
        elif items[0][1] == 4:
            quad = items[0][0]
            kicker = max(r for r in ranks if r != quad)
            score = (7, [quad, kicker])
        elif items[0][1] == 3 and items[1][1] == 2:
            trips = items[0][0]
            pair = items[1][0]
            score = (6, [trips, pair])
        elif is_flush:
            score = (5, ranks)
        elif straight_hi is not None:
            score = (4, [straight_hi])
        elif items[0][1] == 3:
            trips = items[0][0]
            kickers = sorted((r for r in ranks if r != trips), reverse=True)
            score = (3, [trips] + kickers)
        elif items[0][1] == 2 and items[1][1] == 2:
            high_pair = max(items[0][0], items[1][0])
            low_pair = min(items[0][0], items[1][0])
            kicker = max(r for r in ranks if r != high_pair and r != low_pair)
            score = (2, [high_pair, low_pair, kicker])
        elif items[0][1] == 2:
            pair = items[0][0]
            kickers = sorted((r for r in ranks if r != pair), reverse=True)
            score = (1, [pair] + kickers)
        else:
            score = (0, ranks)

        if score > best:
            best = score
    return best


class _Node:
    __slots__ = ("regret_sum", "strategy_sum")

    def __init__(self) -> None:
        self.regret_sum = [0.0, 0.0, 0.0]
        self.strategy_sum = [0.0, 0.0, 0.0]

    def strategy(self, reach: float) -> List[float]:
        # regret-matching
        positive = [max(r, 0.0) for r in self.regret_sum]
        s = sum(positive)
        if s > 1e-12:
            strat = [r / s for r in positive]
        else:
            strat = [1.0 / len(self.regret_sum)] * len(self.regret_sum)
        for i in range(len(self.strategy_sum)):
            self.strategy_sum[i] += reach * strat[i]
        return strat

    def avg_strategy(self) -> List[float]:
        s = sum(self.strategy_sum)
        if s > 1e-12:
            return [x / s for x in self.strategy_sum]
        return [1.0 / len(self.strategy_sum)] * len(self.strategy_sum)


class CFR:
    """
    Actually-usable CFR-style bot for heads-up Hold'em.

    - Uses simple hand & board abstraction (hole strength + board texture + pot odds).
    - Runs a small amount of self-play training in __init__.
    - Public API stays compatible with the old version.
    """

    def __init__(self, iterations: int = 2000, seed: Optional[int] = None) -> None:
        self.rng = random.Random(seed)
        self.nodes: Dict[str, _Node] = {}
        self._train(iterations)

    # ---------- Abstraction helpers ----------

    def _hole_key(self, hole_cards: List[Any]) -> str:
        r1, r2 = sorted((_card_rank(c) for c in hole_cards), reverse=True)
        suited = _card_suit(hole_cards[0]) == _card_suit(hole_cards[1])
        return f"{r1}{r2}{'s' if suited else 'o'}"

    def _board_key(self, community_cards: List[Any]) -> str:
        if not community_cards:
            return "none"
        ranks = sorted((_card_rank(c) for c in community_cards), reverse=True)
        suits = [_card_suit(c) for c in community_cards]
        paired = len(set(ranks)) < len(ranks)
        flushy = max(suits.count(s) for s in set(suits)) >= 3
        distinct = sorted(set(ranks), reverse=True)
        straighty = _is_straight(distinct) is not None
        hi = ranks[0]
        return f"{hi}|p{int(paired)}f{int(flushy)}s{int(straighty)}"

    def _to_call_bucket(self, to_call: int, pot: int) -> str:
        if to_call <= 0:
            return "0"
        if pot <= 0:
            return "hi"
        odds = to_call / pot
        if odds < 0.25:
            return "lo"
        if odds < 0.6:
            return "mid"
        return "hi"

    def _info_set(
        self,
        player: int,
        hole_cards: List[Any],
        community_cards: List[Any],
        street: str,
        pot: int,
        to_call: int,
    ) -> str:
        return "|".join(
            [
                str(player),
                street,
                self._hole_key(hole_cards),
                self._board_key(community_cards),
                self._to_call_bucket(to_call, pot),
            ]
        )

    def _node(self, info: str) -> _Node:
        node = self.nodes.get(info)
        if node is None:
            node = _Node()
            self.nodes[info] = node
        return node

    # ---------- Virtual deck for training ----------

    def _deal_virtual_card(self, seen: set) -> Any:
        ranks = list(_RANK_TO_INT.keys())
        suits = ["♠", "♥", "♦", "♣"]
        while True:
            r = self.rng.choice(ranks)
            s = self.rng.choice(suits)
            key = f"{r}{s}"
            if key not in seen:
                seen.add(key)

                class _TmpCard:
                    __slots__ = ("rank", "suit")

                    def __init__(self, rank, suit):
                        self.rank = rank
                        self.suit = suit

                    def __str__(self) -> str:
                        return f"{self.rank}{self.suit}"

                return _TmpCard(r, s)

    # ---------- CFR training ----------

    def _train(self, iterations: int) -> None:
        streets = [("preflop", 0), ("flop", 3), ("turn", 1), ("river", 1)]
        for _ in range(iterations):
            seen: set = set()
            p0_hole = [self._deal_virtual_card(seen), self._deal_virtual_card(seen)]
            p1_hole = [self._deal_virtual_card(seen), self._deal_virtual_card(seen)]
            board: List[Any] = []
            pot = 100
            stacks = [950, 950]
            contrib = [50, 50]
            self._cfr_round(
                player=0,
                p0_hole=p0_hole,
                p1_hole=p1_hole,
                board=board,
                streets=streets,
                street_i=0,
                pot=pot,
                stacks=stacks,
                contrib=contrib,
                raised_this_street=False,
                history=[],
                reach0=1.0,
                reach1=1.0,
            )

    def _cfr_round(
        self,
        player: int,
        p0_hole: List[Any],
        p1_hole: List[Any],
        board: List[Any],
        streets,
        street_i: int,
        pot: int,
        stacks: List[int],
        contrib: List[int],
        raised_this_street: bool,
        history: List[str],
        reach0: float,
        reach1: float,
    ) -> float:
        # terminal due to fold
        if history and history[-1] == "fold":
            folder = 1 - player
            return pot if folder == 1 else -pot

        street_name, to_reveal = streets[street_i]

        # if last two actions were (call/raise, call/fold) -> street finished
        if len(history) >= 2 and history[-2] in ("call", "raise") and history[-1] in ("call", "fold"):
            if street_i == len(streets) - 1:
                return self._showdown_utility(p0_hole, p1_hole, board, pot)

            new_board = list(board)
            seen = {str(c) for c in p0_hole + p1_hole + board}
            for _ in range(to_reveal):
                new_board.append(self._deal_virtual_card(seen))

            return self._cfr_round(
                player=0,
                p0_hole=p0_hole,
                p1_hole=p1_hole,
                board=new_board,
                streets=streets,
                street_i=street_i + 1,
                pot=pot,
                stacks=stacks,
                contrib=contrib,
                raised_this_street=False,
                history=[],
                reach0=reach0,
                reach1=reach1,
            )

        # otherwise decision node
        hole = p0_hole if player == 0 else p1_hole
        to_call = max(contrib) - contrib[player]
        info = self._info_set(player, hole, board, street_name, pot, to_call)
        node = self._node(info)
        strat = node.strategy(reach0 if player == 0 else reach1)

        action_utils = [0.0, 0.0, 0.0]
        node_utility = 0.0

        for i, action in enumerate(ACTIONS):
            if action == "raise" and (raised_this_street or stacks[player] <= to_call):
                continue

            next_pot = pot
            next_stacks = stacks[:]
            next_contrib = contrib[:]
            next_hist = history + [action]
            next_raised = raised_this_street

            if action == "fold":
                util = self._cfr_round(
                    1 - player,
                    p0_hole,
                    p1_hole,
                    board,
                    streets,
                    street_i,
                    next_pot,
                    next_stacks,
                    next_contrib,
                    next_raised,
                    next_hist,
                    reach0,
                    reach1,
                )
            elif action == "call":
                pay = min(to_call, next_stacks[player])
                next_stacks[player] -= pay
                next_contrib[player] += pay
                next_pot += pay
                util = self._cfr_round(
                    1 - player,
                    p0_hole,
                    p1_hole,
                    board,
                    streets,
                    street_i,
                    next_pot,
                    next_stacks,
                    next_contrib,
                    next_raised,
                    next_hist,
                    reach0,
                    reach1,
                )
            else:  # raise
                raise_amt = 100 if street_name in ("preflop", "flop") else 200
                pay = min(to_call + raise_amt, next_stacks[player])
                next_stacks[player] -= pay
                next_contrib[player] += pay
                next_pot += pay
                next_raised = True
                util = self._cfr_round(
                    1 - player,
                    p0_hole,
                    p1_hole,
                    board,
                    streets,
                    street_i,
                    next_pot,
                    next_stacks,
                    next_contrib,
                    next_raised,
                    next_hist,
                    reach0,
                    reach1,
                )

            action_utils[i] = util
            node_utility += strat[i] * util

        # regret update
        for i in range(len(ACTIONS)):
            regret = action_utils[i] - node_utility
            if player == 0:
                self._node(info).regret_sum[i] += reach1 * regret
            else:
                self._node(info).regret_sum[i] += reach0 * -regret

        return node_utility

    def _showdown_utility(
        self,
        p0_hole: List[Any],
        p1_hole: List[Any],
        board: List[Any],
        pot: int,
    ) -> float:
        v0 = evaluate_7card_hand(p0_hole + board)
        v1 = evaluate_7card_hand(p1_hole + board)
        if v0 > v1:
            return pot
        if v1 > v0:
            return -pot
        return 0.0

    # ---------- Public API ----------

    def get_average_strategy(self, info_set: str) -> List[float]:
        return self._node(info_set).avg_strategy()

    def act(
        self,
        player: int,
        hole_cards: List[Any],
        community_cards: List[Any],
        street: str,
        pot: int,
        to_call: int,
    ):
        info = self._info_set(player, hole_cards, community_cards, street, pot, to_call)
        strat = self.get_average_strategy(info)

        r = self.rng.random()
        cum = 0.0
        choice = "call"
        for i, a in enumerate(ACTIONS):
            cum += strat[i]
            if r <= cum:
                choice = a
                break

        if choice == "fold":
            return "fold", 0
        if choice == "call":
            return "call", max(0, to_call)

        raise_amt = 100 if street in ("preflop", "flop") else 200
        return "raise", max(0, to_call + raise_amt)

    def get_action(
        self,
        hole_cards: List[Any],
        community_cards: List[Any],
        pot: int = 0,
        to_call: int = 0,
        street: Optional[str] = None,
    ):
        # Backwards compatible: if street not given, infer from board size
        if street is None:
            n = len(community_cards)
            if n == 0:
                street = "preflop"
            elif n == 3:
                street = "flop"
            elif n == 4:
                street = "turn"
            else:
                street = "river"
        return self.act(1, hole_cards, community_cards, street, pot, to_call)

    def evaluate_hands(self, hand1: List[Any], hand2: List[Any]) -> int:
        v1 = evaluate_7card_hand(hand1)
        v2 = evaluate_7card_hand(hand2)
        # Return 0 if hand1 wins or ties, 1 if hand2 wins strictly.
        return 0 if v1 >= v2 else 1