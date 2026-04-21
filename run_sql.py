import pandas as pd
import sqlite3

print("Loading All Casino Data into SQL...\n")

# 1. Load BOTH CSV files
df_regular = pd.read_csv('casino_population_ledger.csv')
df_kelly = pd.read_csv('kelly_card_counters_ledger.csv')

# 2. Combine them into one massive spreadsheet
df_combined = pd.concat([df_regular, df_kelly], ignore_index=True)

# 3. Create the fast SQL database in memory
conn = sqlite3.connect(':memory:')
df_combined.to_sql('master_ledger', conn, index=False)

# ==========================================
# 4. THE ULTIMATE COMPARISON QUERY
# ==========================================
# We use ROUND() to make the decimals look clean!
query = """
SELECT 
    Strategy, 
    COUNT(Player_ID) AS Total_Players,
    ROUND(AVG(CASE WHEN Result = 'Win' THEN 100.0 ELSE 0 END), 2) AS Win_Percentage,
    ROUND(AVG(Rounds_Survived), 0) AS Avg_Rounds_Played,
    SUM(Starting_Wallet - Final_Wallet) AS Total_Casino_Profit
FROM 
    master_ledger
GROUP BY 
    Strategy
ORDER BY 
    Total_Casino_Profit DESC;
"""

# 5. Run the query and print
result = pd.read_sql_query(query, conn)

print("--- THE ULTIMATE STRATEGY COMPARISON ---")
print(result.to_string(index=False))