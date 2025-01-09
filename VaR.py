import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# Connect to the database
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)
cursor = conn.cursor()

# Query to fetch price data for the last 365 days
query = """
SELECT date, asset_id, close
FROM market_data
WHERE date >= (CURRENT_DATE - INTERVAL '365 days')
ORDER BY date, asset_id;
"""

# Read data into a DataFrame
price_data = pd.read_sql(query, conn)

# Pivot the data to create a table of asset prices with dates as rows and assets as columns
price_data = price_data.pivot(index='date', columns='asset_id', values='close').dropna()

# Calculate daily returns
returns = price_data.pct_change(fill_method=None).dropna()

# Fetch portfolio weights
cursor.execute("SELECT asset_id, shares FROM assets")
portfolio_data = cursor.fetchall()
portfolio_weights = {
    row[0]: row[1] for row in portfolio_data
}

total_shares = sum(portfolio_weights.values())
weights = np.array([portfolio_weights[asset_id] / total_shares for asset_id in price_data.columns])

# Calculate portfolio returns
portfolio_returns = returns @ weights

# Calculate Historical VaR
confidence_level = 0.95
var_historical = np.percentile(portfolio_returns, (1 - confidence_level) * 100)

# Calculate Parametric VaR
mean_return = portfolio_returns.mean()
std_dev = portfolio_returns.std()
var_parametric = mean_return - std_dev * np.percentile(np.random.randn(100000), 100 * (1 - confidence_level))

# Calculate Monte Carlo VaR
num_simulations = 100000
simulated_returns = np.random.normal(mean_return, std_dev, num_simulations)
var_monte_carlo = np.percentile(simulated_returns, (1 - confidence_level) * 100)

# Store VaR results in the database
try:
    cursor.execute("""
        INSERT INTO portfolio_risk (date, historical_var, parametric_var, monte_carlo_var)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (date) DO UPDATE SET
            historical_var = EXCLUDED.historical_var,
            parametric_var = EXCLUDED.parametric_var,
            monte_carlo_var = EXCLUDED.monte_carlo_var;
    """, (
        datetime.now().date(),
        float(var_historical),
        float(var_parametric),
        float(var_monte_carlo)
    ))
    conn.commit()
    print("VaR results successfully stored in the database.")
except Exception as e:
    conn.rollback()
    print(f"Error storing VaR results: {e}")

# Print results
print(f"Historical VaR (95% confidence): {var_historical:.2f}")
print(f"Parametric VaR (95% confidence): {var_parametric:.2f}")
print(f"Monte Carlo VaR (95% confidence): {var_monte_carlo:.2f}")

# Close the connection
conn.close()
