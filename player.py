import numpy as np

class Player:
    def __init__(self, wallet, goal, p, casino_money):
        self.wallet = wallet
        self.goal = goal
        self.p = p
        self.casino_money = casino_money

    def timid_guy(self):
        player_wallet = np.random.randint(low=1, high=self.wallet)
        player_goal = np.random.randint(low=player_wallet + 10, high=self.goal)
        player_wallet_history = [player_wallet]
        casino_money_history = [self.casino_money]
        bet_amount = 1

        while 0 < player_wallet < player_goal:
            bet_result = np.random.choice([1,-1], p=[self.p, 1 - self.p])

            player_wallet += bet_amount * bet_result
            self.casino_money += bet_amount * -bet_result

            player_wallet_history.append(player_wallet)
            casino_money_history.append(self.casino_money)

        if player_wallet >= player_goal:
            return 1, player_wallet_history, casino_money_history, player_goal
        elif player_wallet <= 0:
            return 0, player_wallet_history, casino_money_history, player_goal


    def bold_guy(self):
        player_wallet = np.random.randint(low=1, high=self.wallet)
        player_goal = np.random.randint(low=player_wallet + 10, high=self.goal)
        player_wallet_history = [player_wallet]
        casino_money_history = [self.casino_money]

        while 0 < player_wallet < player_goal:
            bet_result = np.random.choice([1, -1], p=[self.p, 1 - self.p])

            if player_wallet <= player_goal / 2:
                bet_amount = player_wallet
            else:
                bet_amount = player_goal - player_wallet

            player_wallet += bet_amount * bet_result
            self.casino_money += bet_amount * -bet_result

            player_wallet_history.append(player_wallet)
            casino_money_history.append(self.casino_money)

        if player_wallet >= player_goal:
            return 1, player_wallet_history, casino_money_history, player_goal
        elif player_wallet <= 0:
            return 0, player_wallet_history, casino_money_history, player_goal

    def martingale_guy(self):
        player_wallet = np.random.randint(low=1, high=self.wallet)
        player_goal = np.random.randint(low=player_wallet + 10, high=self.goal)
        player_wallet_history = [player_wallet]
        casino_money_history = [self.casino_money]
        current_bet = 1


        while 0 < player_wallet < player_goal:
            current_bet = min(current_bet, player_wallet)

            bet_result = np.random.choice([1, -1], p=[self.p, 1 - self.p])

            player_wallet += current_bet * bet_result
            self.casino_money += current_bet * -bet_result

            player_wallet_history.append(player_wallet)
            casino_money_history.append(self.casino_money)

            if bet_result == 1:
                current_bet = 1
            elif bet_result == -1:
                current_bet *= 2
        if player_wallet >= player_goal:
            return 1, player_wallet_history, casino_money_history, player_goal
        else:
            return 0, player_wallet_history, casino_money_history, player_goal

    def kelly_guy(self):
        # 1. Generate the wallet and goal safely
        player_wallet = np.random.randint(low=1, high=self.wallet)
        safe_low = player_wallet + 1
        safe_high = max(safe_low + 1, self.goal)
        player_goal = np.random.randint(low=safe_low, high=safe_high)

        player_wallet_history = [player_wallet]
        casino_money_history = [self.casino_money]

        # 2. Calculate the Kelly Edge: f* = 2p - 1
        # Example: If p=0.51, edge is 0.02 (Bet 2% of wallet)
        f_star = (2 * self.p) - 1
        if f_star <= 0:
            f_star = 0.01  # Safety net just in case p is lower than 0.5!

        while 0 < player_wallet < player_goal:
            # 3. Bet exact Kelly percentage of current wallet
            bet_amount = int(player_wallet * f_star)

            # Minimum bet is $1, and don't bet more than needed to reach goal
            if bet_amount < 1:
                bet_amount = 1
            if player_wallet + bet_amount > player_goal:
                bet_amount = player_goal - player_wallet

            # Flip the coin
            bet_result = np.random.choice([1, -1], p=[self.p, 1 - self.p])

            player_wallet += bet_amount * bet_result
            self.casino_money += bet_amount * -bet_result

            player_wallet_history.append(player_wallet)
            casino_money_history.append(self.casino_money)

        # 4. Return the data
        if player_wallet >= player_goal:
            return 1, player_wallet_history, casino_money_history, player_goal
        else:
            return 0, player_wallet_history, casino_money_history, player_goal

#casino_player = Player(wallet=100, goal=500, p=0.5, casino_money=10000000)

#win_result, p_history, c_history, p_goal = casino_player.timid_guy()

#starting_wallet = p_history[0]

'''print("=====================================")
print("A NEW PLAYER ENTERS THE CASINO")
print("=====================================")
print(f"Starting Wallet: ${starting_wallet}")
print(f"Player's Goal:   ${p_goal}")
print("-------------------------------------")
print(f"Game Result (1=Win, 0=Ruin): {win_result}")
print(f"Player's Final Wallet: ${p_history[-1]}")
print(f"Casino's Final Bankroll: ${c_history[-1]}")
print(f"Number of rounds played: {len(p_history) - 1}")
print("=====================================")'''