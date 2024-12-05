import requests
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

# Ensure Bitcoin asset_id exists
cursor.execute("SELECT 1 FROM assets WHERE asset_id = %s", (1,))
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO assets (asset_id, asset_name) VALUES (%s, %s)", (1, 'Bitcoin'))
    conn.commit()

# Fetch crypto data
url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
params = {'vs_currency': 'usd', 'days': '30'}  # Last 30 days
response = requests.get(url, params=params)
data = response.json()

# Insert cryptocurrency prices
try:
    for i, row in enumerate(data['prices']):
        date = datetime.utcfromtimestamp(row[0] / 1000).date()
        price = row[1]
        volume = data['total_volumes'][i][1] if data['total_volumes'][i][1] is not None else 0
        cursor.execute("""
            INSERT INTO market_data (asset_id, date, open, close, high, low, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            1,  # Bitcoin asset_id
            date,
            price,
            price,  # Use the same price for open/close/high/low
            price,
            price,
            volume
        ))
    conn.commit()
except Exception as e:
    conn.rollback()
    print(f"Error occurred: {e}")