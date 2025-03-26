class Player:
    def __init__(self):
        self.cards = []
        self.chips = 1000  # Starting chips
        self.current_bet = 0

    def bet(self, amount):
        if amount > self.chips:
            raise ValueError("Not enough chips to bet this amount")
        self.chips -= amount
        self.current_bet += amount

    def fold(self):
        self.cards = []
        self.current_bet = 0

    def raise_bet(self, current_bet):
        raise_amount = current_bet * 1.5
        if raise_amount > self.chips:
            raise ValueError("Not enough chips to raise this amount")
        self.chips -= raise_amount
        self.current_bet += raise_amount
        return raise_amount

    def call(self, current_bet):
        call_amount = current_bet - self.current_bet
        if call_amount > self.chips:
            raise ValueError("Not enough chips to call this amount")
        self.chips -= call_amount
        self.current_bet += call_amount