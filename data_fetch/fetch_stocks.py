import yfinance as yf
import psycopg2
from datetime import datetime

# Connect to the database
conn = psycopg2.connect(
    host="your-rds-endpoint",
    database="postgres",
    user="your-username",
    password="your-password"
)
cursor = conn.cursor()

# Fetch stock data
ticker = "AAPL"  # Apple stock
data = yf.download(ticker, start="2023-01-01", end="2023-12-31")
for date, row in data.iterrows():
    cursor.execute("""
        INSERT INTO market_data (asset_id, date, open, close, high, low, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        3,  # Apple asset_id from the `assets` table
        date,
        row['Open'],
        row['Close'],
        row['High'],
        row['Low'],
        row['Volume']
    ))

conn.commit()
conn.close()