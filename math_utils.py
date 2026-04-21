# Your dictionary of games
casino_games = {
    "Coin Flip (Fair)": 0.5000,
    "Black Jack (Basic Strategy)": 0.4950,
    "Craps (Pass Line)": 0.4929,
    "Roulette (European - 1 Zero)": 0.4865,
    "Roulette (American - 2 Zeros)": 0.4737
}

# Your theoretical truth function
def calculate_theoretical_truth(wallet, goal, p):
    if p == 0.5:
        return (wallet / goal) * 100
    else:
        q = 1 - p
        prob = (1 - (q / p) ** wallet) / (1 - (q / p) ** goal)
        return prob * 100