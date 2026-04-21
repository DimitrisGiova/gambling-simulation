import numpy as np

class Strategy:

    def __init__(self, wallet, goal, p, num_of_rounds, lam = 1.0):
        self.wallet = wallet
        self.goal = goal
        self.p = p
        self.num_of_rounds = num_of_rounds
        self.lam = lam

    def timid_play(self):
        current_wallet = self.wallet
        wallet_history = [current_wallet]

        while current_wallet < self.goal and current_wallet > 0:
            self.num_of_rounds += 1
            bet_result = np.random.choice([1,-1], p=[self.p, 1 - self.p])

            current_wallet += bet_result

            wallet_history.append(current_wallet)

            if current_wallet >= self.goal:
                return 1, wallet_history
            elif current_wallet <= 0:
                return 0, wallet_history

    def bold_play(self):
        current_wallet = self.wallet

        wallet_history = [current_wallet]

        while current_wallet < self.goal and current_wallet > 0:
            self.num_of_rounds += 1
            bet_result = np.random.choice([1,-1], p=[self.p, 1 - self.p])
            if 0 < current_wallet <= self.goal/2:
                current_wallet += current_wallet * bet_result
            elif self.goal / 2 < current_wallet < self.goal:
                current_wallet += (self.goal - current_wallet) * bet_result

            wallet_history.append(current_wallet)

        if current_wallet >= self.goal:
            return 1, wallet_history
        elif current_wallet <= 0:
            return 0, wallet_history



    def martingale_play(self):
        current_wallet = self.wallet
        current_bet = 1
        wallet_history = [current_wallet]

        wallet_history = [current_wallet]

        while 0 < current_wallet < self.goal:
            self.num_of_rounds += 1
            current_bet = min(current_bet, current_wallet)

            bet_result = np.random.choice([1,-1], p=[self.p, 1 - self.p])

            current_wallet += current_bet * bet_result
            wallet_history.append(current_wallet)

            if bet_result == 1:
                current_bet = 1
            elif bet_result == -1:
                current_bet *= 2
        if current_wallet >= self.goal:
            return 1, wallet_history
        else:
            return 0, wallet_history

    def poisson_play(self):
        current_wallet = self.wallet
        cost_to_play = 1
        while 0 < current_wallet < self.goal:
            self.num_of_rounds += 1
            current_wallet -= 1
            if current_wallet <= 0:
                return 0
            payout = np.random.poisson(self.lam)
            current_wallet += payout
            if current_wallet >= self.goal:
                return 1
            elif current_wallet <= 0:
                return 0
