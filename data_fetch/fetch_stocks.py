import yfinance as yf
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
import time
from datetime import datetime  # Import datetime module

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

# Fetch all stock assets from the 'assets' table
cursor.execute("SELECT asset_id, asset_name FROM assets WHERE asset_type = 'stock'")
stocks = cursor.fetchall()  # Returns a list of tuples (asset_id, asset_name)

# Set the date range
start_date = "2024-01-01"
end_date = datetime.now().strftime("%Y-%m-%d")  # Convert to string formatted as 'YYYY-MM-DD'

for asset_id, ticker in stocks:
    try:
        print(f"Fetching data for {ticker} (asset_id: {asset_id})")
        # Fetch stock data
        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            print(f"No data found for {ticker}. Skipping...")
            continue

        # Flatten multi-level columns if necessary
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)  # Keep first-level column names

        # Reset index to make 'Date' a column
        data = data.reset_index()

        # Rename columns to match database columns
        data = data.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'Close': 'close',
            'High': 'high',
            'Low': 'low',
            'Volume': 'volume',
        })

        # Ensure the 'date' column is in proper datetime format
        data['date'] = pd.to_datetime(data['date'], errors='coerce')

        # Drop rows where 'date' is invalid
        data = data.dropna(subset=['date'])

        # Handle missing data
        data = data.replace({pd.NA: None})

        # Keep only the necessary columns
        data = data[['date', 'open', 'close', 'high', 'low', 'volume']]

        # Insert data into the database
        for _, row in data.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO market_data (asset_id, date, open, close, high, low, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (asset_id, date) DO NOTHING
                """, (
                    asset_id,
                    row['date'].to_pydatetime() if hasattr(row['date'], 'to_pydatetime') else row['date'],
                    float(row['open']) if pd.notna(row['open']) else None,
                    float(row['close']) if pd.notna(row['close']) else None,
                    float(row['high']) if pd.notna(row['high']) else None,
                    float(row['low']) if pd.notna(row['low']) else None,
                    int(row['volume']) if pd.notna(row['volume']) else None
                ))
            except Exception as row_error:
                print(f"Error inserting row for {ticker} on {row['date']}: {row_error}")
                conn.rollback()

        # Commit after each stock
        conn.commit()
        print(f"Data for {ticker} inserted successfully.")

        # Optional: Sleep to respect API rate limits
        time.sleep(1)

    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        conn.rollback()
        continue

print("Data fetching completed.")
conn.close()