import numpy as np
import time
import matplotlib.pyplot as plt

from strategies import Strategy
from player import Player
from math_utils import calculate_theoretical_truth, casino_games

import concurrent.futures

import pandas as pd

n_simulations = 200
wallet = 50
goal = 100
p = 0.5
num_of_rounds = 0
casino_money = 1000000

num_of_wins = 0
num_of_simulations = n_simulations

sim = Strategy(wallet, goal, p, num_of_rounds, lam = 1.0)
player = Player(wallet, goal, p, casino_money)



#Directories
Strategies = {
    "Timid": sim.timid_play,
    "Bold": sim.bold_play,
    "Martingale": sim.martingale_play
}

player_strategies = {
    "Timid_Player": player.timid_guy,
    "Bold_Player": player.bold_guy,
    "Martingale_Player": player.martingale_guy
}


# MULTIPROCESSING
def simulate_single_visitor(args):
    # Unpack the arguments
    player_id, strategy_choice = args

    worker_player = Player(wallet=50, goal=250, p=0.48, casino_money=0)

    if strategy_choice == "Timid_Player":
        win_status, p_history, c_history, p_goal = worker_player.timid_guy()
    elif strategy_choice == "Bold_Player":
        win_status, p_history, c_history, p_goal = worker_player.bold_guy()
    else:
        win_status, p_history, c_history, p_goal = worker_player.martingale_guy()

    starting_wallet = p_history[0]
    final_wallet = p_history[-1]
    casino_profit = starting_wallet - final_wallet

    # Create the exact dictionary Pandas needs
    receipt = {
        "Player_ID": player_id,
        "Strategy": strategy_choice.replace("_Player", ""),
        "Starting_Wallet": starting_wallet,
        "Goal": p_goal,
        "Final_Wallet": final_wallet,
        "Rounds_Survived": len(p_history) - 1,
        "Result": "Win" if win_status == 1 else "Loss"
    }

    return receipt, win_status, casino_profit


# MULTIPROCESSING
def simulate_single_kelly_visitor(player_id):
    # The Card Counter has an edge! p = 0.51
    worker_player = Player(wallet=50, goal=500, p=0.51, casino_money=0)

    win_status, p_history, c_history, p_goal = worker_player.kelly_guy()

    starting_wallet = p_history[0]
    final_wallet = p_history[-1]
    casino_profit = starting_wallet - final_wallet

    # Create the receipt
    receipt = {
        "Player_ID": player_id,
        "Strategy": "Kelly_Criterion",
        "Starting_Wallet": starting_wallet,
        "Goal": p_goal,
        "Final_Wallet": final_wallet,
        "Rounds_Played": len(p_history) - 1,
        "Result": "Win" if win_status == 1 else "Loss"
    }

    return receipt, win_status, casino_profit



