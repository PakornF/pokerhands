class Player:
    def __init__(self):
        self.cards = []
        self.name = ""
        self.chips = 1000  # Starting chips
        self.current_bet = 0
        self.small_blind = False
        self.big_blind = False
        self.folded = False