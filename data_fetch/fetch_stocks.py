import yfinance as yf
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

# Fetch stock data
ticker = "AAPL"  # Apple stock
data = yf.download(ticker, start="2023-01-01", end="2023-12-31")

# Flatten multi-level columns
data.columns = data.columns.droplevel(0)  # Keep only the second level (Ticker)
data.columns.name = None  # Remove the name of the index
print(data.head())

# Rename columns
data.columns = ['Open', 'Close', 'High', 'Low', 'Volume', 'Adj Close']
print(data.head())

# Iterate over rows and insert into the database
for date, row in data.iterrows():
    cursor.execute("""
        INSERT INTO market_data (asset_id, date, open, close, high, low, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        3,  # Apple asset_id
        date,  # Use the index as the date
        None if pd.isna(row['Open']) else float(row['Open']),
        None if pd.isna(row['Close']) else float(row['Close']),
        None if pd.isna(row['High']) else float(row['High']),
        None if pd.isna(row['Low']) else float(row['Low']),
        None if pd.isna(row['Volume']) else float(row['Volume']),
    ))

conn.commit()
conn.close()