# Loop through the GAMES instead of the strategies
def run_game_comparison():

    print("\n--- Running Casino Game Comparison ---")

    game_win_rate_history = {game: [] for game in casino_games.keys()}

    for game_name, game_p in casino_games.items():
        wins = 0
        # Update the player's probability for this specific game
        sim = Strategy(wallet=wallet, goal=goal, p=game_p, num_of_rounds=0)

        for i in range(1, n_simulations + 1):
            sim.num_of_rounds = 0
            result, _ = sim.timid_play()  # Timid Play
            wins += result

            current_win_rate = (wins / i) * 100
            game_win_rate_history[game_name].append(current_win_rate)

        final_win_percentage = (wins / n_simulations) * 100
        truth = calculate_theoretical_truth(wallet, goal, game_p)
        print(f"{game_name} | Simulated: {final_win_percentage:.2f}% | True Math: {truth:.2f}%")

    # PLOTTING THE GAME COMPARISON
    plt.figure(figsize=(12, 7))

    # Colors to make it look nice
    colors = ['blue', 'purple', 'orange', 'green', 'red']

    for (game_name, game_p), color in zip(casino_games.items(), colors):
        # Plot the simulated convergence line
        plt.plot(game_win_rate_history[game_name], label=f"{game_name} Sim", color=color, alpha=0.7)

        # Calculate and plot the TRUE mathematical line
        truth = calculate_theoretical_truth(wallet, goal, game_p)
        plt.axhline(y=truth, color=color, linestyle='--', alpha=0.5)

    plt.title(f"Gambler's Ruin: How the House Edge Destroys Timid Play (Wallet: ${wallet}, Goal: ${goal})")
    plt.xlabel("Number of Simulations")
    plt.ylabel("Cumulative Win Percentage (%)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # Moves legend outside the graph
    plt.grid(True, alpha=0.3)
    plt.tight_layout()  # Keeps the legend from getting cut off

    plt.savefig("my_graph9.png")

    #PANDAS EXPORT
    print("Exporting Game Comparison to CSV...")
    df_games = pd.DataFrame(game_win_rate_history)
    df_games.index += 1  # Make the index start at 1 instead of 0
    df_games.index.name = 'Simulation_Number'
    df_games.to_csv("game_comparison_results.csv")




# Running simulations and keeping track of the wallet for each game
def run_strategy_convergence():
    print(f"Number of simulations: {num_of_simulations}")

    sim.p = 0.5

    # Graph Plotting
    print("\nGenerating graphs...")

    _, timid_hist = sim.timid_play()
    _, bold_hist = sim.bold_play()
    _, mart_hist = sim.martingale_play()

    rounds_history = {"Timid": [], "Bold": [], "Martingale": []}

    for name, method in Strategies.items():
        wins = 0
        start_time = time.perf_counter()

        original_rounds_val = num_of_simulations

        for _ in range(num_of_simulations):
            sim.num_of_rounds = 0
            result, history = method()
            rounds_history[name].append(sim.num_of_rounds)
            wins += result

        execution_time = time.perf_counter() - start_time
        sim.num_of_rounds = original_rounds_val

    # Win Percentage Calculation
    win_rate_history = {"Timid": [], "Bold": [], "Martingale": []}

    for name, method in Strategies.items():
        wins = 0
        start_time = time.perf_counter()

        for i in range(1, n_simulations+ 1):
            sim.num_of_rounds = i
            sim.num_of_rounds = 0
            result, _ = method()
            wins += result

            current_win_rate = (wins / i) * 100
            win_rate_history[name].append(current_win_rate)
        execution_time = time.perf_counter() - start_time
        final_win_percentage = (wins / n_simulations) * 100
        print(f"{name} Win %: {final_win_percentage:.2f}% | Time: {execution_time:.4f} sec")

    # timid strategy wallet history for one simulation
    plt.figure(1)
    plt.plot(timid_hist, label="Timid Play", color="blue", alpha=0.7)
    plt.title(f"Timid Play Wallet History (Wallet: ${wallet}, Goal: ${goal})")
    plt.xlabel("Number of Rounds")
    plt.ylabel("Wallet Amount ($)")
    plt.axhline(y=goal, color='g', linestyle='--', label="Goal")
    plt.axhline(y=0, color='r', linestyle='--', label="Ruin")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig("my_graph1.png")

    # Bold Play wallet history graph for one simulation
    plt.figure(2)
    plt.plot(bold_hist, label="Bold Play", color="orange", linewidth=2, marker='o')
    plt.title(f"Bold Play Wallet History (Wallet: ${wallet}, Goal: ${goal})")
    plt.xlabel("Number of Rounds")
    plt.ylabel("Wallet Amount ($)")
    plt.axhline(y=goal, color='g', linestyle='--', label="Goal")
    plt.axhline(y=0, color='r', linestyle='--', label="Ruin")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig("my_graph2.png")

    # Martingale Play wallet history graph for one simulation
    plt.figure(3)
    plt.plot(mart_hist, label="Martingale", color="purple", alpha=0.7)
    plt.title(f"Martingale Play Wallet History (Wallet: ${wallet}, Goal: ${goal})")
    plt.xlabel("Number of Rounds")
    plt.ylabel("Wallet Amount ($)")
    plt.axhline(y=goal, color='g', linestyle='--', label="Goal")
    plt.axhline(y=0, color='r', linestyle='--', label="Ruin")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig("my_graph3.png")

    # Bold and Martingale Play wallet history graph for one simulation
    plt.figure(4)
    plt.plot(bold_hist, label="Bold Play", color="orange", linewidth=2, marker='o')
    plt.plot(mart_hist, label="Martingale", color="purple", alpha=0.7)
    plt.title(f"Bold & Martingale Play Wallet Histories (Wallet: ${wallet}, Goal: ${goal})")
    plt.xlabel("Number of Rounds")
    plt.ylabel("Wallet Amount ($)")
    plt.axhline(y=goal, color='g', linestyle='--', label="Goal")
    plt.axhline(y=0, color='r', linestyle='--', label="Ruin")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig("my_graph4.png")

    # All plays graph wallet history
    plt.figure(5)
    plt.plot(timid_hist, label="Timid Play", color="blue", alpha=0.7)
    plt.plot(bold_hist, label="Bold Play", color="orange", linewidth=2, marker='o')
    plt.plot(mart_hist, label="Martingale", color="purple", alpha=0.7)
    plt.title(f"Timid & Bold & Martingale Play Wallet Histories (Wallet: ${wallet}, Goal: ${goal})")
    plt.xlabel("Number of Rounds")
    plt.ylabel("Wallet Amount ($)")
    plt.axhline(y=goal, color='g', linestyle='--', label="Goal")
    plt.axhline(y=0, color='r', linestyle='--', label="Ruin")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig("my_graph5.png")

    # Win rate history graph plotting
    plt.figure(figsize=(10, 6))
    plt.plot(win_rate_history["Timid"], label="Timid Play", color="blue", alpha=0.8)
    plt.plot(win_rate_history["Bold"], label="Bold Play", color="orange", alpha=0.8)
    plt.plot(win_rate_history["Martingale"], label="Martingale", color="purple", alpha=0.8)

    theoretical_win_rate = calculate_theoretical_truth(wallet, goal, p)

    plt.title(f"Strategy Convergence (Wallet: ${wallet}, Goal: ${goal}, p={p})")
    plt.xlabel("Number of Simulations")
    plt.ylabel("Cumulative Win Percentage (%)")
    plt.axhline(y=theoretical_win_rate, color='black', linestyle='--', linewidth=2,
                label=f"Theoretical Truth ({theoretical_win_rate}%)")

    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig("my_graph6.png")

    #PANDAS EXPORT
    print("Exporting Strategy Data to CSV...")

    # 1. Export the Win Rates
    df_win_rates = pd.DataFrame(win_rate_history)
    df_win_rates.index += 1
    df_win_rates.index.name = 'Simulation_Number'
    df_win_rates.to_csv("strategy_win_rates.csv")

    # 2. Export the Rounds Played
    df_rounds = pd.DataFrame(rounds_history)
    df_rounds.index += 1
    df_rounds.index.name = 'Simulation_Number'
    df_rounds.to_csv("strategy_rounds_played.csv")



#Simulating n players entering a casino
def run_population_simulation():
    n_players = 100_000  # Let's crunch 100,000 players!
    strategy_names = ["Timid_Player", "Bold_Player", "Martingale_Player"]
    strategy_probs = [0.60, 0.30, 0.10]

    print(f"\n--- Simulating {n_players:,} visitors across all CPU Cores ---")
    start_time = time.perf_counter()

    # 1. Prepare the Data
    crowd_strategies = np.random.choice(strategy_names, size=n_players, p=strategy_probs)

    # Create a list of tuples: (Player_ID, Strategy) for the workers
    tasks = [(i + 1, crowd_strategies[i]) for i in range(n_players)]

    total_winners = 0
    total_losers = 0
    current_bankroll = 1_000_000
    overall_casino_bankroll = [current_bankroll]

    # The master list for Pandas
    player_database = []

    # 2. Start the Multi-Core Engine
    import concurrent.futures
    with concurrent.futures.ProcessPoolExecutor() as executor:

        # Hand the tasks to the cores
        results = executor.map(simulate_single_visitor, tasks)

        # 3. Collect the data as the cores finish
        for receipt, win_status, casino_profit in results:
            player_database.append(receipt)  # Save to Pandas database

            if win_status == 1:
                total_winners += 1
            else:
                total_losers += 1

            current_bankroll += casino_profit
            overall_casino_bankroll.append(current_bankroll)

    execution_time = time.perf_counter() - start_time

    # 4. Final Calculations
    win_percent = (total_winners / n_players) * 100
    loss_percent = (total_losers / n_players) * 100

    print(f"Simulation Time:          {execution_time:.2f} seconds")
    print(f"Casino starting bankroll: ${overall_casino_bankroll[0]:,}")
    print(f"Casino final bankroll:    ${overall_casino_bankroll[-1]:,}")
    print(f"Total Winners:            {total_winners:,} players ({win_percent:.1f}%)")
    print(f"Total Losers:             {total_losers:,} players ({loss_percent:.1f}%)")

    # 5. Pandas Export
    print("\nExporting Population Ledger to CSV...")
    df_population = pd.DataFrame(player_database)
    df_population.to_csv("casino_population_ledger.csv", index=False)

    # 6. Generate Graphs
    print("Generating Population Graphs...")

    plt.figure(figsize=(10, 6))
    plt.plot(overall_casino_bankroll, color="green", linewidth=2)
    plt.title(f"The House Always Wins: Casino Bankroll over {n_players:,} Players")
    plt.xlabel("Number of Players")
    plt.ylabel("Casino Total Bankroll ($)")
    plt.grid(True, alpha=0.3)
    plt.savefig("my_graph7_casino_bankroll.png")

    plt.figure(figsize=(8, 8))
    labels = ['Reached Goal', 'Lost Everything']
    sizes = [total_winners, total_losers]
    colors = ['#4CAF50', '#F44336']
    explode = (0.1, 0)
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title(f"Outcome of {n_players:,} Casino Visitors")
    plt.savefig("my_graph8_population_pie.png")

    plt.show()


def run_kelly_simulation():
    n_players = 1_00 # 10,000 Card Counters enter the casino...

    print(f"\n--- Simulating {n_players:,} Card Counters (Kelly Strategy) ---")
    start_time = time.perf_counter()

    tasks = [i + 1 for i in range(n_players)]

    total_winners = 0
    total_losers = 0

    # The Casino starts with $1 Million. Will they survive?
    current_bankroll = 1_000_000
    overall_casino_bankroll = [current_bankroll]

    player_database = []

    import concurrent.futures
    import pandas as pd

    # ThreadPool is generally safer for file writing/IDE environments
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Use chunksize for speed!
        results = executor.map(simulate_single_kelly_visitor, tasks, chunksize=100)

        for receipt, win_status, casino_profit in results:
            player_database.append(receipt)

            if win_status == 1:
                total_winners += 1
            else:
                total_losers += 1

            current_bankroll += casino_profit
            overall_casino_bankroll.append(current_bankroll)

    execution_time = time.perf_counter() - start_time

    win_percent = (total_winners / n_players) * 100
    loss_percent = (total_losers / n_players) * 100

    print(f"Simulation Time:          {execution_time:.2f} seconds")
    print(f"Total Winners:            {total_winners:,} players ({win_percent:.1f}%)")
    print(f"Total Losers:             {total_losers:,} players ({loss_percent:.1f}%)")
    print(f"Casino starting bankroll: ${overall_casino_bankroll[0]:,}")
    print(f"Casino final bankroll:    ${overall_casino_bankroll[-1]:,}")

    # --- PANDAS EXPORT ---
    print("\nExporting Kelly Ledger to CSV...")
    df_kelly = pd.DataFrame(player_database)
    df_kelly.to_csv("kelly_card_counters_ledger.csv", index=False)

    # --- GRAPHING ---
    print("Generating Kelly Graphs...")

    plt.figure(figsize=(10, 6))
    plt.plot(overall_casino_bankroll, color="red", linewidth=2)  # Red because the casino is bleeding!
    plt.title(f"The Casino is Bleeding: Bankroll vs {n_players:,} Card Counters")
    plt.xlabel("Number of Players Processed")
    plt.ylabel("Casino Total Bankroll ($)")
    plt.axhline(y=1_000_000, color='black', linestyle='--', label="Starting Bankroll")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("my_graph10_kelly_casino_bankroll.png")

    plt.figure(figsize=(8, 8))
    labels = ['Winners (Card Counters)', 'Losers (Bad Luck)']
    sizes = [total_winners, total_losers]
    colors = ['#4CAF50', '#F44336']
    explode = (0.1, 0)
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title(f"Outcome of {n_players:,} Card Counters (p=0.51)")
    plt.savefig("my_graph11_kelly_pie.png")

    plt.show()


if __name__ == "__main__":

    #run_game_comparison()
    #run_strategy_convergence()
    #run_population_simulation()
    run_kelly_simulation()
