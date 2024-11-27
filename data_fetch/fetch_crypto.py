import requests

# Connect to the database
conn = psycopg2.connect(
    host="your-rds-endpoint",
    database="postgres",
    user="your-username",
    password="your-password"
)
cursor = conn.cursor()

# Fetch crypto data
url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
params = {'vs_currency': 'usd', 'days': '30'}  # Last 30 days
response = requests.get(url, params=params)
data = response.json()

for i, row in enumerate(data['prices']):
    date = datetime.utcfromtimestamp(row[0] / 1000).date()
    price = row[1]
    volume = data['total_volumes'][i][1]
    cursor.execute("""
        INSERT INTO market_data (asset_id, date, open, close, high, low, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        1,  # Bitcoin asset_id from the `assets` table
        date,
        price,
        price,  # Use the same price for open/close/high/low
        price,
        price,
        volume
    ))

conn.commit()
conn.close()