import requests
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime
import time

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

# Fetch all crypto assets from the 'assets' table
cursor.execute("SELECT asset_id, asset_name FROM assets WHERE asset_type = 'crypto'")
cryptos = cursor.fetchall()  # Returns a list of tuples (asset_id, asset_name)

# Iterate through each crypto asset and fetch its market data
for asset_id, crypto_name in cryptos:
    try:
        print(f"Fetching data for {crypto_name} (asset_id: {asset_id})")
        
        # Fetch crypto data from CoinGecko API
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_name.lower()}/market_chart"
        params = {'vs_currency': 'usd', 'days': '30'}  # Last 30 days
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Failed to fetch data for {crypto_name}: {response.status_code} - {response.text}")
            continue
        
        data = response.json()
        
        # Insert cryptocurrency prices
        for i, row in enumerate(data['prices']):
            date = datetime.utcfromtimestamp(row[0] / 1000).date()
            price = row[1]
            volume = data['total_volumes'][i][1] if data['total_volumes'][i][1] is not None else 0
            cursor.execute("""
                INSERT INTO market_data (asset_id, date, open, close, high, low, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (asset_id, date) DO NOTHING
            """, (
                asset_id,
                date,
                price,
                price,  # Use the same price for open/close/high/low
                price,
                price,
                volume
            ))
        # Commit after each cryptocurrency
        conn.commit()
        print(f"Data for {crypto_name} inserted successfully.")
        
        # Optional: Sleep to respect API rate limits
        time.sleep(1)
    
    except Exception as e:
        print(f"Error occurred while processing {crypto_name}: {e}")
        conn.rollback()
        continue

# Close the database connection
conn.close()
print("Crypto data fetching completed.")