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
    row[0]: float(row[1]) for row in portfolio_data  # Convert shares to float explicitly
}

# Calculate portfolio weights
total_shares = sum(portfolio_weights.values())
weights = np.array([portfolio_weights.get(asset_id, 0) / total_shares for asset_id in price_data.columns])

# Calculate portfolio returns
portfolio_returns = returns @ weights

# Helper function to calculate VaR
def calculate_var(data, confidence_level=0.95, num_simulations=100000):
    # Historical VaR
    var_historical = np.percentile(data, (1 - confidence_level) * 100)

    # Parametric VaR
    mean_return = data.mean()
    std_dev = data.std()
    var_parametric = mean_return - std_dev * np.percentile(np.random.randn(num_simulations), 100 * (1 - confidence_level))

    # Monte Carlo VaR
    simulated_returns = np.random.normal(mean_return, std_dev, num_simulations)
    var_monte_carlo = np.percentile(simulated_returns, (1 - confidence_level) * 100)

    return var_historical, var_parametric, var_monte_carlo

# Calculate VaR for crypto, stocks, and the portfolio separately
crypto_returns = returns[returns.columns.intersection([1, 2, 3])]  # Assuming asset_ids for crypto are 1, 2, 3
stock_returns = returns[returns.columns.difference([1, 2, 3])]      # All other asset_ids are stocks

crypto_var = calculate_var(crypto_returns.mean(axis=1))
stock_var = calculate_var(stock_returns.mean(axis=1))
portfolio_var = calculate_var(portfolio_returns)

# Calculate VaR in actual portfolio values
portfolio_value_query = """
SELECT SUM(market_data.close * assets.shares) AS portfolio_value
FROM market_data
JOIN assets ON market_data.asset_id = assets.asset_id
WHERE market_data.date = (SELECT MAX(date) FROM market_data);
"""
cursor.execute(portfolio_value_query)
portfolio_value = float(cursor.fetchone()[0])  # Convert to float explicitly

crypto_value = float(sum(price_data.iloc[-1][crypto_returns.columns] * np.array([portfolio_weights.get(asset_id, 0) for asset_id in crypto_returns.columns])))
stock_value = float(sum(price_data.iloc[-1][stock_returns.columns] * np.array([portfolio_weights.get(asset_id, 0) for asset_id in stock_returns.columns])))

# Convert VaR (returns) to VaR (values)
def convert_var_to_value(var, total_value):
    return [float(v) * total_value for v in var]

crypto_var_value = convert_var_to_value(crypto_var, crypto_value)
stock_var_value = convert_var_to_value(stock_var, stock_value)
portfolio_var_value = convert_var_to_value(portfolio_var, portfolio_value)

def store_var_results(date, var_results, var_type, asset_type):
    try:
        cursor.execute("""
            INSERT INTO portfolio_risk (date, historical_var, parametric_var, monte_carlo_var, type, asset_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (date, type, asset_type) DO UPDATE SET
                historical_var = EXCLUDED.historical_var,
                parametric_var = EXCLUDED.parametric_var,
                monte_carlo_var = EXCLUDED.monte_carlo_var;
        """, (
            date,
            float(var_results[0]),
            float(var_results[1]),
            float(var_results[2]),
            var_type,
            asset_type
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error storing {var_type} VaR results for {asset_type}: {e}")

# Store results for all types
store_var_results(datetime.now().date(), crypto_var, "return", "crypto")
store_var_results(datetime.now().date(), stock_var, "return", "stocks")
store_var_results(datetime.now().date(), portfolio_var, "return", "portfolio")
store_var_results(datetime.now().date(), crypto_var_value, "value", "crypto")
store_var_results(datetime.now().date(), stock_var_value, "value", "stocks")
store_var_results(datetime.now().date(), portfolio_var_value, "value", "portfolio")

# Print results
print("Crypto VaR (95% confidence):", crypto_var)
print("Stocks VaR (95% confidence):", stock_var)
print("Portfolio VaR (95% confidence):", portfolio_var)
print("Crypto VaR in Value (95% confidence):", crypto_var_value)
print("Stocks VaR in Value (95% confidence):", stock_var_value)
print("Portfolio VaR in Value (95% confidence):", portfolio_var_value)

# Close the connection
conn.close()
