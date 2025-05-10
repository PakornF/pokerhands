import random
from itertools import combinations

class CFR:
    def __init__(self):
        self.regret_sum = {}
        self.strategy_sum = {}
        self.actions = ["fold", "call", "raise"]

    def get_info_set(self, hole_cards, community_cards):
        return str(hole_cards) + str(community_cards)

    def get_strategy(self, info_set):
        if info_set not in self.regret_sum:
            self.regret_sum[info_set] = [0.0] * len(self.actions)
            self.strategy_sum[info_set] = [0.0] * len(self.actions)

        total_regret = sum(max(0, r) for r in self.regret_sum[info_set])
        strategy = [max(0, r) / total_regret if total_regret > 0 else 1.0 / len(self.actions)
                    for r in self.regret_sum[info_set]]
        return strategy

    def get_action(self, hole_cards, community_cards):
        info_set = self.get_info_set(hole_cards, community_cards)
        strategy = self.get_strategy(info_set)
        r = random.random()
        cumulative = 0.0
        for i, prob in enumerate(strategy):
            cumulative += prob
            if r < cumulative:
                action = self.actions[i]
                amount = 100 if action == "raise" else 50 if action == "call" else 0
                return action, amount
        return "call", 50 # Default to call if no action chosen

    def evaluate_hands(self, hand1, hand2):
        def hand_value(hand):
            values = sorted([card.value() for card in hand], reverse=True)
            return sum(values[:5])  # Use 5 best cards

        value1 = hand_value(hand1)
        value2 = hand_value(hand2)
        return 0 if value1 > value2 else 1